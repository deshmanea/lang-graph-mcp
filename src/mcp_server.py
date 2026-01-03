import sys
import traceback
import subprocess
import json
from pathlib import Path

try:
    from fastmcp import FastMCP
except Exception as e:
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    sys.exit(1)

# Initialize MCP server
mcp = FastMCP("run-api-test-server")

# Path to your Java project
PROJECT_DIR = Path("/home/abhijit/projects/java-api-demo")

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
        
        # Prepare the response
        response = {
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except Exception as e:
        response = {
            "return_code": -1,
            "stdout": "",
            "stderr": str(e)
        }

    return response  # Optional, FastMCP may use this internally

# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")


### TO_DO_Later ::Maven logs stream live to MCP in real time