# Investment-Analyzer
This project simulates long-term investment portfolio growth to model variability of financial markets. Instead of relying on single fixed rate of return, this program should run randomized simulations of possible market futures.

By inputting initial portfolio value, monthly contributions, target financial goals, and risks involved. Compared against good and years of historic markets, it will deliver a possible range of what the investment should return.

How It Works

Each month of the simulation draws a random market return from a bell curve based on S&P 500 historical averages (10% mean annual return, 15% volatility). Running 1,000 of these simulated futures and analyzing the results produces a realistic range of outcomes, showing pessimistic, median, and optimistic portfolio values over time, along with the probability of hitting a target goal. Running 1,000 of these simulated futures and analyzing the results produces a realistic range of outcomes.

Project Steps

Step 1: Drawing Random Returns

Wrote and tested the first foundational functions: drawing a single random monthly return from a normal distribution using random.gauss, chaining 12 monthly returns into a compounded annual return, and a demo that prints 3 example years of market returns. Tests verify that the output is always 12 values per year, no monthly return exceeds ±60%, and the average of 100,000 samples converges to the expected mean.

Step 2: Simulating a Full Portfolio

Built on Step 1 by adding simulate_portfolio, a function that takes a starting dollar amount, a monthly contribution, and a number of years, and simulates how the portfolio grows month by month. There is a monthly loop where each month the portfolio is multiplied by a random return and the contribution is added at the end of the month. The portfolio value is recorded at the end of each year, returning a list of yearly snapshots. Snapshots and rounding happen at the end of the yearly loops to keep code clean and to return a manageable number of outputs. Tests confirm the correct number of yearly values are returned and the final value is always positive. This function is then tested and demonstrated using a random but constant seed to make returns reproducible. Generative AI and research into Monte Carlo simulations were used in finding the typical path to test the simulation (giving us some standard values of $10000 starting, $500 monthly, and 30 years). Generative AI was also used in debugging and finding ideal formatting. An example is asking generative AI the best way to formulate the since changed line 213 to make formatting 1-10 and aligning the outputs correctly to give a right-aligned clean format.

Step 3: Running 1,000 Simulations

Added run_simulations, a function that calls simulate_portfolio 1,000 times, each with different random returns, and collects results into a  list where each row is one simulation's yearly portfolio values. Tests confirm the grid has exactly 1,000 rows and each row has the correct number of yearly values. The demo prints the lowest and highest final portfolio values across all 1,000 simulations to show the full range of possible outcomes.
Running 1,000 Simulations to capture market uncertainty and show range of possible results. Added run_simulations(), a function that calls simulate_portfolio 1,000 times, each with different random returns, and collects results into a  list where each row is one simulation's yearly portfolio values. Added a block to run_tests(). Tests confirm the grid has exactly 1,000 rows and each row has the correct number of yearly values (30). Added a block to def demo() that prints the lowest and highest final portfolio values across all 1,000 simulations to show the full range of possible outcomes.  

Step 4

In step 4 we created the analyze_results function taking all the paths created and the target amount as its inputs. The portfolio value at the end of each year is sorted into a column. These values were then sorted into low and high percentiles (p10, p50, and p90). The final value of the portfolio in each path is then calculated and compared to the target amount. The probability that the final portfolio value is above the target is calculated across simulations and then returned. The function is then called on and tested. Tests use $1000000 as an example target goal. Tests then confirm the correct number of yearly values, that the pessimistic (p10) return is less than the Median (p50) which is less than the Optimistic (p90) return values across simulations as a sanity check. Tests then confirm that the probability is a valid percentage (between 0 and 100). The function is then demonstrated running the analysis and printing the results cleanly. Generative AI and research on Monte Carlo simulations were used in debugging and ideal formatting once again. The two biggest examples are once again the print statements in 229-233 and needed help grabbing the final values cleanly in line 99. Original print statements were not cleanly formatted  and there were bugs in grabbing the final values of the portfolio so generative AI was consulted in how to format the returns cleanly. I gave the goal of line 99, to grab the final value of the portfolio, and it helped breakthrough this block.

Step 5: User input

Added interactive user input and formatted output display to make the simulation practical. The program now prompts users to enter their own investment parameters (starting amount, monthly contribution, years, and target goal) and runs a complete investment analysis based on their inputs.

Citations

We used Claude to assist at certain points in this project, primarily for explanations and debugging help.
We used Claude to help explain certain Python concepts we weren't familiar with, such as how random.gauss works. We also used AI to find out how to structure the test assertions.
For step 5, used AI to help debug, help format our outputs, and assist with proper f-string formatting.

Debugging

When the code threw an AssertionError on the portfolio test, we used AI to help identify the cause. It pointed out that the assertion was testing something dependent on random market performance, and found out we had to update it to assert path[-1] > 0 instead.
Step 5 Debugging: Initially had issues with the table alignment when dollar amounts varied in length. Used AI to help with f-string formatting with width specifiers and the format code for comma separators with no decimal places, which fixed the alignment issues and made the table look better.
