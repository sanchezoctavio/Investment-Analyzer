"""
Investment Portfolio Simulator — Flask web app
Reads user input from a form, runs simulations, and renders results in a template.
"""

from flask import Flask, render_template, request

# Import simulation engine functions from standalone module so we can keep this file focused on the web app logic.
from monthlyreturn import (
    run_simulations,
    analyze_results,
    years_to_target,
    ASSET_MIXES,
)

# Standard Flask boilerplate — creates the application object that
# routes requests to the functions defined later in this file.
app = Flask(__name__)

NUM_SIMULATIONS  = 1000
MAX_SCENARIOS    = 3
SCENARIO_COLORS  = ["#2c3e7a", "#c0392b", "#27ae60"]   # navy / red / green

# Defaults shown on first page load — pre-fills a meaningful comparison
# (same plan but different monthly contributions) so the user can just
# hit "Run" to see the chart.
DEFAULT_FORM_VALUES = {
    "scenario_1_name":     "Plan A",
    "scenario_1_initial":  "10000",
    "scenario_1_monthly":  "300",
    "scenario_1_growth":   "0",
    "scenario_1_years":    "30",
    "scenario_1_target":   "1000000",
    "scenario_1_mix":      "stocks",
    "scenario_1_strategy": "flat",

    "scenario_2_name":     "Plan B",
    "scenario_2_initial":  "10000",
    "scenario_2_monthly":  "500",
    "scenario_2_growth":   "0",
    "scenario_2_years":    "30",
    "scenario_2_target":   "1000000",
    "scenario_2_mix":      "stocks",
    "scenario_2_strategy": "flat",

    "scenario_3_name":     "",
    "scenario_3_initial":  "",
    "scenario_3_monthly":  "",
    "scenario_3_growth":   "0",
    "scenario_3_years":    "30",
    "scenario_3_target":   "1000000",
    "scenario_3_mix":      "stocks",
    "scenario_3_strategy": "flat",
}

# Pull all the scenario inputs out of the submitted HTML form and
# return them as a list of dictionaries — one dict per scenario that
# the user actually filled in.
def parse_scenarios(form):
    """Return a list of populated scenarios (skipping rows without a name)."""
    scenarios = []
    # Loop through scenario 1, 2, 3 (range stops before max+1)
    for i in range(1, MAX_SCENARIOS + 1):
        name = form.get(f"scenario_{i}_name", "").strip()
        if not name:
            continue
        # Same thing for starting value, if that's missing,
        # skip the scenario even if they filled in other fields.
        initial_raw = form.get(f"scenario_{i}_initial", "").strip()
        if not initial_raw:
            continue

        # Scenario dictionary
        scenarios.append({
            "name":                 name,
            "initial_value":        float(initial_raw),
            "monthly_contribution": float(form.get(f"scenario_{i}_monthly") or 0),
            "years":                int(form.get(f"scenario_{i}_years") or 30),
            "target_goal":          float(form.get(f"scenario_{i}_target") or 0),
            "asset_mix":            form.get(f"scenario_{i}_mix", "stocks"),
            "strategy":             form.get(f"scenario_{i}_strategy", "flat"),
            "contribution_growth":  float(form.get(f"scenario_{i}_growth") or 0) / 100.0,
            "color":                SCENARIO_COLORS[i - 1],
        })
    return scenarios


# Check a single parsed scenario for invalid inputs and return a
# human readable error message describing the first problem found.
# Returns None if the scenario passes every check.
def validate_scenario(s):
    """Return an error message if the scenario is invalid, else None."""
    # Starting value must be > 0, monthly contribution can't be negative,
    # years must be reasonable, etc.
    if s["initial_value"] <= 0:
        return f"'{s['name']}': starting value must be positive."
    # Monthly contribution can be zero (for lump sum scenarios) but not negative.
    if s["monthly_contribution"] < 0:
        return f"'{s['name']}': monthly contribution can't be negative."
    # Cap years at 60 to avoid very long runs that might crash the server
    # or make users wait too long.
    if s["years"] <= 0 or s["years"] > 60:
        return f"'{s['name']}': years must be between 1 and 60."
    # Target goal must be positive to avoid weirdness
    # in the probability of success calculation.
    if s["target_goal"] <= 0:
        return f"'{s['name']}': target goal must be positive."
    # Asset mix must be one of the predefined options we know how to simulate.
    if s["asset_mix"] not in ASSET_MIXES:
        return f"'{s['name']}': unknown asset mix."
    # Contribution strategy must be one of the options we know how to simulate.
    if s["strategy"] not in ("flat", "growing", "lump_sum"):
        return f"'{s['name']}': unknown contribution strategy."
    return None

# Run the simulations for one scenario and analyze the results to get the
# data we need to render the template.
def run_scenario(s):
    """Run NUM_SIMULATIONS sims for one scenario and analyze the result."""
    # Run NUM_SIMULATIONS independent portfolio paths using the user's
    # inputs. Each path is a list of yearly portfolio values. We get
    # back a list-of-lists with one row per simulation.
    paths = run_simulations(
        s["initial_value"], s["monthly_contribution"], s["years"],
        NUM_SIMULATIONS,
        asset_mix=s["asset_mix"],
        strategy=s["strategy"],
        contribution_growth=s["contribution_growth"],
    )
    return analyze_results(paths, s["target_goal"])

# Combine the user's inputs and the simulation results into a single
# dictionary ready to hand off to the HTML template (and to the
# Chart.js JavaScript on the page).
def build_scenario_payload(s, results):
    """Combine inputs + results into a serializable payload for the template."""
    return {
        "name":                   s["name"],
        "color":                  s["color"],
        "initial_value":          s["initial_value"],
        "monthly_contribution":   s["monthly_contribution"],
        "years":                  s["years"],
        "target_goal":            s["target_goal"],
        "asset_mix":              s["asset_mix"],
        "asset_mix_name":         ASSET_MIXES[s["asset_mix"]]["name"],
        "strategy":               s["strategy"],
        "contribution_growth_pct": round(s["contribution_growth"] * 100, 2),
        "year_bands":             results["year_bands"],
        "probability_of_success": results["probability_of_success"],
        "median_final_value":     results["median_final_value"],
        "years_to_target":        years_to_target(results["year_bands"], s["target_goal"]),
    }

# A what if analysis, re-run the base scenario with one input
# nudged up slightly, and report how each tweak changes the median
# final value and the probability of success.
def compute_impact(base_scenario, base_results):
    """
    Show how small tweaks to the base scenario change the outcome.
    Each entry compares to the base run we already have in hand,
    so we only run 3 extra simulation batches.
    """
    base_median = base_results["median_final_value"]
    base_prob   = base_results["probability_of_success"]
    impacts = []

    tweaks = [
        ("Add $100 / month",      {"monthly_contribution": base_scenario["monthly_contribution"] + 100}),
        ("Wait 5 more years",     {"years":                base_scenario["years"] + 5}),
        ("Start with $5,000 more",{"initial_value":        base_scenario["initial_value"] + 5000}),
    ]

    for label, override in tweaks:
        s = dict(base_scenario)
        s.update(override)
        # Cap years at 60 to match the validator (avoids surprise on 56+ scenarios)
        if s["years"] > 60:
            continue
        r = run_scenario(s)
        impacts.append({
            "label":         label,
            "median_change": r["median_final_value"]          - base_median,
            "prob_change":   r["probability_of_success"] - base_prob,
            "new_median":    r["median_final_value"],
            "new_prob":      r["probability_of_success"],
        })

    return impacts

# @app.route maps URL paths to Python functions. This one says:
# "when someone visits / using either GET (page load) or POST
# (form submission), call index()."
@app.route("/", methods=["GET", "POST"])
def index():
    # Initialize all four template variables to their "empty" state.
    # On a GET request these stay None and the page renders with just
    # the form (no results, no error). On a POST they may get filled in.
    scenarios_data = None
    impact_data    = None
    error          = None
    form_values    = dict(DEFAULT_FORM_VALUES)

    if request.method == "POST":
        # Overwrite defaults with whatever the user submitted so the form
        # stays filled in after submit.
        for k, v in request.form.items():
            form_values[k] = v

        try:
            scenarios = parse_scenarios(request.form)
            if not scenarios:
                error = "Please fill in at least one scenario (name + starting value)."
            else:
                for s in scenarios:
                    err = validate_scenario(s)
                    if err:
                        error = err
                        break

                if not error:
                    scenarios_data = []
                    base_results   = None
                    for idx, s in enumerate(scenarios):
                        results = run_scenario(s)
                        scenarios_data.append(build_scenario_payload(s, results))
                        if idx == 0:
                            base_results = results

                    impact_data = compute_impact(scenarios[0], base_results)

        except (ValueError, KeyError):
            error = "Please enter numbers only — no letters or symbols."

    return render_template(
        "final_index.html",
        scenarios_data=scenarios_data,
        impact_data=impact_data,
        asset_mixes=ASSET_MIXES,
        error=error,
        form_values=form_values,
    )


if __name__ == "__main__":
    app.run(debug=True)
