# Investment-Analyzer
This project simulates long-term investment portfolio growth to model variability of financial markets. Instead of relying on single fixed rate of return, this program should run randomized simulations of possible market futures.

By inputting initial portfolio value, monthly contributions, target financial goals, and risks involved. Compared against good and years of historic markets, it will deliver a possible range of what the investment should return.

How It Works

Each month of the simulation draws a random market return from a bell curve based on S&P 500 historical averages (10% mean annual return, 15% volatility). Running 1,000 of these simulated futures and analyzing the results produces a realistic range of outcomes — showing pessimistic, median, and optimistic portfolio values over time, along with the probability of hitting a target goal.

Project Steps

Step 1 — Algorithm Sketch

Designed the core Monte Carlo simulation algorithm. The key idea is that instead of assuming a fixed annual return, each month gets a random return drawn from a bell curve based on S&P 500 historical averages. Running 1,000 of these simulated futures and sorting the results produces a realistic range of outcomes — showing the pessimistic, median, and optimistic portfolio values over time, along with the probability of hitting a target goal.

Step 2 — Initial Implementation

Wrote and tested the foundational functions in Python using only the random module. This includes drawing a single random monthly return, compounding 12 months into an annual return, and simulating a full portfolio path over any number of years by growing the portfolio each month and recording yearly snapshots. All functions are verified with assertions to confirm correct output size, realistic return ranges, and statistical accuracy.
