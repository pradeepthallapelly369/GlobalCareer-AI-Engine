import requests
import json
from typing import List, Dict, Any

class ModelConnector:
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "qwen2.5-coder:32b"):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def set_config(self, base_url: str, model_name: str):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def chat_completion(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sends chat messages to local inference engine (Ollama/vLLM/OpenAI format)."""
        # Try OpenAI compatible endpoint first
        url = f"{self.base_url}/v1/chat/completions"
        if not self.base_url.endswith("/v1") and "/v1" not in self.base_url and "11434" in self.base_url:
            url = f"{self.base_url}/v1/chat/completions"

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 4096
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        headers = {"Content-Type": "application/json"}

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=120)
            if resp.status_code == 200:
                return resp.json()
            else:
                # Fallback for native Ollama API endpoint (/api/chat)
                ollama_url = f"{self.base_url}/api/chat"
                ollama_payload = {
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.2, "num_ctx": 32768}
                }
                if tools:
                    ollama_payload["tools"] = tools

                ollama_resp = requests.post(ollama_url, json=ollama_payload, headers=headers, timeout=120)
                if ollama_resp.status_code == 200:
                    data = ollama_resp.json()
                    # Convert Ollama native response to standard OpenAI format
                    msg = data.get("message", {})
                    return {
                        "choices": [{
                            "message": {
                                "role": "assistant",
                                "content": msg.get("content", ""),
                                "tool_calls": msg.get("tool_calls", None)
                            }
                        }]
                    }
                return {"error": f"API HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"error": f"Failed to connect to local model backend at {self.base_url}: {str(e)}"}
