import psutil
import subprocess

def get_system_stats() -> dict:
    """Returns local system metrics (CPU, RAM, GPU if available)."""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    
    gpu_info = "N/A"
    try:
        res = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            gpu_info = res.stdout.strip()
    except Exception:
        pass
        
    return {
        "cpu_usage": f"{cpu_percent}%",
        "ram_used_gb": round(ram.used / (1024**3), 2),
        "ram_total_gb": round(ram.total / (1024**3), 2),
        "ram_percent": f"{ram.percent}%",
        "gpu_stats": gpu_info
    }
