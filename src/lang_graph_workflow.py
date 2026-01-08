from langgraph.graph import StateGraph
from pydantic import BaseModel
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from utils import parse_mcp_result
from langchain_ollama import ChatOllama
from analysis_category import FailureAnalysis
from mcp_client import MCPClient
from constant import Constants

mcp = MCPClient()


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
    result = mcp.run_tool("run_api_sanity_tests")
    print(">>> MCP test execution result: %s", result)

    parsed = parse_mcp_result(result)

    return {
        "return_code": parsed["return_code"],
        "test_result": parsed["test_result"],
        "stderr": parsed.get("stderr"),
    }


### Anyalyze test results
def analyze_failure(state: State) -> FailureAnalysis | None:
    if state["return_code"] == 0:
        print("There is no test failure reported !!")
        return{
            "test_name": "Batch",
            "failure": "No",
            "category": "Passed",
            "analysis": "N/A",
            "possible_fix": "N/A",
        }


    else:

        model = ChatOllama(
            model=Constants.MODEL_NAME,
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

        Here are the test results: {state["test_result"]}"""
        llm_response = structured_model.invoke(prompt)
        print('=' * 60)
        print(llm_response)

        print("RAW LLM OUTPUT:")
        print(llm_response["raw"].content)

        print("PARSING ERROR:")
        print(llm_response["parsing_error"])

        parsed: FailureAnalysis | None = llm_response["parsed"]

        if parsed is None:
            raise ValueError(f"LLM parsing failed: {llm_response['parsing_error']}")

        return{
            "test_name": parsed.test_name,
            "failure": parsed.failure,
            "category": parsed.category,
            "analysis": parsed.analysis,
            "possible_fix": parsed.possible_fix,
        }

### Query SQL DB for data issues
def mcp_query_sql(state: State) -> dict:
    print(">>> entering mcp query sql tool")
    result = mcp.run_tool("mcp_query_sql")
    print(">>> MCP test execution result: %s", result)
    print("Querying SQL database for data issues...")
    return {"data_issue_found": True, "details": "Missing user record in DB."}

### Check Auth issues
def check_auth(state: State) -> dict:
    print("Checking authentication issues...")    
    return {"auth_issue_found": True, "details": "Invalid API token."}

### Check Service issues
def check_service(state: State) -> dict:
    print("Checking service availability...")    
    return {"service_issue_found": True, "details": "Service returned 503 error."}

### Human service node
def human_service(state: State) -> dict:
    print("Routing to human for further analysis and fix...")    
    return {"human_intervention": True, "details": "Please investigate the issue."}

### Test service node
def test_service(state: State) -> dict:
    with open(Constants.TEST_DATA_PATH, 'w') as f:
        f.write('saturn')
        print("Updated test data!!")     


def route_after_analysis(state: State) -> str:
    if "category" not in state:
        print("Test return code 0")
    else:
        category = state["category"]

        if category == "TEST_BUG":
            return "test-service"
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
workflow.add_node("check-auth", check_auth)
workflow.add_node("check-service", check_service)
workflow.add_node("human-service", human_service)
workflow.add_node("test-service", test_service)

workflow.set_entry_point("mcp-run-test")
workflow.add_edge("mcp-run-test", "analyze-failure")

workflow.add_conditional_edges(
    "analyze-failure",
    route_after_analysis,
)

workflow.set_finish_point("mcp-query-sql")
workflow.set_finish_point("check-auth")
workflow.set_finish_point("check-service")
workflow.set_finish_point("human-service")

compiled = workflow.compile()

# Execute workflow from START
initial_state = {}
run_test_node = compiled.invoke(initial_state)
