CREATE TABLE IF NOT EXISTS fact_payments (
    id              INTEGER PRIMARY KEY,
    date            DATE NOT NULL,
    amount          NUMERIC(12,2) NOT NULL,
    load_timestamp  TIMESTAMP WITH TIME ZONE NOT NULL
);

