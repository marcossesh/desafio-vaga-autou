#!/usr/bin/env python3
#classify agora retorna 503 enquanto os modelos estiverem carregando
# Usa PORT da env (para ambientes como DigitalOcean Apps / Render)

import os
import sys
import io
import re
import html
import logging
import threading
from pathlib import Path
from io import BytesIO

from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import PyPDF2

from dotenv import load_dotenv
load_dotenv()

# Tente não importar EmailClassifier até carregar em background


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email-classifier")

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

app = FastAPI(
    title="Classificador de Emails",
    description="Sistema de classificação de emails com IA",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

classifier = None
_model_ready = False
_model_lock = threading.Lock()


def is_ready() -> bool:
    return _model_ready


def set_ready(value: bool):
    global _model_ready
    with _model_lock:
        _model_ready = value


def load_models_background():

    global classifier

    try:
        logger.info("Carregando modelos de IA em background (pode demorar)...")
        # Import dinâmico para reduzir impacto na importação do módulo
        from app.classifier import EmailClassifier
        classifier = EmailClassifier()
        set_ready(True)
        logger.info("Modelos carregados com sucesso. Readiness OK.")
    except Exception as e:
        set_ready(False)
        logger.exception("Falha ao carregar modelos de IA: %s", e)


@app.on_event("startup")
def startup_event():

    logger.info("Startup: iniciando carregamento de modelos em background...")
    t = threading.Thread(target=load_models_background, daemon=True)
    t.start()

def sanitize_email_text(text: str) -> str:

    if text is None:
        return ""

    try:
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="replace")
    except Exception:
        text = str(text)

    text = str(text).strip()
    if not text:
        return ""

    dangerous_patterns = [
        r"<script[^>]*>.*?</script>",
        r"on\w+\s*=",
        r"javascript:",
        r"data:text/html",
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"INSERT\s+INTO",
        r"UPDATE\s+.*\s+SET",
        r"--",
        r"/\*.*?\*/",
    ]

    for pattern in dangerous_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

    text = html.escape(text, quote=True)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text


def extract_text_from_pdf(pdf_content: bytes) -> str:

    try:
        pdf_file = BytesIO(pdf_content)
        reader = PyPDF2.PdfReader(pdf_file)

        if len(reader.pages) == 0:
            logger.warning("PDF sem páginas.")
            return ""

        parts = []
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    parts.append(page_text)
                logger.debug("Página %d processada", i + 1)
            except Exception as e:
                logger.warning("Erro ao processar página %d: %s", i + 1, e)
                continue

        return "\n".join(parts).strip()
    except Exception as e:
        logger.exception("Erro ao extrair texto do PDF: %s", e)
        return ""

@app.get("/")
async def root():

    try:
        fpath = STATIC_DIR / "index.html"
        if fpath.exists():
            return HTMLResponse(content=fpath.read_text(encoding="utf-8"))
        else:
            return HTMLResponse(content="<h1>Email Classifier AI</h1><p>Index não encontrado.</p>", status_code=200)
    except Exception as e:
        logger.exception("Erro servindo index: %s", e)
        return HTMLResponse(content="<h1>Erro interno</h1>", status_code=500)


@app.get("/health")
async def health_check():

    return {"status": "alive", "version": "1.0.0"}


@app.get("/ready")
async def readiness_check():

    if is_ready():
        return {"status": "ready"}
    return JSONResponse(status_code=503, content={"status": "loading", "message": "Modelos ainda carregando"})


@app.post("/classify")
async def classify_email(email_text: str = Form(None), file: UploadFile = File(None)):

    if not is_ready():
        logger.info("Request de /classify recusado: modelos ainda carregando")
        return JSONResponse(status_code=503, content={"error": "Serviço iniciando — modelos ainda carregando. Tente novamente em alguns instantes."})

    if email_text and file:
        return JSONResponse(status_code=400, content={"error": "Envie apenas texto ou um arquivo, não ambos."})

    if not email_text and not file:
        return JSONResponse(status_code=400, content={"error": "Envie texto ou um arquivo (.txt ou .pdf)."})

    if file:
        filename = file.filename or ""
        ext = Path(filename).suffix.lower()
        if ext not in {".txt", ".pdf"}:
            return JSONResponse(status_code=400, content={"error": "Tipo de arquivo inválido. Use .txt ou .pdf."})

        try:
            raw = await file.read()
            if ext == ".txt":
                email_text = raw.decode("utf-8", errors="replace")
            else:
                email_text = extract_text_from_pdf(raw)
                if not email_text:
                    return JSONResponse(status_code=400, content={"error": "Não foi possível extrair texto do PDF."})
        except Exception as e:
            logger.exception("Erro lendo arquivo: %s", e)
            return JSONResponse(status_code=400, content={"error": f"Erro ao processar arquivo: {str(e)}"})

    email_text = sanitize_email_text(email_text) if email_text else ""
    if not email_text:
        return JSONResponse(status_code=400, content={"error": "O email está vazio após processamento."})

    if len(email_text) < 10:
        return JSONResponse(status_code=400, content={"error": "Email muito curto. Forneça pelo menos 10 caracteres."})

    if len(email_text) > 5000:
        return JSONResponse(status_code=400, content={"error": "Email muito longo. Máximo 5000 caracteres."})

    try:
        result = classifier.classify(email_text)
        categoria = result.get("categoria")
        confianca = result.get("confianca")
    except ValueError as ve:
        logger.warning("Validação do classifier: %s", ve)
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        logger.exception("Erro ao classificar: %s", e)
        return JSONResponse(status_code=500, content={"error": "Erro ao processar a classificação."})

    try:
        resposta = classifier.generate_response(categoria, email_text)
    except Exception:
        logger.exception("Erro ao gerar resposta automática")
        resposta = "Obrigado pelo contato! Estamos analisando sua solicitação."

    payload = {
        "sucesso": True,
        "categoria": categoria,
        "confianca": confianca,
        "resposta_automatica": resposta,
        "email_preview": (email_text[:200] + "...") if len(email_text) > 200 else email_text
    }
    return JSONResponse(status_code=200, content=payload, media_type="application/json; charset=utf-8")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    logger.info("Executando localmente em http://0.0.0.0:%s", port)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)