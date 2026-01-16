from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union

class AgentResponse(BaseModel):
    status: str                  # "success" | "error"
    agent: str                   # research | data | etc
    data: Optional[Dict[str, Any]]
    errors: Optional[List[str]]
    metadata: Dict[str, Any]

class FinanceModelScaffold(BaseModel):
    thesis: str
    model_type: str  # "DCF" | "Comps"
    assumptions: Dict[str, Union[str, float]]
    model_scaffold: Dict[str, Union[int, List[str]]]
    placeholders: Dict[str, str]
    checks: List[str]
    risks: List[str]
    sources: List[str]

class FinanceAnalysis(BaseModel):
    thesis: str
    business_overview: str
    key_drivers: List[str]
    assumptions: Dict[str, float | str]
    valuation_method: str
    valuation_summary: Dict[str, float | str]
    risks: List[str]
    sources: List[str]