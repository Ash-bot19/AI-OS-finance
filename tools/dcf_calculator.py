from typing import Dict, List, Union


def calculate_dcf(inputs: Dict) -> Dict:
    """
    Deterministic DCF calculator.
    - No LLMs
    - No external dependencies
    - Scalar-safe (API friendly)
    """

    # -----------------------------
    # 1. REQUIRED INPUTS (SAFE)
    # -----------------------------
    revenue = inputs.get("revenue") or inputs.get("base_revenue")
    if revenue is None:
        raise ValueError("Missing required input: revenue")

    shares_outstanding = inputs.get("shares_outstanding")
    net_debt = inputs.get("net_debt")

    if shares_outstanding is None and net_debt is None:
        raise ValueError("At least one of shares_outstanding or net_debt is required")

    # -----------------------------
    # 2. MODEL PARAMETERS
    # -----------------------------
    years = inputs.get("years", 5)

    revenue_growth = inputs.get("revenue_growth", 0.05)
    ebit_margin = inputs.get("ebit_margin", 0.25)
    tax_rate = inputs.get("tax_rate", 0.25)
    capex_pct = inputs.get("capex_pct", 0.05)
    nwc_pct = inputs.get("nwc_pct", 0.02)
    wacc = inputs.get("wacc", 0.09)
    terminal_growth = inputs.get("terminal_growth", 0.025)

    # -----------------------------
    # 3. NORMALIZE SCALARS → LISTS
    # -----------------------------
    if isinstance(revenue_growth, (int, float)):
        revenue_growth = [revenue_growth] * years

    if len(revenue_growth) != years:
        raise ValueError("revenue_growth length must equal number of years")

    # -----------------------------
    # 4. PROJECTIONS
    # -----------------------------
    projections: List[Dict[str, Union[int, float]]] = []
    fcff_list: List[float] = []

    current_revenue = float(revenue)

    for year in range(years):
        current_revenue *= (1 + revenue_growth[year])

        ebit = current_revenue * ebit_margin
        nopat = ebit * (1 - tax_rate)
        capex = current_revenue * capex_pct
        delta_nwc = current_revenue * nwc_pct

        fcff = nopat - capex - delta_nwc
        fcff_list.append(fcff)

        projections.append({
            "year": year + 1,
            "revenue": round(current_revenue, 2),
            "ebit": round(ebit, 2),
            "nopat": round(nopat, 2),
            "fcff": round(fcff, 2)
        })

    # -----------------------------
    # 5. DISCOUNT CASH FLOWS
    # -----------------------------
    discounted_fcff = [
        fcff_list[t] / ((1 + wacc) ** (t + 1)) for t in range(years)
    ]

    # Terminal value (Gordon Growth)
    if wacc <= terminal_growth:
        raise ValueError("WACC must be greater than terminal growth rate")

    terminal_value = (
        fcff_list[-1] * (1 + terminal_growth)
    ) / (wacc - terminal_growth)

    discounted_terminal = terminal_value / ((1 + wacc) ** years)

    enterprise_value = sum(discounted_fcff) + discounted_terminal

    equity_value = None
    if net_debt is not None:
        equity_value = enterprise_value - net_debt

    value_per_share = None
    if equity_value is not None and shares_outstanding is not None:
        value_per_share = equity_value / shares_outstanding

    # -----------------------------
    # 6. FINAL OUTPUT
    # -----------------------------
    return {
        "projections": projections,
        "enterprise_value": round(enterprise_value, 2),
        "equity_value": round(equity_value, 2),
        "value_per_share": round(value_per_share, 2)
    }
