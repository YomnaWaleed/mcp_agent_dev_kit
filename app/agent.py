# app/agent.py - Banking Agent with Real Data
import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Get MCP API key
MCP_API_KEY = os.getenv("MCP_API_KEY", "banking-dev-token-2026")

# Initialize MCP Toolset
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=["src/mcp/server.py"],
            env={"MCP_API_KEY": MCP_API_KEY},
        )
    )
)

# Create the banking agent
root_agent = Agent(
    name="banking_assistant",
    model=LiteLlm(model="ollama_chat/qwen3-vl:235b-cloud"),
    description="Banking assistant with database access",
    instruction=f"""Use the tools to fetch customer data. Customer IDs are integers like 1, 2, 3.

When user says "customer 1" or "customer ID 1", extract the number and call:
get_customer_info(customer_id=1, api_key="{MCP_API_KEY}")

Always use the tools. Never guess.""",
    tools=[mcp_toolset],
)
