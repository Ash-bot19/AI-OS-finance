from core.llm import call_llm
from agents.data.prompt import SYSTEM_PROMPT, build_prompt
from core.schemas import AgentResponse
import json
import os

def run(task, context=None, constraints=None):
    try:
        raw = call_llm(SYSTEM_PROMPT, build_prompt(task, context, constraints))
        parsed = json.loads(raw)

        return AgentResponse(
            status="success",
            agent="data",
            data=parsed,
            errors=None,
            metadata={"llm_mode": os.getenv("LLM_MODE")}
        )

    except Exception as e:
        return AgentResponse(
            status="error",
            agent="data",
            data=None,
            errors=[str(e)],
            metadata={"llm_mode": os.getenv("LLM_MODE")}
        )

