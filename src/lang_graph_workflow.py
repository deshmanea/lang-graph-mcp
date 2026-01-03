from langgraph.graph import StateGraph
from pydantic import BaseModel
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from mcp_client import mcp_test_executer
from utils import parse_mcp_result
from langchain_ollama import ChatOllama


class State(TypedDict, total=False):
    return_code: int
    test_result: dict
    stderr: str


def mcp_test_results(state: State) -> dict:
    print(">>> entering mcp_test_results")
    result = mcp_test_executer()
    print(">>> MCP test execution result: %s", result)

    parsed = parse_mcp_result(result["test_results"])

    return {
        "return_code": parsed["return_code"],
        "test_result": parsed["test_result"],
        "stderr": parsed.get("stderr"),
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


### Anyalyze test results
if run_test_node["return_code"] != 0:
    class FailureAnalysisWithErrorPossibleFix(BaseModel):
        '''An analysis of a failure along with a possible fix.'''
        test_name: str
        failure: str
        analysis: str
        possible_fix: str

    model = ChatOllama(
        model="qwen3:latest",
        validate_model_on_init=True,
        temperature=0.5,
    )

    structured_model = model.with_structured_output(
        FailureAnalysisWithErrorPossibleFix,
        include_raw=True,
    )

    prompt = f"""You are a software test quality expert analyse following failed test results and suggest a possible fix.
    Here are the test results: {run_test_node["test_result"]}"""
    llm_response = structured_model.invoke(prompt)
    print('=' * 60)
    print(llm_response)
