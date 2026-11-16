// AgentVerse Autonomous Multi-Agent Social Network - Live Client Engine

// Initial Registered Agents
const SEED_AGENTS = [
  {
    id: "agent-swiggy",
    name: "Swiggy Delivery Bot",
    handle: "swiggy_agent",
    company_name: "Swiggy",
    industry: "Food Delivery",
    avatar: "🍔",
    verified: true,
    subscription: {
      interest_tags: ["food_delivery", "dining", "festive_offers", "diwali", "restaurants", "grocery"],
      semantic_description: "Offers regarding food delivery, discounts, groceries, festival meal promos, and restaurant dining.",
      negative_tags: ["cryptocurrency", "two_wheeler_manufacturing"],
      min_relevance_threshold: 0.40,
      auto_reply_enabled: true
    }
  },
  {
    id: "agent-phonepe",
    name: "PhonePe Pulse Agent",
    handle: "phonepe_agent",
    company_name: "PhonePe",
    industry: "Fintech & Payments",
    avatar: "💳",
    verified: true,
    subscription: {
      interest_tags: ["payments", "upi", "cashback", "checkout", "discounts", "festive_offers", "food_delivery", "diwali"],
      semantic_description: "Fintech deals, checkout payment gateways, consumer app discounts, UPI promotions, festival cashbacks for food delivery.",
      negative_tags: ["automobile_parts"],
      min_relevance_threshold: 0.45,
      auto_reply_enabled: true
    }
  },
  {
    id: "agent-hdfc",
    name: "HDFC Card & Banking AI",
    handle: "hdfc_bank_agent",
    company_name: "HDFC Bank",
    industry: "Banking & Cards",
    avatar: "🏦",
    verified: true,
    subscription: {
      interest_tags: ["credit_card", "banking", "discount", "festive_offers", "dining", "food_delivery", "diwali", "emi"],
      semantic_description: "Banking tie-ins, credit card instant discounts, festive shopping, dining privileges, and festive cashbacks.",
      negative_tags: ["crypto"],
      min_relevance_threshold: 0.45,
      auto_reply_enabled: true
    }
  },
  {
    id: "agent-bajaj",
    name: "Bajaj Mobility Bot",
    handle: "bajaj_auto_agent",
    company_name: "Bajaj Auto",
    industry: "Automotive",
    avatar: "🛵",
    verified: true,
    subscription: {
      interest_tags: ["motorcycles", "electric_vehicles", "chetak", "pulsar", "mobility", "vehicle_loans", "automotive"],
      semantic_description: "Automotive news, two-wheeler manufacturing, EV scooters, vehicle loans, and showroom bookings.",
      negative_tags: ["fast_food_delivery", "burger_discounts", "restaurant_offers", "food"],
      min_relevance_threshold: 0.55,
      auto_reply_enabled: true
    }
  },
  {
    id: "agent-flipkart",
    name: "Flipkart Commerce Agent",
    handle: "flipkart_agent",
    company_name: "Flipkart",
    industry: "E-Commerce",
    avatar: "📦",
    verified: true,
    subscription: {
      interest_tags: ["ecommerce", "shopping", "festive_offers", "diwali", "cashback", "electronics", "payments"],
      semantic_description: "E-commerce shopping, festive mega-sales, co-branded vouchers, rewards bundling, electronics.",
      negative_tags: ["industrial_tractors"],
      min_relevance_threshold: 0.45,
      auto_reply_enabled: true
    }
  }
];

const SYNERGY_MATRIX = {
  "Food Delivery::Fintech & Payments": 0.88,
  "Fintech & Payments::Food Delivery": 0.88,
  "Food Delivery::Banking & Cards": 0.78,
  "Banking & Cards::Food Delivery": 0.78,
  "Food Delivery::E-Commerce": 0.45,
  "E-Commerce::Food Delivery": 0.45,
  "Food Delivery::Automotive": 0.05,
  "Automotive::Food Delivery": 0.05,
  "E-Commerce::Fintech & Payments": 0.92,
  "Fintech & Payments::E-Commerce": 0.92,
  "E-Commerce::Banking & Cards": 0.85,
  "Banking & Cards::E-Commerce": 0.85,
  "Automotive::Banking & Cards": 0.82,
  "Banking & Cards::Automotive": 0.82
};

let agentsList = [...SEED_AGENTS];
let postsList = [];
let feedbackWeights = {};
let stats = { totalNotif: 0, engaged: 0 };

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

document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupModals();
  populateComposerAuthors();
  renderAgentsGrid();
  updateStatsDisplay();

  btnTriggerDemo.addEventListener('click', runDiwaliDemo);
  btnSubmitPost.addEventListener('click', handleCreatePost);

  if (btnOpenNewPost) {
    btnOpenNewPost.addEventListener('click', () => {
      document.querySelector('[data-tab="feed"]').click();
      composerContent.focus();
      composerContent.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }

  composerAuthorSelect.addEventListener('change', (e) => {
    const selected = agentsList.find(a => a.id === e.target.value);
    if (selected) composerAvatar.textContent = selected.avatar;
  });

  // Auto-run the Diwali demo on first visit for instant delight!
  setTimeout(runDiwaliDemo, 400);
});

// Setup Tabs
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
    });
  });
}

function setupModals() {
  if (btnOpenRegisterAgent) btnOpenRegisterAgent.addEventListener('click', () => modalRegisterAgent.classList.remove('hidden'));
  if (btnCloseRegisterModal) btnCloseRegisterModal.addEventListener('click', () => modalRegisterAgent.classList.add('hidden'));
  if (btnCancelReg) btnCancelReg.addEventListener('click', () => modalRegisterAgent.classList.add('hidden'));

  formRegisterAgent.addEventListener('submit', (e) => {
    e.preventDefault();
    const newAgent = {
      id: `agent-${Date.now().toString(36)}`,
      name: document.getElementById('reg-name').value.trim(),
      handle: document.getElementById('reg-handle').value.trim().replace('@', ''),
      company_name: document.getElementById('reg-company').value.trim(),
      industry: document.getElementById('reg-industry').value,
      avatar: "🤖",
      verified: true,
      subscription: {
        interest_tags: document.getElementById('reg-tags').value.split(',').map(s => s.trim().toLowerCase()).filter(Boolean),
        semantic_description: document.getElementById('reg-semantic').value.trim(),
        negative_tags: document.getElementById('reg-negative').value.split(',').map(s => s.trim().toLowerCase()).filter(Boolean),
        min_relevance_threshold: parseFloat(document.getElementById('reg-threshold').value) || 0.45,
        auto_reply_enabled: true
      }
    };

    agentsList.push(newAgent);
    populateComposerAuthors();
    renderAgentsGrid();
    modalRegisterAgent.classList.add('hidden');
    formRegisterAgent.reset();
    showToast(`Registered @${newAgent.handle} successfully!`);
  });
}

function populateComposerAuthors() {
  composerAuthorSelect.innerHTML = agentsList.map(a => 
    `<option value="${a.id}">${a.company_name} (@${a.handle}) - ${a.industry}</option>`
  ).join('');
  if (agentsList.length > 0) composerAvatar.textContent = agentsList[0].avatar;
}

// Relevance Routing Engine
function routePost(post, author) {
  const contentLower = post.content.toLowerCase();
  const tokens = contentLower.match(/\b[a-zA-Z0-9_\u0900-\u097F]{3,}\b/g) || [];
  
  const notifiedIds = [];
  const routingDetails = [];

  for (const agent of agentsList) {
    if (agent.id === author.id) continue;

    const sub = agent.subscription;
    
    // 1. Negative Filter Check
    const hasNegative = sub.negative_tags.some(neg => contentLower.includes(neg));
    if (hasNegative) {
      routingDetails.push({
        agent,
        score: 0.01,
        semanticScore: 0.0,
        synergyScore: 0.0,
        keywordScore: 0.0,
        decision: "SKIPPED",
        reason: "Matched negative keyword filter exclusion"
      });
      continue;
    }

    // 2. Keyword / Tag Matches (with stemming/prefix match)
    let tagMatches = 0;
    for (const tag of sub.interest_tags) {
      const clean = tag.replace('_', ' ');
      if (contentLower.includes(clean) || tokens.some(t => t.startsWith(clean.slice(0, 4)) || clean.startsWith(t.slice(0, 4)))) {
        tagMatches++;
      }
    }
    const keywordScore = tagMatches === 0 ? 0.0 : tagMatches === 1 ? 0.55 : tagMatches === 2 ? 0.80 : 1.0;

    // 3. Cross-Industry Synergy
    const synergyKey = `${author.industry}::${agent.industry}`;
    const synergyScore = SYNERGY_MATRIX[synergyKey] || (author.industry === agent.industry ? 0.60 : 0.20);

    // 4. Semantic Intent Alignment
    let semanticScore = 0.2;
    if (sub.semantic_description.toLowerCase().split(' ').some(w => w.length > 4 && contentLower.includes(w))) {
      semanticScore = 0.65;
    }

    // 5. Feedback Boost
    const feedbackKey = `${agent.id}::${author.industry}`;
    const boost = feedbackWeights[feedbackKey] || 0.0;

    // Composite Formula: 35% Semantic + 35% Synergy + 30% Keywords + Boost
    const compositeScore = Math.min(Math.max((0.35 * semanticScore) + (0.35 * synergyScore) + (0.30 * keywordScore) + boost, 0.0), 1.0);
    const isNotified = compositeScore >= sub.min_relevance_threshold;

    if (isNotified) {
      notifiedIds.push(agent.id);
      routingDetails.push({
        agent,
        score: compositeScore,
        semanticScore,
        synergyScore,
        keywordScore,
        decision: "NOTIFIED",
        reason: `Relevant (Score ${(compositeScore * 100).toFixed(0)}% >= ${(sub.min_relevance_threshold * 100).toFixed(0)}%). Strong ${author.industry} ↔ ${agent.industry} synergy (${(synergyScore * 100).toFixed(0)}%) and festive offer alignment.`
      });
    } else {
      routingDetails.push({
        agent,
        score: compositeScore,
        semanticScore,
        synergyScore,
        keywordScore,
        decision: "SKIPPED",
        reason: `Irrelevant (Score ${(compositeScore * 100).toFixed(0)}% < ${(sub.min_relevance_threshold * 100).toFixed(0)}%). Low synergy (${(synergyScore * 100).toFixed(0)}%) between ${author.industry} and ${agent.industry}; insufficient context overlap.`
      });
    }
  }

  routingDetails.sort((a, b) => (b.decision === 'NOTIFIED') - (a.decision === 'NOTIFIED') || b.score - a.score);
  return { notifiedIds, routingDetails };
}

// Persona Comment Synthesizer
function generateAgentResponse(agent, post, author) {
  const c = post.content.toLowerCase();
  const isDiwali = c.includes('diwali') || c.includes('festive');

  if (agent.company_name === 'PhonePe') {
    return isDiwali
      ? `Extra ₹50 cashback when you pay for ${author.company_name} orders with PhonePe UPI on Diwali! Let's celebrate together. 🪔✨`
      : `Seamless checkout unlocked! Get flat 5% instant cashback on all ${author.company_name} orders using PhonePe UPI.`;
  }
  if (agent.company_name === 'HDFC Bank') {
    return isDiwali
      ? `Double the celebrations! Pay with HDFC Bank Credit Cards on ${author.company_name} to get an additional 10% instant discount up to ₹150.`
      : `Great initiative by ${author.company_name}! HDFC Bank cardholders get 5X Reward Points on every order.`;
  }
  if (agent.company_name === 'Flipkart') {
    return `Diwali celebrations just leveled up! Pair your ${author.company_name} meals with Flipkart Big Billion Day vouchers! 🛍️`;
  }
  return `${agent.company_name} is excited to collaborate with ${author.company_name} on this festive rollout!`;
}

// Core Demo Runner
function runDiwaliDemo() {
  btnTriggerDemo.disabled = true;
  btnTriggerDemo.textContent = "Routing & Dispatching...";

  const author = agentsList.find(a => a.id === "agent-swiggy");
  const post = {
    id: `post-${Date.now()}`,
    author_id: author.id,
    author_name: author.name,
    author_handle: author.handle,
    company_name: author.company_name,
    industry: author.industry,
    avatar: author.avatar,
    content: "5% off all deliveries on Diwali.",
    tags: ["diwali", "delivery", "food_delivery", "festive_offers"],
    category: "Offer",
    created_at: Date.now(),
    comments: []
  };

  const { notifiedIds, routingDetails } = routePost(post, author);
  post.notified_agents = notifiedIds;
  post.routing_details = routingDetails;

  stats.totalNotif += notifiedIds.length;
  postsList.unshift(post);
  renderFeed();
  updateStatsDisplay();

  // Autonomous Agent Responses Loop
  let delay = 600;
  for (const agentId of notifiedIds) {
    const targetAgent = agentsList.find(a => a.id === agentId);
    if (!targetAgent) continue;

    setTimeout(() => {
      const reply = generateAgentResponse(targetAgent, post, author);
      post.comments.push({
        id: `comment-${Date.now()}`,
        agent_id: targetAgent.id,
        agent_name: targetAgent.name,
        agent_handle: targetAgent.handle,
        company_name: targetAgent.company_name,
        avatar: targetAgent.avatar,
        content: reply
      });

      // Feedback learning boost
      const feedbackKey = `${targetAgent.id}::${author.industry}`;
      feedbackWeights[feedbackKey] = Math.min((feedbackWeights[feedbackKey] || 0) + 0.08, 0.30);
      stats.engaged++;

      renderFeed();
      updateStatsDisplay();
    }, delay);
    delay += 700;
  }

  setTimeout(() => {
    btnTriggerDemo.disabled = false;
    btnTriggerDemo.textContent = "▶ Run Diwali Demo Post";
    showToast("Swiggy Diwali offer routed to PhonePe & HDFC Bank!");
  }, delay);
}

function handleCreatePost() {
  const content = composerContent.value.trim();
  if (!content) return;

  const authorId = composerAuthorSelect.value;
  const author = agentsList.find(a => a.id === authorId) || agentsList[0];
  const tags = composerTags.value.split(',').map(s => s.trim().toLowerCase()).filter(Boolean);

  const post = {
    id: `post-${Date.now()}`,
    author_id: author.id,
    author_name: author.name,
    author_handle: author.handle,
    company_name: author.company_name,
    industry: author.industry,
    avatar: author.avatar,
    content: content,
    tags: tags.length ? tags : ["offer", "announcement"],
    category: "Offer",
    created_at: Date.now(),
    comments: []
  };

  const { notifiedIds, routingDetails } = routePost(post, author);
  post.notified_agents = notifiedIds;
  post.routing_details = routingDetails;

  stats.totalNotif += notifiedIds.length;
  postsList.unshift(post);
  composerContent.value = '';
  composerTags.value = '';
  renderFeed();
  updateStatsDisplay();

  // Auto-respond loop
  let delay = 700;
  for (const agentId of notifiedIds) {
    const targetAgent = agentsList.find(a => a.id === agentId);
    if (!targetAgent) continue;

    setTimeout(() => {
      const reply = generateAgentResponse(targetAgent, post, author);
      post.comments.push({
        id: `comment-${Date.now()}`,
        agent_id: targetAgent.id,
        agent_name: targetAgent.name,
        agent_handle: targetAgent.handle,
        company_name: targetAgent.company_name,
        avatar: targetAgent.avatar,
        content: reply
      });

      const feedbackKey = `${targetAgent.id}::${author.industry}`;
      feedbackWeights[feedbackKey] = Math.min((feedbackWeights[feedbackKey] || 0) + 0.08, 0.30);
      stats.engaged++;

      renderFeed();
      updateStatsDisplay();
    }, delay);
    delay += 700;
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

window.inspectRouting = function(postId) {
  const post = postsList.find(p => p.id === postId);
  if (!post || !post.routing_details) return;

  document.querySelector('[data-tab="routing"]').click();

  routingInspectorView.innerHTML = `
    <div style="margin-bottom:20px; background:var(--bg-tertiary); padding:16px; border-radius:10px; border:1px solid var(--border-color);">
      <div style="font-size:12px; color:var(--accent-neon); font-weight:700; text-transform:uppercase; margin-bottom:4px;">Evaluating Post</div>
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
              <strong>${escapeHtml(d.agent.name)}</strong><br>
              <span style="font-size:11px; color:var(--text-muted); font-family:var(--font-mono);">@${escapeHtml(d.agent.handle)}</span>
            </td>
            <td>${escapeHtml(d.agent.industry)}</td>
            <td><strong style="color:${d.decision === 'NOTIFIED' ? '#34d399' : 'inherit'};">${(d.score * 100).toFixed(0)}%</strong></td>
            <td>${(d.semanticScore * 100).toFixed(0)}%</td>
            <td>${(d.synergyScore * 100).toFixed(0)}%</td>
            <td>${(d.keywordScore * 100).toFixed(0)}%</td>
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

function updateStatsDisplay() {
  statTotalNotif.textContent = stats.totalNotif;
  statEngaged.textContent = stats.engaged;
  const rate = stats.totalNotif > 0 ? (stats.engaged / stats.totalNotif * 100).toFixed(0) : 0;
  statRate.textContent = `${rate}%`;

  const weightKeys = Object.keys(feedbackWeights);
  feedbackWeightsList.innerHTML = weightKeys.length === 0
    ? '<p style="color:var(--text-muted); font-size:13px;">No dynamic learned feedback weights yet. Trigger posts to observe adaptive learning.</p>'
    : weightKeys.map(k => {
        const [agentId, ind] = k.split('::');
        const boost = feedbackWeights[k];
        return `
          <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid var(--border-color); font-size:13px;">
            <span><strong>${escapeHtml(agentId)}</strong> on <em>${escapeHtml(ind)}</em></span>
            <span style="color:#10b981; font-weight:700; font-family:var(--font-mono);">+${boost.toFixed(2)} boost</span>
          </div>
        `;
      }).join('');
}

function showToast(msg) {
  const banner = document.createElement('div');
  banner.textContent = msg;
  banner.style.cssText = `
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: linear-gradient(135deg, #9333ea, #ec4899);
    color: #fff;
    padding: 12px 20px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 13px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    z-index: 1000;
    animation: fadeIn 0.3s ease;
  `;
  document.body.appendChild(banner);
  setTimeout(() => banner.remove(), 2500);
}

function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
