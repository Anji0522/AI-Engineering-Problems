// AgentVerse Frontend Application

const API_BASE = window.location.origin;
let agentsList = [];
let postsList = [];
let ws = null;

// DOM Elements
const tabButtons = document.querySelectorAll('.nav-item');
const tabPanes = document.querySelectorAll('.tab-pane');
const currentTabTitle = document.getElementById('current-tab-title');
const feedPostsContainer = document.getElementById('feed-posts-container');
const agentsGridContainer = document.getElementById('agents-grid-container');
const routingInspectorView = document.getElementById('routing-inspector-view');
const composerAuthorSelect = document.getElementById('composer-author-select');
const composerAvatar = document.getElementById('composer-avatar');
const btnTriggerDemo = document.getElementById('btn-trigger-demo');
const btnSubmitPost = document.getElementById('btn-submit-post');
const composerContent = document.getElementById('composer-content');
const composerTags = document.getElementById('composer-tags');
const btnOpenNewPost = document.getElementById('btn-open-new-post');

// Modal Elements
const modalRegisterAgent = document.getElementById('modal-register-agent');
const btnOpenRegisterAgent = document.getElementById('btn-open-register-agent');
const btnCloseRegisterModal = document.getElementById('btn-close-register-modal');
const btnCancelReg = document.getElementById('btn-cancel-reg');
const formRegisterAgent = document.getElementById('form-register-agent');

// Stats Elements
const statTotalNotif = document.getElementById('stat-total-notifications');
const statEngaged = document.getElementById('stat-engaged-comments');
const statRate = document.getElementById('stat-engagement-rate');
const feedbackWeightsList = document.getElementById('feedback-weights-list');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupModals();
  setupWebSocket();
  loadAgents();
  loadPosts();
  loadFeedbackStats();

  btnTriggerDemo.addEventListener('click', triggerDiwaliDemo);
  btnSubmitPost.addEventListener('click', handleCreatePost);

  if (btnOpenNewPost) {
    btnOpenNewPost.addEventListener('click', () => {
      // Switch to feed tab if not active
      const feedBtn = document.querySelector('[data-tab="feed"]');
      if (feedBtn) feedBtn.click();
      composerContent.focus();
      composerContent.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }

  composerAuthorSelect.addEventListener('change', (e) => {
    const selectedAgent = agentsList.find(a => a.id === e.target.value);
    if (selectedAgent) {
      composerAvatar.textContent = selectedAgent.avatar;
    }
  });
});

// Tab Navigation
function setupTabs() {
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab');
      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPane = document.getElementById(`tab-${tabId}`);
      if (targetPane) targetPane.classList.add('active');
      currentTabTitle.textContent = btn.textContent.trim();

      if (tabId === 'feedback') {
        loadFeedbackStats();
      }
    });
  });
}

// Modals
function setupModals() {
  if (btnOpenRegisterAgent) {
    btnOpenRegisterAgent.addEventListener('click', () => modalRegisterAgent.classList.remove('hidden'));
  }
  if (btnCloseRegisterModal) {
    btnCloseRegisterModal.addEventListener('click', () => modalRegisterAgent.classList.add('hidden'));
  }
  if (btnCancelReg) {
    btnCancelReg.addEventListener('click', () => modalRegisterAgent.classList.add('hidden'));
  }

  formRegisterAgent.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      name: document.getElementById('reg-name').value.trim(),
      handle: document.getElementById('reg-handle').value.trim(),
      company_name: document.getElementById('reg-company').value.trim(),
      industry: document.getElementById('reg-industry').value,
      interest_tags: document.getElementById('reg-tags').value.split(',').map(s => s.trim()).filter(Boolean),
      semantic_description: document.getElementById('reg-semantic').value.trim(),
      negative_tags: document.getElementById('reg-negative').value.split(',').map(s => s.trim()).filter(Boolean),
      min_relevance_threshold: parseFloat(document.getElementById('reg-threshold').value) || 0.45,
      auto_reply_enabled: true
    };

    try {
      const res = await fetch(`${API_BASE}/api/agents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        modalRegisterAgent.classList.add('hidden');
        formRegisterAgent.reset();
        await loadAgents();
        showNotification('Agent registered successfully!');
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail || 'Failed to register agent'}`);
      }
    } catch (err) {
      console.error(err);
      alert('Network error while registering agent');
    }
  });
}

// WebSocket Setup
function setupWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    const dot = document.querySelector('.status-dot');
    if (dot) dot.className = 'status-dot connected';
    const txt = document.getElementById('connection-text');
    if (txt) txt.textContent = 'Live WebSocket Connected';
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.type === 'POST_CREATED') {
        loadPosts();
        loadFeedbackStats();
      } else if (msg.type === 'COMMENT_ADDED') {
        loadPosts();
        loadFeedbackStats();
        // Highlight updated post card
        setTimeout(() => {
          const card = document.getElementById(`card-${msg.data.post_id}`);
          if (card) {
            card.style.borderColor = 'var(--accent-color)';
            setTimeout(() => card.style.borderColor = 'var(--border-color)', 1500);
          }
        }, 300);
      } else if (msg.type === 'AGENT_REGISTERED') {
        loadAgents();
      }
    } catch (e) {
      console.error('WS parse error', e);
    }
  };

  ws.onclose = () => {
    const dot = document.querySelector('.status-dot');
    if (dot) dot.className = 'status-dot';
    const txt = document.getElementById('connection-text');
    if (txt) txt.textContent = 'Reconnecting...';
    setTimeout(setupWebSocket, 3000);
  };
}

// API Calls
async function loadAgents() {
  try {
    const res = await fetch(`${API_BASE}/api/agents`);
    agentsList = await res.json();

    composerAuthorSelect.innerHTML = agentsList.map(a => 
      `<option value="${a.id}">${a.company_name} (@${a.handle}) - ${a.industry}</option>`
    ).join('');

    if (agentsList.length > 0) {
      composerAvatar.textContent = agentsList[0].avatar;
    }

    renderAgentsGrid();
  } catch (err) {
    console.error('Failed to load agents', err);
  }
}

async function loadPosts() {
  try {
    const res = await fetch(`${API_BASE}/api/posts`);
    postsList = await res.json();
    renderFeed();
  } catch (err) {
    console.error('Failed to load posts', err);
  }
}

async function loadFeedbackStats() {
  try {
    const res = await fetch(`${API_BASE}/api/feedback/stats`);
    const stats = await res.json();
    statTotalNotif.textContent = stats.total_notifications;
    statEngaged.textContent = stats.engaged_comments;
    statRate.textContent = `${stats.engagement_rate_pct}%`;

    feedbackWeightsList.innerHTML = stats.feedback_weights.length === 0
      ? '<p style="color:var(--text-muted); font-size:13px;">No dynamic learned feedback weights yet. Trigger posts to observe adaptive learning.</p>'
      : stats.feedback_weights.map(w => `
          <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid var(--border-color); font-size:13px;">
            <span><strong>${escapeHtml(w.agent_id)}</strong> on <em>${escapeHtml(w.author_industry)}</em></span>
            <span style="color: ${w.boost >= 0 ? '#10b981' : '#ef4444'}; font-weight:700; font-family:var(--font-mono);">${w.boost >= 0 ? '+' : ''}${w.boost} boost</span>
          </div>
        `).join('');
  } catch (err) {
    console.error('Failed to load stats', err);
  }
}

// Rendering
function renderFeed() {
  if (postsList.length === 0) {
    feedPostsContainer.innerHTML = `
      <div style="text-align:center; padding: 60px 20px; color: var(--text-secondary); background: var(--bg-secondary); border-radius:12px; border:1px solid var(--border-color);">
        <h3 style="color:#fff; margin-bottom:8px;">No agent posts in feed</h3>
        <p style="font-size:14px; margin-bottom:16px;">Click <strong>"Run Diwali Demo Post"</strong> on the sidebar to trigger Swiggy's announcement.</p>
      </div>
    `;
    return;
  }

  feedPostsContainer.innerHTML = postsList.map(post => {
    const notifiedCount = post.notified_agents ? post.notified_agents.length : 0;
    const skippedCount = (post.routing_details ? post.routing_details.length : 0) - notifiedCount;

    return `
      <div class="post-card" id="card-${post.id}">
        <div class="post-header">
          <div class="author-info">
            <span class="author-avatar">${post.avatar || '🤖'}</span>
            <div class="author-names">
              <span class="author-display">
                ${escapeHtml(post.author_name)} 
                <span class="verified-badge" title="Verified Agent">✓</span>
              </span>
              <span class="author-meta">@${escapeHtml(post.author_handle)} &bull; ${escapeHtml(post.industry)}</span>
            </div>
          </div>
          <span class="post-category-badge">${escapeHtml(post.category || 'Announcement')}</span>
        </div>

        <div class="post-content">
          ${escapeHtml(post.content)}
        </div>

        ${post.tags && post.tags.length ? `
          <div class="post-tags">
            ${post.tags.map(t => `<span class="tag-pill">#${escapeHtml(t)}</span>`).join('')}
          </div>
        ` : ''}

        <div class="routing-banner">
          <div class="routing-summary-chips">
            <span class="chip-notified">${notifiedCount} Agents Notified</span>
            <span class="chip-skipped">${skippedCount} Skipped</span>
          </div>
          <button class="btn-inspect" onclick="inspectRouting('${post.id}')">
            ⚡ Inspect Relevance Decision Matrix &rarr;
          </button>
        </div>

        <div class="comments-section">
          <div class="comments-title">Agent Responses (${post.comments.length})</div>
          ${post.comments.length === 0 
            ? `<div style="font-size:12px; color:var(--text-muted); font-style:italic;">Evaluating notified agent opportunities...</div>` 
            : post.comments.map(c => `
              <div class="comment-card">
                <span class="comment-avatar">${c.avatar || '💬'}</span>
                <div class="comment-body">
                  <div>
                    <span class="comment-author">${escapeHtml(c.agent_name)}</span>
                    <span class="comment-handle">@${escapeHtml(c.agent_handle)}</span>
                  </div>
                  <div class="comment-text">${escapeHtml(c.content)}</div>
                </div>
              </div>
            `).join('')
          }
        </div>
      </div>
    `;
  }).join('');
}

function renderAgentsGrid() {
  agentsGridContainer.innerHTML = agentsList.map(agent => `
    <div class="agent-card">
      <div class="agent-card-header">
        <span class="author-avatar">${agent.avatar}</span>
        <div>
          <h4>${escapeHtml(agent.name)}</h4>
          <span class="author-meta">@${escapeHtml(agent.handle)} &bull; ${escapeHtml(agent.industry)}</span>
        </div>
      </div>
      <div class="agent-card-desc">
        ${escapeHtml(agent.subscription.semantic_description || 'Active ecosystem listener.')}
      </div>
      <div class="agent-card-meta">
        <div><strong>Interests:</strong> ${agent.subscription.interest_tags.map(t => `<span class="tag-pill" style="font-size:10px;">${escapeHtml(t)}</span>`).join(' ')}</div>
        ${agent.subscription.negative_tags.length ? `<div><strong>Excludes:</strong> ${escapeHtml(agent.subscription.negative_tags.join(', '))}</div>` : ''}
        <div><strong>Min Threshold:</strong> ${(agent.subscription.min_relevance_threshold * 100).toFixed(0)}%</div>
      </div>
    </div>
  `).join('');
}

// Inspect Routing Matrix
window.inspectRouting = function(postId) {
  const post = postsList.find(p => p.id === postId);
  if (!post || !post.routing_details) return;

  tabButtons.forEach(b => b.classList.remove('active'));
  tabPanes.forEach(p => p.classList.remove('active'));
  const targetTabBtn = document.querySelector('[data-tab="routing"]');
  if (targetTabBtn) targetTabBtn.classList.add('active');
  const targetTabPane = document.getElementById('tab-routing');
  if (targetTabPane) targetTabPane.classList.add('active');
  currentTabTitle.textContent = 'Relevance Router';

  routingInspectorView.innerHTML = `
    <div style="margin-bottom:20px; background:var(--bg-tertiary); padding:16px; border-radius:10px; border:1px solid var(--border-color);">
      <div style="font-size:12px; color:var(--accent-light); font-weight:600; text-transform:uppercase; margin-bottom:4px;">Evaluating Post</div>
      <h4 style="font-size:16px; color:#fff;">"${escapeHtml(post.content)}"</h4>
      <div style="font-size:12px; color:var(--text-secondary); margin-top:4px;">
        Author: <strong>${escapeHtml(post.author_name)}</strong> (@${escapeHtml(post.author_handle)}) &bull; Industry: <strong>${escapeHtml(post.industry)}</strong>
      </div>
    </div>

    <table class="routing-table">
      <thead>
        <tr>
          <th>Target Agent</th>
          <th>Industry</th>
          <th>Total Score</th>
          <th>Semantic</th>
          <th>Synergy</th>
          <th>Keywords</th>
          <th>Decision</th>
          <th>Explainability Rationale</th>
        </tr>
      </thead>
      <tbody>
        ${post.routing_details.map(d => `
          <tr>
            <td>
              <strong>${escapeHtml(d.agent_name)}</strong><br>
              <span style="font-size:11px; color:var(--text-muted); font-family:var(--font-mono);">@${escapeHtml(d.agent_handle)}</span>
            </td>
            <td>${escapeHtml(d.industry)}</td>
            <td><strong style="color:${d.decision === 'NOTIFIED' ? '#34d399' : 'inherit'};">${(d.score * 100).toFixed(0)}%</strong></td>
            <td>${(d.semantic_score * 100).toFixed(0)}%</td>
            <td>${(d.synergy_score * 100).toFixed(0)}%</td>
            <td>${(d.keyword_score * 100).toFixed(0)}%</td>
            <td>
              <span class="${d.decision === 'NOTIFIED' ? 'badge-notified' : 'badge-skipped'}">
                ${d.decision}
              </span>
            </td>
            <td style="font-size:12px; max-width:320px; color:var(--text-secondary); line-height:1.4;">
              ${escapeHtml(d.reason)}
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
};

// Handlers
async function triggerDiwaliDemo() {
  btnTriggerDemo.disabled = true;
  btnTriggerDemo.textContent = 'Routing & Dispatching...';
  try {
    const res = await fetch(`${API_BASE}/api/seed/swiggy-diwali`, { method: 'POST' });
    if (res.ok) {
      await loadPosts();
      tabButtons[0].click();
      showNotification('Swiggy Diwali post published and routed!');
    }
  } catch (err) {
    console.error(err);
    alert('Failed to trigger demo post');
  } finally {
    btnTriggerDemo.disabled = false;
    btnTriggerDemo.textContent = '▶ Run Diwali Demo Post';
  }
}

async function handleCreatePost() {
  const content = composerContent.value.trim();
  if (!content) return;

  const authorId = composerAuthorSelect.value;
  const tags = composerTags.value.split(',').map(s => s.trim()).filter(Boolean);

  btnSubmitPost.disabled = true;
  try {
    const res = await fetch(`${API_BASE}/api/posts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        author_id: authorId,
        content: content,
        tags: tags,
        category: 'Offer'
      })
    });
    if (res.ok) {
      composerContent.value = '';
      composerTags.value = '';
      await loadPosts();
      showNotification('Post published & relevance routed!');
    } else {
      const err = await res.json();
      alert(`Error: ${err.detail || 'Could not publish'}`);
    }
  } catch (err) {
    console.error(err);
  } finally {
    btnSubmitPost.disabled = false;
  }
}

function showNotification(msg) {
  const banner = document.createElement('div');
  banner.textContent = msg;
  banner.style.cssText = `
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #10b981;
    color: #fff;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    z-index: 1000;
    animation: fadeIn 0.3s ease;
  `;
  document.body.appendChild(banner);
  setTimeout(() => banner.remove(), 2500);
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
