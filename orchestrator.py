import os

from agents.research.agent import run as run_research_agent
from agents.data.agent import run as run_data_agent
from tools.executor import execute_tool
from core.schemas import AgentResponse
from agents.finance_v1.agent import run as run_finance_agent

def run_agent(agent: str, task: str, context=None, constraints=None, depth="brief") -> AgentResponse:
    """
    Central agent router with:
    - explicit agent selection
    - single tool-call maximum
    - no unbounded loops
    """

    # -----------------------------
    # 1. Dispatch to correct agent
    # -----------------------------
    if agent == "research":
        result = run_research_agent(task, context, depth)

    elif agent == "data":
        result = run_data_agent(task, context, constraints)
    
    elif agent == "finance":
        result = run_finance_agent(task, context)

    else:
        return AgentResponse(
            status="error",
            agent=agent,
            data=None,
            errors=[f"Unknown agent type: {agent}"],
            metadata={"llm_mode": os.getenv("LLM_MODE")}
        )

    # -----------------------------
    # 2. Handle tool request (ONE TIME)
    # -----------------------------
    if result.status == "tool_requested":
        tool_name = result.data.get("tool")
        tool_args = result.data.get("args", {})

        try:
            tool_result = execute_tool(tool_name, tool_args)
        except Exception as e:
            return AgentResponse(
                status="error",
                agent=agent,
                data=None,
                errors=[str(e)],
                metadata={"llm_mode": os.getenv("LLM_MODE")}
            )

        # -----------------------------
        # 3. Final agent call with tool context
        # -----------------------------
        if agent == "research":
            return run_research_agent(
                task=task,
                context=str(tool_result),
                depth=depth
            )

        if agent == "data":
            return run_data_agent(
                task=task,
                context=str(tool_result),
                constraints=constraints
            )

    # -----------------------------
    # 4. Normal success / error
    # -----------------------------
    return result
