from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def mcp_test_executer():
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_mcp_test_executer_async())
    else:
        return loop.run_until_complete(_mcp_test_executer_async())
    

async def _mcp_test_executer_async():
    # 1. Define how to connect to the server
    server_params = StdioServerParameters(
        command=".venv/bin/python",
        args=["src/mcp_server.py"]
    )
    
    # 2. Establish the core protocol session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 3. DIRECT CALL (No LLM involved)
            result = await session.call_tool("run_api_sanity_tests", arguments={})
            
            return {"test_results": result.content}





    
if __name__ == "__main__":
    import asyncio
    test_results = asyncio.run(mcp_test_executer())
    print(test_results)