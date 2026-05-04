"""
CS32 Final Project: Investment Analyzer
"""

import random
import matplotlib.pyplot as plt

# Annual S&P 500 historical averages
# These are rough estimates based on long-term historical data,
# so not actual data being imported
annual_mean = 0.10   # 10% average return
annual_std  = 0.15   # 15% volatility

# Convert to monthly (mean divides by 12, std divides by sqrt(12))
monthly_mean = annual_mean / 12
monthly_std  = annual_std / (12 ** 0.5)

# Asset Mix Presets
ASSET_MIXES = {
    "stocks": {
        "name":         "100% Stocks (S&P 500)",
        "annual_mean":  0.10,
        "annual_std":   0.15
    },
    "balanced": {
        "name":         "60% Stocks / 40% Bonds",
        "annual_mean":  0.075,
        "annual_std":   0.10
    },
    "conservative": {
        "name":         "40% Stocks / 60% Bonds",
        "annual_mean":  0.06,
        "annual_std":   0.07,
    },
    "bonds": {
        "name":         "100% Bonds",
        "annual_mean":  0.04,
        "annual_std":   0.05
    }
}

def get_monthly_params(asset_mix="stocks"):
    """Return (monthly_mean, monthly_std) for the given asset mix"""
    mix = ASSET_MIXES.get(asset_mix, ASSET_MIXES["stocks"])
    monthly_mean = mix["annual_mean"] / 12
    monthly_std = mix["annual_std"] / (12 ** 0.5)
    return monthly_mean, monthly_std

# Function to draw a single monthly return from the normal distribution
def draw_monthly_return(monthly_mean=monthly_mean, monthly_std=monthly_std):
    # Use random.gauss to pick a random point on bell curve
    # defined by our monthly mean and std
    return random.gauss(monthly_mean, monthly_std)

# Function to draw a year's worth of monthly returns
def draw_year_of_returns(monthly_mean=monthly_mean, monthly_std=monthly_std):
    # Draw 12 monthly returns and return them as a list
    return [draw_monthly_return(monthly_mean, monthly_std) for _ in range(12)]


def compound_annual_return(monthly_returns):
    # Chain 12 monthly returns into a single annual return
    # Value is a $1 placeholder that we will grow by multiplying by (1 + monthly return),
    # the period makes it a float to reutrn as a decimal form after multiplication
    value = 1.0
    for r in monthly_returns:
        value *= (1 + r)
        # -1 at the end to convert back from growth factor to return percentage
        # example: if value is 1.20, that means we had a 20% return, so we subtract 1 to get 0.20
    return value - 1


def simulate_portfolio(initial_value, monthly_contribution, years,
                       asset_mix="stocks",
                       strategy="flat",
                       contribution_growth=0.0):
    monthly_mean, monthly_std = get_monthly_params(asset_mix)

    if strategy == "lump_sum":
        # Front load all contributions at the start of the simulation
        total_future_contributions = monthly_contribution * 12 * years
        portfolio_value = initial_value + total_future_contributions
        current_monthly = 0.0
    else:
        # Flat or growth strategy will contribute monthly as we go
        portfolio_value = initial_value
        current_monthly = monthly_contribution

    yearly_values = []
    # Simulate one possible portfolio path over a given number of years
    # Each month, grow the portfolio by a random return, then add the contribution
    # Record the portfolio value at the end of each year
    # Return a list of the portfolio value at the end of each year

    for year in range(years):
        # Simulate 12 months for this year
        for _ in range(12):
            r = draw_monthly_return(monthly_mean, monthly_std)
            portfolio_value = portfolio_value * (1 + r) + current_monthly

        # Snapshot the portfolio value at the end of the year
        yearly_values.append(round(portfolio_value, 2))

        if strategy == "growing":
            # Increase the monthly contribution by the growth rate for the next year
            current_monthly *= (1 + contribution_growth)

    return yearly_values

def run_simulations(initial_value, monthly_contribution, years, num_simulations,
                    asset_mix="stocks",
                    strategy="flat",
                    contribution_growth=0.0):
    # Run portfolio simulation multiple times to see a range of possible outcomes
    # Each run will produce a different path due to randomness,
    # so we can analyze the distribution of final values
    # Return list where each row is one simulation's yearly values
    all_paths = []

    for _ in range(num_simulations):
        path = simulate_portfolio(
            initial_value, monthly_contribution, years,
            asset_mix=asset_mix,
            strategy=strategy,
            contribution_growth=contribution_growth)
        all_paths.append(path)

    return all_paths

# Analyze the distribution of final portfolio values from our simulations,
# looking at metrics like the median, 10th percentile, and 90th percentile
# to understand the range of outcomes
# Count how many simulations reached target goal by final year
def analyze_results(all_paths, target_goal):
    num_simulations = len(all_paths)
    num_years = len(all_paths[0])
    year_bands = []

    for year in range(num_years):
        # Collect the portfolio values for this year across all simulations
        column = [all_paths[sim][year] for sim in range(num_simulations)]
        # sort column so it can be indexed to find percentiles
        column.sort()

        # indnex into sorted list to get the 10th, 50th (median), and 90th percentiles
        p10 = column[int(num_simulations * 0.10)]
        p50 = column[int(num_simulations * 0.50)]
        p90 = column[int(num_simulations * 0.90)]

        year_bands.append({"year": year + 1, "p10": p10, "p50": p50, "p90": p90})

    # Count how many simulations reached the target goal by the final year
    final_values = [all_paths[sim][-1] for sim in range(num_simulations)]
    success_count = sum(1 for value in final_values if value >= target_goal)
    probability = round(success_count / num_simulations * 100, 1)

    return {"year_bands": year_bands, "probability_of_success": probability,
            "median_final_value": year_bands[-1]["p50"],}

def years_to_target(year_bands, target_goal):
    """First year where the median (p50) value reaches the target goal, or None if it never does"""
    for band in year_bands:
        if band["p50"] >= target_goal:
            return band["year"]
    return None

def plot_results(results, target_goal, years):
    # Plot the percentile bands over time
    years = [band["year"] for band in results["year_bands"]]
    p10 = [band["p10"] for band in results["year_bands"]]
    p50 = [band["p50"] for band in results["year_bands"]]
    p90 = [band["p90"] for band in results["year_bands"]]

    plt.figure(figsize=(10, 6))
    plt.plot(years, p10, label="Pessimistic (p10)", color="red")
    plt.plot(years, p50, label="Median (p50)", color="blue")
    plt.plot(years, p90, label="Optimistic (p90)", color="green")
    plt.axhline(y=target_goal, color='gray', linestyle='--', label=f'Target Goal (${target_goal:,.0f})')
    plt.title("Portfolio Value Percentiles Over Time")
    plt.xlabel("Year")
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.grid(True)
    plt.savefig("portfolio_chart.png")

    print("Chart saved as portfolio_chart.png")

# Test functions to validate the behavior of our monthly
# return generator and compounding logic

def run_tests():
    # random.seed is used to ensure that the same sequence of random numbers is generated each time we run the tests,
    random.seed(42)
    samples = [draw_monthly_return() for _ in range(100000)]
    # debugging tool used to verify that a condition is True during program execution
    # confirms that a year actually produces 12 monthly returns and not some other number.
    assert len(draw_year_of_returns()) == 12

    total = 0
    for r in samples:
        # runs through 100,000 samples and checks none are more than +/- 60% in a month,
        #  which would be an extreme outlier for a monthly return
        assert abs(r) < 0.60
        total += r
    sample_mean = total / len(samples)
    # checks that the average of our 100,000 samples is close to the expected monthly mean
    assert abs(sample_mean - monthly_mean) < 0.001

    # simulate_portfolio should return one value per year
    path = simulate_portfolio(10000, 500, 30)
    assert len(path) == 30
    # Final portfolio value should be positive
    assert path[-1] > 0

    all_paths = run_simulations(10000, 500, 30, 1000)
    # We should have 1000 simulations, each with 30 yearly values
    assert len(all_paths) == 1000
    assert len(all_paths[0]) == 30

    results = analyze_results(all_paths, 1000000)
    # should be one band per year
    assert len(results["year_bands"]) == 30
    # p10 should be less than p50, which should be less than p90 for each year
    for band in results["year_bands"]:
        assert band["p10"] < band["p50"] < band["p90"]
    # probability of success should be between 0 and 100
    assert 0 <= results["probability_of_success"] <= 100

    # Asset Mix check, bonds should have lower mean than stocks
    random.seed(1)
    stocks_paths = run_simulations(10000, 500, 30, 500, asset_mix="stocks")
    random.seed(1)
    bonds_paths  = run_simulations(10000, 500, 30, 500, asset_mix="bonds")
    stocks_med = analyze_results(stocks_paths, 1)["median_final_value"]
    bonds_med  = analyze_results(bonds_paths, 1)["median_final_value"]
    assert stocks_med > bonds_med, "Stocks should outperform bonds in median over 30y"

    # lump_sum should produce higher than flat strategy because all contributions are invested from the start
    random.seed(7)
    flat_paths = run_simulations(10000, 500, 30, 500, strategy="flat")
    random.seed(7)
    lump_paths = run_simulations(10000, 500, 30, 500, strategy="lump_sum")
    assert analyze_results(lump_paths, 1)["median_final_value"] > \
           analyze_results(flat_paths, 1)["median_final_value"]

    print("All tests passed")

# Demo function to show how the monthly returns compound into an annual return

def demo():
    random.seed(99)
    print(f"Monthly mean: {monthly_mean*100:.4f}%  |  Monthly std: {monthly_std*100:.4f}%\n")
# Draw and display 3 years of returns to see how they compound into annual returns
    for i in range(1, 4):
        # generate list of 12 random monthly returns for the year,
        # then calculate the annual return by compounding those monthly returns together
        months = draw_year_of_returns()
        annual = compound_annual_return(months)
        # :+.f formats the number as a percentage with one decimal place and includes a plus sign for positive numbers
        print(f"Year {i}: " + "  ".join(f"{r*100:+.1f}%" for r in months))
        print(f"        Annual Return: {annual*100:+.1f}%\n")

    print("Enter your own portfolio investment details")
    initial_value = float(input("Starting portfolio value: $"))
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
    #print("\nRunning 1,000 simulations ($10,000 start, $500/month, 30 years)")
    all_paths = run_simulations(initial_value, monthly_contribution, years, 1000)
    #all_paths = run_simulations(10000, 500, 30, 1000)
    final_values = [path[-1] for path in all_paths]
    print(f"Lowest final value: ${min(final_values):,.2f}")
    print(f"Highest final value: ${max(final_values):,.2f}")

    print(f"\nPercentile bands by year (${target_goal:,.0f} target goal)")
    #print("\nPercentile bands by year ($1,000,000 target goal)")
    results = analyze_results(all_paths, target_goal)
    #results = analyze_results(all_paths, 1000000)
    print(f" {'Year':>4} | {'Pessimistic (p10)':>18} | {'Median (p50)':>14} | {'Optimistic (p90)':>16}")
    print(f" {'-'*58}")
    for band in results["year_bands"]:
        print(f" {band['year']:>4} | ${band['p10']:>17,.0f} | ${band['p50']:>13,.0f} | ${band['p90']:>15,.0f}")
    print(f"\nProbability of reaching ${target_goal:,.0f} in {years} years: {results['probability_of_success']}%")
    #print(f"\nProbability of reaching $1,000,000 in 30 years: {results['probability_of_success']}%")

    # Plot the results
    plot_results(results, target_goal, years)


if __name__ == "__main__":
    run_tests()
    demo()

