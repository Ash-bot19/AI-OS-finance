import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

LLM_MODE = os.getenv("LLM_MODE", "MOCK")


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """
    Single public LLM entrypoint used by all agents.
    Must return a JSON string.
    """

    if LLM_MODE == "MOCK":
        return _mock_response(user_prompt)

    # REAL / PROD MODE
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt + """
You MUST respond ONLY with valid JSON.
You MUST include an "action" field.
"""
            },
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content


# -----------------------------
# PRIVATE MOCK IMPLEMENTATION
# -----------------------------
def _mock_response(user_prompt: str) -> str:
    prompt_lower = user_prompt.lower()

    # -----------------------------
    # FINANCE AGENT v2 (INTERPRETER) — MUST BE FIRST
    # -----------------------------
    if "interpret" in prompt_lower or "produce a finance analysis memo" in prompt_lower:
        return json.dumps({
            "action": "final",
            "result": {
                "thesis": "Conservative intrinsic valuation based on disciplined cash flow assumptions",
                "business_overview": "Large-cap, cash-generative business evaluated using a DCF framework",
                "key_drivers": [
                    "Revenue growth sustainability",
                    "Operating margin stability",
                    "Capital intensity"
                ],
                "assumptions": {
                    "revenue_growth": "5–7%",
                    "wacc": "9–10%",
                    "terminal_growth": "2–3%"
                },
                "valuation_method": "Discounted Cash Flow (DCF)",
                "valuation_summary": {
                    "approach": "Intrinsic valuation via projected FCFF discounted at WACC",
                    "note": "Final valuation depends on required placeholders"
                },
                "risks": [
                    "Terminal value sensitivity",
                    "Assumption variance"
                ],
                "sources": []
            }
        })

    # -----------------------------
    # FINANCE AGENT v1 (MODEL BUILDER)
    # -----------------------------
    if "model scaffold" in prompt_lower or "valuation model" in prompt_lower or "dcf" in prompt_lower:
        return json.dumps({
            "action": "final",
            "result": {
                "thesis": "Conservative intrinsic valuation framework",
                "model_type": "DCF",
                "assumptions": {
                    "revenue_growth": "5–7%",
                    "wacc": "9–10%",
                    "terminal_growth": "2–3%"
                },
                "model_scaffold": {
                    "time_horizon_years": 5,
                    "income_statement": ["Revenue", "EBITDA", "EBIT", "NOPAT"],
                    "cash_flow": ["CapEx", "ΔNWC", "FCFF"],
                    "discounting": ["WACC", "PV(FCFF)", "Terminal Value"]
                },
                "placeholders": {
                    "shares_outstanding": "REQUIRED",
                    "net_debt": "REQUIRED"
                },
                "checks": [
                    "WACC > terminal growth",
                    "Revenue growth fades to terminal"
                ],
                "risks": [
                    "Terminal value sensitivity",
                    "Margin compression"
                ],
                "sources": []
            }
        })

    # -----------------------------
    # RESEARCH TOOL FOLLOW-UP
    # -----------------------------
    if "tool result:" in prompt_lower:
        return json.dumps({
            "action": "final",
            "result": {
                "summary": "Spark Structured Streaming provides end-to-end exactly-once guarantees.",
                "key_points": [
                    "Uses checkpointing and write-ahead logs",
                    "Exactly-once depends on sink idempotency",
                    "Supports stateful stream processing"
                ],
                "risks": [
                    "Non-transactional sinks break guarantees",
                    "Checkpoint corruption can cause reprocessing"
                ]
            }
        })

    # -----------------------------
    # RESEARCH TOOL REQUEST
    # -----------------------------
    if "latest" in prompt_lower or "find" in prompt_lower:
        return json.dumps({
            "action": "tool_call",
            "tool": "web_search",
            "args": {
                "query": user_prompt[:200]
            }
        })

    # -----------------------------
    # DEFAULT FALLBACK
    # -----------------------------
    return json.dumps({
        "action": "final",
        "result": {
            "summary": "Mock research result",
            "key_points": ["Placeholder result"],
            "risks": []
        }
    })


