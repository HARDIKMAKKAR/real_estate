import numpy as np
import numpy_financial as npf


def calculate_noi(annual_rent, annual_expenses):
    return annual_rent - annual_expenses


def calculate_cap_rate(noi, property_price):
    return (noi / property_price) * 100


def calculate_cashflow(annual_rent, annual_expenses, annual_loan_payment):
    return annual_rent - annual_expenses - annual_loan_payment


def calculate_roi(total_profit, total_investment):
    return (total_profit / total_investment) * 100


def calculate_irr(initial_investment, annual_cashflow, years):
    appreciation_rate = 0.05  # 5% yearly growth (can tune)

    # Future property value
    future_price = initial_investment * ((1 + appreciation_rate) ** years)

    # Cashflow timeline
    cash_flows = [-initial_investment]

    for i in range(1, years):
        cash_flows.append(annual_cashflow)

    # Last year includes sale value
    cash_flows.append(annual_cashflow + future_price)

    irr = npf.irr(cash_flows)
    return irr * 100 if irr is not None else 0