// Colibrì Studio Frontend Application

let currentMode = 'auto'; // 'auto' | 'manual'
let selectedTier = 'tier4';
let tiersData = {};
let isStreaming = false;

// Sample prompts for quick testing
const SAMPLES = {
  1: "Formally prove the safety invariants of Paxos consensus under asynchronous network partitions with Byzantine faults, and optimize the distributed state machine transition kernel.",
  2: "Architect an end-to-end event-driven microservices platform using Docker, Kubernetes, and Kafka with asynchronous Dead Letter Queues and distributed tracing.",
  3: "Create an asynchronous FastAPI backend service with PostgreSQL pooling, Redis caching, and an automated ETL pipeline that ingests financial time series.",
  4: "Write a high-performance Python regex to validate IPv4 and IPv6 addresses and explain how the regex parser executes each non-capturing group.",
  5: "Analyze the sentiment of this user feedback: 'The application is blazing fast and the UI is gorgeous!'"
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  initCortexCanvas();
  fetchTiers();
  fetchTelemetry();
  setInterval(fetchTelemetry, 3000);
});

// Fetch Tiers & Render Hierarchy Cards
async function fetchTiers() {
  try {
    const res = await fetch('/api/tiers');
    const data = await res.json();
    tiersData = data.tiers;
    renderTierGrid(tiersData);
  } catch (err) {
    console.error("Failed to load tiers:", err);
  }
}

function renderTierGrid(tiers) {
  const container = document.getElementById('tierGrid');
  container.innerHTML = '';

  const order = ['tier1', 'tier2', 'tier3', 'tier4', 'tier5'];

  order.forEach(tid => {
    const t = tiers[tid];
    if (!t) return;

    const card = document.createElement('div');
    card.className = `tier-card ${tid === selectedTier ? 'active' : ''}`;
    card.style.setProperty('--card-color', t.color);
    card.onclick = () => selectTier(tid);

    let hwClass = 'hw-ready';
    let hwText = '✓ Fits on Disk';
    if (t.hardware_status === 'requires_external_nvme') {
      hwClass = 'hw-external';
      hwText = '⚠ External NVMe Needed';
    } else if (t.hardware_status === 'tight_fit') {
      hwClass = 'hw-tight';
      hwText = '● Tight NVMe Fit';
    }

    card.innerHTML = `
      <div>
        <div class="tier-card-header">
          <span class="tier-num-pill">${t.badge.split('·')[0].trim()}</span>
          <span class="tier-binary-status">Binary: ${t.target_binary}</span>
        </div>
        <div class="tier-name">${t.name.split('(')[0].trim()}</div>
        <div class="tier-params">${t.total_params} Params</div>
      </div>

      <div class="tier-specs">
        <div class="tier-spec-item">
          <span>Active / Token</span>
          <span>${t.active_params}</span>
        </div>
        <div class="tier-spec-item">
          <span>Experts</span>
          <span>${t.total_experts.toLocaleString()} (${t.layers} L)</span>
        </div>
        <div class="tier-spec-item">
          <span>Disk Footprint</span>
          <span>${t.disk_size_gb} GB</span>
        </div>
        <div class="hardware-pill ${hwClass}">${hwText}</div>
      </div>
    `;

    container.appendChild(card);
  });
}

function selectTier(tid) {
  selectedTier = tid;
  document.querySelectorAll('.tier-card').forEach((c, idx) => {
    const keys = ['tier1', 'tier2', 'tier3', 'tier4', 'tier5'];
    if (keys[idx] === tid) {
      c.classList.add('active');
    } else {
      c.classList.remove('active');
    }
  });

  if (currentMode === 'manual') {
    updateVisualizerForTier(tid);
  }
}

function setMode(mode) {
  currentMode = mode;
  document.getElementById('modeAutoBtn').classList.toggle('active', mode === 'auto');
  document.getElementById('modeManualBtn').classList.toggle('active', mode === 'manual');
  
  const sub = document.getElementById('activeTierSubtitle');
  if (mode === 'auto') {
    sub.textContent = 'Auto-Routing Active (Dynamic Complexity Classifier)';
  } else {
    sub.textContent = `Locked to ${tiersData[selectedTier]?.badge || selectedTier}`;
    updateVisualizerForTier(selectedTier);
  }
}

function applySample(num) {
  const prompt = SAMPLES[num];
  document.getElementById('promptInput').value = prompt;
  if (currentMode === 'auto') {
    previewRouting(prompt);
  }
}

// Live Route Preview
async function previewRouting(prompt) {
  if (!prompt.trim()) {
    document.getElementById('routingCard').style.display = 'none';
    return;
  }
  try {
    const res = await fetch('/api/route', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });
    const data = await res.json();
    
    const card = document.getElementById('routingCard');
    card.style.display = 'flex';
    document.getElementById('routeTitle').textContent = `Auto-Routed to: ${data.badge}`;
    document.getElementById('routeRationale').textContent = data.reasons.join(' · ');
    document.getElementById('routeConfidenceTag').textContent = `Confidence: ${(data.confidence * 100).toFixed(0)}%`;
    
    selectTier(data.selected_tier);
    updateVisualizerForTier(data.selected_tier);
  } catch (err) {
    console.error("Routing preview failed:", err);
  }
}

// Update Cortex HUD for Tier
function updateVisualizerForTier(tid) {
  const t = tiersData[tid];
  if (!t) return;
  document.getElementById('statActiveParams').textContent = t.active_params;
  document.getElementById('statTotalExperts').textContent = t.total_experts.toLocaleString();
  document.getElementById('statActiveExperts').textContent = `Top-${t.default_experts_per_token || 4} per token`;
}

// Send Message & Stream Response
async function handleSend() {
  const input = document.getElementById('promptInput');
  const prompt = input.value.trim();
  if (!prompt || isStreaming) return;

  isStreaming = true;
  document.getElementById('sendBtn').disabled = true;

  // Append user bubble
  appendChatBubble('user', prompt);
  input.value = '';

  // Append assistant placeholder bubble
  const assistantBubble = appendChatBubble('assistant', '<span class="pulse-dot"></span> Streaming experts...');
  const textContainer = assistantBubble.querySelector('.bubble-content');
  const metaContainer = assistantBubble.querySelector('.bubble-meta');

  const effectiveTier = currentMode === 'auto' ? 'auto' : selectedTier;

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tier: effectiveTier, prompt })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let fullResponse = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep partial line

      let currentEvent = null;

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.startsWith('event:')) {
          currentEvent = line.replace('event:', '').trim();
        } else if (line.startsWith('data:') && currentEvent) {
          const rawData = line.replace('data:', '').trim();
          try {
            const data = JSON.parse(rawData);
            handleStreamEvent(currentEvent, data, textContainer, metaContainer);
          } catch (e) {
            console.error("JSON parse error:", e);
          }
          currentEvent = null;
        }
      }
    }
  } catch (err) {
    console.error("Inference stream error:", err);
    if (textContainer) {
      textContainer.innerHTML += `<br><span style="color: #ef4444;">[Stream connection interrupted]</span>`;
    }
  } finally {
    isStreaming = false;
    document.getElementById('sendBtn').disabled = false;
  }
}

function handleStreamEvent(event, data, textContainer, metaContainer) {
  if (event === 'meta') {
    selectTier(data.tier);
    updateVisualizerForTier(data.tier);
    metaContainer.innerHTML = `
      <span class="tier-tag" style="background: rgba(139, 92, 246, 0.2); color: #c084fc;">${data.model}</span>
      <span>${data.is_simulated ? 'MoE Simulation & Benchmark' : 'Native C Engine'}</span>
    `;
    textContainer.innerHTML = '';
  } else if (event === 'expert') {
    document.getElementById('activeCortexLayer').textContent = `Layer: ${data.layer + 1} · Routing ${data.experts.length} Experts`;
    triggerExpertActivation(data.layer, data.experts, data.tier_source);
    
    // Log entry
    const log = document.getElementById('routingLog');
    const entry = document.createElement('div');
    entry.className = `log-entry ${data.tier_source === 'RAM' ? 'ram-hit' : 'nvme-hit'}`;
    entry.textContent = `[L${String(data.layer + 1).padStart(2, '0')}] Experts [${data.experts.join(',')}] ← ${data.tier_source}`;
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
  } else if (event === 'token') {
    textContainer.innerHTML += data.chunk;
    const scrollPane = document.getElementById('chatHistory');
    scrollPane.scrollTop = scrollPane.scrollHeight;
  } else if (event === 'done') {
    document.getElementById('statTokRate').textContent = `${data.tokens_per_second} tok/s`;
    document.getElementById('statTTFT').textContent = `TTFT: ${data.ttft_seconds}s`;
    document.getElementById('statHitRate').textContent = data.expert_cache_hit_rate;
    
    const finishNote = document.createElement('div');
    finishNote.style.cssText = 'margin-top: 10px; font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono); border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px;';
    finishNote.textContent = `⚡ Generated ${data.tokens_generated} tokens in ${data.elapsed_seconds}s (${data.tokens_per_second} tok/s) · Cache Hit Rate: ${data.expert_cache_hit_rate}`;
    textContainer.appendChild(finishNote);
  }
}

function appendChatBubble(role, content) {
  const history = document.getElementById('chatHistory');
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${role}`;

  if (role === 'user') {
    bubble.innerHTML = `<div class="bubble-content">${escapeHtml(content)}</div>`;
  } else {
    bubble.innerHTML = `
      <div class="bubble-meta">
        <span class="tier-tag" style="background: rgba(6, 182, 212, 0.15); color: var(--accent-cyan);">Colibrì Engine</span>
        <span>Local MoE</span>
      </div>
      <div class="bubble-content">${content}</div>
    `;
  }

  history.appendChild(bubble);
  history.scrollTop = history.scrollHeight;
  return bubble;
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Telemetry Polling
async function fetchTelemetry() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();

    document.getElementById('cpuUsageTxt').textContent = `${data.cpu.usage_percent}%`;
    document.getElementById('ramUsageTxt').textContent = `${data.memory.used_gb} / ${data.memory.total_gb} GB`;
    document.getElementById('diskFreeTxt').textContent = `${data.disk.free_gb} GB`;

    const readyCount = Object.values(data.engine.binaries).filter(Boolean).length;
    document.getElementById('engineStatusTxt').textContent = `Ready (${readyCount}/5 Binaries)`;
  } catch (err) {
    console.error("Telemetry fetch error:", err);
  }
}

// Cortex Visualizer (Canvas)
let canvas, ctx;
let cortexNodes = [];
const NUM_LAYERS = 24;
const EXPERTS_PER_LAYER = 16;

function initCortexCanvas() {
  canvas = document.getElementById('cortexCanvas');
  ctx = canvas.getContext('2d');
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);
  buildCortexNodes();
  requestAnimationFrame(renderCortex);
}

function resizeCanvas() {
  const wrap = canvas.parentElement;
  canvas.width = wrap.clientWidth;
  canvas.height = wrap.clientHeight;
  buildCortexNodes();
}

function buildCortexNodes() {
  cortexNodes = [];
  const w = canvas.width;
  const h = canvas.height;
  const xMargin = 30;
  const yMargin = 20;
  
  const layerSpacing = (w - 2 * xMargin) / (NUM_LAYERS - 1);
  const expertSpacing = (h - 2 * yMargin) / (EXPERTS_PER_LAYER - 1);

  for (let l = 0; l < NUM_LAYERS; l++) {
    for (let e = 0; e < EXPERTS_PER_LAYER; e++) {
      cortexNodes.push({
        layer: l,
        expert: e,
        x: xMargin + l * layerSpacing,
        y: yMargin + e * expertSpacing,
        intensity: 0.1,
        color: '#06b6d4',
        hitType: 'RAM'
      });
    }
  }
}

function triggerExpertActivation(layerIndex, experts, hitType) {
  const normLayer = layerIndex % NUM_LAYERS;
  cortexNodes.forEach(node => {
    if (node.layer === normLayer) {
      if (experts.some(exp => (exp % EXPERTS_PER_LAYER) === node.expert)) {
        node.intensity = 1.0; // Flash white
        node.hitType = hitType;
        node.color = hitType === 'RAM' ? '#34d399' : '#f59e0b';
      }
    }
  });
}

function renderCortex() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw light interconnect lines between adjacent layer nodes
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.025)';
  ctx.lineWidth = 1;

  for (let l = 0; l < NUM_LAYERS - 1; l += 2) {
    const x1 = cortexNodes[l * EXPERTS_PER_LAYER].x;
    const x2 = cortexNodes[(l + 1) * EXPERTS_PER_LAYER].x;
    ctx.beginPath();
    ctx.moveTo(x1, 0);
    ctx.lineTo(x2, canvas.height);
    ctx.stroke();
  }

  // Draw nodes
  cortexNodes.forEach(node => {
    // Fade intensity gradually
    if (node.intensity > 0.12) {
      node.intensity -= 0.035;
    }

    ctx.beginPath();
    const radius = node.intensity > 0.5 ? 3.5 : 1.8;
    ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);

    if (node.intensity > 0.6) {
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = '#ffffff';
      ctx.shadowBlur = 8;
    } else {
      ctx.fillStyle = node.color;
      ctx.globalAlpha = node.intensity;
      ctx.shadowColor = node.color;
      ctx.shadowBlur = node.intensity > 0.2 ? 4 : 0;
    }

    ctx.fill();
    ctx.globalAlpha = 1.0;
    ctx.shadowBlur = 0;
  });

  requestAnimationFrame(renderCortex);
}
