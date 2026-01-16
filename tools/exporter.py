import csv
import io
from typing import Dict, Any


def export_dcf_to_csv(dcf_result: Dict[str, Any]) -> str:
    """
    Export DCF calculation result to CSV.
    Returns CSV as string.
    """

    output = io.StringIO()
    writer = csv.writer(output)

    # ---- Header
    writer.writerow(["DCF PROJECTIONS"])

    # ---- Projection table
    projections = dcf_result.get("projections", [])

    if projections:
        writer.writerow([])
        writer.writerow(projections[0].keys())

        for row in projections:
            writer.writerow(row.values())

    # ---- Summary
    writer.writerow([])
    writer.writerow(["SUMMARY"])
    writer.writerow(["Enterprise Value", dcf_result.get("enterprise_value")])
    writer.writerow(["Equity Value", dcf_result.get("equity_value")])
    writer.writerow(["Value Per Share", dcf_result.get("value_per_share")])

    return output.getvalue()
