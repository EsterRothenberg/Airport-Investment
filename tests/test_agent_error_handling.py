import pytest
from unittest.mock import MagicMock, patch

from agent.agent import AirportInvestmentAgent, AgentError


class TestAgentErrorHandling:
    def test_agent_error_is_not_wrapped_again(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = AirportInvestmentAgent()
            
            mock_response = MagicMock()
            mock_response.id = "test-id"
            mock_response.output = []
            
            with patch.object(agent.client, "responses") as mock_responses:
                with patch.object(
                    agent,
                    "_resolve_tool_calls",
                    side_effect=AgentError("Tool error"),
                ):
                    with pytest.raises(AgentError) as exc_info:
                        agent.chat("test message")
                    
                    assert str(exc_info.value) == "Tool error"

    def test_agent_communication_error_is_wrapped(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = AirportInvestmentAgent()
            
            with patch.object(agent.client, "responses") as mock_responses:
                mock_responses.create.side_effect = Exception("API error")
                
                with pytest.raises(AgentError) as exc_info:
                    agent.chat("test message")
                
                assert "Agent communication failed" in str(exc_info.value)

    def test_empty_message_raises_agent_error(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = AirportInvestmentAgent()
            
            with pytest.raises(AgentError, match="Message cannot be empty"):
                agent.chat("")
            
            with pytest.raises(AgentError, match="Message cannot be empty"):
                agent.chat("   ")

    def test_max_tool_iterations_protection(self):
        with patch.dict(
            "os.environ",
            {"OPENAI_API_KEY": "test-key"},
        ):
            agent = AirportInvestmentAgent()

            mock_tool_call = MagicMock()
            mock_tool_call.type = "function_call"
            mock_tool_call.name = "test_tool"
            mock_tool_call.arguments = "{}"
            mock_tool_call.call_id = "call-1"

            mock_response = MagicMock()
            mock_response.id = "resp-id"
            mock_response.output = [mock_tool_call]

            with patch.object(
                agent,
                "_execute_tool",
                return_value={"success": True},
            ):
                with patch.object(
                    agent.client.responses,
                    "create",
                    return_value=mock_response,
                ):
                    with pytest.raises(
                        AgentError,
                        match="Max tool iterations exceeded",
                    ):
                        agent._resolve_tool_calls(
                            mock_response
                        )
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                agent = AirportInvestmentAgent()
                
                mock_tool_call = MagicMock()
                mock_tool_call.type = "function_call"
                mock_tool_call.name = "test_tool"
                mock_tool_call.arguments = "{}"
                mock_tool_call.call_id = "call-1"
                
                mock_response = MagicMock()
                mock_response.id = "resp-id"
                mock_response.output = [mock_tool_call]
                
                with patch.object(
                    agent, "_execute_tool", return_value={"success": True}
                ):
                    with pytest.raises(AgentError, match="Max tool iterations exceeded"):
                        agent._resolve_tool_calls(mock_response)
