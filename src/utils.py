import json
import re
from mcp.types import TextContent

def parse_mcp_result(content):
    """
    content: TextContent | list[TextContent]
    """

    if isinstance(content, list):
        if not content:
            raise ValueError("Empty MCP content list")
        content = content[0]

    if not isinstance(content, TextContent):
        raise TypeError(f"Unexpected MCP content type: {type(content)}")

    text = content.text.strip()

    # Try direct JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: extract JSON object from logs
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in MCP output")

        return json.loads(match.group())