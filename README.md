# Investment-Analyzer
This project simulates long-term investment portfolio growth to model variability of financial markets. Instead of relying on single fixed rate of return, this program should run randomized simulations of possible market futures.

By inputting initial portfolio value, monthly contributions, target financial goals, and risks involved. Compared against good and years of historic markets, it will deliver a possible range of what the investment should return.

How It Works

Each month of the simulation draws a random market return from a bell curve based on S&P 500 historical averages (10% mean annual return, 15% volatility). Running 1,000 of these simulated futures and analyzing the results produces a realistic range of outcomes, showing pessimistic, median, and optimistic portfolio values over time, along with the probability of hitting a target goal. Running 1,000 of these simulated futures and analyzing the results produces a realistic range of outcomes.

Project Steps

Step 1: Drawing Random Returns

Wrote and tested the first foundational functions: drawing a single random monthly return from a normal distribution using random.gauss, chaining 12 monthly returns into a compounded annual return, and a demo that prints 3 example years of market returns. Tests verify that the output is always 12 values per year, no monthly return exceeds ±60%, and the average of 100,000 samples converges to the expected mean.

Step 2: Simulating a Full Portfolio

Built on Step 1 by adding simulate_portfolio, a function that takes a starting dollar amount, a monthly contribution, and a number of years, and simulates how the portfolio grows month by month. Each month the portfolio is multiplied by a random return and the contribution is added. The portfolio value is recorded at the end of each year, returning a list of yearly snapshots. Tests confirm the correct number of yearly values are returned and the final value is always positive.

Step 3: Running 1,000 Simulations

Added run_simulations, a function that calls simulate_portfolio 1,000 times, each with different random returns, and collects results into a  list where each row is one simulation's yearly portfolio values. Tests confirm the grid has exactly 1,000 rows and each row has the correct number of yearly values. The demo prints the lowest and highest final portfolio values across all 1,000 simulations to show the full range of possible outcomes.
Running 1,000 Simulations to capture market uncertainty and show range of possible results. Added run_simulations(), a function that calls simulate_portfolio 1,000 times, each with different random returns, and collects results into a  list where each row is one simulation's yearly portfolio values. Added a block to run_tests(). Tests confirm the grid has exactly 1,000 rows and each row has the correct number of yearly values (30). Added a block to def demo() that prints the lowest and highest final portfolio values across all 1,000 simulations to show the full range of possible outcomes.  

Step 5: User input

Added interactive user input and formatted output display to make the simulation practical. The program now prompts users to enter their own investment parameters (starting amount, monthly contribution, years, and target goal) and runs a complete Monte Carlo analysis based on their inputs.	

Citations

We used Claude to assist at certain points in this project, primarily for explanations and debugging help.
We used Claude to help explain certain Python concepts we weren't familiar with, such as how random.gauss works. We also used AI to find out how to structure the test assertions.

Debugging

When the code threw an AssertionError on the portfolio test, we used AI to help identify the cause. It pointed out that the assertion was testing something dependent on random market performance, and found out we had to update it to assert path[-1] > 0 instead.
