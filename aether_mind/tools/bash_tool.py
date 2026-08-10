import asyncio
import subprocess
import os

async def run_bash(command: str, cwd: str = None, timeout: int = 30) -> str:
    """Executes a bash command safely within the specified workspace directory."""
    if not cwd or not os.path.exists(cwd):
        cwd = os.getcwd()
        
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            process.kill()
            return f"[ERROR] Command timed out after {timeout} seconds."
            
        out_str = stdout.decode('utf-8', errors='replace').strip()
        err_str = stderr.decode('utf-8', errors='replace').strip()
        
        res = ""
        if out_str:
            res += f"STDOUT:\n{out_str}\n"
        if err_str:
            res += f"STDERR:\n{err_str}\n"
        if not res:
            res = f"Command executed successfully (exit code {process.returncode})."
            
        return res[:4000]  # Cap response to avoid context bloat
    except Exception as e:
        return f"[ERROR] Failed to run command: {str(e)}"
