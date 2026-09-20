"""
colibri-studio Models Configuration: 5-Tier MoE Hierarchy
"""

TIER_MODELS = {
    "tier1": {
        "id": "tier1",
        "name": "GLM-5.2 / Kimi K3 (Frontier MoE)",
        "badge": "Tier 1 · Frontier Ultra",
        "total_params": "744B – 2.8T",
        "active_params": "~40B / token (5.4%)",
        "total_experts": 19456,
        "layers": 75,
        "disk_size_gb": 370.0,
        "ram_resident_gb": 9.9,
        "target_binary": "colibri",
        "family": "glm52",
        "color": "#8b5cf6",
        "tagline": "Uncompromising Frontier Reasoning & Deep System Architecture",
        "description": "Massive mixture-of-experts model activating only ~40B parameters per token. Streams 19,456 experts from NVMe on demand with ~10GB RAM resident attention/embedding core.",
        "best_for": [
            "Mathematical theorem proving & complex symbolic logic",
            "Multi-system architecture & deep kernel optimization",
            "High-stakes strategic planning & algorithmic synthesis"
        ],
        "hardware_status": "requires_external_nvme",
        "default_experts_per_token": 8
    },
    "tier2": {
        "id": "tier2",
        "name": "DeepSeek V4.1 Flash / GLM-5.3-Flash",
        "badge": "Tier 2 · Heavy MoE",
        "total_params": "321B – 552B",
        "active_params": "~28B – 35B / token",
        "total_experts": 16384,
        "layers": 64,
        "disk_size_gb": 180.0,
        "ram_resident_gb": 8.0,
        "target_binary": "deepseek_v41",
        "family": "dsv41",
        "color": "#ec4899",
        "tagline": "Advanced Multimodal & High-Throughput Deep Code Synthesis",
        "description": "Next-gen MoE with multi-head latent attention (MLA) and deep sparse activation. Optimized for vision-language tasks and heavy multi-file codebase operations.",
        "best_for": [
            "Full-stack software engineering & refactoring",
            "Complex document parsing & visual intelligence",
            "Multi-turn analytical deep-dives"
        ],
        "hardware_status": "requires_external_nvme",
        "default_experts_per_token": 8
    },
    "tier3": {
        "id": "tier3",
        "name": "Qwen3.8-Flash-Next (125B + 51B)",
        "badge": "Tier 3 · Balanced MoE",
        "total_params": "125B (+ 51B n-gram)",
        "active_params": "~14B / token",
        "total_experts": 8192,
        "layers": 48,
        "disk_size_gb": 65.0,
        "ram_resident_gb": 5.5,
        "target_binary": "qwen38",
        "family": "qwen38",
        "color": "#06b6d4",
        "tagline": "Balanced Enterprise Workhorse for Autonomous Tool Calling",
        "description": "Dual-stream MoE architecture with native speculative n-gram decoding. Delivers high accuracy for API orchestration, ETL pipelines, and daily development tasks.",
        "best_for": [
            "API tool calling & agent workflow orchestration",
            "Database SQL query optimization & data modeling",
            "Comprehensive technical documentation & summarization"
        ],
        "hardware_status": "tight_fit",
        "default_experts_per_token": 6
    },
    "tier4": {
        "id": "tier4",
        "name": "Qwen3.6-A3B (35B Compact)",
        "badge": "Tier 4 · Compact MoE",
        "total_params": "35B",
        "active_params": "~3B / token (8.5%)",
        "total_experts": 4096,
        "layers": 32,
        "disk_size_gb": 18.0,
        "ram_resident_gb": 3.8,
        "target_binary": "qwen36",
        "family": "qwen36",
        "color": "#10b981",
        "tagline": "Fast, High-Residency Local Assistant for Daily Workflows",
        "description": "Ultra-responsive 35B MoE with small disk footprint. Ideal for machines with standard NVMe drives, keeping almost all active experts pinned in RAM.",
        "best_for": [
            "Real-time code assistance & syntax fixes",
            "Rapid conversation & interactive brainstorming",
            "Structured JSON extraction & agent classification"
        ],
        "hardware_status": "ready_local",
        "default_experts_per_token": 4
    },
    "tier5": {
        "id": "tier5",
        "name": "OLMoE-1B-7B (Edge MoE)",
        "badge": "Tier 5 · Edge MoE",
        "total_params": "7B",
        "active_params": "~1B / token (14.2%)",
        "total_experts": 2048,
        "layers": 16,
        "disk_size_gb": 3.5,
        "ram_resident_gb": 1.5,
        "target_binary": "olmoe",
        "family": "olmoe",
        "color": "#f59e0b",
        "tagline": "Ultra-Low Latency Edge Model with Near-Zero Memory Footprint",
        "description": "Fully open 7B MoE running comfortably on lightweight CPUs. Loads in seconds and provides fast, deterministic outputs with minimal compute overhead.",
        "best_for": [
            "Sub-second command classification & intent detection",
            "Low-power edge execution & offline fallback",
            "High-frequency text categorization & parsing"
        ],
        "hardware_status": "ready_local",
        "default_experts_per_token": 2
    }
}
