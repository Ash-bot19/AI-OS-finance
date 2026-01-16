from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Optional, Union, Dict
from agents.research.agent import run as run_research
from agents.data.agent import run as run_data_agent
from agents.finance_v1.agent import run as run_finance_v1_agent
from agents.finance_v2.agent import run as run_finance_v2_agent
from fastapi.responses import PlainTextResponse
from fastapi.responses import Response


app = FastAPI(title="AI OS")

class ResearchRequest(BaseModel):
    task: str
    context: Optional[str] = None
    depth: str = "brief"

class DataAgentRequest(BaseModel):
    task: str
    context: Optional[str] = None
    constraints: Optional[Union[str, Dict]] = None

class FinancePipelineRequest(BaseModel):
    task: str
    context: Optional[str] = None
    dcf_inputs: Optional[Dict[str, Any]] = None

class FinanceV1Request(BaseModel):
    task: str
    context: Optional[str] = None

class FinanceV2Request(BaseModel):
    model_scaffold: Dict[str, Any]

class DCFCalculatorRequest(BaseModel):
    inputs: Dict[str, Any]

class FinanceExportRequest(BaseModel):
    valuation: Dict[str, Any]

class FinanceScenarioRequest(BaseModel):
    base_inputs: Dict[str, Any]
    scenarios: Dict[str, Dict[str, Any]]

class FinanceScenarioExportRequest(BaseModel):
    scenario_result: Dict[str, Dict[str, Any]]


@app.post("/research")
def research_agent(req: ResearchRequest):
    result = run_research(req.task, req.context, req.depth)
    return {"result": result}

@app.post("/data-engineer")
def data_engineer(req: DataAgentRequest):
    try:
        result = run_data_agent(req.task, req.context, req.constraints)
        return {"result": result}
    except Exception as e:
        return {
                "result": {
                "status": "error",
                "agent": "data_engineer",
                "data": None,
                "errors": [str(e)]
            }
        }
@app.post("/finance/v1")
def run_finance_v1(req: FinanceV1Request):
    result = run_finance_v1_agent(req.task, req.context)
    return {"result": result}

@app.post("/finance/v2")
def run_finance_v2(req: FinanceV2Request):
    result = run_finance_v2_agent(req.model_scaffold)
    return {"result": result}

@app.post("/finance/dcf")
def run_dcf_calculator(req: DCFCalculatorRequest):
    from tools.dcf_calculator import calculate_dcf
    result = calculate_dcf(req.inputs)
    return {
        "result": {
            "status": "success",
            "agent": "dcf_calculator",
            "data": result,
            "errors": None
        }
    }
@app.post("/finance/pipeline")
def run_finance_pipeline(req: FinancePipelineRequest):
    # ---- Step 1: Finance v1 (model builder)
    v1 = run_finance_v1_agent(req.task, req.context)

    if v1.status != "success" or not v1.data:
        return {
            "result": {
                "status": "error",
                "agent": "finance_pipeline",
                "data": None,
                "errors": ["Finance v1 failed"],
                "metadata": v1.metadata,
            }
        }

    valuation = None

    # ---- Step 2: Optional DCF calculator
    if req.dcf_inputs:
        from tools.dcf_calculator import calculate_dcf
        try:
            valuation = calculate_dcf(req.dcf_inputs)
        except Exception as e:
            return {
                "result": {
                    "status": "error",
                    "agent": "finance_pipeline",
                    "data": None,
                    "errors": [f"DCF calculator failed: {str(e)}"],
                    "metadata": v1.metadata,
                }
            }

    # ---- Step 3: Finance v2 (interpreter)
    v2 = run_finance_v2_agent(v1.data)

    if v2.status != "success" or not v2.data:
        return {
            "result": {
                "status": "error",
                "agent": "finance_pipeline",
                "data": None,
                "errors": ["Finance v2 failed"],
                "metadata": v1.metadata,
            }
        }

    # ---- Success
    return {
        "result": {
            "status": "success",
            "agent": "finance_pipeline",
            "data": {
                "model": v1.data,
                "valuation": valuation,
                "analysis": v2.data
            },
            "errors": None,
            "metadata": {
                "llm_mode": v1.metadata.get("llm_mode")
            }
        }
    }

@app.post("/finance/export/csv")
def export_finance_csv(req: FinanceExportRequest):
    from tools.exporter import export_dcf_to_csv

    csv_data = export_dcf_to_csv(req.valuation)

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=valuation.csv"
        }
    )

@app.post("/finance/scenario")
def run_finance_scenario(req: FinanceScenarioRequest):
    from tools.scenario_analyzer import run_scenario_analysis

    try:
        result = run_scenario_analysis(
            base_inputs=req.base_inputs,
            scenarios=req.scenarios
        )

        return {
            "result": {
                "status": "success",
                "agent": "scenario_analysis",
                "data": result,
                "errors": None
            }
        }

    except Exception as e:
        return {
            "result": {
                "status": "error",
                "agent": "scenario_analysis",
                "data": None,
                "errors": [str(e)]
            }
        }

@app.post("/finance/scenario/export/csv")
def export_finance_scenario_csv(req: FinanceScenarioExportRequest):
    from tools.scenario_exporter import export_scenario_to_csv

    try:
        csv_data = export_scenario_to_csv(req.scenario_result)

        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=scenario_analysis.csv"
            }
        )

    except Exception as e:
        return {
            "result": {
                "status": "error",
                "agent": "scenario_export",
                "data": None,
                "errors": [str(e)]
            }
        }
