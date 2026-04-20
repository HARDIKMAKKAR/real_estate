import numpy as np


def monte_carlo_simulation(expected_return, volatility, simulations=1000):

    simulated_returns = np.random.normal(
        expected_return,
        volatility,
        simulations
    )

    return simulated_returns.tolist()   # convert to normal list



def calculate_risk_score(simulated_returns):

    simulated_array = np.array(simulated_returns)

    probability_of_loss = float(np.mean(simulated_array < 0))

    if probability_of_loss < 0.2:
        risk_level = "Low"
    elif probability_of_loss < 0.4:
        risk_level = "Medium"
    else:
        risk_level = "High"

    mean_return = float(np.mean(simulated_array))
    std_dev = float(np.std(simulated_array))
    best_case = float(np.max(simulated_array))
    worst_case = float(np.min(simulated_array))

    return {
        "probability_of_loss": round(probability_of_loss * 100, 2),
        "risk_level": risk_level,
        "mean_return": round(mean_return, 2),
        "volatility": round(std_dev, 2),
        "best_case": round(best_case, 2),
        "worst_case": round(worst_case, 2)
    }