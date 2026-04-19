def generate_recommendation(roi, irr, risk_level):

    score = 0

    # ROI Weight
    if roi > 20:
        score += 3
    elif roi > 10:
        score += 2
    elif roi > 5:
        score += 1

    # IRR Weight
    if irr > 15:
        score += 3
    elif irr > 8:
        score += 2
    elif irr > 0:
        score += 1

    # Risk Weight
    if risk_level == "Low":
        score += 3
    elif risk_level == "Medium":
        score += 2
    else:
        score += 0

    # 🔥 Improved Final Decision (Professional Text)
    if score >= 7:
        decision = "BUY - Strong Investment Opportunity"
    elif score >= 5:
        decision = "HOLD - Good Investment Potential"
    elif score >= 3:
        decision = "HOLD - Moderate Risk Investment"
    else:
        decision = "AVOID - High Risk Investment"

    return decision