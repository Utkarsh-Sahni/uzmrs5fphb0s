CREATE TABLE IF NOT EXISTS fuel_hh (
    settlement_date DATE,
    settlement_period INTEGER,
    fuel_type TEXT,
    value_mw REAL,
    publish_date_time DATETIME,
    PRIMARY KEY (settlement_date, settlement_period, fuel_type)
);

CREATE TABLE IF NOT EXISTS wind_for (
    forecast_publish_date_time DATETIME,
    target_date DATE,
    target_period INTEGER,
    forecast_value_mw REAL,
    PRIMARY KEY (forecast_publish_date_time, target_date, target_period)
);

CREATE INDEX IF NOT EXISTS idx_wind_for_target ON wind_for(target_date, target_period);
CREATE INDEX IF NOT EXISTS idx_wind_for_publish ON wind_for(forecast_publish_date_time);
