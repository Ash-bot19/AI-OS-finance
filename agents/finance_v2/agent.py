import json
import os
import time

from core.llm import call_llm
from core.schemas import AgentResponse
from agents.finance_v2.prompt import SYSTEM_PROMPT
from core.logging import logger
from core.metrics import inc
from core.eval import record


def run(model_scaffold: dict):
    start_time = time.time()
    logger.info("[FINANCE_V2] Start | interpreting model scaffold")

    try:
        user_prompt = f"""
MODEL SCAFFOLD (SOURCE OF TRUTH):
{json.dumps(model_scaffold, indent=2)}

Rules:
- Use ONLY this scaffold.
- Do NOT invent or adjust numbers.
- Produce a finance analysis memo.
- Respond ONLY in JSON.
"""

        raw = call_llm(SYSTEM_PROMPT, user_prompt)
        parsed = json.loads(raw)

        if parsed.get("action") != "final":
            inc("finance_v2.error")
            return AgentResponse(
                status="error",
                agent="finance_v2",
                data=None,
                errors=["Finance v2 failed to return final analysis"],
                metadata={"llm_mode": os.getenv("LLM_MODE")}
            )

        elapsed = round(time.time() - start_time, 3)
        logger.info(f"[FINANCE_V2] Success | latency={elapsed}s")
        inc("finance_v2.success")
        record("finance_v2", "interpret_model", parsed.get("result"))

        return AgentResponse(
            status="success",
            agent="finance_v2",
            data=parsed.get("result"),
            errors=None,
            metadata={"llm_mode": os.getenv("LLM_MODE")}
        )

    except Exception as e:
        inc("finance_v2.error")
        elapsed = round(time.time() - start_time, 3)
        logger.error(f"[FINANCE_V2] Exception | latency={elapsed}s | error={str(e)}")

        return AgentResponse(
            status="error",
            agent="finance_v2",
            data=None,
            errors=[str(e)],
            metadata={"llm_mode": os.getenv("LLM_MODE")}
        )
