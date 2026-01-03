from langgraph.graph import StateGraph, START
from pydantic import BaseModel
from mcp_lang_client import server_client

from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated, TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime


client = server_client()
tools = client.get_tools()

def reducer(a: list, b: int | None) -> list:
    if b is not None:
        return a + [b]
    return a

class State(TypedDict):
    x: Annotated[list, reducer]

class Context(TypedDict):
    r: float


# Define the MCP node function
def mcp_test_executer(state: State):
    # Call the FastMCP server
    result = client.run(
        server_name="run-api-test-server",
        input={"tool": "run_api_sanity_tests"}
    )
    state["test_results"] = result
    return {"test_results": result}  

### Api test execution node
workflow = StateGraph(state_schema=State, context_schema=Context)
workflow.add_node("mcp-run-test", mcp_test_executer)
workflow.set_entry_point("mcp-run-test")
workflow.set_finish_point("mcp-run-test")
compiled = workflow.compile()

# Execute workflow from START
initial_state = {}
run_test_node = compiled.invoke(initial_state)

### Router node to decide based test execution status
