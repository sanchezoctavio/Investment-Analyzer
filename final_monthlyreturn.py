"""
CS32 Final Project: Investment Analyzer
"""

import random
import matplotlib.pyplot as plt

# Default S&P 500 historical averages (used when no asset mix is specified)
annual_mean = 0.10   # 10% average return
annual_std  = 0.15   # 15% volatility

monthly_mean = annual_mean / 12
monthly_std  = annual_std / (12 ** 0.5)

# ---------------------------------------------------------------------------
# Asset mix presets
# Each preset has its own historical-average annual mean and volatility.
# Stocks are higher-return / higher-risk; bonds are lower-return / lower-risk.
# ---------------------------------------------------------------------------
ASSET_MIXES = {
    "stocks": {
        "name":        "100% Stocks (S&P 500)",
        "annual_mean": 0.10,
        "annual_std":  0.15,
    },
    "balanced": {
        "name":        "60/40 Balanced",
        "annual_mean": 0.075,
        "annual_std":  0.10,
    },
    "conservative": {
        "name":        "40/60 Conservative",
        "annual_mean": 0.06,
        "annual_std":  0.07,
    },
    "bonds": {
        "name":        "100% Bonds",
        "annual_mean": 0.04,
        "annual_std":  0.05,
    },
}


def get_monthly_params(asset_mix="stocks"):
    """Return (monthly_mean, monthly_std) for the chosen asset mix."""
    mix = ASSET_MIXES.get(asset_mix, ASSET_MIXES["stocks"])
    m_mean = mix["annual_mean"] / 12
    m_std  = mix["annual_std"] / (12 ** 0.5)
    return m_mean, m_std


def draw_monthly_return(m_mean=monthly_mean, m_std=monthly_std):
    # Use random.gauss to pick a random point on the bell curve
    return random.gauss(m_mean, m_std)


def draw_year_of_returns(m_mean=monthly_mean, m_std=monthly_std):
    # Draw 12 monthly returns and return them as a list
    return [draw_monthly_return(m_mean, m_std) for _ in range(12)]


def compound_annual_return(monthly_returns):
    # Chain 12 monthly returns into a single annual return
    value = 1.0
    for r in monthly_returns:
        value *= (1 + r)
    return value - 1


# ---------------------------------------------------------------------------
# Step 2 (extended): single portfolio path
# Now supports asset mix and three contribution strategies:
#   - "flat":      same contribution every month (original behavior)
#   - "growing":   contribution grows by `contribution_growth` each year
#                  (e.g., 0.03 = a 3% raise every year)
#   - "lump_sum":  all future contributions are added at the start instead
# ---------------------------------------------------------------------------
def simulate_portfolio(initial_value, monthly_contribution, years,
                       asset_mix="stocks",
                       strategy="flat",
                       contribution_growth=0.0):
    m_mean, m_std = get_monthly_params(asset_mix)

    if strategy == "lump_sum":
        # Front-load every dollar that would have been contributed
        total_future_contributions = monthly_contribution * 12 * years
        portfolio_value = initial_value + total_future_contributions
        current_monthly = 0.0
    else:
        portfolio_value = initial_value
        current_monthly = monthly_contribution

    yearly_values = []

    for year in range(years):
        for _ in range(12):
            r = draw_monthly_return(m_mean, m_std)
            portfolio_value = portfolio_value * (1 + r) + current_monthly

        yearly_values.append(round(portfolio_value, 2))

        # Apply raise at end of year for next year's contributions
        if strategy == "growing":
            current_monthly *= (1 + contribution_growth)

    return yearly_values


# Step 3
def run_simulations(initial_value, monthly_contribution, years, num_simulations,
                    asset_mix="stocks",
                    strategy="flat",
                    contribution_growth=0.0):
    all_paths = []
    for _ in range(num_simulations):
        path = simulate_portfolio(
            initial_value, monthly_contribution, years,
            asset_mix=asset_mix,
            strategy=strategy,
            contribution_growth=contribution_growth,
        )
        all_paths.append(path)
    return all_paths


# Step 4
def analyze_results(all_paths, target_goal):
    num_simulations = len(all_paths)
    num_years = len(all_paths[0])
    year_bands = []

    for year in range(num_years):
        column = [all_paths[sim][year] for sim in range(num_simulations)]
        column.sort()

        p10 = column[int(num_simulations * 0.10)]
        p50 = column[int(num_simulations * 0.50)]
        p90 = column[int(num_simulations * 0.90)]

        year_bands.append({"year": year + 1, "p10": p10, "p50": p50, "p90": p90})

    final_values = [all_paths[sim][-1] for sim in range(num_simulations)]
    success_count = sum(1 for v in final_values if v >= target_goal)
    probability = round(success_count / num_simulations * 100, 1)

    return {
        "year_bands":            year_bands,
        "probability_of_success": probability,
        "median_final":          year_bands[-1]["p50"],
    }


def years_to_target(year_bands, target_goal):
    """First year in which the median portfolio value reaches the target, or None."""
    for band in year_bands:
        if band["p50"] >= target_goal:
            return band["year"]
    return None


# Step 6 (kept for the CLI demo)
def plot_results(results, target_goal, years):
    years_x = [band["year"] for band in results["year_bands"]]
    p10 = [band["p10"] for band in results["year_bands"]]
    p50 = [band["p50"] for band in results["year_bands"]]
    p90 = [band["p90"] for band in results["year_bands"]]

    plt.figure(figsize=(10, 6))
    plt.plot(years_x, p10, label="Pessimistic (p10)", color="red")
    plt.plot(years_x, p50, label="Median (p50)",      color="blue")
    plt.plot(years_x, p90, label="Optimistic (p90)",  color="green")
    plt.axhline(y=target_goal, color='gray', linestyle='--',
                label=f'Target Goal (${target_goal:,.0f})')
    plt.title("Portfolio Value Percentiles Over Time")
    plt.xlabel("Year")
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.grid(True)
    plt.savefig("portfolio_chart.png")
    print("Chart saved as portfolio_chart.png")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_tests():
    random.seed(42)
    samples = [draw_monthly_return() for _ in range(100000)]
    assert len(draw_year_of_returns()) == 12

    total = 0
    for r in samples:
        assert abs(r) < 0.60
        total += r
    sample_mean = total / len(samples)
    assert abs(sample_mean - monthly_mean) < 0.001

    # Step 2 tests
    path = simulate_portfolio(10000, 500, 30)
    assert len(path) == 30
    assert path[-1] > 0

    # Step 3 tests
    all_paths = run_simulations(10000, 500, 30, 1000)
    assert len(all_paths) == 1000
    assert len(all_paths[0]) == 30

    # Step 4 tests
    results = analyze_results(all_paths, 1000000)
    assert len(results["year_bands"]) == 30
    for band in results["year_bands"]:
        assert band["p10"] < band["p50"] < band["p90"]
    assert 0 <= results["probability_of_success"] <= 100

    # New: asset mix sanity check — bonds should have lower median than stocks
    random.seed(1)
    stocks_paths = run_simulations(10000, 500, 30, 500, asset_mix="stocks")
    random.seed(1)
    bonds_paths  = run_simulations(10000, 500, 30, 500, asset_mix="bonds")
    stocks_med = analyze_results(stocks_paths, 1)["median_final"]
    bonds_med  = analyze_results(bonds_paths, 1)["median_final"]
    assert stocks_med > bonds_med, "Stocks should outperform bonds in median over 30y"

    # New: lump_sum should produce higher final than flat (ignoring ordering risk avg)
    random.seed(7)
    flat_paths = run_simulations(10000, 500, 30, 500, strategy="flat")
    random.seed(7)
    lump_paths = run_simulations(10000, 500, 30, 500, strategy="lump_sum")
    assert analyze_results(lump_paths, 1)["median_final"] > \
           analyze_results(flat_paths, 1)["median_final"]

    print("All tests passed")


def demo():
    random.seed(99)
    print(f"Monthly mean: {monthly_mean*100:.4f}%  |  Monthly std: {monthly_std*100:.4f}%\n")
    for i in range(1, 4):
        months = draw_year_of_returns()
        annual = compound_annual_return(months)
        print(f"Year {i}: " + "  ".join(f"{r*100:+.1f}%" for r in months))
        print(f"        Annual Return: {annual*100:+.1f}%\n")

    # Step 5 user input
    print("Enter your own portfolio investment details")
    initial_value        = float(input("Starting portfolio value: $"))
    monthly_contribution = float(input("Monthly contribution: $"))
    years = int(input("Number of years to simulate: "))
    while years <= 0 or years > 60:
        print("Please enter a number of years between 1 and 60.")
        years = int(input("Number of years to simulate: "))
    target_goal = float(input("Target goal: $"))

    print(f"One portfolio simulation (${initial_value:,.0f} start, ${monthly_contribution:,.0f}/month, {years} years)")
    path = simulate_portfolio(initial_value, monthly_contribution, years)
    for i, value in enumerate(path):
        print(f"Year {i+1:>2}: ${value:>12,.2f}")

    print(f"\nRunning 1,000 simulations (${initial_value:,.0f} start, ${monthly_contribution:,.0f}/month, {years} years)")
    all_paths = run_simulations(initial_value, monthly_contribution, years, 1000)
    final_values = [path[-1] for path in all_paths]
    print(f"Lowest final value: ${min(final_values):,.2f}")
    print(f"Highest final value: ${max(final_values):,.2f}")

    print(f"\nPercentile bands by year (${target_goal:,.0f} target goal)")
    results = analyze_results(all_paths, target_goal)
    print(f" {'Year':>4} | {'Pessimistic (p10)':>18} | {'Median (p50)':>14} | {'Optimistic (p90)':>16}")
    print(f" {'-'*58}")
    for band in results["year_bands"]:
        print(f" {band['year']:>4} | ${band['p10']:>17,.0f} | ${band['p50']:>13,.0f} | ${band['p90']:>15,.0f}")
    print(f"\nProbability of reaching ${target_goal:,.0f} in {years} years: {results['probability_of_success']}%")

    plot_results(results, target_goal, years)


if __name__ == "__main__":
    run_tests()
    demo()
