import random

# Annual S&P 500 historical averages
# These are rough estimates based on long-term historical data,
# so not actual data being imported
annual_mean = 0.10   # 10% average return
annual_std  = 0.15   # 15% volatility

# Convert to monthly (mean divides by 12, std divides by sqrt(12))
monthly_mean = annual_mean / 12
monthly_std  = annual_std / (12 ** 0.5)

# Function to draw a single monthly return from the normal distribution
def draw_monthly_return():
    # Use random.gauss to pick a random point on bell curve
    # defined by our monthly mean and std
    return random.gauss(monthly_mean, monthly_std)

# Function to draw a year's worth of monthly returns
def draw_year_of_returns():
    # Draw 12 monthly returns and return them as a list
    return [draw_monthly_return() for _ in range(12)]


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


# Step 2
def simulate_portfolio(initial_value, monthly_contribution, years):
    # Simulate one possible portfolio path over a given number of years
    # Each month, grow the portfolio by a random return, then add the contribution
    # Record the portfolio value at the end of each year
    # Return a list of the portfolio value at the end of each year
    portfolio_value = initial_value
    yearly_values = []

    for year in range(years):
        # Simulate 12 months for this year
        for month in draw_year_of_returns():
            portfolio = portfolio_value * (1 + month) + monthly_contribution

        # Snapshot the portfolio value at the end of the year
        yearly_values.append(round(portfolio, 2))

    return yearly_values


# Test functions to validate the behavior of our monthly
# return generator and compounding logic

def run_tests():
    # random.seed is used to ensure that the same sequence of random numbers is generated each time we run the tests,
    random.seed(1)
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

    # Step 2 tests
    # simulate_portfolio should return one value per year
    path = simulate_portfolio(10000, 500, 30)
    assert len(path) == 30

    # portfolio should grow over time, so the final value should be higher than the initial value
    # initial + contributions
    total_contributed = 10000 + 500 * 12 * 30
    # shows that even a poor simulation should yield a final portfolio value that is
    # at least 50% of the total contributed amount, which would be a very bad return over 30 years
    assert path[-1] > total_contributed * 0.5

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

    # Show a full portfolio simulation over 10 years
    print("One portfolio simulation ($10,000 start, $500/month, 10 years)")
    random.seed(99)
    path = simulate_portfolio(10000, 500, 10)
    for i, value in enumerate(path):
        print(f"Year {i+1:>2}: ${value:>12,.2f}")


if __name__ == "__main__":
    run_tests()
    demo()

