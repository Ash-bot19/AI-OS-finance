from typing import Dict, Any
from copy import deepcopy
from tools.dcf_calculator import calculate_dcf


def run_scenario_analysis(
    base_inputs: Dict[str, Any],
    scenarios: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Runs DCF valuation across multiple scenarios.

    - base_inputs: full DCF input set
    - scenarios: dict of scenario_name -> input overrides
    """

    results = {}

    # -----------------------------
    # Base case
    # -----------------------------
    base_result = calculate_dcf(base_inputs)
    results["base"] = {
        "enterprise_value": base_result["enterprise_value"],
        "equity_value": base_result["equity_value"],
        "value_per_share": base_result["value_per_share"],
    }

    # -----------------------------
    # Scenario cases
    # -----------------------------
    for scenario_name, overrides in scenarios.items():
        scenario_inputs = deepcopy(base_inputs)

        # Apply overrides
        for key, value in overrides.items():
            scenario_inputs[key] = value

        scenario_result = calculate_dcf(scenario_inputs)

        results[scenario_name] = {
            "enterprise_value": scenario_result["enterprise_value"],
            "equity_value": scenario_result["equity_value"],
            "value_per_share": scenario_result["value_per_share"],
        }

    return results
