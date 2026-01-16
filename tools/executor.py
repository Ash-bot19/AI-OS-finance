def execute_tool(tool_name: str, args: dict):
    if tool_name == "web_search":
        return {
            "results": [
                "Mock search result 1",
                "Mock search result 2"
            ]
        }

    if tool_name == "read_file":
        return {
            "content": "Mock file contents"
        }

    raise ValueError(f"Unknown tool: {tool_name}")
