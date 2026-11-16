// Linux Hardware Assistant Frontend

const API_BASE = window.location.origin;

const chatMessagesContainer = document.getElementById('chat-messages-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const btnSend = document.getElementById('btn-send');
const inspectorContent = document.getElementById('inspector-content');

// Telemetry Elements
const teleCpu = document.getElementById('tele-cpu');
const teleRam = document.getElementById('tele-ram');
const teleDisk = document.getElementById('tele-disk');
const teleGpu = document.getElementById('tele-gpu');

document.addEventListener('DOMContentLoaded', () => {
  loadTelemetry();
  chatForm.addEventListener('submit', handleSend);
});

async function loadTelemetry() {
  try {
    const res = await fetch(`${API_BASE}/api/system/overview`);
    const data = await res.json();
    if (data.cpu) {
      teleCpu.textContent = data.cpu.model_name.replace("(R)", "").replace("(TM)", "").trim();
    }
    if (data.memory_slots) {
      const slots = data.memory_slots;
      teleRam.textContent = `${slots.installed_gb} GB (${slots.slots_used}/${slots.slots_total} Slots)`;
    }
    if (data.storage && data.storage.length > 0) {
      const d = data.storage[0];
      teleDisk.textContent = `${d.size_gb}GB ${d.is_nvme ? 'NVMe SSD' : 'Disk'}`;
    }
    if (data.pci && data.pci.gpus && data.pci.gpus.length > 0) {
      const discrete = data.pci.gpus.find(g => g.is_dedicated) || data.pci.gpus[0];
      teleGpu.textContent = discrete.description.replace("NVIDIA Corporation", "").replace("Intel Corporation", "").trim();
    }
  } catch (err) {
    console.error('Failed to load telemetry', err);
  }
}

async function handleSend(e) {
  if (e) e.preventDefault();
  const query = userInput.value.trim();
  if (!query) return;

  // Append user message
  appendMessage('user', query);
  userInput.value = '';
  btnSend.disabled = true;

  // Show thinking state
  const loadingId = appendMessage('assistant', '🔍 Inspecting system hardware tools...');

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query })
    });

    if (res.ok) {
      const data = await res.json();
      updateMessage(loadingId, data.answer);
      renderInspector(data);
    } else {
      const err = await res.json();
      updateMessage(loadingId, `Error: ${err.detail || 'Failed to inspect system'}`);
    }
  } catch (err) {
    console.error(err);
    updateMessage(loadingId, 'Network error contacting hardware agent.');
  } finally {
    btnSend.disabled = false;
    userInput.focus();
  }
}

window.askQuick = function(promptText) {
  userInput.value = promptText;
  handleSend();
};

function appendMessage(role, text) {
  const msgId = 'msg-' + Math.random().toString(36).substr(2, 9);
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.id = msgId;

  div.innerHTML = `
    <div class="msg-avatar">${role === 'user' ? '👤' : '🐧'}</div>
    <div class="msg-content">${escapeHtml(text)}</div>
  `;
  chatMessagesContainer.appendChild(div);
  chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
  return msgId;
}

function updateMessage(msgId, text) {
  const el = document.getElementById(msgId);
  if (el) {
    const content = el.querySelector('.msg-content');
    if (content) content.textContent = text;
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
  }
}

function renderInspector(data) {
  if (!data.tool_executions || data.tool_executions.length === 0) {
    inspectorContent.innerHTML = `
      <div class="empty-inspector">
        No external tools were required for this turn.
      </div>
    `;
    return;
  }

  inspectorContent.innerHTML = `
    <div style="font-size:12px; margin-bottom:8px; color:var(--text-muted);">
      <strong>Tools Invoked:</strong> ${data.selected_tools.join(', ')}
    </div>
    ${data.tool_executions.map(ex => `
      <div class="tool-run-card">
        <div class="tool-run-header">
          <span class="tool-cmd">$ ${escapeHtml(ex.command)}</span>
          <span class="tool-badge-success">exit: ${ex.exit_code}</span>
        </div>
        
        <div class="block-title">Raw Telemetry Output</div>
        <pre class="code-block">${escapeHtml(ex.raw_output)}</pre>

        <div class="block-title">Normalized Structured JSON</div>
        <pre class="code-block">${escapeHtml(JSON.stringify(ex.parsed_data, null, 2))}</pre>
      </div>
    `).join('')}
  `;
}

function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
