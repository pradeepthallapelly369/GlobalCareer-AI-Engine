document.addEventListener("DOMContentLoaded", () => {
  const baseUrlInput = document.getElementById("baseUrlInput");
  const modelNameInput = document.getElementById("modelNameInput");
  const saveConfigBtn = document.getElementById("saveConfigBtn");
  const taskInput = document.getElementById("taskInput");
  const cwdInput = document.getElementById("cwdInput");
  const runTaskBtn = document.getElementById("runTaskBtn");
  const timeline = document.getElementById("timeline");
  const agentStatus = document.getElementById("agentStatus");
  const cpuUsage = document.getElementById("cpuUsage");
  const ramUsage = document.getElementById("ramUsage");
  const gpuStats = document.getElementById("gpuStats");

  let ws = null;

  // Fetch Initial Config & System Stats
  async function loadSystemStats() {
    try {
      const res = await fetch("/api/system");
      if (res.ok) {
        const stats = await res.json();
        cpuUsage.textContent = stats.cpu_usage;
        ramUsage.textContent = `${stats.ram_used_gb} / ${stats.ram_total_gb} GB (${stats.ram_percent})`;
        gpuStats.textContent = stats.gpu_stats || "N/A";
      }
    } catch (e) {
      console.error("Failed to load system stats:", e);
    }
  }

  async function loadConfig() {
    try {
      const res = await fetch("/api/config");
      if (res.ok) {
        const cfg = await res.json();
        baseUrlInput.value = cfg.base_url;
        modelNameInput.value = cfg.model_name;
      }
    } catch (e) {
      console.error("Failed to load config:", e);
    }
  }

  saveConfigBtn.addEventListener("click", async () => {
    try {
      const res = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          base_url: baseUrlInput.value.trim(),
          model_name: modelNameInput.value.trim()
        })
      });
      if (res.ok) {
        alert("Configuration updated successfully!");
      }
    } catch (e) {
      alert("Error saving config: " + e.message);
    }
  });

  function addTimelineEvent(type, headerTitle, contentText, step = null) {
    const card = document.createElement("div");
    card.className = `event-card ${type}`;

    const header = document.createElement("div");
    header.className = "event-header";
    header.innerHTML = `<span class="event-title">${headerTitle}</span> ${step ? `<span>STEP ${step}</span>` : ''}`;

    const body = document.createElement("div");
    body.textContent = contentText;

    card.appendChild(header);
    card.appendChild(body);
    timeline.appendChild(card);
    timeline.scrollTop = timeline.scrollHeight;
  }

  runTaskBtn.addEventListener("click", () => {
    const task = taskInput.value.trim();
    const cwd = cwdInput.value.trim();
    if (!task) return alert("Please enter a task for AetherMind agent.");

    timeline.innerHTML = "";
    agentStatus.textContent = "RUNNING";
    agentStatus.style.color = "var(--accent-amber)";
    runTaskBtn.disabled = true;

    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(`${protocol}//${location.host}/ws/task`);

    ws.onopen = () => {
      ws.send(JSON.stringify({ task, cwd }));
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === "status") {
        addTimelineEvent("thought", "AGENT STATUS", msg.data);
      } else if (msg.type === "thought") {
        addTimelineEvent("thought", "AETHERMIND THOUGHT", msg.data, msg.step);
      } else if (msg.type === "tool_call") {
        addTimelineEvent("tool_call", `TOOL CALL: ${msg.tool}`, JSON.stringify(msg.args, null, 2), msg.step);
      } else if (msg.type === "tool_output") {
        addTimelineEvent("tool_output", `OBSERVATION: ${msg.tool}`, msg.output, msg.step);
      } else if (msg.type === "final_result") {
        addTimelineEvent("final", "TASK COMPLETED", msg.data);
      } else if (msg.type === "error") {
        addTimelineEvent("tool_output", "ERROR", msg.data);
        agentStatus.textContent = "ERROR";
        agentStatus.style.color = "red";
      } else if (msg.type === "complete") {
        agentStatus.textContent = "IDLE";
        agentStatus.style.color = "var(--accent-green)";
        runTaskBtn.disabled = false;
      }
    };

    ws.onerror = (err) => {
      addTimelineEvent("tool_output", "CONNECTION ERROR", "WebSocket connection error.");
      agentStatus.textContent = "ERROR";
      runTaskBtn.disabled = false;
    };

    ws.onclose = () => {
      runTaskBtn.disabled = false;
    };
  });

  loadConfig();
  loadSystemStats();
  setInterval(loadSystemStats, 3000);
});
