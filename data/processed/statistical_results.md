# Statistical Analysis Results

## Business question
Does showing a regular ad (`ad`) increase conversion compared with showing a public-service announcement (`psa`)?

## Test used
Chi-square test of independence for the categorical outcome `converted`.

## Group results
| Group | Users | Conversions | Conversion rate |
|---|---:|---:|---:|
| PSA control | 23,524 | 420 | 1.79% |
| Ad treatment | 564,577 | 14,423 | 2.55% |

## Test result
- Chi-square statistic: 54.006
- Degrees of freedom: 1
- P-value: 1.999e-13
- Statistical significance threshold: 0.05

## Effect size
- Raw conversion-rate difference: 0.77% (0.77 percentage points)
- 95% confidence interval: 0.60% to 0.94%
- Minimum detectable effect (MDE): 2% (2 percentage points)

## Assumption checks
- Independent user-level observations: assumed from unique user IDs.
- Expected count rule: smallest expected cell count = 593.7.
- Expected counts are at least 5: True.
- Normality and equal-variance checks are not required because conversion is a binary categorical metric, not a continuous metric.

## Decision
- Statistically significant: True
- Practically significant at the 2-point MDE: False

Although the ad group has a statistically higher conversion rate, the observed lift does not meet the pre-defined 2-percentage-point MDE. Under the original decision rule, this result alone does not justify a full rollout.
