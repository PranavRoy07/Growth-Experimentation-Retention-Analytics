from pathlib import Path
from math import sqrt
import pandas as pd
from scipy.stats import chi2_contingency

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "marketing_ab_clean.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "statistical_results.md"

df = pd.read_csv(INPUT_PATH)

# Create the two-by-two contingency table
table = pd.crosstab(df["test_group"], df["converted"])

# Keep groups in a consistent order: control first, treatment second
control = table.loc["psa"]
treatment = table.loc["ad"]

control_users = control.sum()
treatment_users = treatment.sum()

control_conversions = control[True]
treatment_conversions = treatment[True]

control_rate = control_conversions / control_users
treatment_rate = treatment_conversions / treatment_users
difference = treatment_rate - control_rate

# Chi-square test
chi2, p_value, degrees_of_freedom, expected = chi2_contingency(
    [[control[False], control[True]],
     [treatment[False], treatment[True]]]
)

# 95% confidence interval for the raw conversion-rate difference
standard_error = sqrt(
    (treatment_rate * (1 - treatment_rate) / treatment_users)
    + (control_rate * (1 - control_rate) / control_users)
)

ci_lower = difference - 1.96 * standard_error
ci_upper = difference + 1.96 * standard_error

# Assumption checks for a chi-square test
minimum_expected_count = expected.min()
assumptions_pass = minimum_expected_count >= 5

# Practical-significance threshold chosen in Phase 1
mde = 0.02
statistically_significant = p_value < 0.05
practically_significant = difference >= mde

report = f"""# Statistical Analysis Results

## Business question
Does showing a regular ad (`ad`) increase conversion compared with showing a public-service announcement (`psa`)?

## Test used
Chi-square test of independence for the categorical outcome `converted`.

## Group results
| Group | Users | Conversions | Conversion rate |
|---|---:|---:|---:|
| PSA control | {control_users:,} | {control_conversions:,} | {control_rate:.2%} |
| Ad treatment | {treatment_users:,} | {treatment_conversions:,} | {treatment_rate:.2%} |

## Test result
- Chi-square statistic: {chi2:.3f}
- Degrees of freedom: {degrees_of_freedom}
- P-value: {p_value:.3e}
- Statistical significance threshold: 0.05

## Effect size
- Raw conversion-rate difference: {difference:.2%} ({difference * 100:.2f} percentage points)
- 95% confidence interval: {ci_lower:.2%} to {ci_upper:.2%}
- Minimum detectable effect (MDE): {mde:.0%} ({mde * 100:.0f} percentage points)

## Assumption checks
- Independent user-level observations: assumed from unique user IDs.
- Expected count rule: smallest expected cell count = {minimum_expected_count:.1f}.
- Expected counts are at least 5: {assumptions_pass}.
- Normality and equal-variance checks are not required because conversion is a binary categorical metric, not a continuous metric.

## Decision
- Statistically significant: {statistically_significant}
- Practically significant at the 2-point MDE: {practically_significant}

Although the ad group has a statistically higher conversion rate, the observed lift does not meet the pre-defined 2-percentage-point MDE. Under the original decision rule, this result alone does not justify a full rollout.
"""

OUTPUT_PATH.write_text(report, encoding="utf-8")

print(report)
print(f"Saved report to: {OUTPUT_PATH}")