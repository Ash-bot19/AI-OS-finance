# AI OS — Agentic Finance & Data System (v1)

A production-oriented, agentic GenAI system focused on **financial analysis, valuation, and scenario modeling**, built with strict reliability and cost-discipline principles.

## Core Capabilities
- Research Agent (RAG-first, tool-aware)
- Data Engineer Agent (pipeline & ETL design)
- Finance Agent v1 (DCF model scaffold)
- Finance Agent v2 (interpretation & narrative layer)
- Deterministic DCF Calculator (no LLMs)
- Scenario Analysis (Base / Bull / Bear)
- CSV Exports (valuation & scenarios)

## Architecture Highlights
- Clear separation of concerns:
  - Agents → reasoning & structure
  - Tools → deterministic computation
  - API → orchestration
- MOCK / PROD LLM mode abstraction
- No unbounded agent loops
- Explicit failure handling
- Analyst-ready outputs (CSV)

## Example Workflow
1. Build valuation model → `/finance/pipeline`
2. Run scenario analysis → `/finance/scenario`
3. Export results → `/finance/export/csv` or `/finance/scenario/export/csv`

## Environment Setup
Create a `.env` file locally (never committed):

```env
LLM_MODE=MOCK
OPENAI_API_KEY=your_api_key_here
```
## Run Locally
- python -m uvicorn api.main:app --reload
- http://127.0.0.1:8000/docs
