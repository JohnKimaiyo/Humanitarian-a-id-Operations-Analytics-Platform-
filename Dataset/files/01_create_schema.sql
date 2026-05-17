-- ============================================================
-- HAOAP - Data Warehouse Schema (SQL Server / Azure SQL)
-- Star Schema with Surrogate Keys & SCD Type 2
-- ============================================================

USE HAOAP_DW;
GO

-- ────────────────────────────────────────────────────────────
-- DIMENSION TABLES
-- ────────────────────────────────────────────────────────────

CREATE TABLE Dim_Time (
    time_sk         INT           NOT NULL PRIMARY KEY,
    full_date       DATE          NOT NULL,
    [day]           TINYINT       NOT NULL,
    [month]         TINYINT       NOT NULL,
    month_name      VARCHAR(10)   NOT NULL,
    quarter         TINYINT       NOT NULL,
    quarter_name    CHAR(2)       NOT NULL,
    [year]          SMALLINT      NOT NULL,
    fiscal_year     SMALLINT      NOT NULL,
    week_number     TINYINT       NOT NULL,
    day_of_week     VARCHAR(10)   NOT NULL,
    is_weekend      BIT           NOT NULL DEFAULT 0,
    is_month_end    BIT           NOT NULL DEFAULT 0
);

CREATE TABLE Dim_Location (
    location_sk               INT          NOT NULL PRIMARY KEY,
    location_id               VARCHAR(10)  NOT NULL UNIQUE,
    camp_name                 VARCHAR(100) NOT NULL,
    district                  VARCHAR(100),
    country                   VARCHAR(100) NOT NULL,
    region                    VARCHAR(100),
    location_type             VARCHAR(50),
    latitude                  DECIMAL(9,6),
    longitude                 DECIMAL(9,6),
    population_density_million DECIMAL(5,2),
    has_health_facility       BIT,
    has_school                BIT,
    water_access_pct          DECIMAL(5,2),
    electricity_pct           DECIMAL(5,2),
    road_condition            VARCHAR(20)
);

-- SCD Type 2 Beneficiary dimension
CREATE TABLE Dim_Beneficiary (
    beneficiary_sk      INT           NOT NULL PRIMARY KEY IDENTITY(1,1),
    beneficiary_id      VARCHAR(20)   NOT NULL,
    household_id        VARCHAR(20),
    first_name          VARCHAR(100),
    last_name           VARCHAR(100),
    gender              VARCHAR(10),
    date_of_birth       DATE,
    age                 TINYINT,
    nationality         VARCHAR(100),
    vulnerability_status VARCHAR(50),
    household_size      TINYINT,
    program_enrolled    VARCHAR(100),
    registration_date   DATE,
    -- SCD2 columns
    scd_start_date      DATE          NOT NULL,
    scd_end_date        DATE          NOT NULL DEFAULT '9999-12-31',
    is_current          BIT           NOT NULL DEFAULT 1,
    record_status       VARCHAR(20),
    biometric_verified  BIT           DEFAULT 0,
    protection_flag     BIT           DEFAULT 0,
    notes               NVARCHAR(500)
);
CREATE INDEX IX_Dim_Beneficiary_id   ON Dim_Beneficiary (beneficiary_id);
CREATE INDEX IX_Dim_Beneficiary_curr ON Dim_Beneficiary (beneficiary_id, is_current);

CREATE TABLE Dim_Program (
    program_sk             INT          NOT NULL PRIMARY KEY,
    program_id             VARCHAR(10)  NOT NULL UNIQUE,
    program_name           VARCHAR(100) NOT NULL,
    sector                 VARCHAR(100),
    objective              NVARCHAR(500),
    implementing_partner   VARCHAR(100),
    [status]               VARCHAR(20),
    reporting_cycle        VARCHAR(20),
    budget_usd             DECIMAL(18,2),
    target_beneficiaries   INT
);

CREATE TABLE Dim_Donor (
    donor_sk               INT          NOT NULL PRIMARY KEY,
    donor_id               VARCHAR(10)  NOT NULL UNIQUE,
    donor_name             VARCHAR(200) NOT NULL,
    donor_country          VARCHAR(100),
    donor_type             VARCHAR(50),
    donor_category         VARCHAR(50),
    min_grant_usd          DECIMAL(18,2),
    max_grant_usd          DECIMAL(18,2),
    funding_type           VARCHAR(50),
    reporting_requirement  VARCHAR(20),
    relationship_since     SMALLINT
);

-- ────────────────────────────────────────────────────────────
-- FACT TABLES
-- ────────────────────────────────────────────────────────────

CREATE TABLE Fact_AidDistribution (
    distribution_sk         BIGINT        NOT NULL PRIMARY KEY IDENTITY(1,1),
    distribution_id         VARCHAR(20)   NOT NULL UNIQUE,
    beneficiary_sk          INT           NOT NULL REFERENCES Dim_Beneficiary(beneficiary_sk),
    location_sk             INT           NOT NULL REFERENCES Dim_Location(location_sk),
    program_sk              INT           NOT NULL REFERENCES Dim_Program(program_sk),
    time_sk                 INT           NOT NULL REFERENCES Dim_Time(time_sk),
    aid_type                VARCHAR(100),
    quantity_distributed    INT,
    unit_cost_usd           DECIMAL(10,2),
    total_cost_usd          DECIMAL(18,2),
    planned_date            DATE,
    actual_date             DATE,
    delay_days              SMALLINT,
    delivery_status         VARCHAR(50),
    transport_mode          VARCHAR(50),
    distribution_point      VARCHAR(20),
    staff_id                VARCHAR(20),
    verification_method     VARCHAR(50),
    beneficiary_confirmed   BIT,
    data_quality_flag       BIT           DEFAULT 0,
    notes                   NVARCHAR(500),
    inserted_at             DATETIME2     DEFAULT GETDATE()
);
CREATE INDEX IX_Fact_AidDist_Loc  ON Fact_AidDistribution (location_sk);
CREATE INDEX IX_Fact_AidDist_Time ON Fact_AidDistribution (time_sk);
CREATE INDEX IX_Fact_AidDist_Prog ON Fact_AidDistribution (program_sk);

CREATE TABLE Fact_Funding (
    funding_sk              BIGINT        NOT NULL PRIMARY KEY IDENTITY(1,1),
    funding_id              VARCHAR(20)   NOT NULL UNIQUE,
    donor_sk                INT           NOT NULL REFERENCES Dim_Donor(donor_sk),
    program_sk              INT           NOT NULL REFERENCES Dim_Program(program_sk),
    location_sk             INT           NOT NULL REFERENCES Dim_Location(location_sk),
    time_sk                 INT           NOT NULL REFERENCES Dim_Time(time_sk),
    pledged_amount_usd      DECIMAL(18,2),
    received_amount_usd     DECIMAL(18,2),
    utilised_amount_usd     DECIMAL(18,2),
    balance_usd             DECIMAL(18,2),
    utilisation_rate_pct    DECIMAL(5,2),
    funding_type            VARCHAR(50),
    grant_code              VARCHAR(20),
    reporting_deadline      DATE,
    compliance_status       VARCHAR(30),
    budget_code             VARCHAR(20),
    fiscal_year             SMALLINT,
    currency                CHAR(3)       DEFAULT 'USD',
    exchange_rate           DECIMAL(10,4) DEFAULT 1.0,
    inserted_at             DATETIME2     DEFAULT GETDATE()
);

CREATE TABLE Fact_HealthServices (
    health_sk               BIGINT        NOT NULL PRIMARY KEY IDENTITY(1,1),
    health_id               VARCHAR(20)   NOT NULL UNIQUE,
    beneficiary_sk          INT           NOT NULL REFERENCES Dim_Beneficiary(beneficiary_sk),
    location_sk             INT           NOT NULL REFERENCES Dim_Location(location_sk),
    program_sk              INT           NOT NULL REFERENCES Dim_Program(program_sk),
    time_sk                 INT           NOT NULL REFERENCES Dim_Time(time_sk),
    visit_type              VARCHAR(50),
    condition_diagnosed     VARCHAR(100),
    severity                VARCHAR(20),
    treatment_provided      VARCHAR(100),
    outcome                 VARCHAR(50),
    days_in_treatment       SMALLINT,
    cost_per_patient_usd    DECIMAL(10,2),
    staff_id                VARCHAR(20),
    facility_type           VARCHAR(50),
    referred_out            BIT,
    muac_cm                 DECIMAL(4,1),
    malnutrition_flag       BIT,
    vaccination_given       BIT,
    data_quality_flag       BIT           DEFAULT 0,
    inserted_at             DATETIME2     DEFAULT GETDATE()
);
GO
