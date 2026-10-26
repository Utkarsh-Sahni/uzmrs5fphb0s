# Domain Notes: Elexon Temporal Resolutions

## Data Source Differences

The WindSight application utilizes two primary datasets from the Elexon BMRS API: `FUELHH` (Actuals) and `WINDFOR` (Forecasts). These datasets have different temporal resolutions and publication characteristics, which requires specific processing logic to ensure accuracy evaluations are valid.

### FUELHH (Actual Generation)
- **Resolution**: Half-hourly (HH).
- **Frequency**: Reported every 30 minutes.
- **Aggregation**: For the purposes of hourly accuracy evaluation, half-hourly actuals are aggregated into hourly averages.
- **Validity Rule**: An hour is considered "complete" only if both half-hourly observations for that hour are present. If one is missing, the hour is marked as incomplete and excluded from the accuracy sample to avoid biasing the results.

### WINDFOR (Wind Forecasts)
- **Resolution**: Hourly.
- **Content**: Each publication contains forecasts for 73 hourly points (covering a 72-hour window inclusively).
- **Publication Logic**: Multiple forecast versions are published for the same target timestamp as the forecast is updated over time.
- **Temporal Filtering**:
    - **As-Of Selection**: For any given decision cutoff, only the latest forecast version published *before* the cutoff is used.
    - **Retrospective Filter**: Forecast targets where the start time is earlier than the publication time are excluded from forward-looking evaluation, as these are historical corrections rather than predictive forecasts.

## Alignment Logic
Actuals and Forecasts are aligned by the exact hourly target timestamp in UTC. No interpolation is performed on hourly forecasts to create half-hourly values, as this would introduce artificial precision.

## Metrics Calculation
Accuracy is calculated using matched hourly pairs. Missing data coverage is reported as the percentage of expected 24 hourly intervals for which both a valid aggregated actual and a valid "As-Of" forecast were available.
