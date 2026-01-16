import json
import os
import time

from core.llm import call_llm
from core.schemas import AgentResponse
from agents.research.prompt import SYSTEM_PROMPT
from tools.registry import TOOLS
from tools.executor import execute_tool
from memory.retriever import retrieve
from core.logging import logger
from core.metrics import inc
from core.eval import record


def run(task, context=None, depth="brief"):
    """
    Research agent runner with:
    - enforced JSON output
    - explicit tool request handling
    - single tool-call maximum
    - RAG-before-generation
    - structured logging, metrics, and eval hooks
    """

    start_time = time.time()
    logger.info(f"[RESEARCH] Start | task='{task}'")

    try:
        # -----------------------------
        # 0. RAG — ALWAYS FIRST
        # -----------------------------
        docs = retrieve(task)
        retrieval_context = "\n".join(docs) if docs else "NO_RELEVANT_DOCUMENTS_FOUND"

        # -----------------------------
        # 1. Build user prompt (WITH RAG)
        # -----------------------------
        user_prompt = f"""
Task:
{task}

Retrieved Context:
{retrieval_context}

Additional Context:
{context or "None"}

Depth:
{depth}

Rules:
- You MUST ground answers in Retrieved Context.
- If Retrieved Context is empty, state assumptions explicitly.
- Respond ONLY in JSON.
"""

        # -----------------------------
        # 2. First LLM call
        # -----------------------------
        raw = call_llm(SYSTEM_PROMPT, user_prompt)
        parsed = json.loads(raw)

        # -----------------------------
        # 3. Tool request handling
        # -----------------------------
        if parsed.get("action") == "tool_call":
            tool_name = parsed.get("tool")
            tool_args = parsed.get("args", {})

            if tool_name not in TOOLS:
                elapsed = round(time.time() - start_time, 3)
                logger.error(f"[RESEARCH] Error | latency={elapsed}s | unregistered tool={tool_name}")
                inc("research.error")

                return AgentResponse(
                    status="error",
                    agent="research",
                    data=None,
                    errors=[f"Tool '{tool_name}' is not registered"],
                    metadata={"llm_mode": os.getenv("LLM_MODE")}
                )

            # Execute tool (platform-controlled)
            tool_result = execute_tool(tool_name, tool_args)

            # -----------------------------
            # 4. Second (final) LLM call
            # -----------------------------
            followup_prompt = f"""
Original Task:
{task}

Tool Used:
{tool_name}

Tool Result:
{tool_result}

Now return the FINAL answer.
Respond ONLY in JSON with:
{{
  "action": "final",
  "result": {{ ... }}
}}
"""

            raw_final = call_llm(SYSTEM_PROMPT, followup_prompt)
            final_parsed = json.loads(raw_final)

            if final_parsed.get("action") != "final":
                elapsed = round(time.time() - start_time, 3)
                logger.error(f"[RESEARCH] Error | latency={elapsed}s | no final after tool")
                inc("research.error")

                return AgentResponse(
                    status="error",
                    agent="research",
                    data=None,
                    errors=["Agent did not return a final answer after tool call"],
                    metadata={"llm_mode": os.getenv("LLM_MODE")}
                )

            # -----------------------------
            # 5. Success (after tool)
            # -----------------------------
            elapsed = round(time.time() - start_time, 3)
            logger.info(f"[RESEARCH] Success | latency={elapsed}s")
            inc("research.success")
            record("research", task, final_parsed.get("result"))

            return AgentResponse(
                status="success",
                agent="research",
                data=final_parsed.get("result"),
                errors=None,
                metadata={"llm_mode": os.getenv("LLM_MODE")}
            )

        # -----------------------------
        # 6. Direct final answer (no tool)
        # -----------------------------
        if parsed.get("action") == "final":
            elapsed = round(time.time() - start_time, 3)
            logger.info(f"[RESEARCH] Success | latency={elapsed}s")
            inc("research.success")
            record("research", task, parsed.get("result"))

            return AgentResponse(
                status="success",
                agent="research",
                data=parsed.get("result"),
                errors=None,
                metadata={"llm_mode": os.getenv("LLM_MODE")}
            )

        # -----------------------------
        # 7. Invalid action
        # -----------------------------
        elapsed = round(time.time() - start_time, 3)
        logger.error(f"[RESEARCH] Error | latency={elapsed}s | invalid action")
        inc("research.error")

        return AgentResponse(
            status="error",
            agent="research",
            data=None,
            errors=["Invalid agent action returned"],
            metadata={"llm_mode": os.getenv("LLM_MODE")}
        )

    # -----------------------------
    # 8. Hard failure catch
    # -----------------------------
    except Exception as e:
        elapsed = round(time.time() - start_time, 3)
        logger.error(f"[RESEARCH] Exception | latency={elapsed}s | error={str(e)}")
        inc("research.error")

        return AgentResponse(
            status="error",
            agent="research",
            data=None,
            errors=[str(e)],
            metadata={"llm_mode": os.getenv("LLM_MODE")}
        )
