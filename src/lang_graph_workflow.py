from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from mcp_client import mcp_test_executer
from utils import parse_mcp_result


class State(TypedDict, total=False):
    return_code: int
    api_result: dict
    stderr: str
    raw_logs: str


def mcp_test_results(state: State) -> dict:
    print(">>> entering mcp_test_results")
    result = mcp_test_executer()
    print(">>> MCP test execution result: %s", result)

    parsed = parse_mcp_result(result["test_results"])

    return {
        "return_code": parsed["return_code"],
        "api_result": parsed["api_result"],
        "stderr": parsed.get("stderr"),
        "raw_logs": parsed.get("raw_logs"),
    }

### Api test execution node
workflow = StateGraph(state_schema=State)
workflow.add_node("mcp-run-test", mcp_test_results)
workflow.set_entry_point("mcp-run-test")
workflow.set_finish_point("mcp-run-test")
compiled = workflow.compile()

# Execute workflow from START
initial_state = {}
run_test_node = compiled.invoke(initial_state)



### Router node to decide based test execution status
