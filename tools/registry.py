from typing import Dict, Any
from tools.dcf_calculator import calculate_dcf
TOOLS: Dict[str, Dict[str, Any]] = {
    "web_search": {
        "description": "Search the web for factual information",
        "input_schema": {
            "query": "string"
        }
    },
    "read_file": {
        "description": "Read a local file from disk",
        "input_schema": {
            "path": "string"
        }
    },
    "dcf_calculator": {
        "description": "Calculate DCF valuation",
        "function": calculate_dcf
    }
}

