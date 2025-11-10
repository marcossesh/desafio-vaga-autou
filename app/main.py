from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from classifier import EmailClassifier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Classificador de Emails", description="Sistema de classificação de emails com IA para o Desafio", version="1.0")

#Serve para permitir requisições de qualquer origem (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Configurar pasta de arquivos estáticos (HTML, CSS, JS)
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend")), name="static")
classifier = EmailClassifier()

@app.get("/")
async def root():
    return {"message": "Email Classifier AI está online!"}

@app.post("/classify-email/")
async def classify_email(email_text: str = Form(None)):
    if not email_text:
        return JSONResponse(status_code=400, content={"error": "O campo 'email_text' é obrigatório."})
    
    try:
        classification_result = classifier.classify(email_text)
        response_message = classifier.generate_response(classification_result['categoria'], email_text)
        
        return {
            "classification": classification_result,
            "response_message": response_message
        }
    
    except ValueError as ve:
        logger.error(f"Valor inválido: {ve}")
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        logger.error(f"Erro ao classificar email: {e}")
        return JSONResponse(status_code=500, content={"error": "Erro interno do servidor ao classificar o email."})
    
@app.get("/")
async 