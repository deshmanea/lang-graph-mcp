from langchain_mcp_adapters.client import MultiServerMCPClient

def server_client():
    client = MultiServerMCPClient(
        {
            "run-api-test-server": {
                "command": ".venv/bin/python",
                "args": ["src/mcp_server.py"],
                "transport": "stdio",
            }
        }
    )
    return client