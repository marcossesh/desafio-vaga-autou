import random
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    logger.info(f"Transformers não disponível: usando fallback com palavras-chave. ({e})")
    pipeline = None
    TRANSFORMERS_AVAILABLE = False

class EmailClassifier:
    def __init__(self):
        self.classifier = None
        self.generator = None
        if TRANSFORMERS_AVAILABLE:
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

        self.productive_keywords = [
            'solicitação', 'solicitou', 'preciso', 'precisa', 'problema', 'erro',
            'help', 'ajuda', 'suporte', 'técnico', 'urgente', 'status', 'atualização',
            'dúvida', 'pergunta', 'requisição', 'pendente', 'prazo', 'informação',
            'dados', 'acesso', 'bug', 'ticket', 'caso', 'número', 'protocolo',
            'andamento', 'verificar', 'checar', 'confirmar', 'retorno', 'feedback',
            'alteração', 'mudança', 'atualizar', 'novo', 'criar', 'adicionar',
            'remover', 'deletar', 'modificar', 'alterar', 'corrigir', 'reportar',
            'relatar', 'comunicar', 'notificar'
        ]
        
        self.unproductive_keywords = [
            'feliz', 'feliz natal', 'feliz ano novo', 'parabéns', 'aniversário',
            'obrigado', 'agradecimento', 'abraço', 'abraços', 'saudações',
            'cumprimento', 'festa', 'celebração', 'feriado', 'férias',
            'boa sorte', 'sucesso', 'tudo bem', 'como vai', 'tudo certo'
        ]

        self.templates = {
            "Produtivo": [
                "Obrigado pelo contato! Estamos analisando sua solicitação.",
                "Recebemos seu email. Nossa equipe está trabalhando nisso.",
                "Ótimo, vamos verificar isso e retornaremos em breve.",
                "Recebido! Vamos priorizando sua solicitação.",
                "Agradecemos os detalhes. Estamos investigando isso agora.",
                "Perfeito! Vamos avaliar sua solicitação e responder em breve."
            ],
            "Improdutivo": [
                "Muito obrigado pelo seu contato! Apreciamos.",
                "Agradecemos a mensagem! Tudo bem com você?",
                "Obrigado! Voltaremos em breve com atualizações.",
                "Obrigado pelo carinho! Estamos aqui para ajudar.",
                "Agradeço sinceramente! Tenha um ótimo dia!",
                "Muito legal! Obrigado pelo carinho com a gente!"
            ]
        }

    def classify(self, email_text: str) -> Dict:
        if not email_text or len(email_text.strip()) < 5:
            raise ValueError("O texto do email é muito curto ou vazio para análise.")
        
        try:
            
            email_truncado = email_text[:512]
            
            result_ia = self.classifier(
                email_truncado,
                candidate_labels=["Produtivo", "Improdutivo"],
                hypothesis_template="Este email é {}."
            )

            categoria_ia = result_ia['labels'][0]
            confianca_ia = round(result_ia['scores'][0] * 100, 2)
            
            logger.info(f"IA: {categoria_ia} ({confianca_ia}%)")
                        
            categoria_keyword, confianca_keyword = self._classify_by_keywords(email_text)
            
            logger.info(f"Keywords: {categoria_keyword} ({confianca_keyword}%)")
            
            if confianca_ia < 60:
                categoria_final = categoria_keyword
                confianca_final = confianca_keyword
                metodo = "keyword"
            else:
                categoria_final = categoria_ia
                confianca_final = confianca_ia
                metodo = "ia"
            
            logger.info(f"Resultado Final: {categoria_final} ({confianca_final}%) - Método: {metodo}")
            
            return {
                "categoria": categoria_final,
                "confianca": confianca_final,
                "labels": result_ia['labels'],
                "scores": [round(s * 100, 2) for s in result_ia['scores']]
            }
            
        except Exception as e:
            logger.error(f"Erro na classificação: {str(e)}")
            raise

    def _classify_by_keywords(self, email_text: str) -> tuple:
        """
        Classifica usando análise de palavras-chave
        Retorna: (categoria, confiança)
        """
        
        email_lower = email_text.lower()
        
        productive_count = sum(1 for kw in self.productive_keywords if kw in email_lower)
        unproductive_count = sum(1 for kw in self.unproductive_keywords if kw in email_lower)
        
        logger.info(f"   Palavras produtivas encontradas: {productive_count}")
        logger.info(f"   Palavras improdutivas encontradas: {unproductive_count}")
        
        if productive_count > unproductive_count:
            categoria = "Produtivo"
            confianca = min(60 + (productive_count * 15), 95)
        elif unproductive_count > productive_count:
            categoria = "Improdutivo"
            confianca = min(60 + (unproductive_count * 15), 95)
        else:
            categoria = "Produtivo"
            confianca = 50
        
        return categoria, confianca

    def generate_response(self, categoria: str, email_text: str = "") -> str:
        """Gera uma resposta automática baseada na categoria"""
        
        if categoria not in self.templates:
            categoria = "Improdutivo"
        
        resposta = random.choice(self.templates[categoria])
        
        return resposta