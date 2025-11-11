# 📧 Classificador de Emails - AutoU Challenge

Solução digital de **classificação automática de emails** utilizando **Inteligência Artificial e Processamento de Linguagem Natural (NLP)** para automatizar a leitura, categorização e geração de respostas automáticas de emails em ambiente corporativo.

> Uma aplicação web desenvolvida para otimizar o fluxo de comunicação empresarial, reduzindo o tempo de resposta e liberando a equipe para tarefas de maior valor agregado.

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Objetivos do Projeto](#objetivos-do-projeto)
- [Categorias de Classificação](#categorias-de-classificação)
- [Arquitetura Técnica](#arquitetura-técnica)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação e Configuração](#instalação-e-configuração)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Decisões Técnicas](#decisões-técnicas)
- [Deploy na Nuvem](#deploy-na-nuvem)
- [Exemplos de Uso](#exemplos-de-uso)
- [Troubleshooting](#troubleshooting)
- [Links Úteis](#links-úteis)
- [Contribuições](#contribuições)

---

## 🎯 Visão Geral

A **aplicação Classificador de Emails** foi desenvolvida para atender às necessidades de uma grande empresa do setor financeiro que processa um **alto volume de emails diariamente**. 

### Problema Identificado

- ❌ **Processamento manual:** Necessidade de uma pessoa dedicada apenas à leitura e categorização de emails
- ❌ **Baixa eficiência:** Alto volume resulta em demora nas respostas e possível perda de prioridade
- ❌ **Inconsistência:** Classificação manual pode variar conforme o operador

### Solução Proposta

- ✅ **Automatização inteligente** de classificação de emails
- ✅ **Geração de respostas automáticas** baseadas no contexto
- ✅ **Interface web intuitiva** para upload e processamento
- ✅ **API robusta** com documentação Swagger/OpenAPI

---

## 🎓 Objetivos do Projeto

1. **Classificar** automaticamente emails em categorias predefinidas
2. **Sugerir respostas automáticas** adequadas ao contexto de cada email
3. **Fornecer interface web** simples, intuitiva e responsiva
4. **Integrar tecnologias de IA** para melhoria contínua da classificação
5. **Disponibilizar aplicação** hospedada em ambiente de produção na nuvem

---

## 📂 Categorias de Classificação

### Produtivo ✅
Emails que **requerem ação ou resposta específica** e demandam processamento pela equipe.

**Exemplos:**
- Solicitações de suporte técnico
- Atualizações sobre casos em aberto
- Dúvidas sobre o sistema
- Requisições de acesso ou informações
- Relatos de bugs ou problemas técnicos
- Mudanças ou atualizações solicitadas

### Improdutivo ❌
Emails que **não necessitam de ação imediata** ou são apenas informativos/comemoratives.

**Exemplos:**
- Mensagens de felicitações (Feliz Natal, Feliz Ano Novo)
- Agradecimentos simples
- Mensagens de cumprimento
- Celebrações e datas festivas
- Mensagens de boa sorte ou sucesso genérico

---

## 🏗️ Arquitetura Técnica

```
┌─────────────────────────────────────────────────────────┐
│                  FRONTEND (HTML/CSS/JS)                 │
│  • Interface web responsiva                             │
│  • Upload de arquivos (.txt, .pdf)                      │
│  • Entrada de texto direto                              │
│  • Exibição de resultados                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ HTTP/REST API
                 │
┌────────────────▼────────────────────────────────────────┐
│              BACKEND (FastAPI + Python)                 │
│  • Roteamento de requisições                            │
│  • Processamento de arquivos (PDF/TXT)                  │
│  • Orquestração de classificação                        │
│  • Geração de respostas automáticas                     │
└────────────────┬────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐  ┌────▼────┐  ┌───▼────┐
│  NLP  │  │ Keywords │  │ Models │
│ Pipeline│  │ Matcher │  │ Hugging│
│        │  │         │  │ Face   │
└────────┘  └─────────┘  └────────┘
```

---

## 🚀 Tecnologias Utilizadas

### Backend
- **FastAPI** (v0.104+) - Framework web moderno e rápido
- **Uvicorn** - ASGI server
- **Transformers** (Hugging Face) - Modelos de IA pré-treinados
  - `facebook/bart-large-mnli` - Classificação zero-shot
  - `gpt2` - Geração de texto (fallback)
- **PyPDF2** - Processamento de arquivos PDF
- **Python 3.9+**

### Frontend
- **HTML5** - Estrutura semântica
- **CSS3** - Estilização responsiva com variáveis CSS
- **JavaScript Vanilla** - Interatividade e integração com API

### DevOps & Hospedagem
- **Docker** (opcional)
- **Git/GitHub** - Versionamento
- Plataformas de deploy: Render, Railway, Replit, etc.

---

## 💾 Instalação e Configuração

### Pré-requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)
- Git
- Conexão com internet (para download de modelos)

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/marcossesh/email-classifier-autou.git
cd email-classifier-autou
```

### Passo 2: Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

**Conteúdo do `requirements.txt`:**
```
fastapi==0.104.1
uvicorn==0.24.0
transformers==4.35.0
torch==2.1.0
PyPDF2==3.0.1
python-multipart==0.0.6
```

### Passo 4: Executar Localmente

```bash
python main.py
```

A aplicação estará disponível em: **http://localhost:8000**

Documentação interativa em: **http://localhost:8000/docs** (Swagger UI)

---

## 🎨 Como Usar

### Pela Interface Web

1. **Acesse** a aplicação em http://localhost:8000
2. **Escolha uma opção:**
   - **Digitar ou Colar Texto:** Cole diretamente o conteúdo do email
   - **Upload de Arquivo:** Selecione um arquivo `.txt` ou `.pdf`
3. **Clique em "Classificar Email"**
4. **Visualize os resultados:**
   - Categoria atribuída (Produtivo/Improdutivo)
   - Nível de confiança da classificação
   - Resposta automática sugerida
   - Preview do email analisado
5. **Copie a resposta** ou faça uma nova classificação

### Via API (cURL)

#### Classificar via texto:

```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email_text=Prezados, gostaria de verificar o status da minha solicitação #12345. Poderiam me dar uma atualização?"
```

#### Classificar via arquivo:

```bash
curl -X POST "http://localhost:8000/classify" \
  -F "file=@email.txt"
```

#### Resposta esperada:

```json
{
  "sucesso": true,
  "categoria": "Produtivo",
  "confianca": 87.5,
  "resposta_automatica": "Obrigado pelo contato! Estamos analisando sua solicitação.",
  "email_preview": "Prezados, gostaria de verificar o status da minha..."
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

---

## 📁 Estrutura do Projeto

```
email-classifier-autou/
├── app/
│   ├── __init__.py
│   ├── classifier.py          # Lógica principal de classificação
│   └── static/
│       ├── css/
│       │   └── style.css      # Estilos da interface
│       └── js/
│           └── script.js      # Lógica do frontend
├── main.py                    # Aplicação FastAPI
├── requirements.txt           # Dependências do projeto
├── README.md                  # Este arquivo
└── .gitignore               # Arquivos ignorados pelo Git
```

### Descrição dos Arquivos Principais

| Arquivo | Descrição |
|---------|-----------|
| `main.py` | Servidor FastAPI com rotas e lógica de processamento |
| `app/classifier.py` | Classe EmailClassifier com lógica de NLP |
| `app/static/index.html` | Interface web responsiva |
| `app/static/css/style.css` | Estilos CSS moderno e responsivo |
| `app/static/js/script.js` | Lógica interativa do frontend |

---

## 🤖 Decisões Técnicas

### 1. **Modelo de Classificação**

**Escolha:** Facebook BART Large MNLI (Zero-Shot Classification)

**Motivo:**
- ✅ Não requer treinamento específico
- ✅ Funciona com categorias customizáveis
- ✅ Alta acurácia em classificação de texto
- ✅ Disponível via Hugging Face Transformers

**Fallback com Keywords:**
Se a confiança do modelo for inferior a 60%, o sistema utiliza análise de palavras-chave como mecanismo de fallback para garantir classificação confiável.

### 2. **Geração de Respostas**

**Escolha:** Templates predefinidos por categoria

**Motivo:**
- ✅ Respostas consistentes e apropriadas
- ✅ Reduz latência (sem gerar texto em tempo real)
- ✅ Fácil manutenção e atualização
- ✅ Alinhamento com políticas da empresa

*Nota: Implementação futura pode integrar GPT-2 ou modelos maiores para geração dinâmica.*

### 3. **Processamento de Arquivos**

**PDF:**
- Extrai texto com PyPDF2
- Concatena conteúdo de múltiplas páginas
- Valida se PDF contém texto legível

**TXT:**
- Decodificação com tratamento de erro UTF-8
- Leitura direta do arquivo

### 4. **Arquitetura do Backend**

**FastAPI:**
- ✅ Tipagem estática com Pydantic
- ✅ Documentação automática com Swagger
- ✅ Performance superior
- ✅ Suporte nativo a CORS
- ✅ Fácil integração com IA

### 5. **Frontend Responsivo**

**Tecnologias:**
- HTML5 semântico
- CSS3 com variáveis customizáveis
- JavaScript Vanilla (sem dependências externas)
- Design Mobile-First
- Experiência offline-ready

---

### Docker

Crie um `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build e execute:

```bash
docker build -t email-classifier .
docker run -p 8000:8000 email-classifier
```

---

## 📊 Exemplos de Uso

### Exemplo 1: Email Produtivo

**Input:**
```
Prezados,

Gostaria de verificar o status da minha solicitação #12345 que foi aberta na semana passada para acesso ao sistema financeiro.

A equipe mencionou que o prazo seria de 3 dias úteis, mas ainda não recebi retorno.

Poderiam me dar uma atualização sobre o andamento?

Obrigado pela atenção.

Atenciosamente,
João Silva
```

**Output:**
```json
{
  "categoria": "Produtivo",
  "confianca": 92.45,
  "resposta_automatica": "Obrigado pelo contato! Estamos analisando sua solicitação.",
  "labels": ["Produtivo", "Improdutivo"],
  "scores": [92.45, 7.55]
}
```

### Exemplo 2: Email Improdutivo

**Input:**
```
Olá a todos!

Queria aproveitar para desejar a toda equipe um Feliz Natal e um próspero Ano Novo!

Que 2026 seja repleto de conquistas e realizações para todos nós!

Um grande abraço,
Maria Santos
```

**Output:**
```json
{
  "categoria": "Improdutivo",
  "confianca": 88.32,
  "resposta_automatica": "Muito obrigado pelo seu contato! Apreciamos.",
  "labels": ["Improdutivo", "Produtivo"],
  "scores": [88.32, 11.68]
}
```

---

## 🛠️ Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'transformers'"

**Solução:**
```bash
pip install transformers torch
```

### Problema: Modelo muito lento para carregar

**Causa:** Primeira execução baixa modelos do Hugging Face (~3GB)

**Solução:**
- Tenha paciência na primeira execução
- Ou use version pré-cacheado configurando `HF_HOME`

### Problema: PDF não é processado corretamente

**Solução:**
- Verifique se é um PDF com texto (não escaneado)
- Tente converter para `.txt` primeiro
- Limite a 5000 caracteres

### Problema: Erro CORS ao acessar de outro domínio

**Solução:**
- Já está configurado no `main.py` com `allow_origins=["*"]`
- Para produção, especifique domínios conhecidos

### Problema: Aplicação lenta na nuvem

**Soluções:**
- Considere usar modelo menor ou cache
- Aumente RAM/CPU da instância
- Implemente queue para processamento assíncrono

---

## ❓ FAQ

**P: Quanto tempo demora para classificar um email?**
R: Entre 1-3 segundos, dependendo do tamanho do email e disponibilidade de recursos.

**P: Qual é o tamanho máximo de arquivo?**
R: 5MB (configurável em `main.py`).

**P: Os emails são armazenados?**
R: Não. A aplicação processa e descarta. Apenas logs de classificação podem ser salvos.

**P: Posso customizar as categorias?**
R: Sim! Edite `classifier.py` e modifique `candidate_labels` e templates.

**P: Como melhorar a acurácia?**
R: Atualize keywords, refine templates ou retreine com dados específicos.

---

## 📚 Links Úteis

| Recurso | Link |
|---------|------|
| Repositório GitHub | https://github.com/marcossesh/email-classifier-autou |
| Vídeo Demonstrativo | [YouTube Link] |
| Aplicação Deployada | [URL da aplicação hospedada] |
| Documentação FastAPI | https://fastapi.tiangolo.com |
| Hugging Face | https://huggingface.co |
| Transformers Docs | https://huggingface.co/docs/transformers |

---

## 🤝 Contribuições

Contribuições são bem-vindas! Para contribuir:

1. **Fork** este repositório
2. **Crie uma branch** para sua feature (`git checkout -b feature/MinhaFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add MinhaFeature'`)
4. **Push** para a branch (`git push origin feature/MinhaFeature`)
5. **Abra um Pull Request**

---

## 📄 Licença

Este projeto foi desenvolvido para o **Desafio AutoU** e segue os termos especificados.

---

## 👨‍💻 Autor

**marcossesh**
- GitHub: [@marcossesh](https://github.com/marcossesh)
- Email: [marcosviniramos62@gmail.com]

---

## 🎉 Considerações Finais

Este projeto foi desenvolvido com foco em:

✅ **Qualidade técnica** - Código limpo e bem documentado
✅ **Experiência do usuário** - Interface intuitiva e responsiva
✅ **Eficiência** - Processamento rápido e confiável
✅ **Escalabilidade** - Pronto para ambientes de produção
✅ **Manutenibilidade** - Fácil adicionar novas features

---

**Última atualização:** Novembro 2025

---

*Se encontrar problemas, abra uma issue no repositório GitHub!* 🚀