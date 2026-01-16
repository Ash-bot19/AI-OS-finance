import json
import os
import time

from core.llm import call_llm
from core.schemas import AgentResponse
from agents.finance_v1.prompt import SYSTEM_PROMPT
from memory.retriever import retrieve
from tools.registry import TOOLS
from tools.executor import execute_tool
from core.logging import logger
from core.metrics import inc
from core.eval import record


def run(task, context=None):
    start_time = time.time()
    logger.info(f"[FINANCE] Start | task='{task}'")

    try:
        # -----------------------------
        # 0. RAG — ALWAYS FIRST
        # -----------------------------
        docs = retrieve(task)
        retrieval_context = "\n".join(docs) if docs else "NO_RELEVANT_DOCUMENTS_FOUND"

        # -----------------------------
        # 1. Build prompt (model-builder)
        # -----------------------------
        user_prompt = f"""
Task:
{task}

Retrieved Context:
{retrieval_context}

Additional Context:
{context or "None"}

Rules:
- Build a valuation MODEL SCAFFOLD.
- Use placeholders where inputs are missing.
- Respond ONLY in JSON.
"""

        # -----------------------------
        # 2. First LLM call
        # -----------------------------
        raw = call_llm(SYSTEM_PROMPT, user_prompt)
        parsed = json.loads(raw)

        # -----------------------------
        # 3. Tool request (optional)
        # -----------------------------
        if parsed.get("action") == "tool_call":
            tool = parsed.get("tool")
            args = parsed.get("args", {})

            if tool not in TOOLS:
                inc("finance.error")
                return AgentResponse(
                    status="error",
                    agent="finance",
                    data=None,
                    errors=[f"Tool '{tool}' not registered"],
                    metadata={"llm_mode": os.getenv("LLM_MODE")}
                )

            tool_result = execute_tool(tool, args)

            followup_prompt = f"""
Original Task:
{task}

Tool Used:
{tool}

Tool Result:
{tool_result}

Now return the FINAL model scaffold.
Respond ONLY in JSON with action='final'.
"""

            raw_final = call_llm(SYSTEM_PROMPT, followup_prompt)
            final_parsed = json.loads(raw_final)

            if final_parsed.get("action") != "final":
                inc("finance.error")
                return AgentResponse(
                    status="error",
                    agent="finance",
                    data=None,
                    errors=["Finance agent failed to return final scaffold"],
                    metadata={"llm_mode": os.getenv("LLM_MODE")}
                )

            elapsed = round(time.time() - start_time, 3)
            logger.info(f"[FINANCE] Success | latency={elapsed}s")
            inc("finance.success")
            record("finance", task, final_parsed.get("result"))

            return AgentResponse(
                status="success",
                agent="finance",
                data=final_parsed.get("result"),
                errors=None,
                metadata={"llm_mode": os.getenv("LLM_MODE")}
            )

        # -----------------------------
        # 4. Direct final answer
        # -----------------------------
        if parsed.get("action") == "final":
            elapsed = round(time.time() - start_time, 3)
            logger.info(f"[FINANCE] Success | latency={elapsed}s")
            inc("finance.success")
            record("finance", task, parsed.get("result"))

            return AgentResponse(
                status="success",
                agent="finance",
                data=parsed.get("result"),
                errors=None,
                metadata={"llm_mode": os.getenv("LLM_MODE")}
            )

        # -----------------------------
        # 5. Invalid action
        # -----------------------------
        inc("finance.error")
        return AgentResponse(
            status="error",
            agent="finance",
            data=None,
            errors=["Invalid finance agent action"],
            metadata={"llm_mode": os.getenv("LLM_MODE")}
        )

    except Exception as e:
        inc("finance.error")
        elapsed = round(time.time() - start_time, 3)
        logger.error(f"[FINANCE] Exception | latency={elapsed}s | error={str(e)}")

        return AgentResponse(
            status="error",
            agent="finance",
            data=None,
            errors=[str(e)],
            metadata={"llm_mode": os.getenv("LLM_MODE")}
        )
