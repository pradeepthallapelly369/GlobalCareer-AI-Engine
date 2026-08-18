# Pradeep's Infrastructure & AI Agents Report

## 🌐 Active Web Applications & Local Hosts

1. **OmniRoute Gateway (Port 20128)**
   - **Type:** Next.js Application
   - **Use Case:** Acts as a centralized AI API gateway and model router for local agents (like Claude Code). It handles connection bypassing, model resolution, and environment variables sharing for your terminal agents.

2. **BharatAlpha Trading Engine - Frontend (Port 5173)**
   - **Type:** React / Vite Application
   - **Use Case:** A dynamic trading dashboard featuring Market Radar, Buffett Scanner, and real-time visualization of agent-driven multi-bagger investment intelligence.

3. **BharatAlpha Trading Engine - Backend (Port 8000)**
   - **Type:** FastAPI / Uvicorn Server
   - **Use Case:** Houses the autonomous multi-agent swarm logic (Chanakya, Arya, Vikram, Kautilya) executing fundamental queries, real-time market data streaming (Fyers brokerage API), and paper trading.

4. **GlobalCareer AI Engine Dashboard (Port 5070 / Configured)**
   - **Type:** FastAPI Backend / Web UI
   - **Use Case:** The dashboard tracking remote global data engineering jobs, application lifecycles, and auto-generated resume/cover letter metrics.

5. **QlikHunter (Port 5050)**
   - **Type:** Python / Flask App
   - **Use Case:** An early iteration or specialized engine for discovering and tracking exclusively Qlik-related remote jobs.

6. **OpenClaw Gateway (Port 18789)**
   - **Type:** Node.js Server
   - **Use Case:** Connects open-source local agents to various interfaces.

---

## 🤖 AI Agents & Multi-Agent Ecosystems

1. **GlobalCareer AI Engine**
   - **Purpose:** Autonomous global job hunter that scores JDs, customizes resumes/cover letters via AI, and auto-emails recruiters.
2. **BharatAlpha Intelligence Swarm**
   - **Purpose:** 4-agent ecosystem (Chanakya, Arya, Vikram, Kautilya) designed for Warren Buffett-style fundamental analysis and live trading execution.
3. **MiroFish**
   - **Purpose:** A multi-agent framework enabling collaborative problem-solving used as inspiration in BharatAlpha.
4. **AetherMind**
   - **Purpose:** Specialized local agent handling data processes, featuring websockets and event loops.
5. **Local Telegram Agent**
   - **Purpose:** An active bot interface to talk directly to your local models and command the AI engine from your phone.
6. **Agent Studio & OpenClaw**
   - **Purpose:** Tools for orchestrating, testing, and developing new bespoke agents locally.

---

## 🧠 Downloaded Local LLM Models (Ollama)

You have a robust set of large models downloaded for offline inference and agentic execution:
- **Qwen family:** `qwen3.6:latest` (23 GB), `qwen3.5:latest` (6.6 GB), `qwen2.5:latest` (4.7 GB)
- **Llama 3 family:** `llama3.1:8b` (4.9 GB), `llama3.2:latest` (2.0 GB), `llama3.1:latest`
- **Gemma family:** `gemma4:12b` (7.6 GB), `gemma4:latest` (9.6 GB), `gemma3:latest` (3.3 GB)
- **Others:** `gpt-oss:20b` (13 GB), `glm-4.7-flash:latest` (19 GB), `minimax-m3:cloud`

**Use Case:** These models are used interchangeably across OmniRoute and your agent hubs. For massive multi-agent thinking, you rely on the larger 20B+ models, while smaller models (like Llama 3.2) handle fast routing or classification tasks.
