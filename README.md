# Growth Experimentation & Retention Analytics

**Live app:** [Open the interactive dashboard](https://YOUR-APP.streamlit.app)

## Recommendation

Do not fully roll out the regular-ad experience yet. It increased conversion from 1.79% to 2.55%, a statistically significant lift of 0.77 percentage points. However, this result did not meet the pre-defined 2-percentage-point minimum detectable effect, so the commercial impact is not yet large enough to justify a full rollout. Run a follow-up experiment that measures revenue and acquisition cost, while prioritizing checkout improvements because checkout is the largest observed funnel drop-off.

![Overview dashboard](assets/screenshots/overview.png)

![A/B test results](assets/screenshots/test-results.png)

![Cohort retention heatmap](assets/screenshots/cohort-retention.png)

## Business question

Does showing a regular advertisement instead of a public-service announcement increase conversion enough to justify rollout?

## Key results

- PSA conversion rate: **1.79%**
- Ad conversion rate: **2.55%**
- Absolute conversion lift: **+0.77 percentage points**
- 95% confidence interval: **+0.60 to +0.94 percentage points**
- P-value: **< 0.001**
- Decision threshold: **+2 percentage points**
- Decision: statistically significant, but not practically significant under the defined rollout rule.

## Dashboard features

- A/B test results with conversion rates, confidence interval, and p-value
- Date- and acquisition-source-filtered funnel analysis
- Funnel drop-off identification
- Signup-cohort retention heatmap
- Acquisition-source retention exploration

## Method

The A/B experiment compares binary conversion outcomes between the `ad` treatment group and `psa` control group using a chi-square test of independence. The analysis reports conversion rates, the raw percentage-point difference, a 95% confidence interval, and a practical-significance threshold.

The funnel analysis counts unique sessions reaching page view, add to cart, checkout, and purchase stages. Cohort retention measures whether a customer generated at least one event in each week after signup.

## Data scope and limitations

This project uses two separate public datasets:

1. [Marketing A/B Testing](https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing) for the ad-versus-PSA conversion experiment.
2. A synthetic e-commerce clickstream dataset for the funnel and cohort-retention views.

The A/B dataset contains no timestamps, signup history, traffic-source information, revenue, or retention events. Therefore, its experiment findings are not merged with the clickstream retention and funnel findings. The clickstream data is synthetic and is used only to demonstrate the analytical workflow and interactive dashboard design.

## Tech stack

Python, pandas, SciPy, Plotly, and Streamlit.