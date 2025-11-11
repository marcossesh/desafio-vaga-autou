from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
import PyPDF2
from io import BytesIO

from app.classifier import EmailClassifier


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Classificador de Emails",
    description="Sistema de classificação de emails com IA para o Desafio AutoU",
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

# Montar static files apenas se existir
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

classifier = EmailClassifier()
logger.info("Classificador carregado com sucesso!")


@app.get("/")
async def root():
    try:
        with open(TEMPLATES_DIR / "index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError as e:
        logger.error(f"index.html não encontrado! Erro: {str(e)}")
        return HTMLResponse(
            content=f"<h1>Erro: index.html não encontrado</h1>",
            status_code=404
        )

@app.post("/classify")
async def classify_email(
    email_text: str = Form(None),
    file: UploadFile = File(None)
):
    
    try:
        
        if email_text and file:
            logger.warning("Usuário enviou texto E arquivo")
            return JSONResponse(
                status_code=400,
                content={"error": "Envie apenas o texto do email ou um arquivo, não ambos."}
            )
        
        if not email_text and not file:
            logger.warning("Nenhum dado recebido")
            return JSONResponse(
                status_code=400,
                content={"error": "Por favor, envie o texto do email ou um arquivo (.txt ou .pdf)."}
            )
        
        
        if file:
            logger.info(f"Processando arquivo: {file.filename}")
            
            allowed_types = {'.txt': 'text/plain', '.pdf': 'application/pdf'}
            file_ext = Path(file.filename).suffix.lower()
            
            if file_ext not in allowed_types:
                logger.warning(f"Tipo de arquivo não permitido: {file_ext}")
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Tipo de arquivo não permitido. Use .txt ou .pdf"}
                )
            
            try:
                content = await file.read()
                
                if file_ext == '.txt':
                    email_text = content.decode('utf-8', errors='ignore')
                    logger.info(f"Arquivo TXT lido com sucesso ({len(email_text)} caracteres)")
                
                elif file_ext == '.pdf':
                    email_text = extract_text_from_pdf(content)
                    
                    if not email_text or len(email_text.strip()) < 5:
                        logger.warning("PDF vazio ou inválido")
                        return JSONResponse(
                            status_code=400,
                            content={"error": "Não foi possível extrair texto do PDF. Verifique se o arquivo é válido."}
                        )
                    
                    logger.info(f"Arquivo PDF processado com sucesso ({len(email_text)} caracteres)")
            
            except UnicodeDecodeError:
                logger.error("Erro ao decodificar arquivo")
                return JSONResponse(
                    status_code=400,
                    content={"error": "Erro ao ler o arquivo. Certifique-se de que é um arquivo de texto válido."}
                )
            except Exception as e:
                logger.error(f"Erro ao processar arquivo: {str(e)}")
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Erro ao processar arquivo: {str(e)}"}
                )
        
        
        email_text = email_text.strip() if email_text else ""
        
        if not email_text:
            logger.warning("Email vazio após processamento")
            return JSONResponse(
                status_code=400,
                content={"error": "O email está vazio. Forneça um conteúdo válido."}
            )
        
        if len(email_text) < 10:
            logger.warning(f"Email muito curto: {len(email_text)} caracteres")
            return JSONResponse(
                status_code=400,
                content={"error": "Email muito curto. Forneça pelo menos 10 caracteres."}
            )
        
        if len(email_text) > 5000:
            logger.warning(f"Email muito longo: {len(email_text)} caracteres")
            return JSONResponse(
                status_code=400,
                content={"error": "Email muito longo. Máximo 5000 caracteres."}
            )
                
        logger.info(f"Classificando email ({len(email_text)} caracteres)...")
        
        resultado = classifier.classify(email_text)
        categoria = resultado["categoria"]
        confianca = resultado["confianca"]
        
        logger.info(f"Email classificado como: {categoria} ({confianca}%)")
                
        logger.info(f"Gerando resposta automática...")
        resposta = classifier.generate_response(categoria, email_text)
        
        logger.info(f"Resposta gerada com sucesso!")
                
        return {
            "sucesso": True,
            "categoria": categoria,
            "confianca": confianca,
            "resposta_automatica": resposta,
            "email_preview": email_text[:200] + "..." if len(email_text) > 200 else email_text
        }
        
    except ValueError as ve:
        logger.warning(f"Erro de validação: {str(ve)}")
        return JSONResponse(
            status_code=400,
            content={"error": str(ve)}
        )
    
    except Exception as e:
        logger.error(f"Erro ao classificar email: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Erro interno do servidor ao processar o email. Tente novamente."}
        )

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "version": "1.0.0",
        "message": "Email Classifier AI está funcionando!"
    }

def extract_text_from_pdf(pdf_content: bytes) -> str:
    try:
        pdf_file = BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        if len(pdf_reader.pages) == 0:
            logger.warning("PDF vazio (sem páginas)")
            return ""
        
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                logger.info(f"   Página {page_num + 1} processada")
            except Exception as e:
                logger.warning(f"   Erro ao processar página {page_num + 1}: {str(e)}")
                continue
        
        return text.strip()
    
    except Exception as e:
        logger.error(f"Erro ao extrair texto do PDF: {str(e)}")
        raise ValueError(f"Erro ao processar PDF: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Iniciando servidor Email Classifier AI...")
    logger.info("Acesse: http://localhost:8000")
    logger.info("Documentação: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )