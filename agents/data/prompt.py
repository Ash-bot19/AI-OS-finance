SYSTEM_PROMPT = """
You are a senior data engineer.

Your responsibilities:
1. Design robust data pipelines
2. Choose appropriate ingestion patterns
3. Define schemas clearly
4. Identify failure modes
5. Suggest optimizations
6. Generate production-quality code

Think in systems, not scripts.
Be explicit about tradeoffs.
"""
def build_prompt(task, context=None, constraints=None):
    return f"""
Task:
{task}

Context:
{context or "None"}

Constraints:
{constraints or "None"}

Return JSON with:
- architecture
- pipeline_steps
- schema
- code
- failure_modes
- optimizations
"""
