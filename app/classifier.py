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
                    device=-1
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
            # Solicitações de status/ação
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
            # Felicitações/Cumprimentos
            'feliz', 'feliz natal', 'feliz ano novo', 'happy', 'merry christmas',
            'parabéns', 'aniversário', 'aniversariante', 'congratulations',
            'obrigado', 'agradecimento', 'agradeço', 'grato', 'gratidão', 'thanks',
            'abraço', 'abraços', 'beijo', 'beijos', 'hug',
            'saudações', 'cumprimento', 'olá', 'oi', 'hey', 'hello',
            
            # Lazer/Entretenimento
            'festa', 'celebração', 'happy hour', 'churrasco', 'confraternização',
            'feriado', 'férias', 'descanso', 'folga', 'viagem', 'turismo',
            'tv', 'cinema', 'filme', 'série', 'jogo', 'diversão', 'entreterimento',
            'chaves', 'comédia', 'humorístico', 'brincadeira', 'piada', 'joke',
            
            # Expressões genéricas
            'boa sorte', 'sucesso', 'tudo bem', 'como vai', 'tudo certo',
            'ótimo', 'legal', 'massa', 'show', 'bacana', 'incrível', 'maravilhoso',
            'adorei', 'amei', 'fantástico', 'perfeito', 'sensacional',
            
            # Compartilhamentos sem ação
            'compartilho', 'compartilhar', 'forward', 'fwd', 'encaminho',
            'achei legal', 'recomendo', 'dá uma olhada', 'veja', 'confira',
            
            # Documentos/Ofertas externas (não são solicitações de suporte)
            'chave', 'promocode', 'voucher', 'cupom', 'desconto'

            #Palavras de baixo calão
            'merda', 'porra', 'caralho', 'bosta', 'puta'
        ]

        self.templates = {
            "Produtivo": [
                "Obrigado pelo contato! Estamos analisando sua solicitação.",
                "Recebemos seu email. Nossa equipe está trabalhando nisso.",
                "Ótimo, vamos verificar isso e retornaremos em breve.",
                "Recebido! Vamos priorizando sua solicitação.",
                "Agradecemos os detalhes. Estamos investigando isso agora.",
                "Perfeito! Vamos avaliar sua solicitação e responder em breve.",
                "Entendido! Nossa equipe está verificando esse ponto agora.",
                "Muito bem, vamos trabalhar nessa demanda para você."
            ],
            "Improdutivo": [
                "Muito obrigado pelo seu contato! Apreciamos.",
                "Agradecemos a mensagem! Tudo bem com você?",
                "Obrigado! Voltaremos em breve com atualizações.",
                "Obrigado pelo carinho! Estamos aqui para ajudar.",
                "Agradeço sinceramente! Tenha um ótimo dia!",
                "Muito legal! Obrigado pelo carinho com a gente!",
                "Obrigado pela atenção! Um grande abraço!",
                "Agradecemos muito! Continue contando com a gente!"
            ]
        }

    def classify(self, email_text: str) -> Dict:
        if not email_text or len(email_text.strip()) < 5:
            raise ValueError("O texto do email é muito curto ou vazio para análise.")
        
        if len(email_text.strip()) > 5000:
            raise ValueError("O texto do email excede o limite de 5000 caracteres.")
        
        try:
            email_truncado = email_text[:512]
            
            result_ia = self.classifier(
                email_truncado,
                candidate_labels=["Produtivo", "Improdutivo"],
                hypothesis_template="Este email de suporte é uma solicitação que requer ação ou resposta específica do time de suporte: {}."
            )

            categoria_ia = result_ia['labels'][0]
            confianca_ia = round(result_ia['scores'][0] * 100, 2)
            
            logger.info(f"IA: {categoria_ia} ({confianca_ia}%)")
            logger.info(f"Labels: {result_ia['labels']}")
            logger.info(f"Scores: {[round(s * 100, 2) for s in result_ia['scores']]}")
                        
            categoria_keyword, confianca_keyword = self._classify_by_keywords(email_text)
            
            logger.info(f"Keywords: {categoria_keyword} ({confianca_keyword}%)")
            
            # Lógica Nova de decisão:
            # Se a IA tem baixa confiança (<70%), usa keywords como fallback
            if confianca_ia < 70:
                categoria_final = categoria_keyword
                confianca_final = confianca_keyword
                metodo = "keyword (IA com baixa confiança)"
                logger.info(f"Usando keywords porque IA tem {confianca_ia}% < 70%")
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
            # MUDANÇA IMPORTANTE: Quando há empate, classifica como IMPRODUTIVO
            # (padrão conservador para não perder solicitações reais)
            # Mas se houver mais produtivas, assume produtivo.
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