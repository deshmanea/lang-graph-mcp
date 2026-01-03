import json
from mcp.types import TextContent

def parse_mcp_result(content):
    """
    content: list[TextContent] OR single TextContent
    """
    if isinstance(content, list):
        content = content[0]

    if not isinstance(content, TextContent):
        raise TypeError(f"Unexpected MCP content type: {type(content)}")

    return json.loads(content.text)