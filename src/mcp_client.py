from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from typing import Any, Dict


class MCPClient:
    def __init__(
        self,
        command: str = ".venv/bin/python",
        args: list[str] = ["src/mcp_server.py"],
    ):
        self.server_params = StdioServerParameters(
            command=command,
            args=args,
        )

    async def _run_tool_async(
        self,
        tool_name: str,
        arguments: Dict[str, Any] | None = None,
    ) -> Any:
        arguments = arguments or {}

        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                return result.content

    def run_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any] | None = None,
    ) -> Any:
        """
        Safe sync wrapper (works inside or outside event loop)
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self._run_tool_async(tool_name, arguments))
        else:
            return loop.run_until_complete(
                self._run_tool_async(tool_name, arguments)
            )
