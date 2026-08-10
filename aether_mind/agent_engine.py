import json
import asyncio
from typing import AsyncGenerator, Dict, Any, List
from model_connector import ModelConnector
from tools.bash_tool import run_bash
from tools.file_tool import read_file, write_file, list_workspace
from tools.system_tool import get_system_stats

SYSTEM_PROMPT = """You are AetherMind 70B, an autonomous local AI agent. You run 100% locally on user hardware with zero cloud dependencies or token limits.
Your mission is to perform real tasks for the user: write code, edit workspace files, run terminal commands, debug errors, and complete complex workflows.

AVAILABLE TOOLS:
1. execute_bash(command: str): Run a bash terminal command in the workspace directory.
2. read_file(path: str): Read the contents of a workspace file.
3. write_file(path: str, content: str): Create or update a file in the workspace.
4. list_workspace(directory: str): List files and folders in a workspace directory.
5. get_system_stats(): Monitor local GPU, VRAM, RAM, and CPU metrics.

BEHAVIORAL RULES:
- Always think step-by-step before executing tools.
- When asked to create or build something, write complete working files and verify by running commands if appropriate.
- Be concise, direct, and actionable.
- Once the task is fully completed, provide a clear final summary.
"""

# Tool JSON schemas for function calling
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "execute_bash",
            "description": "Execute a bash shell command in the local workspace.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "The command line string to run"}},
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file content from filesystem.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Absolute or relative file path"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write to"},
                    "content": {"type": "string", "description": "Text content to write"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_workspace",
            "description": "List directory contents.",
            "parameters": {
                "type": "object",
                "properties": {"directory": {"type": "string", "description": "Directory path"}},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_stats",
            "description": "Get current CPU, RAM, and GPU VRAM statistics.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

class AetherMindAgent:
    def __init__(self, connector: ModelConnector):
        self.connector = connector

    async def execute_tool(self, tool_name: str, args: dict, cwd: str = ".") -> str:
        try:
            if tool_name == "execute_bash":
                return await run_bash(args.get("command", ""), cwd=cwd)
            elif tool_name == "read_file":
                return read_file(args.get("path", ""))
            elif tool_name == "write_file":
                return write_file(args.get("path", ""), args.get("content", ""))
            elif tool_name == "list_workspace":
                return list_workspace(args.get("directory", cwd))
            elif tool_name == "get_system_stats":
                return json.dumps(get_system_stats(), indent=2)
            else:
                return f"[ERROR] Unknown tool '{tool_name}'"
        except Exception as e:
            return f"[ERROR] Tool execution failed: {str(e)}"

    async def run_task_stream(self, user_task: str, cwd: str = ".", max_steps: int = 15) -> AsyncGenerator[Dict[str, Any], None]:
        """Runs the ReAct agent loop and yields real-time step events."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Task: {user_task}\nWorking Directory: {cwd}"}
        ]

        yield {"type": "status", "data": f"Starting AetherMind Agent for task: '{user_task}'"}

        for step in range(1, max_steps + 1):
            yield {"type": "step_start", "step": step}

            # Call local 70B model
            response = self.connector.chat_completion(messages, tools=TOOLS_SCHEMA)
            
            if "error" in response:
                yield {"type": "error", "data": response["error"]}
                break

            choices = response.get("choices", [])
            if not choices:
                yield {"type": "error", "data": "No response choice returned from model backend."}
                break

            message = choices[0].get("message", {})
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", None)

            if content:
                yield {"type": "thought", "step": step, "data": content}

            # If no tool calls, model completed task or gave final response
            if not tool_calls:
                messages.append({"role": "assistant", "content": content})
                yield {"type": "final_result", "data": content}
                break

            # Handle tool call execution
            messages.append(message)
            for tool_call in tool_calls:
                function_info = tool_call.get("function", {})
                tool_name = function_info.get("name", "")
                
                # Parse arguments
                raw_args = function_info.get("arguments", "{}")
                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except Exception:
                        args = {}
                else:
                    args = raw_args

                yield {
                    "type": "tool_call",
                    "step": step,
                    "tool": tool_name,
                    "args": args
                }

                # Execute tool locally
                observation = await self.execute_tool(tool_name, args, cwd=cwd)

                yield {
                    "type": "tool_output",
                    "step": step,
                    "tool": tool_name,
                    "output": observation
                }

                # Append tool observation to conversation history
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", f"call_{step}"),
                    "name": tool_name,
                    "content": observation
                })

            await asyncio.sleep(0.1)
