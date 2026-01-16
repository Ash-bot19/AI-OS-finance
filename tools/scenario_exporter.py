import csv
import io
from typing import Dict, Any


def export_scenario_to_csv(scenario_result: Dict[str, Any]) -> str:
    """
    Convert scenario analysis output into a CSV string.

    Expected input format:
    {
        "base": {...},
        "bull": {...},
        "bear": {...}
    }
    """

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "scenario",
        "enterprise_value",
        "equity_value",
        "value_per_share"
    ])

    # Rows
    for scenario, metrics in scenario_result.items():
        writer.writerow([
            scenario,
            metrics.get("enterprise_value"),
            metrics.get("equity_value"),
            metrics.get("value_per_share")
        ])

    return output.getvalue()
