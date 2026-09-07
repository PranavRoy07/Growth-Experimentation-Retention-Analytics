# Cleaning audit

## Source
- Raw file: `marketing_AB.csv`
- Original rows: 588,101

## Audit results
- Missing values: {'Unnamed: 0': 0, 'user id': 0, 'test group': 0, 'converted': 0, 'total ads': 0, 'most ads day': 0, 'most ads hour': 0}
- Duplicate rows: 0
- Duplicate user IDs: 0
- Invalid test groups: 0
- Invalid weekday values: 0
- Invalid hour values: 0
- Negative ad-count values: 0

## Cleaning actions
1. Renamed columns to lowercase snake_case.
2. Dropped `unnamed:_0`, an exported row-index column with no analytical meaning.
3. Retained all 588,101 user records because no duplicate, missing, or invalid records were found.
4. Did not create cohort or retention fields because this source contains no signup or event timestamp.
