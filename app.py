from flask import Flask, render_template, request
import matplotlib
matplotlib.use("Agg")  # use non-interactive backend so it works on a server
import matplotlib.pyplot as plt
import base64
import io

# Import all simulation functions from your existing file
from monthlyreturn import run_simulations, analyze_results

app = Flask(__name__)


def generate_chart(results, target_goal):
    # Pull percentile data out of results
    year_labels = [band["year"] for band in results["year_bands"]]
    p10_values  = [band["p10"]  for band in results["year_bands"]]
    p50_values  = [band["p50"]  for band in results["year_bands"]]
    p90_values  = [band["p90"]  for band in results["year_bands"]]

    # Build the chart
    plt.figure(figsize=(10, 5))
    plt.plot(year_labels, p10_values, color="red",   label="Pessimistic (p10)")
    plt.plot(year_labels, p50_values, color="blue",  label="Median (p50)")
    plt.plot(year_labels, p90_values, color="green", label="Optimistic (p90)")
    plt.fill_between(year_labels, p10_values, p90_values, alpha=0.1, color="blue")
    plt.axhline(y=target_goal, color="black", linestyle="--", label=f"Target: ${target_goal:,.0f}")
    plt.title("Investment Portfolio Simulation — Projected Growth")
    plt.xlabel("Year")
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.tight_layout()

    # Save chart to memory as a PNG and encode it as base64
    # so it can be embedded directly in the HTML page
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close()

    return image_base64


@app.route("/", methods=["GET", "POST"])
def index():
    results     = None
    chart       = None
    error       = None
    form_values = {}

    if request.method == "POST":
        try:
            # Read user inputs from the form
            initial_value        = float(request.form["initial_value"])
            monthly_contribution = float(request.form["monthly_contribution"])
            years                = int(request.form["years"])
            target_goal          = float(request.form["target_goal"])

            # Validate inputs
            if initial_value <= 0 or monthly_contribution < 0 or years <= 0 or years > 60 or target_goal <= 0:
                error = "Please enter valid values. Years must be between 1 and 60, all amounts must be positive."
            else:
                # Save form values so they stay filled in after submit
                form_values = {
                    "initial_value":        initial_value,
                    "monthly_contribution": monthly_contribution,
                    "years":                years,
                    "target_goal":          target_goal,
                }

                # Run the simulation
                all_paths = run_simulations(initial_value, monthly_contribution, years, 1000)
                results   = analyze_results(all_paths, target_goal)
                chart     = generate_chart(results, target_goal)

        except ValueError:
            error = "Please enter numbers only — no letters or symbols."

    return render_template("index.html",
                           results=results,
                           chart=chart,
                           error=error,
                           form_values=form_values)


if __name__ == "__main__":
    app.run(debug=True)
