# 🐦 Colibrì Studio

A local multi-tier **Mixture-of-Experts (MoE)** orchestrator built on top of the pure-C **Colibrì** inference engine (`JustVugg/colibri`).

---

## 🚀 Overview

Colibrì Studio organizes frontier and edge MoE models into an intelligent **5-tier hierarchy**:

| Tier | Target Model | Total Params | Active Params / Tok | Disk Footprint | Memory Residency | Status on This Machine |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1 (Frontier)** | GLM-5.2 / Kimi K3 | **744B – 2.8T** | ~40B (5.4%) | ~370 GB – 1.4 TB | ~9.9 GB RAM | Requires External NVMe |
| **Tier 2 (Heavy MoE)** | DeepSeek V4.1 / GLM-5.3-Flash | **321B – 552B** | ~28B – 35B | ~160 GB – 280 GB | ~8.0 GB RAM | Requires External NVMe |
| **Tier 3 (Balanced MoE)** | Qwen3.8-Flash-Next | **125B (+51B)** | ~14B | ~65 GB | ~5.5 GB RAM | Tight Internal NVMe Fit |
| **Tier 4 (Compact MoE)** | Qwen3.6-A3B | **35B** | ~3B (8.5%) | ~18 GB | ~3.8 GB RAM | **Ready Local** |
| **Tier 5 (Edge MoE)** | OLMoE-1B-7B | **7B** | ~1B (14.2%) | ~3.5 GB | ~1.5 GB RAM | **Ready Local** |

---

## 🛠️ Features

1. **Pure C Engine Binaries Built Locally**:
   - `colibri` (Tier 1 GLM-5.2 engine)
   - `deepseek_v41` (Tier 2 DeepSeek engine)
   - `qwen38` (Tier 3 Qwen3.8 engine)
   - `qwen36` (Tier 4 Qwen3.6 engine)
   - `olmoe` (Tier 5 OLMoE engine)
   
2. **Dynamic Complexity Auto-Router**:
   - Analyzes incoming queries (keywords, code syntax, proof logic, sentiment) and automatically routes to the best tier.

3. **Live MoE Brain Cortex Visualizer**:
   - HTML5 Canvas displays real-time sparse expert activations across layers as tokens stream in.
   - Differentiates between RAM cache hits and NVMe disk streaming.

4. **Hardware & NVMe Guard**:
   - Monitors available RAM (64 GB) and internal NVMe free space (~85 GB) in real-time, preventing disk exhaustion.

---

## 🖥️ Management Commands

```bash
# Start Colibrì Studio
./start.sh

# Check Service & Engine Status
./status.sh

# Stop Colibrì Studio
./stop.sh
```

**Web Dashboard URL:** [http://127.0.0.1:8088](http://127.0.0.1:8088)
