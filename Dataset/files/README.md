# 🌍 Humanitarian Aid Operations Analytics Platform (HAOAP)

> End-to-end analytics solution tracking aid distribution, beneficiary impact,
> and operational efficiency across 15 crisis regions (2022–2024).

---

## 📁 Repository Structure

```
haoap/
├── data/
│   ├── raw/
│   │   ├── Dim_Beneficiary.csv           # 5,000 beneficiary records
│   │   ├── Dim_Location.csv              # 15 crisis locations
│   │   ├── Dim_Time.csv                  # 1,096 date records (2022–2024)
│   │   ├── Dim_Program.csv               # 10 humanitarian programs
│   │   ├── Dim_Donor.csv                 # 10 donor organisations
│   │   ├── Fact_AidDistribution.csv      # 10,000 distribution events
│   │   ├── Fact_Funding.csv              # 1,000 funding transactions
│   │   ├── Fact_HealthServices.csv       # 8,000 health visit records
│   │   └── Raw_AidDistribution_WithErrors.csv  # DQ demo dataset
│   └── clean/
│       ├── Clean_AidDistribution.csv
│       ├── Clean_Beneficiary.csv
│       └── Clean_Funding.csv
├── sql/
│   ├── 01_create_schema.sql              # Full star schema DDL
│   └── 02_analytics_queries.sql          # CTEs, window functions, RLS
├── python/
│   ├── generate_haoap_data.py            # Synthetic data generator
│   └── python_pipeline.py                # Validation & cleaning pipeline
├── reports/
│   └── data_quality_report.json
└── README.md
```

---

## 🏗️ Architecture

```
[Simulated Sources]
  Beneficiary Registrations
  Aid Distribution Events
  Health Service Records
  Donor Funding Flows
        │
        ▼
[Python Pipeline]
  generate_haoap_data.py  → Synthetic data generation
  python_pipeline.py      → Validation, cleaning, quality flags
        │
        ▼
[SQL Server / Azure SQL]
  Star Schema (01_create_schema.sql)
  Analytics Queries (02_analytics_queries.sql)
  Row-Level Security
        │
        ▼
[Power BI]
  Page 1: Executive Overview
  Page 2: Operations Efficiency
  Page 3: Impact Analysis
  Page 4: Data Quality Monitor
```

---

## 📊 Data Model (Star Schema)

| Table | Type | Rows | Key Fields |
|-------|------|------|-----------|
| Dim_Beneficiary | Dimension (SCD2) | 5,000 | beneficiary_sk, scd_start/end |
| Dim_Location | Dimension | 15 | location_sk, country, coordinates |
| Dim_Time | Dimension | 1,096 | time_sk, fiscal_year, quarter |
| Dim_Program | Dimension | 10 | program_sk, sector, budget |
| Dim_Donor | Dimension | 10 | donor_sk, donor_type |
| Fact_AidDistribution | Fact | 10,000 | total_cost_usd, delay_days |
| Fact_Funding | Fact | 1,000 | pledged, received, utilised |
| Fact_HealthServices | Fact | 8,000 | outcome, cost_per_patient |

---

## 🐍 Python Pipeline Features

- **Data Generation**: Synthetic, realistic humanitarian data with correct distributions
- **Duplicate Detection**: Flags repeated distribution IDs
- **Null Checks**: Critical fields (beneficiary_sk, delivery_status, aid_type)
- **Range Validation**: Quantities, ages, household sizes, costs
- **Date Validation**: Future date anomalies, format checks
- **Domain Validation**: Aid types, delivery statuses against allowed values
- **Quality Scoring**: Per-table quality score (0–100%)
- **JSON Report**: Machine-readable quality report for Power BI integration

---

## 🔍 SQL Highlights

1. **Region Aid Ranking** — RANK() + PERCENT_RANK() window functions
2. **Monthly Trend with Running Total** — SUM() OVER with ROWS UNBOUNDED PRECEDING
3. **Cost Per Beneficiary** — DENSE_RANK() for efficiency ranking
4. **Delivery Delay Analysis** — PERCENTILE_CONT for median calculation
5. **Funding Utilisation** — Multi-donor aggregation with budget tracking
6. **Health Outcomes** — Recovery rates by condition and severity
7. **Data Quality Monitor** — UNION ALL across fact tables
8. **Row-Level Security** — Security predicate function restricting by country

---

## 📋 Data Quality Framework

The pipeline flags five categories of issues:

| Issue Type | Description |
|-----------|-------------|
| `duplicate_id` | Same record ID appears multiple times |
| `null_critical_field` | Required field is empty |
| `invalid_quantity` | Negative or non-numeric quantity |
| `future_date_anomaly` | Date set beyond 2026 |
| `invalid_status` | Value not in allowed set |

A `data_quality_report.json` is produced each run with per-table scores.

---

## 🔐 Security

- **Row-Level Security (RLS)**: Regional managers see only their country's data
- **Role Mapping**: Country name maps to SQL login for automatic filtering
- **GlobalAdmin** role bypasses filtering for HQ users

---

## 💼 Business Value

| Problem | Solution |
|---------|---------|
| Fragmented beneficiary data | Unified star schema with SCD2 history |
| Delayed reporting | Automated pipeline + Power BI refresh |
| Aid delivery delays | Delay analysis dashboard with alerts |
| Donor accountability | Utilisation tracking per grant |
| Data integrity | Automated DQ framework + quality score |

---

*Generated for HAOAP Portfolio Project — Data Analytics for Humanitarian Operations*
