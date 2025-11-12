import random
import logging
import os
from typing import Dict

from google import genai
from google.genai import types
from google.genai.errors import APIError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailClassifier:
    def __init__(self):
        
        self.client = None
        self.model_name = "gemini-2.5-flash" 
        self.ia_api_available = False
        
        try:
            gemini_key = os.getenv("GEMINI_API_KEY") 
            if gemini_key:
                self.client = genai.Client(api_key=gemini_key)
                self.ia_api_available = True 
                logger.info("Usando GEMINI API para IA em cloud (gemini-2.5-flash)")
            else:
                logger.warning("GEMINI_API_KEY não configurada. Usando fallback apenas com keywords.")
        except Exception as e:
            self.ia_api_available = False
            logger.error(f"Erro ao inicializar Gemini Client: {e}")
        
        self.productive_keywords = [
            'solicitação', 'solicitou', 'solicito', 'preciso', 'precisa', 'necessito',
            'problema', 'erro', 'bug', 'falha', 'não funciona', 'travou',
            'help', 'ajuda', 'suporte', 'técnico', 'urgente', 'prioridade',
            'status', 'atualização', 'andamento', 'progresso',
            'dúvida', 'pergunta', 'questão', 'informação', 'esclarecimento',
            'requisição', 'pendente', 'prazo', 'data', 'prazos',
            'dados', 'acesso', 'senha', 'login', 'autenticação', 'permissão',
            'ticket', 'caso', 'número', 'protocolo', 'id',
            'verificar', 'checar', 'confirmar', 'retorno', 'feedback',
            'alteração', 'mudança', 'atualizar', 'novo', 'criar', 'adicionar',
            'remover', 'deletar', 'modificar', 'corrigir', 'conserto',
            'reportar', 'relatar', 'comunicar', 'notificar', 'informar',
            'quando', 'como', 'por quê', 'qual', 'quem', 'onde',
            'transferência', 'pagamento', 'fatura', 'conta', 'saldo',
            'empréstimo', 'cartão', 'limite', 'taxa', 'juros', 'comissão', 'código',
            'desbloquear', 'bloquear', 'cancelar', 'suspender', 'reativar', 'reativação'
        ]
        
        self.unproductive_keywords = [
            'feliz', 'feliz natal', 'feliz ano novo', 'happy', 'merry christmas',
            'parabéns', 'aniversário', 'aniversariante', 'congratulations',
            'obrigado', 'agradecimento', 'agradeço', 'grato', 'gratidão', 'thanks',
            'abraço', 'abraços', 'beijo', 'beijos', 'hug',
            'saudações', 'cumprimento', 'olá', 'oi', 'hey', 'hello',
            'festa', 'celebração', 'happy hour', 'churrasco', 'confraternização',
            'feriado', 'férias', 'descanso', 'folga', 'viagem', 'turismo',
            'tv', 'cinema', 'filme', 'série', 'jogo', 'diversão', 'entreterimento',
            'chaves', 'comédia', 'humorístico', 'brincadeira', 'piada', 'joke',
            'boa sorte', 'sucesso', 'tudo bem', 'como vai', 'tudo certo',
            'ótimo', 'legal', 'massa', 'show', 'bacana', 'incrível', 'maravilhoso',
            'adorei', 'amei', 'fantástico', 'perfeito', 'sensacional',
            'compartilho', 'compartilhar', 'forward', 'fwd', 'encaminho',
            'achei legal', 'recomendo', 'dá uma olhada', 'veja', 'confira',
            'chave', 'promocode', 'voucher', 'cupom', 'desconto',
            'merda', 'porra', 'caralho', 'bosta', 'puta'
        ]

        self.templates = {
            "Produtivo": [
                "Obrigado por entrar em contato! Sua solicitação foi recebida e está sendo priorizada. Nossa equipe entrará em contato em breve.",
                "Recebemos sua mensagem! Um de nossos especialistas já está analisando e responderá em até 24 horas.",
                "Perfeito! Anotamos sua demanda e vamos verificar isso com urgência. Você receberá uma atualização em breve.",
                "Sua solicitação foi registrada no sistema. Nossa equipe técnica está investigando e fornecerá um feedback assim que possível.",
                "Entendido! Vamos trabalhar nisso imediatamente. Fique atento para nossas comunicações.",
                "Agradecemos os detalhes. Nosso time especializado está analisando sua solicitação neste momento.",
                "Excelente! Sua demanda foi aceita na fila de prioridades. Você será notificado sobre o progresso.",
                "Obrigado por reportar isso. Nossa equipe de suporte já está investigando o problema."
            ],
            "Improdutivo": [
                "Obrigado pela mensagem! Apreciamos muito o contato e os bons votos.",
                "Agradecemos genuinamente! Sua consideração significa muito para o nosso time.",
                "Muito obrigado! Continuaremos trabalhando para oferecer o melhor serviço.",
                "Agradecemos de coração! Estamos sempre aqui para ajudar quando precisar.",
                "Sua mensagem foi muito bem-vinda! Obrigado pelo apoio e confiança.",
                "Muito legal! Agradecemos pela amizade e continue contando conosco para suas necessidades.",
                "Obrigado pela atenção! Um grande abraço para você e sua equipe.",
                "Agradecemos sinceramente! Esperamos continuar servindo você com excelência."
            ]
        }
        
    def _classify_via_api(self, email_text: str) -> Dict:
        if not self.client:
            raise Exception("Cliente Gemini não inicializado.")

        prompt = f"""
        Classifique o email abaixo em uma das duas categorias: 'Produtivo' ou 'Improdutivo'.
        Produtivo: Requer uma ação, resposta técnica, solução de problema, ou tem caráter urgente.
        Improdutivo: Cumprimentos, agradecimentos, mensagens sociais, ou não requer ação imediata do time técnico.

        Sua resposta deve ser APENAS uma palavra: 'Produtivo' ou 'Improdutivo'.

        EMAIL:
        ---
        {email_text}
        ---
        """
        
        try:
            logger.info("Chamando Gemini API para classificação...")
            
            config = types.GenerateContentConfig(
                temperature=0.0,
                system_instruction="Você é um classificador de emails profissional e conciso. Retorne apenas a categoria.",
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            categoria_ia = response.text.strip().replace("'", "").title()
            
            if categoria_ia in ["Produtivo", "Improdutivo"]:
                confianca_score = 0.95
                return {
                    'labels': ["Produtivo", "Improdutivo"],
                    'scores': [confianca_score, 1 - confianca_score] if categoria_ia == "Produtivo" else [1 - confianca_score, confianca_score]
                }
            else:
                 logger.warning(f"Resposta inválida da IA: {response.text}. Usando fallback.")
                 return None
            
        except APIError as e:
            logger.error(f"Erro na API do Gemini: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro geral: {e}")
            return None

    def classify(self, email_text: str) -> Dict:
        
        if not email_text or len(email_text.strip()) < 5:
            raise ValueError("O texto do email é muito curto ou vazio para análise.")
        
        if len(email_text.strip()) > 5000:
            raise ValueError("O texto do email excede o limite de 5000 caracteres.")
        
        try:
            email_truncado = email_text[:512]
            
            if self.ia_api_available:
                try:
                    result_ia = self._classify_via_api(email_truncado)
                    
                    if result_ia and result_ia.get('labels'):
                        
                        categoria_ia = result_ia['labels'][0]
                        confianca_ia = round(result_ia['scores'][0] * 100, 2)
                        
                        logger.info(f"IA (Gemini): {categoria_ia} ({confianca_ia}%)")
                        
                        gemini_labels = ["Produtivo", "Improdutivo"]
                        if categoria_ia == "Improdutivo":
                            result_ia['scores'] = result_ia['scores'][::-1]
                        
                        logger.info(f"Usando classificação de IA (confiança: {confianca_ia}%)")
                        return {
                            "categoria": categoria_ia,
                            "confianca": confianca_ia,
                            "labels": gemini_labels,
                            "scores": [round(s * 100, 2) for s in result_ia['scores']],
                            "metodo": "gemini-api"
                        }
                    else:
                        logger.info("API da IA não retornou um resultado válido. Usando keywords como fallback.")
                
                except Exception as e:
                    logger.warning(f"Erro na API de IA: {e}. Usando fallback com keywords.")
            
            categoria_keyword, confianca_keyword = self._classify_by_keywords(email_text)
            
            logger.info(f"Usando Keywords: {categoria_keyword} ({confianca_keyword}%)")
            
            return {
                "categoria": categoria_keyword,
                "confianca": confianca_keyword,
                "labels": ["Produtivo", "Improdutivo"],
                "scores": [confianca_keyword if categoria_keyword == "Produtivo" else 100 - confianca_keyword, 
                          100 - confianca_keyword if categoria_keyword == "Produtivo" else confianca_keyword],
                "metodo": "keywords-fallback"
            }
            
        except Exception as e:
            logger.error(f"Erro na classificação: {str(e)}")
            raise

    def _classify_by_keywords(self, email_text: str) -> tuple:
        email_lower = email_text.lower()
        
        productive_count = sum(1 for kw in self.productive_keywords if kw in email_lower)
        unproductive_count = sum(1 for kw in self.unproductive_keywords if kw in email_lower)
        
        logger.info(f"   Palavras produtivas encontradas: {productive_count}")
        logger.info(f"   Palavras improdutivas encontradas: {unproductive_count}")
        
        if productive_count > unproductive_count:
            categoria = "Produtivo"
            confianca = min(60 + (productive_count * 10), 95)
        elif unproductive_count > productive_count:
            categoria = "Improdutivo"
            confianca = min(60 + (unproductive_count * 10), 95)
        else:
            if productive_count > 0:
                categoria = "Produtivo"
            else:
                categoria = "Improdutivo"
            confianca = 50
        
        return categoria, confianca

    def generate_response(self, categoria: str, email_text: str = "") -> str:
        if categoria not in self.templates:
            categoria = "Improdutivo"
        
        resposta = random.choice(self.templates[categoria])
        return resposta