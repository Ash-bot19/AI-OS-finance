# 🧠 AI OS for Financial Analysis  
**A Deterministic, Agentic Finance System (MOCK-first, PROD-ready)**

---

## 📌 Overview
![image alt](https://github.com/Ash-bot19/AI-OS-finance/blob/main/AI%20OS.png?raw=true)
**AI OS for Financial Analysis** is a production-shaped, agentic system designed to perform **deterministic financial valuation and scenario analysis** using strict agent boundaries, schema-validated data flow, and external orchestration.

The system intentionally prioritizes:

- **Correctness over prediction**
- **Determinism over probabilistic outputs**
- **Auditability over black-box automation**
- **MOCK-first execution with PROD readiness**

This project is **not** a trading bot or an “AI wrapper.”  
It is a **finance-grade analytical system** built to emulate how professional analyst workflows should be automated—safely and reproducibly.

---

## 🎯 Core Design Principles

- **Deterministic computation**  
  All financial math (DCF, scenario analysis) is strictly deterministic.  
  No LLM is ever used for numerical calculations.

- **Strict agent boundaries**  
  Each agent has a single responsibility and communicates only through schema-validated contracts.

- **Schema-first architecture**  
  All agent inputs and outputs are validated using hard JSON / Pydantic schemas.  
  No free-text handoffs. No hidden state.

- **MOCK-first, PROD-ready**  
  The system defaults to MOCK execution for safety, reproducibility, and cost control.  
  Switching to PROD LLM execution requires **no code changes**, only environment configuration.

- **External orchestration**  
  Execution is coordinated externally using **n8n**, keeping business logic inside code and orchestration outside.

---

## 🧩 System Architecture (Conceptual)
```
User / External Trigger
     ↓
FastAPI API Layer
     ↓
Research Agent (LLM – MOCK-first)
     ↓
Schema-Validated Boundary
     ↓
Data Engineering Agent
     ↓
Schema-Validated Boundary
     ↓
Finance Agent
 - Deterministic DCF Engine
 - Scenario Engine (Base / Bull / Bear)
        ↓
Versioned CSV Artifacts
```
### Orchestration (Sidecar)
n8n (External Control Plane)
 - HTTP triggers
 - Execution ordering
 - Error propagation
 - Retry / halt control

---

## 🤖 Agents & Responsibilities

### 1️⃣ Research Agent

**Responsibility:**  
Translate user intent into structured analytical context.

**What it does:**
- Interprets the analysis request (e.g., company, valuation intent)
- Generates narrative context and assumption scaffolding
- Uses LLMs **only** for reasoning and interpretation

**What it does NOT do:**
- No numerical computation  
- No valuation logic  
- No data mutation  

**Execution Mode:**  
- MOCK-first (deterministic responses)  
- PROD-ready via environment flag

---

### 🔐 Schema-Validated Boundary

Every agent handoff passes through a **hard schema gate**.

- JSON Schema / Pydantic enforced
- Fail-fast on contract violation
- No silent coercion
- Guarantees reproducibility

---

### 2️⃣ Data Engineering Agent

**Responsibility:**  
Prepare clean, validated financial datasets for downstream computation.

**What it does:**
- Validates incoming structured data
- Normalizes financial inputs
- Handles missing or partial fields explicitly
- Prepares time-series inputs for valuation

**Key properties:**
- Idempotent execution
- Backfill-safe
- No hidden state

---

### 🔐 Schema-Validated Boundary (Again)

Finance logic never runs unless data contracts are satisfied.

---

### 3️⃣ Finance Agent

**Responsibility:**  
Perform deterministic financial analysis.

**Components:**
- **Deterministic DCF Engine**
- **Scenario Engine** (Base / Bull / Bear)

**Hard guarantees:**
- ❌ No LLM involvement in math  
- ✅ Fully reproducible results  
- ✅ Same input → same output  

**Outputs:**
- Enterprise value
- Equity value
- Value per share
- Scenario-wise breakdowns

---

## 🔄 Orchestration with n8n

The system is orchestrated using **n8n** as an **external control plane**.

### What n8n does:
- Triggers execution via HTTP
- Controls execution order across agents
- Propagates errors explicitly
- Enables retries or halts

### What n8n does NOT do:
- No business logic
- No computation
- No data transformation

This separation ensures:
- Clear ownership of logic
- Easier debugging
- Safer evolution of the system

---

## 📤 Outputs

### Versioned CSV Artifacts

The final outputs are **analyst-ready CSV files**, not UI screenshots or console logs.

Example columns:
- `scenario` (base / bull / bear)
- `enterprise_value`
- `equity_value`
- `value_per_share`

These artifacts are:
- Diff-able
- Version-controlled
- Suitable for Excel / BI / downstream pipelines

---

## ⚙️ Execution Modes

### MOCK Mode (Default)
- Deterministic LLM stubs
- No external API calls
- Fully reproducible
- Safe for demos and testing

### PROD Mode (Optional)
- Real LLM execution
- Same interfaces
- Same schemas
- Same orchestration
- Enabled via environment variables only

---

## 🐳 Running the System Locally

### Prerequisites
- Docker
- Docker Compose

### Start the system

```bash
docker compose up
```
This will start:
- FastAPI service
- n8n orchestration engine
- All agents in a controlled environment

API Documentation
Once running:
bash
```
http://localhost:8000/docs
```
