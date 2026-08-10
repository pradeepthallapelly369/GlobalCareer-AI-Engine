import asyncio
import sys
import os
from model_connector import ModelConnector
from agent_engine import AetherMindAgent

async def run_cli(task: str, model_name: str = "qwen2.5-coder:32b", base_url: str = "http://localhost:11434"):
    connector = ModelConnector(base_url=base_url, model_name=model_name)
    agent = AetherMindAgent(connector)
    cwd = os.getcwd()

    print(f"\n=======================================================")
    print(f" 🚀 AetherMind 70B Local Autonomous Agent CLI")
    print(f" Model: {model_name} | Target Dir: {cwd}")
    print(f"=======================================================\n")

    async for event in agent.run_task_stream(task, cwd=cwd):
        event_type = event.get("type")
        if event_type == "status":
            print(f"[STATUS] {event['data']}")
        elif event_type == "thought":
            print(f"\n🧠 [AetherMind Thought Step {event['step']}]\n{event['data']}")
        elif event_type == "tool_call":
            print(f"\n🛠️  [Tool Call: {event['tool']}]\nArguments: {event['args']}")
        elif event_type == "tool_output":
            print(f"📥 [Observation ({event['tool']})]\n{event['output']}\n" + "-"*50)
        elif event_type == "final_result":
            print(f"\n✅ [Task Complete]\n{event['data']}\n")
        elif event_type == "error":
            print(f"\n❌ [Error] {event['data']}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cli.py \"<Your task instructions here>\" [model_name] [base_url]")
        sys.exit(1)
        
    task_prompt = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5-coder:32b"
    url = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:11434"
    
    asyncio.run(run_cli(task_prompt, model_name=model, base_url=url))
