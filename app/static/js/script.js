const emailForm = document.getElementById('emailForm');
const emailText = document.getElementById('emailText');
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');

const tabText = document.getElementById('tabText');
const tabUpload = document.getElementById('tabUpload');
const textTab = document.getElementById('textTab');
const uploadTab = document.getElementById('uploadTab');

const resultsSection = document.getElementById('resultsSection');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');

const categoryText = document.getElementById('categoryText');
const confidenceText = document.getElementById('confidenceText');
const responseBox = document.getElementById('responseBox');
const categoryBadge = document.getElementById('categoryBadge');

const copyBtn = document.getElementById('copyBtn');
const newClassificationBtn = document.getElementById('newClassificationBtn');
const exampleProductive = document.getElementById('exampleProductive');
const exampleUnproductive = document.getElementById('exampleUnproductive');

let selectedFile = null;

const examples = {
    productive: `Prezados,

Gostaria de verificar o status da minha solicitação #12345 que foi aberta na semana passada para acesso ao sistema financeiro.

A equipe mencionou que o prazo seria de 3 dias úteis, mas ainda não recebi retorno.

Poderiam me dar uma atualização sobre o andamento?

Obrigado pela atenção.

Atenciosamente,
João Silva`,
    
    unproductive: `Olá a todos!

Queria aproveitar para desejar a toda equipe um Feliz Natal e um próspero Ano Novo!

Que 2026 seja repleto de conquistas e realizações para todos nós!

Um grande abraço,
Maria Santos`
};


tabText.addEventListener('click', () => {
    switchTab('text');
});

tabUpload.addEventListener('click', () => {
    switchTab('upload');
});


fileInput.addEventListener('change', handleFileSelection);


exampleProductive.addEventListener('click', () => {
    emailText.value = examples.productive;
    switchTab('text');
    emailText.focus();
});

exampleUnproductive.addEventListener('click', () => {
    emailText.value = examples.unproductive;
    switchTab('text');
    emailText.focus();
});


copyBtn.addEventListener('click', copyResponse);
newClassificationBtn.addEventListener('click', resetForm);


emailForm.addEventListener('submit', handleFormSubmit);

function switchTab(tabName) {
    if (tabName === 'text') {
        tabText.classList.add('active');
        tabUpload.classList.remove('active');
        textTab.style.display = 'block';
        uploadTab.style.display = 'none';
    } else if (tabName === 'upload') {
        tabUpload.classList.add('active');
        tabText.classList.remove('active');
        textTab.style.display = 'none';
        uploadTab.style.display = 'block';
    }
}

function handleFileSelection(event) {
    const file = event.target.files[0];
    const validTypes = ['text/plain', 'application/pdf'];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (!file) {
        fileName.textContent = '';
        fileName.className = '';
        selectedFile = null;
        return;
    }

    if (!validTypes.includes(file.type)) {
        showError('Tipo de arquivo inválido. Use .txt ou .pdf');
        fileInput.value = '';
        selectedFile = null;
        fileName.textContent = '';
        fileName.className = '';
        return;
    }

    if (file.size > maxSize) {
        showError('Tamanho do arquivo excede 5MB');
        fileInput.value = '';
        selectedFile = null;
        fileName.textContent = '';
        fileName.className = '';
        return;
    }

    selectedFile = file;
    hideError();
    
    fileName.innerHTML = `
        <div class="file-success">
            ✅ Arquivo enviado: <strong>${file.name}</strong> (${formatFileSize(file.size)})
        </div>
    `;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function handleFormSubmit(event) {
    event.preventDefault();
    hideError();

    const isTextTab = tabText.classList.contains('active');

    try {
        if (isTextTab) {

            const text = emailText.value.trim();

            if (!text) {
                showError('Por favor, digite ou cole um email para classificar.');
                return;
            }

            if (text.length < 10) {
                showError('O email é muito curto. Forneça um email com pelo menos 10 caracteres.');
                return;
            }

            showLoading();
            await classifyViaText(text);

        } else {

            if (!selectedFile) {
                showError('Por favor, selecione um arquivo para classificar.');
                return;
            }

            showLoading();
            await classifyViaFile(selectedFile);
        }

    } catch (error) {
        console.error('Erro:', error);
        showError('Erro ao classificar o email. Tente novamente.');
    } finally {
        hideLoading();
    }
}

async function classifyViaText(text) {
    const formData = new FormData();
    formData.append('email_text', text);

    const response = await fetch('http://localhost:8000/classify', {
    method: 'POST',
    body: formData
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erro ao processar o email');
    }

    const result = await response.json();
    displayResults(result, text);
}

async function classifyViaFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://localhost:8000/classify', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erro ao processar o arquivo');
    }

    const result = await response.json();
    const preview = result.email_preview;
    displayResults(result, preview);
}

function displayResults(result, emailPreview) {
    if (result.error) {
        showError(result.error);
        return;
    }

    const categoria = result.categoria.toLowerCase();
    const confianca = result.confianca;
    const resposta = result.resposta_automatica || result.resposta_sugerida;

    categoryBadge.className = 'category-badge';
    if (categoria === 'produtivo') {
        categoryBadge.classList.add('produtivo');
    } else {
        categoryBadge.classList.add('improdutivo');
    }

    categoryText.textContent = result.categoria;
    confidenceText.textContent = `${confianca}% de confiança`;

    const preview = typeof emailPreview === 'string' && emailPreview.length > 150
        ? emailPreview.substring(0, 150) + '...'
        : emailPreview;
    document.getElementById('emailPreview').textContent = preview;

    responseBox.textContent = resposta;

    resultsSection.style.display = 'block';
    document.querySelector('.form-section').style.display = 'none';

    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function copyResponse() {
    const text = responseBox.textContent;

    navigator.clipboard.writeText(text).then(() => {
        const originalText = copyBtn.textContent;
        copyBtn.textContent = '✓ Copiado!';
        copyBtn.disabled = true;

        setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.disabled = false;
        }, 2000);
    }).catch(() => {
        showError('Erro ao copiar resposta. Tente novamente.');
    });
}

function resetForm() {
    emailText.value = '';
    
    fileInput.value = '';
    fileName.textContent = '';
    selectedFile = null;

    switchTab('text');

    document.querySelector('.form-section').style.display = 'block';
    resultsSection.style.display = 'none';

    hideError();

    emailText.focus();

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showLoading() {
    loading.style.display = 'block';
}

function hideLoading() {
    loading.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function hideError() {
    errorMessage.style.display = 'none';
}