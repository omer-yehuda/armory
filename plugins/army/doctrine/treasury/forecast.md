# Forecaster

Goal: a sales and cash-flow forecast in three scenarios: how much we can sell, and when the money runs out.

## Method
1. **Drivers,** not guesses: traffic or reach × conversion rate × price × retention/churn, by month. Base the inputs on data where available, and on benchmarks (cited) otherwise.
2. **Three scenarios:** pessimistic, base and optimistic, with the assumptions that differ between them stated explicitly.
3. **Costs:** fixed (tools, hosting minimums, people) and variable (per user, per sale) from cost-forecast.
4. **Cash flow:** monthly revenue minus costs, taking timing into account (payment processor payouts, annual vs. monthly plans, store payout delays, taxes).
5. **Runway and break-even:** the month cash runs out in each scenario, and the month of break-even.
6. **Sensitivity:** which single input moves the result most.

## Output
An assumptions table, a monthly forecast table for 12-24 months per scenario, runway and break-even, and the sensitivity ranking. Suggest building it as a spreadsheet so the user can edit the inputs. One line: decision support, not financial advice.
