# 📧 Classificador de Emails com IA

Sistema inteligente de classificação automática de emails utilizando IA (Google Gemini) para categorizar mensagens como **Produtivas** ou **Improdutivas**, otimizando o gerenciamento de comunicações corporativas.

## 🎯 Funcionalidades

* **Classificação Inteligente**: Utiliza API do Google Gemini para análise contextual avançada
* **Fallback por Keywords**: Sistema de contingência baseado em palavras-chave caso a API esteja indisponível
* **Interface Responsiva**: Frontend moderno com suporte a tema claro/escuro
* **Upload de Arquivos**: Suporte para análise de arquivos `.txt` e `.pdf` (até 5MB)
* **Exemplos Práticos**: Exemplos pré-configurados para teste rápido
* **Respostas Automáticas**: Geração de respostas contextualizadas baseadas na categoria

## 🛠️ Tecnologias Utilizadas

### Backend

* **Python 3.x**
* **FastAPI**: Framework web de alta performance
* **Google Gemini API**: Modelo de IA para classificação (gemini-2.5-flash)
* **PyPDF2**: Extração de texto de arquivos PDF
* **python-dotenv**: Gerenciamento de variáveis de ambiente
* **NumPy 1.26.4**: Processamento numérico e compatibilidade

### Frontend

* **HTML5/CSS3**: Interface moderna e responsiva
* **JavaScript Vanilla**: Manipulação DOM e requisições assíncronas

## Video Demostrativo

[![Video Demonstrativo](https://www.youtube.com/watch?v=8nV4q6Qqn5w)](https://www.youtube.com/watch?v=8nV4q6Qqn5w)

## 📋 Pré-requisitos

* Python 3.8 ou superior
* Chave de API do Google Gemini (gratuita)
* pip (gerenciador de pacotes Python)
* Bash (para execução do script de setup automático)

## 🚀 Instalação e Execução Local

### Método 1: Setup Automático (Recomendado)

#### 1. Clone o repositório

git clone https://github.com/marcossesh/desafio-vaga-autou  
cd desafio-vaga-autou


#### 2. Crie um ambiente virtual

python -m venv venv
Windows

venv\Scripts\activate
Linux/Mac

source venv/bin/activate


#### 3. Execute o script de setup

Linux/Mac

chmod +x setup.sh
./setup.sh

Windows (Git Bash)

bash setup.sh


O script irá automaticamente:
* Atualizar pip, setuptools e wheel
* Instalar NumPy 1.26.4 para compatibilidade
* Instalar todas as dependências do requirements.txt

#### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

* GOOGLE_API_KEY=sua_chave_api_aqui

* GEMINI_MODEL=gemini-2.5-flash


**Como obter a chave da API Google Gemini**:
1. Acesse [Google AI Studio](https://aistudio.google.com/apikey)
2. Crie uma nova API Key
3. Copie e cole no arquivo `.env`

#### 5. Execute a aplicação

uvicorn main:app --reload --host 0.0.0.0 --port 8000


#### 6. Acesse no navegador

http://localhost:8000


### Método 2: Instalação Manual

#### 1. Clone e crie ambiente virtual

git clone https://github.com/marcossesh/desafio-vaga-autou  
cd desafio-vaga-autou  
python -m venv venv  
source venv/bin/activate # Linux/Mac


#### 2. Instale as dependências manualmente

Atualize pip

python -m pip install --upgrade pip setuptools wheel  
Instale NumPy primeiro (compatibilidade)  
pip install numpy==1.26.4  
Instale as demais dependências

pip install fastapi uvicorn python-dotenv PyPDF2 google-genai


#### 3. Configure o arquivo .env e execute

Siga os passos 4, 5 e 6 do Método 1.

## 📁 Estrutura do Projeto

projeto/  
│  
├── app/  
│ ├── static/  
│ │ ├── index.html # Interface principal  
│ │ └── script.js # Lógica frontend  
│ └── classifier.py # Motor de classificação IA  
│  
├── main.py # Servidor FastAPI  
├── setup.sh # Script de instalação automática  
├── requirements.txt # Dependências Python  
├── .env # Variáveis de ambiente (criar)  
└── README.md # Este arquivo  


## 📝 Como Usar

### Classificação por Texto

1. Na aba "Digitar Texto", cole ou digite o conteúdo do email
2. Clique em "Classificar Email"
3. Veja o resultado com categoria, confiança e resposta sugerida

### Classificação por Arquivo

1. Alterne para a aba "Upload de Arquivo"
2. Selecione um arquivo `.txt` ou `.pdf` (máximo 5MB)
3. Clique em "Classificar Email"
4. O sistema extrairá o texto e classificará automaticamente

### Exemplos Prontos

Clique nos botões de exemplo para testar classificações:
* **Email Produtivo**: Solicitação de suporte técnico
* **Email Improdutivo**: Mensagem de felicitações

## 🔍 Categorias de Classificação

### Produtivo

Emails que requerem ação, resposta técnica ou têm caráter urgente:
* Solicitações de suporte/ajuda
* Reportes de bugs/problemas
* Pedidos de informação/acesso
* Atualizações de status
* Questões financeiras/pagamentos

### Improdutivo

Emails que não requerem ação imediata:
* Cumprimentos e saudações
* Agradecimentos
* Mensagens comemorativas
* Conteúdo social/pessoal
* Forwards informativos

## 🤖 Sistema de Fallback

O sistema possui **dois métodos de classificação**:

1. **Gemini API** (Primário): Análise contextual avançada com ~95% de confiança
2. **Keywords** (Fallback): Classificação por palavras-chave quando a API está indisponível

O sistema **automaticamente** alterna para o fallback em caso de:
* API Key inválida ou ausente
* Erros de servidor (500, 503)
* Rate limit excedido (429)
* Falhas de rede

## 📊 Endpoints da API

### `GET /`

Retorna a interface HTML principal

### `POST /classify`

Classifica um email por texto ou arquivo

**Parâmetros**:
* `email_text` (opcional): Texto do email
* `file` (opcional): Arquivo .txt ou .pdf

**Resposta**:

{  
"categoria": "Produtivo",  
"confianca": 95.5,  
"resposta": "Obrigado por entrar em contato!...",  
"metodo": "gemini-api",  
"labels": ["Produtivo", "Improdutivo"],  
"scores": [95.5, 4.5]  
}  


### `GET /health`

Verifica o status do serviço

### `GET /readiness`

Verifica se os modelos de IA estão carregados

## ⚙️ Configurações Avançadas

### Variáveis de Ambiente

Obrigatórias

GOOGLE_API_KEY=sua_chave_aqui
Opcionais

GEMINI_MODEL=gemini-2.5-flash # Modelo Gemini a usar
PORT=8000 # Porta do servidor


### Limites e Validações

* Tamanho mínimo de texto: 10 caracteres
* Tamanho máximo de texto: 5000 caracteres
* Tamanho máximo de arquivo: 5MB
* Formatos aceitos: `.txt`, `.pdf`

## 🐛 Solução de Problemas

### Erro: "GOOGLE_API_KEY não encontrada"

**Solução**: Crie o arquivo `.env` com sua chave da API

### Erro: "google-genai não instalado"

**Solução**: Execute o script `setup.sh` ou `pip install google-genai`

### Erro de compatibilidade com NumPy

**Solução**: O script `setup.sh` instala automaticamente a versão compatível (1.26.4). Se instalou manualmente, execute:

pip install numpy==1.26.4


### Sistema usando fallback ao invés da IA

**Possíveis causas**:
* API Key inválida
* Limite de requisições excedido
* Problema de conexão com a internet

### Arquivo PDF não é processado

**Soluções**:
* Verifique se o PDF tem texto extraível (não imagem)
* Confirme que o arquivo não está corrompido
* Teste com um arquivo `.txt` primeiro

### Erro ao executar setup.sh no Windows

**Solução**: Use Git Bash ou WSL:

Git Bash

bash setup.sh
WSL

chmod +x setup.sh
./setup.sh


## 🔒 Segurança

O sistema implementa:
* **Sanitização de input**: Proteção contra XSS e SQL injection
* **Validação de arquivos**: Verificação de tipo e tamanho
* **HTML Escape**: Escape de caracteres perigosos
* **CORS configurado**: Controle de origens permitidas

## 📈 Performance

* **Carregamento assíncrono**: Modelos carregam em background na inicialização
* **Retry automático**: 3 tentativas com backoff exponencial em caso de falha
* **Timeout**: 30 segundos por requisição
* **Truncamento inteligente**: Primeiros 512 caracteres para análise rápida

## Testando a Instalação

Após seguir os passos de instalação, teste o sistema:

1. Verifique se o servidor está rodando

curl http://localhost:8000/health
2. Teste a classificação via API

curl -X POST http://localhost:8000/classify
-F "email_text=Preciso de ajuda urgente com meu login"
3. Acesse a interface web
Abra http://localhost:8000 no navegador


## Contribuindo

Sugestões de melhorias são bem-vindas! Sinta-se à vontade para:
* Reportar bugs
* Sugerir novas funcionalidades
* Melhorar a documentação
* Adicionar mais keywords ao fallback
* Otimizar o script de setup

## 📄 Licença

Este projeto está sob a licença MIT (ou sua licença preferida).

## 👥 Autor

Marcos Vinicius

---

**Nota**: Este sistema foi desenvolvido para fins educacionais/demonstrativos. Para uso em produção, considere implementar autenticação, rate limiting adicional e monitoramento robusto.

## Suporte

Para dúvidas ou problemas:
* Abra uma issue no repositório
* Entre em contato com a equipe de desenvolvimento
* Consulte a documentação da [API Google Gemini](https://ai.google.dev/docs)

---

**Desenvolvido usando FastAPI e Google Gemini**