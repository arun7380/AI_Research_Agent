// API Configuration
const API_BASE = 'http://localhost:8000/api/v1';
const WS_BASE = 'ws://localhost:8000/ws/chat';

let token = localStorage.getItem('nexus_token') || null;
let documents = [];

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initAuthModal();
  initFileUpload();
  initChat();
  initReportsAndSlides();
  loadDocuments();
  checkHealth();
});

// Tab Switching
function initTabs() {
  const tabs = document.querySelectorAll('.nav-tab');
  const contents = document.querySelectorAll('.tab-content');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      contents.forEach(c => c.classList.remove('active'));

      tab.classList.add('active');
      const targetId = `tab-${tab.dataset.tab}`;
      document.getElementById(targetId).classList.add('active');
    });
  });
}

// Health Check
async function checkHealth() {
  const statusEl = document.getElementById('backendStatus');
  try {
    const res = await fetch('http://localhost:8000/health');
    if (res.ok) {
      statusEl.innerHTML = '<span class="status-dot"></span> Backend Active';
    } else {
      statusEl.innerHTML = '<span class="status-dot" style="background:var(--warning)"></span> Server Issue';
    }
  } catch (e) {
    statusEl.innerHTML = '<span class="status-dot" style="background:var(--warning)"></span> Offline (Demo Mode)';
  }
}

// Auth Modal & Handlers
function initAuthModal() {
  const authBtn = document.getElementById('authBtn');
  const modal = document.getElementById('authModal');
  const closeBtn = document.getElementById('closeAuthModal');
  const loginTab = document.getElementById('loginTab');
  const signupTab = document.getElementById('signupTab');
  const fullNameGroup = document.getElementById('fullNameGroup');
  const authForm = document.getElementById('authForm');
  const authSubmitBtn = document.getElementById('authSubmitBtn');

  let isSignup = false;

  authBtn.addEventListener('click', () => modal.style.display = 'flex');
  closeBtn.addEventListener('click', () => modal.style.display = 'none');

  loginTab.addEventListener('click', () => {
    isSignup = false;
    loginTab.classList.add('active');
    signupTab.classList.remove('active');
    fullNameGroup.style.display = 'none';
    authSubmitBtn.textContent = 'Login';
  });

  signupTab.addEventListener('click', () => {
    isSignup = true;
    signupTab.classList.add('active');
    loginTab.classList.remove('active');
    fullNameGroup.style.display = 'flex';
    authSubmitBtn.textContent = 'Signup';
  });

  authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('authEmail').value;
    const password = document.getElementById('authPassword').value;
    const fullName = document.getElementById('authFullName').value;

    try {
      if (isSignup) {
        const res = await fetch(`${API_BASE}/auth/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ full_name: fullName, email, password })
        });
        if (!res.ok) throw new Error('Signup failed');
        alert('Signup successful! Please login.');
        loginTab.click();
      } else {
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        if (!res.ok) throw new Error('Login failed');
        const data = await res.json();
        token = data.access_token;
        localStorage.setItem('nexus_token', token);
        modal.style.display = 'none';
        authBtn.textContent = 'Logged In ✓';
        loadDocuments();
      }
    } catch (err) {
      alert(err.message);
    }
  });
}

// File Upload
function initFileUpload() {
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--accent-primary)';
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = 'var(--border-glow)';
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--border-glow)';
    if (e.dataTransfer.files.length) {
      uploadFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
      uploadFile(fileInput.files[0]);
    }
  });
}

async function uploadFile(file) {
  const progressContainer = document.getElementById('uploadProgress');
  const progressBar = document.getElementById('progressBar');
  progressContainer.style.display = 'block';
  progressBar.style.width = '30%';

  const formData = new FormData();
  formData.append('file', file);

  try {
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      headers,
      body: formData
    });

    progressBar.style.width = '100%';

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Upload failed');
    }

    const doc = await res.json();
    alert(`File uploaded and indexed successfully into FAISS! (${doc.total_chunks} chunks)`);
    loadDocuments();
  } catch (err) {
    alert(`Upload Error: ${err.message}`);
  } finally {
    setTimeout(() => { progressContainer.style.display = 'none'; progressBar.style.width = '0%'; }, 1000);
  }
}

// Load Documents
async function loadDocuments() {
  const tableBody = document.getElementById('docTableBody');
  const selector = document.getElementById('docSelector');

  try {
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/documents/`, { headers });
    if (!res.ok) return;

    documents = await res.json();

    if (documents.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center; color: var(--text-muted)">No documents uploaded yet.</td></tr>';
      return;
    }

    tableBody.innerHTML = '';
    selector.innerHTML = '<option value="">All Uploaded Documents</option>';

    documents.forEach(doc => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${doc.filename}</strong></td>
        <td><span class="badge">${doc.file_type.toUpperCase()}</span></td>
        <td>${(doc.file_size / 1024).toFixed(1)} KB</td>
        <td>${doc.total_chunks}</td>
        <td>${doc.embedding_model}</td>
        <td>${new Date(doc.created_at).toLocaleDateString()}</td>
      `;
      tableBody.appendChild(tr);

      const opt = document.createElement('option');
      opt.value = doc.id;
      opt.textContent = doc.filename;
      selector.appendChild(opt);
    });
  } catch (e) {
    console.log('Failed to fetch documents', e);
  }
}

// Chat & Agent Execution
function initChat() {
  const sendBtn = document.getElementById('sendBtn');
  const questionInput = document.getElementById('questionInput');

  sendBtn.addEventListener('click', sendQuestion);
  questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendQuestion();
    }
  });
}

async function sendQuestion() {
  const questionInput = document.getElementById('questionInput');
  const question = questionInput.value.trim();
  const docSelector = document.getElementById('docSelector');
  const docId = docSelector.value || null;

  if (!question) return;

  appendMessage('user', question);
  questionInput.value = '';

  // Highlight Planner Agent
  setAgentStep('planner');

  try {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    setAgentStep('research');
    setAgentStep('web');
    setAgentStep('memory');
    setAgentStep('citation');

    const res = await fetch(`${API_BASE}/chat/`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ question, document_id: docId })
    });

    setAgentStep('critic');

    if (!res.ok) throw new Error('Agent execution failed');

    const data = await res.json();
    setAgentStep('completed');
    appendMessage('assistant', data.answer, data.citations);

  } catch (err) {
    setAgentStep('error');
    appendMessage('assistant', `⚠️ Agent Error: ${err.message}`);
  }
}

function appendMessage(role, text, citations = []) {
  const container = document.getElementById('chatMessages');
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${role}-message`;

  const icon = role === 'user' ? '👤' : '🤖';
  let formattedText = typeof marked !== 'undefined' ? marked.parse(text) : text;

  if (citations.length) {
    formattedText += '<div style="margin-top:12px; font-size:12px; color:var(--accent-primary)"><strong>Citations:</strong><br>' + citations.join('<br>') + '</div>';
  }

  msgDiv.innerHTML = `
    <div class="avatar">${icon}</div>
    <div class="bubble">${formattedText}</div>
  `;

  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;
}

function setAgentStep(step) {
  const badge = document.getElementById('workflowStatusBadge');
  const nodes = ['planner', 'research', 'web', 'memory', 'citation', 'critic'];

  nodes.forEach(n => {
    const el = document.getElementById(`node-${n}`);
    if (el) el.classList.remove('active');
  });

  if (step === 'completed') {
    badge.textContent = 'Execution Good ✓';
    badge.style.background = 'rgba(16, 185, 129, 0.2)';
    return;
  }

  if (step === 'error') {
    badge.textContent = 'Error';
    badge.style.background = 'rgba(239, 68, 68, 0.2)';
    return;
  }

  badge.textContent = `Running: ${step.toUpperCase()} Node`;
  const activeNode = document.getElementById(`node-${step}`);
  if (activeNode) activeNode.classList.add('active');
}

// Reports & Slides
function initReportsAndSlides() {
  document.getElementById('generateReportBtn').addEventListener('click', async () => {
    const topic = document.getElementById('reportTopicInput').value.trim();
    if (!topic) return;

    const viewer = document.getElementById('reportViewer');
    viewer.innerHTML = '<div class="empty-state">🧠 Multi-Agent system compiling academic report...</div>';

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API_BASE}/reports/generate?topic=${encodeURIComponent(topic)}`, {
        method: 'POST',
        headers
      });

      const data = await res.json();
      viewer.innerHTML = typeof marked !== 'undefined' ? marked.parse(data.content_markdown) : data.content_markdown;
    } catch (e) {
      viewer.innerHTML = `<div class="empty-state">Failed to generate report: ${e.message}</div>`;
    }
  });

  document.getElementById('generateSlidesBtn').addEventListener('click', async () => {
    const topic = document.getElementById('slideTopicInput').value.trim();
    if (!topic) return;

    const viewer = document.getElementById('slidesViewer');
    viewer.innerHTML = '<div class="empty-state">📊 Generating presentation slide deck...</div>';

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API_BASE}/slides/generate?topic=${encodeURIComponent(topic)}`, {
        method: 'POST',
        headers
      });

      const data = await res.json();
      let slidesHtml = '<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">';
      data.slides.forEach(slide => {
        slidesHtml += `
          <div style="background: rgba(15,23,42,0.8); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px;">
            <span class="badge" style="margin-bottom:8px; display:inline-block">Slide ${slide.slide_number}</span>
            <h3 style="font-size:16px; margin-bottom:12px">${slide.title}</h3>
            <ul style="padding-left:16px; font-size:13px; color: var(--text-muted)">
              ${slide.bullets.map(b => `<li style="margin-bottom:6px">${b}</li>`).join('')}
            </ul>
          </div>
        `;
      });
      slidesHtml += '</div>';
      viewer.innerHTML = slidesHtml;
    } catch (e) {
      viewer.innerHTML = `<div class="empty-state">Failed to generate slides: ${e.message}</div>`;
    }
  });
}
