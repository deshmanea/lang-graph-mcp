import sys
import traceback
import subprocess
import json
from pathlib import Path
import re

ANSI_ESCAPE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)

try:
    from fastmcp import FastMCP
except Exception as e:
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    sys.exit(1)

# Initialize MCP server
mcp = FastMCP("run-api-test-server")

# Path to your Java project
PROJECT_DIR = Path("/home/abhijit/IdeaProjects/api-tests")

@mcp.tool(name="run_api_sanity_tests")
def run_maven_tests():

    """
    Execute backend API sanity tests using Maven.
    This tool MUST be used to run API tests.
    """
      
    # The command to run
    command = ["mvn", "test", "-Dtags=sanity"]

    try:
        # Run the command and capture output
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_DIR
            
        )

        clean_stdout = strip_ansi(result.stdout)
        
        # Prepare the response
        response = {
            "return_code": result.returncode,
            "api_result": extract_api_result(result.stdout),
            "stderr": result.stderr,
            "raw_logs": clean_stdout
        }

    except Exception as e:
        response = {
            "return_code": -1,
            "api_result": None,
            "stderr": str(e),
            "raw_logs": clean_stdout
        }

    return response  # Optional, FastMCP may use this internally

def extract_api_result(stdout: str) -> dict | None:
    for line in stdout.splitlines():
        if line.startswith("API_RESULT::"):
            payload = line[len("API_RESULT::"):]
            return json.loads(payload)

    return None

# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")


### TO_DO_Later ::Maven logs stream live to MCP in real time