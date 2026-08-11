import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from agent.prompts import SYSTEM_PROMPT
from agent.tool_definitions import TOOLS
from agent.tools import (
    analyze_airport,
    compare_airports,
    find_airports,
    get_long_haul_analysis,
    rank_airports,
    rank_airports_by_geography,
)


load_dotenv()


class AgentError(Exception):
    pass


class AirportInvestmentAgent:
    def __init__(
        self,
        model: str | None = None,
    ):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")

        self.client = OpenAI(api_key=api_key)

        self.model = model or os.getenv(
            "OPENAI_MODEL",
            "gpt-4o-mini",
        )

        # Keeps conversational context between chat() calls.
        self.previous_response_id: str | None = None

        # Maps the tool name returned by the LLM
        # to the actual Python function.
        self.tool_map = {
            "analyze_airport": analyze_airport,
            "compare_airports": compare_airports,
            "get_long_haul_analysis": get_long_haul_analysis,
            "rank_airports": rank_airports,
            "find_airports": find_airports,
            "rank_airports_by_geography": rank_airports_by_geography,
        }

    def chat(
        self,
        message: str,
    ) -> str:

        if not message or not message.strip():
            raise AgentError("Message cannot be empty")

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=SYSTEM_PROMPT,
                input=message,
                tools=TOOLS,
                previous_response_id=self.previous_response_id,
            )

            response = self._resolve_tool_calls(response)

            self.previous_response_id = response.id

            return response.output_text

        except AgentError:
            raise

        except Exception as exc:
            raise AgentError(f"Agent communication failed: {exc}") from exc

    def reset(self) -> None:
        """
        Start a new conversation.
        """
        self.previous_response_id = None

    def _resolve_tool_calls(
        self,
        response,
    ):

        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            
            tool_calls = [
                item for item in response.output if item.type == "function_call"
            ]

            if not tool_calls:
                return response

            tool_outputs = []

            for tool_call in tool_calls:
                result = self._execute_tool(
                    tool_name=tool_call.name,
                    arguments_json=tool_call.arguments,
                )

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": json.dumps(
                            result,
                            ensure_ascii=False,
                            default=str,
                        ),
                    }
                )

            try:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=SYSTEM_PROMPT,
                    tools=TOOLS,
                    previous_response_id=response.id,
                    input=tool_outputs,
                )
            except Exception as exc:
                raise AgentError(f"Tool execution failed: {exc}") from exc
        
        raise AgentError("Max tool iterations exceeded")

    def _execute_tool(
        self,
        tool_name: str,
        arguments_json: str,
    ) -> dict | list:

        tool = self.tool_map.get(tool_name)

        if tool is None:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
            }

        try:
            arguments = json.loads(arguments_json)
            result = tool(**arguments)
            return {"success": True, "data": result}

        except json.JSONDecodeError as exc:
            return {
                "success": False,
                "error": f"Invalid tool arguments JSON: {exc}",
                "tool": tool_name,
            }

        except ValueError as exc:
            return {
                "success": False,
                "error": f"Invalid argument value: {exc}",
                "tool": tool_name,
            }

        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
                "tool": tool_name,
                "type": type(exc).__name__,
            }
