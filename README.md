🌍 Humanitarian Aid Operations Analytics Platform (HAOAP)
📌 Project Overview

The Humanitarian Aid Operations Analytics Platform (HAOAP) is an end-to-end data analytics and reporting solution designed to simulate real-world humanitarian operations. The project demonstrates how data engineering, analytics, and the Microsoft Power Platform can be used to support decision-making in crisis response environments.

This solution replicates the type of analytics ecosystem used by organizations such as the International Rescue Committee (IRC) to track aid distribution, monitor program impact, and optimize operational efficiency.

🎯 Objectives
Build analytics-ready datasets using SQL and Python
Design a scalable data warehouse using star schema modeling
Develop interactive dashboards in Power BI
Enable automation and applications using Power Apps and Power Automate
Implement data quality monitoring and governance frameworks
🏗️ Architecture
Raw Data (CSV / API Simulation)
        ↓
Python Data Processing (Cleaning & Validation)
        ↓
SQL Server Data Warehouse (Star Schema)
        ↓
Power BI Dataset (Semantic Model)
        ↓
Power BI Dashboards + Power Apps + Power Automate
🧱 Data Model
⭐ Fact Tables
Fact_AidDistribution
Fact_Funding
Fact_HealthServices
📊 Dimension Tables
Dim_Beneficiary
Dim_Location
Dim_Time
Dim_Program
Dim_Donor
Key Features
Star schema design
Surrogate keys
Slowly Changing Dimensions (SCD)
Optimized relationships for reporting
📊 Power BI Dashboards
1. Executive Overview
Total beneficiaries reached
Total aid distributed
Funding vs utilization
KPI tracking and trends
2. Operations Efficiency
Delivery timelines
Cost per beneficiary
Regional performance
Bottleneck identification
3. Impact Analysis
Health service outcomes
Food security metrics
Program success rates
4. Data Quality Monitoring 🚨
Missing values tracking
Duplicate detection
Data freshness indicators
⚙️ Power Platform Integration
📱 Power Apps
Field data collection app
Mobile-friendly forms for aid distribution reporting
🔄 Power Automate
Alerts for delayed aid delivery
Notifications for budget overruns
Automated workflow triggers
🐍 Python (Data Engineering)

Used for:

Data cleaning and preprocessing
Data validation and anomaly detection
Synthetic dataset generation

Example tasks:

Removing duplicates
Validating beneficiary IDs
Creating anomaly flags
🧮 SQL (Advanced Analytics)

Key techniques demonstrated:

Common Table Expressions (CTEs)
Window functions
Aggregations and ranking

Example:

SELECT 
    location,
    SUM(aid_amount) AS total_aid,
    RANK() OVER (ORDER BY SUM(aid_amount) DESC) AS aid_rank
FROM Fact_AidDistribution
GROUP BY location;
🛡️ Data Governance & Security
Row-Level Security (RLS) in Power BI
Role-based access control
Secure dataset design
🔍 Data Quality Framework
SQL-based validation tests
Python data checks
Data quality dashboard
📁 Project Structure
/data
    raw/
    processed/

/scripts
    python/
    sql/

/powerbi
    dashboards.pbix

/docs
    architecture_diagram.png
    data_model_erd.png
💼 Business Case
Problem

Humanitarian organizations often face:

Fragmented data systems
Delayed reporting
Limited visibility into operations and impact
Solution

This platform provides:

Centralized analytics datasets
Real-time dashboards
Automated alerts and workflows
Impact
Improved decision-making
Faster aid delivery
Enhanced accountability to donors
Better outcomes for beneficiaries
🚀 Tools & Technologies
Python (Pandas, NumPy)
SQL Server / Azure SQL
Power BI
Power Apps
Power Automate
Git & GitHub
📌 Key Highlights

✔ End-to-end data pipeline
✔ Enterprise-grade data modeling
✔ Advanced Power BI dashboards
✔ Power Platform integration
✔ Data quality and governance framework

📽️ Demo (Optional)

Add your demo video here:
👉 [Project Demo Link]

🤝 Author

John Kipkemboi Kimaiyo
📧 kimaiyojohn6@gmail.com
🌐 Portfolio: https://johnkimaiyo-rosy.vercel.app/

⭐ How to Use
Clone the repository
Run Python scripts to generate data
Load data into SQL Server
Connect Power BI to the database
Explore dashboards and insights
📢 Final Note

This project is designed to showcase analytics engineering, data modeling, and Power Platform integration skills in a humanitarian context, aligning with modern data roles in global organizations.
