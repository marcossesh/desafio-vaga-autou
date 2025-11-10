from transformers import pipeline
import random
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailClassifier:
    def __init__(self):
        try:
            logger.info("Carregando modelos de IA...")

            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1 #Você pode alterar para 0 se quiser usar GPU
            )

            self.generator = pipeline(
                "text-generation",
                model="gpt2",
                device=-1
            )

            logger.info("Modelos carregados com sucesso")

        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
            raise

        self.templates = {
            "Produtivo": [
                "Obrigado pelo contato! Estamos analisando sua solicitação.",
                "Recebemos seu email. Nossa equipe está trabalhando nisso.",
                "Ótimo, vamos verificar isso e retornaremos em breve."
            ],
            "Improdutivo": [
                "Muito obrigado pelo seu contato! Apreciamos.",
                "Agradecemos a mensagem! Tudo bem com você?",
                "Obrigado! Voltaremos em breve com atualizações."
            ]
        }

    def classify(self, email_text: str) -> Dict:

        if not email_text or len(email_text.strip()) < 5:
            raise ValueError("O texto do email é muito curto ou vazio para análise.")
        
        try:
            email_truncado = email_text[:512]

            result = self.classifier(
                email_truncado,
                candidate_labels=["Produtivo", "Improdutivo"],
                hypothesis_template="Este email é {}"
            )

            return {
                "categoria": result['labels'][0],
                "confianca": round(result['scores'][0] * 100, 2),
                "labels": result['labels'],
                "scores": [round(s * 100, 2) for s in result['scores']]
            }

        except Exception as e:
            logger.error(f"Erro na classificação: {e}")
            raise

    def generate_response(self, categoria: str, email_text: str = "")-> str:

        if categoria not in self.templates:
            logger.warning(f"Categoria desconhecida: {categoria}. Usando 'Improdutivo' como padrão.")
            categoria = "Improdutivo"
        
        resposta = random.choice(self.templates[categoria])
        logger.info(f"Resposta gerada para categoria {categoria}: {resposta}")
        return resposta