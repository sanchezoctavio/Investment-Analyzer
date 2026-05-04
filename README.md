Investment Portfolio Simulator

Our program is an Investment Analyzer portfolio simulator that takes possible market futures for an investment portfolio and allows the user to then compare three different investment plans side-by-side.


What it does
The user picks a starting amount of money to invest, a monthly contribution amount, a time horizon to allow the money to grow, and a savings goal amount. The app then simulates 1,000 possible market futures by drawing monthly returns from a normal distribution set in accordance with long-run historical averages. It then shows the following:

The probability of reaching the set savings goal amount
A range of possible portfolio values at each year (10th, 50th, and 90th percentiles)
An interactive growth chart that lets the user see exact values
An impact analysis showing how small changes (an extra $100/month contributed, 5 more years of growth, $5,000 more upfront invested initially) affect the investment

You can run up to three scenarios at once to compare different asset mixes (Stocks / Balanced / Conservative / Bonds) and contribution strategies (flat monthly, with annual raises, or a single lump sum).


Features
Multi-scenario comparison: define up to three plans and overlay them on the same chart
Asset mix presets: switch between historical-average return / volatility profiles
Contribution strategies: flat, growing (annual raise %), or lump-sum
Quick presets: one-click setups for "Recent grad", "Mid-career saver", "Late starter", and "Aggressive vs Conservative"
Interactive Chart.js graph: hover for exact values, toggle p10/p90 ranges, click legend to hide individual scenarios
Impact analysis: automatic re-runs of the first scenario with small tweaks
Tabbed year-by-year breakdown: full percentile table for each scenario
Animated grid-beam background: pure CSS + SMIL-animated SVG, no JS framework


Setup
Special installment steps:
pip install flask matplotlib


Running the app
From the project root:
python3 final_app.py
Then open http://127.0.0.1:5000 in your browser.

You can also run the engine standalone (no web UI) to use the CLI version with prompts and a saved PNG chart:
python3 monthlyreturn.py



How it works
Each simulation draws 12 monthly returns for each year from random.gauss(mean, std), where mean and std come from the chosen asset mix. The portfolio compounds month by month: value = value * (1 + return) + monthly_contribution. After 1,000 paths, the results are analyzed by sorting each year's values and showing the 10th, 50th, and 90th percentile to produce the "pessimistic / median / optimistic" bands the user will see in the chart.

The probability of success is the fraction of the 1,000 simulated final values for the investment that meet or exceed the target goal amount.

The impact analysis runs the first scenario again three times over with one input slightly changed (+$100/month, +5 years, +$5,000 starting) and reports the change in median final value and probability of success.



Acknowledgements

Generative AI tools
We used Anthropic's Claude as a coding collaborator to extend our project from a single-scenario CLI / Flask demo into the multi-scenario comparison web app described above. Specifically:

Original work: the core of the Investment Analyzer simulation logic in monthlyreturn.py: draw_monthly_return, draw_year_of_returns, compound_annual_return, the original simulate_portfolio, run_simulations, analyze_results.

AI-assisted (Claude): Claude helped us extend monthlyreturn.py with the ASSET_MIXES preset dictionary, the get_monthly_params helper, the new asset_mix / strategy / contribution_growth parameters on simulate_portfolio and run_simulations, the years_to_target helper, and two additional unit tests (an asset-mix sanity check and a lump-sum vs flat comparison).

AI-assisted (Claude): Claude rewrote final_app.py to handle up to three scenarios per submission. Specifically, the helpers parse_scenarios, validate_scenario, run_scenario, build_scenario_payload, and the compute_impact analysis function were authored by Claude.

AI-assisted (Claude): Claude rewrote templates/final_index.html with the multi-scenario form, the preset buttons (Recent grad, Mid-career saver, etc.), Chart.js integration in place of the matplotlib PNG, the outcome-summary cards, the impact-analysis cards, the tab system for the breakdown table, and the CSS styling. Claude also helped refactor the template to eliminate false-positive lint warnings (moving dynamic colors to data-color attributes, consolidating duplicate <script> blocks, embedding the scenarios JSON in a <script type="application/json"> block).
