from langgraph.graph import StateGraph
from pydantic import BaseModel
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from mcp_client import mcp_test_executer
from utils import parse_mcp_result
from langchain_ollama import ChatOllama
from analysis_category import FailureAnalysis


class State(TypedDict, total=False):
    return_code: int
    test_result: dict
    stderr: str
    test_name:str
    failure:str
    category:str
    analysis:str
    possible_fix:str


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


### Anyalyze test results
def analyze_failure(state: State) -> FailureAnalysis | None:
    if run_test_node["return_code"] != 0:

        model = ChatOllama(
            model="qwen3:latest",
            validate_model_on_init=True,
            temperature=0.0,
        )

        structured_model = model.with_structured_output(
            FailureAnalysis,
            include_raw=True,
        )

        prompt = f"""You are a software test quality expert analyse following failed test results and suggest a possible fix.
        Classify the PRIMARY failure cause into one category.

        Rules:
        - Pick ONE category only
        - Base your decision on error patterns
        - Do not speculate beyond logs

        Here are the test results: {run_test_node["test_result"]}"""
        llm_response = structured_model.invoke(prompt)
        print('=' * 60)
        print(llm_response)
        return{
            "test_name": llm_response.test_name,
            "failure": llm_response.failure,
            "category": llm_response.category,
            "analysis": llm_response.analysis,
            "possible_fix": llm_response.possible_fix,
        }

### Query SQL DB for data issues
def mcp_query_sql(state: State) -> dict:
    print(">>> entering mcp query sql tool")
    result = mcp_test_executer()
    print(">>> MCP test execution result: %s", result)
    print("Querying SQL database for data issues...")
    return {"data_issue_found": True, "details": "Missing user record in DB."}


def route_after_analysis(state: State) -> str:
    category = state["category"]

    if category == "DATA_ISSUE":
        return "mcp-query-sql"
    if category == "AUTH_ISSUE":
        return "check-auth"
    if category == "SERVICE_UNAVAILABLE":
        return "check-service"
    if category == "ASSERTION_MISMATCH":
        return "human-service"  # human fix
    return "human-service"  # default to human fix
    
### Api test execution node
workflow = StateGraph(state_schema=State)
workflow.add_node("mcp-run-test", mcp_test_results)
workflow.add_node("analyze-failure", analyze_failure)
workflow.add_node("mcp-query-sql", mcp_query_sql)

workflow.set_entry_point("mcp-run-test")
workflow.set_finish_point("mcp-run-test")
compiled = workflow.compile()

# Execute workflow from START
initial_state = {}
run_test_node = compiled.invoke(initial_state)
