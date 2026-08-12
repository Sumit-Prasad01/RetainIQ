-- ============================================================
-- LOCATION TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS location (
    LocationId INTEGER PRIMARY KEY,
    Geography VARCHAR(15)
);


-- ============================================================
-- DEMOGRAPHIC TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS demographic (
    CustomerId INTEGER PRIMARY KEY,
    Gender VARCHAR(10),
    Age INTEGER,
    Salary DECIMAL(10, 2),
    LocationId INTEGER,
    Churned BOOLEAN,

    CONSTRAINT fk_demographic_location
        FOREIGN KEY (LocationId)
        REFERENCES location(LocationId)
);


-- ============================================================
-- ACCOUNT TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS account (
    CustomerId INTEGER PRIMARY KEY,
    Tenure INTEGER,
    Balance DECIMAL(10, 2),
    NumProducts INTEGER,
    HasCreditCard BOOLEAN,
    IsActive BOOLEAN,

    CONSTRAINT fk_account_customer
        FOREIGN KEY (CustomerId)
        REFERENCES demographic(CustomerId)
);