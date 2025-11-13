import random
import logging
import os
from typing import Dict, Optional
from google.genai.errors import ServerError, ClientError
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailClassifier:
    def __init__(self):
        self.client = None
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.ia_api_available = False
        
        try:
            from google import genai
            logger.info("google.genai importado com sucesso.")
            
            google_api_key = os.getenv("GOOGLE_API_KEY")
            if not google_api_key:
                logger.warning("GOOGLE_API_KEY não encontrada. Usando fallback por keywords.")
                self.ia_api_available = False
            else:
                try:
                    self.client = genai.Client(api_key=google_api_key)
                    logger.info("google.genai Client inicializado com API key.")
                    self.ia_api_available = True
                except Exception as e:
                    logger.error("Falha ao inicializar genai.Client: %s", e)
                    self.ia_api_available = False
                    
        except ImportError as e:
            logger.error("google-genai não instalado. Instale com: pip install google-genai")
            logger.error("Detalhes: %s", e)
            self.ia_api_available = False
        
        # Keywords para fallback
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
    
    def _classify_via_api(self, email_text: str) -> Optional[Dict]:
        if not self.ia_api_available or not self.client:
            raise Exception("Cliente Gemini não inicializado.")
        
        prompt = f"""
    Classifique o email abaixo em uma das duas categorias: 'Produtivo' ou 'Improdutivo'.
    Produtivo: Requer uma ação, resposta técnica, solução de problema, ou tem caráter urgente.
    Improdutivo: Cumprimentos, agradecimentos, mensagens sociais, ou não requer ação imediata do time técnico.
    Responda APENAS com uma das duas palavras: Produtivo ou Improdutivo.

    EMAIL:
    ---
    {email_text}
    ---
    """
        
        max_retries = 3
        base_delay = 2  # segundos
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Chamando Gemini API para classificação... (tentativa {attempt + 1}/{max_retries})")
                
                resp = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                
                logger.debug("Chamada models.generate_content executada com sucesso.")
                
                try:
                    text = resp.text
                except Exception:
                    try:
                        text = resp.candidates[0].content.parts[0].text
                    except Exception:
                        text = None
                
                if not text:
                    logger.warning("Resposta da API sem corpo textual.")
                    return None
                
                categoria_ia = str(text).strip().strip(" '\"").title()
                logger.info("Resposta bruta da IA: %s -> interpretado como: %s", text.strip(), categoria_ia)
                
                if categoria_ia in ["Produtivo", "Improdutivo"]:
                    confianca_score = 0.95
                    if categoria_ia == "Produtivo":
                        return {'labels': ["Produtivo", "Improdutivo"], 'scores': [confianca_score, 1 - confianca_score]}
                    else:
                        return {'labels': ["Produtivo", "Improdutivo"], 'scores': [1 - confianca_score, confianca_score]}
                else:
                    logger.warning("Resposta inválida da IA: %s. Usando fallback.", text)
                    return None
            
            except ServerError as e:
                if e.code in [500, 503]:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Erro {e.code} ({e.message}). Tentando novamente em {delay}s...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Erro na API do Gemini após {max_retries} tentativas: {e}")
                        return None
                else:
                    logger.error(f"Erro não recuperável na API do Gemini: {e}")
                    return None
            
            except ClientError as e:
                if e.code == 429:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limit atingido (429). Tentando novamente em {delay}s...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Rate limit excedido após {max_retries} tentativas.")
                        return None
                else:
                    logger.error(f"Erro de cliente na API: {e}")
                    return None
            
            except Exception as e:
                logger.exception(f"Erro inesperado na API do Gemini: {e}")
                return None
        
        return None
    
    def classify(self, email_text: str) -> Dict:
        if not email_text or len(email_text.strip()) < 10:
            raise ValueError("O texto do email é muito curto ou vazio para análise.")
        
        if len(email_text.strip()) > 5000:
            raise ValueError("O texto do email excede o limite de 5000 caracteres.")
        
        try:
            email_truncado = email_text[:512]
            
            if self.ia_api_available:
                try:
                    result_ia = self._classify_via_api(email_truncado)
                    if result_ia and result_ia.get('labels'):
                        scores = result_ia['scores']
                        labels = result_ia['labels']
                        
                        if not scores or not labels or len(scores) != len(labels):
                            logger.warning("Resultado IA malformado: %s", result_ia)
                        else:
                            max_idx = int(scores.index(max(scores)))
                            categoria_ia = labels[max_idx]
                            confianca_ia = round(scores[max_idx] * 100, 2)
                            
                            logger.info(f"IA (Gemini): {categoria_ia} ({confianca_ia}%)")
                            return {
                                "categoria": categoria_ia,
                                "confianca": confianca_ia,
                                "labels": labels,
                                "scores": [round(s * 100, 2) for s in scores],
                                "metodo": "gemini-api"
                            }
                    else:
                        logger.info("API da IA não retornou um resultado válido. Usando keywords como fallback.")
                except Exception as e:
                    logger.warning(f"Erro na API de IA: {e}. Usando fallback com keywords.")
            
            # Fallback: classificação por keywords
            categoria_keyword, confianca_keyword = self._classify_by_keywords(email_text)
            logger.info(f"Usando Keywords: {categoria_keyword} ({confianca_keyword}%)")
            
            return {
                "categoria": categoria_keyword,
                "confianca": confianca_keyword,
                "labels": ["Produtivo", "Improdutivo"],
                "scores": [
                    confianca_keyword if categoria_keyword == "Produtivo" else 100 - confianca_keyword,
                    100 - confianca_keyword if categoria_keyword == "Produtivo" else confianca_keyword
                ],
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
