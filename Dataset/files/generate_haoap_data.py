import csv
import random
import uuid
from datetime import datetime, timedelta

random.seed(42)

# ── helpers ──────────────────────────────────────────────────────────────────
def rand_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def fmt(d): return d.strftime("%Y-%m-%d")

START = datetime(2022, 1, 1)
END   = datetime(2024, 12, 31)

# ── Dim_Beneficiary ───────────────────────────────────────────────────────────
NATIONALITIES = ["South Sudanese","Somali","Congolese","Sudanese","Ethiopian",
                 "Yemeni","Afghan","Syrian","Rohingya","Nigerian"]
PROGRAMS      = ["Food Security","Health","Shelter","WASH","Education",
                 "Cash Assistance","Protection","Livelihoods"]
VULNERABILITY = ["Refugee","IDP","Host Community","Returnee","Stateless"]
GENDERS       = ["Male","Female"]
STATUS        = ["Active","Inactive","Transferred","Deceased"]

rows = []
for i in range(1, 5001):
    dob  = rand_date(datetime(1950,1,1), datetime(2020,1,1))
    reg  = rand_date(START, END)
    rows.append({
        "beneficiary_sk": i,
        "beneficiary_id": f"BEN-{str(i).zfill(5)}",
        "household_id":   f"HH-{str(random.randint(1,2000)).zfill(4)}",
        "first_name":     random.choice(["Amina","Fatima","Omar","Ali","Yusuf","Halima","Ibrahim","Mariam","Hassan","Zainab"]),
        "last_name":      random.choice(["Diallo","Osman","Mohamed","Ahmed","Warsame","Ndlovu","Kofi","Barre","Jama","Musa"]),
        "gender":         random.choice(GENDERS),
        "date_of_birth":  fmt(dob),
        "age":            (datetime(2024,12,31) - dob).days // 365,
        "nationality":    random.choice(NATIONALITIES),
        "vulnerability_status": random.choice(VULNERABILITY),
        "household_size": random.randint(1, 12),
        "program_enrolled": random.choice(PROGRAMS),
        "registration_date": fmt(reg),
        "scd_start_date": fmt(reg),
        "scd_end_date":   "9999-12-31",
        "is_current":     1,
        "record_status":  random.choices(STATUS, weights=[70,15,10,5])[0],
        "biometric_verified": random.choice([1,0,0]),
        "protection_flag": random.choice([0,0,0,1]),
        "notes":          ""
    })

with open("/home/claude/Dim_Beneficiary.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(f"Dim_Beneficiary: {len(rows)} rows")

# ── Dim_Location ──────────────────────────────────────────────────────────────
locations = [
    ("LOC-001","Dadaab","Garissa","Kenya","East Africa","Camp",-0.09,40.31,3.2),
    ("LOC-002","Kakuma","Turkana","Kenya","East Africa","Camp",3.72,34.85,2.1),
    ("LOC-003","Baidoa","Bay","Somalia","East Africa","Urban",3.11,43.65,0.4),
    ("LOC-004","Mogadishu","Banadir","Somalia","East Africa","Urban",2.05,45.34,0.2),
    ("LOC-005","Bentiu","Unity","South Sudan","East Africa","Camp",9.23,29.84,1.8),
    ("LOC-006","Malakal","Upper Nile","South Sudan","East Africa","Camp",9.53,31.66,1.3),
    ("LOC-007","Kassala","Kassala","Sudan","East Africa","Urban",15.45,36.40,0.6),
    ("LOC-008","Khartoum","Khartoum","Sudan","East Africa","Urban",15.55,32.53,0.3),
    ("LOC-009","Aden","Aden","Yemen","Middle East","Urban",12.77,45.04,0.5),
    ("LOC-010","Marib","Marib","Yemen","Middle East","Camp",15.47,45.32,0.9),
    ("LOC-011","Goma","North Kivu","DRC","Central Africa","Urban",-1.67,29.22,0.7),
    ("LOC-012","Bunia","Ituri","DRC","Central Africa","Camp",1.56,30.25,0.8),
    ("LOC-013","Maiduguri","Borno","Nigeria","West Africa","Urban",11.84,13.16,0.4),
    ("LOC-014","Cox's Bazar","Chittagong","Bangladesh","South Asia","Camp",21.43,91.99,4.1),
    ("LOC-015","Kabul","Kabul","Afghanistan","South Asia","Urban",34.53,69.17,0.3),
]
loc_fields = ["location_sk","location_id","camp_name","district","country","region",
              "location_type","latitude","longitude","population_density_million",
              "has_health_facility","has_school","water_access_pct","electricity_pct","road_condition"]
loc_rows = []
for idx,(lid,camp,dist,country,region,ltype,lat,lon,pop) in enumerate(locations,1):
    loc_rows.append({
        "location_sk": idx,
        "location_id": lid,
        "camp_name":   camp,
        "district":    dist,
        "country":     country,
        "region":      region,
        "location_type": ltype,
        "latitude":    lat,
        "longitude":   lon,
        "population_density_million": pop,
        "has_health_facility": random.choice([1,1,0]),
        "has_school":          random.choice([1,1,0]),
        "water_access_pct":    round(random.uniform(40,95),1),
        "electricity_pct":     round(random.uniform(20,80),1),
        "road_condition":      random.choice(["Good","Fair","Poor"])
    })
with open("/home/claude/Dim_Location.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=loc_fields); w.writeheader(); w.writerows(loc_rows)
print(f"Dim_Location: {len(loc_rows)} rows")

# ── Dim_Time ──────────────────────────────────────────────────────────────────
time_rows = []
cur = START; sk = 1
while cur <= END:
    q = (cur.month-1)//3+1
    time_rows.append({
        "time_sk":     sk,
        "full_date":   fmt(cur),
        "day":         cur.day,
        "month":       cur.month,
        "month_name":  cur.strftime("%B"),
        "quarter":     q,
        "quarter_name":f"Q{q}",
        "year":        cur.year,
        "fiscal_year": cur.year if cur.month >= 7 else cur.year-1,
        "week_number": cur.isocalendar()[1],
        "day_of_week": cur.strftime("%A"),
        "is_weekend":  1 if cur.weekday()>=5 else 0,
        "is_month_end":1 if (cur+timedelta(days=1)).month != cur.month else 0
    })
    cur += timedelta(days=1); sk += 1
with open("/home/claude/Dim_Time.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=time_rows[0].keys()); w.writeheader(); w.writerows(time_rows)
print(f"Dim_Time: {len(time_rows)} rows")

# ── Dim_Program ───────────────────────────────────────────────────────────────
programs = [
    ("PRG-001","Food Security","Nutrition","Reduce acute malnutrition","WFP","Active","Annual"),
    ("PRG-002","Primary Healthcare","Health","Improve health outcomes","WHO","Active","Bi-annual"),
    ("PRG-003","Emergency Shelter","Shelter","Provide safe shelter","UNHCR","Active","One-time"),
    ("PRG-004","WASH","Infrastructure","Clean water & sanitation","UNICEF","Active","Annual"),
    ("PRG-005","Child Education","Education","Increase school enrolment","UNICEF","Active","Annual"),
    ("PRG-006","Cash Assistance","Livelihoods","Support purchasing power","WFP","Active","Monthly"),
    ("PRG-007","GBV Prevention","Protection","Reduce gender-based violence","UNFPA","Active","Annual"),
    ("PRG-008","Livelihoods","Economic","Income generation","ILO","Active","Bi-annual"),
    ("PRG-009","Mental Health","Health","Psychosocial support","WHO","Inactive","Annual"),
    ("PRG-010","Winterization","Shelter","Cold weather supplies","UNHCR","Active","Seasonal"),
]
prog_fields = ["program_sk","program_id","program_name","sector","objective",
               "implementing_partner","status","reporting_cycle","budget_usd","target_beneficiaries"]
prog_rows = []
for idx,(pid,name,sector,obj,partner,status,cycle) in enumerate(programs,1):
    prog_rows.append({
        "program_sk": idx, "program_id": pid, "program_name": name,
        "sector": sector, "objective": obj, "implementing_partner": partner,
        "status": status, "reporting_cycle": cycle,
        "budget_usd": round(random.uniform(500000,8000000),2),
        "target_beneficiaries": random.randint(5000,50000)
    })
with open("/home/claude/Dim_Program.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=prog_fields); w.writeheader(); w.writerows(prog_rows)
print(f"Dim_Program: {len(prog_rows)} rows")

# ── Dim_Donor ─────────────────────────────────────────────────────────────────
donors = [
    ("DNR-001","USAID","United States","Government","Bilateral",5000000,50000000,"Unrestricted"),
    ("DNR-002","ECHO","European Union","Government","Multilateral",3000000,30000000,"Restricted"),
    ("DNR-003","DFID","United Kingdom","Government","Bilateral",2000000,20000000,"Restricted"),
    ("DNR-004","SIDA","Sweden","Government","Bilateral",1000000,10000000,"Unrestricted"),
    ("DNR-005","Bill & Melinda Gates Foundation","United States","Foundation","Private",500000,15000000,"Restricted"),
    ("DNR-006","OCHA","United Nations","UN Agency","Multilateral",2500000,25000000,"Pooled"),
    ("DNR-007","BPRM","United States","Government","Bilateral",1500000,12000000,"Restricted"),
    ("DNR-008","GIZ","Germany","Government","Bilateral",800000,8000000,"Unrestricted"),
    ("DNR-009","Islamic Development Bank","Saudi Arabia","Development Bank","Multilateral",600000,6000000,"Restricted"),
    ("DNR-010","Private Donors","Various","Individual","Private",50000,500000,"Unrestricted"),
]
don_fields = ["donor_sk","donor_id","donor_name","donor_country","donor_type",
              "donor_category","min_grant_usd","max_grant_usd","funding_type",
              "reporting_requirement","relationship_since"]
don_rows = []
for idx,(did,name,country,dtype,cat,mn,mx,ftype) in enumerate(donors,1):
    don_rows.append({
        "donor_sk": idx, "donor_id": did, "donor_name": name,
        "donor_country": country, "donor_type": dtype, "donor_category": cat,
        "min_grant_usd": mn, "max_grant_usd": mx, "funding_type": ftype,
        "reporting_requirement": random.choice(["Monthly","Quarterly","Annual"]),
        "relationship_since": random.randint(2010,2020)
    })
with open("/home/claude/Dim_Donor.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=don_fields); w.writeheader(); w.writerows(don_rows)
print(f"Dim_Donor: {len(don_rows)} rows")

# ── Fact_AidDistribution ──────────────────────────────────────────────────────
AID_TYPES  = ["Food Ration","Cash Transfer","NFI Kit","Medical Supplies",
               "Shelter Kit","WASH Kit","Education Kit","Winterization Kit"]
UNIT_COSTS = {"Food Ration":45,"Cash Transfer":100,"NFI Kit":85,"Medical Supplies":120,
               "Shelter Kit":250,"WASH Kit":60,"Education Kit":35,"Winterization Kit":75}
DELIVERY   = ["Completed","Delayed","Partial","Failed","In Transit"]

aid_rows = []
for i in range(1, 10001):
    dist_date = rand_date(START, END)
    loc_sk    = random.randint(1, 15)
    prog_sk   = random.randint(1, 10)
    ben_sk    = random.randint(1, 5000)
    aid_type  = random.choice(AID_TYPES)
    qty       = random.randint(1, 50)
    unit_cost = UNIT_COSTS[aid_type]
    status    = random.choices(DELIVERY, weights=[60,15,12,5,8])[0]
    planned   = dist_date
    actual    = planned + timedelta(days=random.randint(0,10) if status != "Delayed" else random.randint(4,20))
    delay     = max(0, (actual - planned).days)
    aid_rows.append({
        "distribution_sk":      i,
        "distribution_id":      f"DIST-{str(i).zfill(6)}",
        "beneficiary_sk":       ben_sk,
        "location_sk":          loc_sk,
        "program_sk":           prog_sk,
        "time_sk":              (dist_date - START).days + 1,
        "aid_type":             aid_type,
        "quantity_distributed": qty,
        "unit_cost_usd":        unit_cost,
        "total_cost_usd":       round(qty * unit_cost, 2),
        "planned_date":         fmt(planned),
        "actual_date":          fmt(actual),
        "delay_days":           delay,
        "delivery_status":      status,
        "transport_mode":       random.choice(["Truck","Air","Boat","Handcarry"]),
        "distribution_point":   f"DP-{random.randint(1,50):02d}",
        "staff_id":             f"STF-{random.randint(1,200):03d}",
        "verification_method":  random.choice(["Biometric","Voucher","List-based","Token"]),
        "beneficiary_confirmed":random.choice([1,1,1,0]),
        "data_quality_flag":    random.choices([0,0,0,1], weights=[90,0,0,10])[0],
        "notes":                ""
    })
with open("/home/claude/Fact_AidDistribution.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=aid_rows[0].keys()); w.writeheader(); w.writerows(aid_rows)
print(f"Fact_AidDistribution: {len(aid_rows)} rows")

# ── Fact_Funding ──────────────────────────────────────────────────────────────
fund_rows = []
for i in range(1, 1001):
    pledge_date  = rand_date(START, END)
    donor_sk     = random.randint(1, 10)
    prog_sk      = random.randint(1, 10)
    pledged      = round(random.uniform(10000, 2000000), 2)
    received_pct = random.uniform(0.3, 1.0)
    received     = round(pledged * received_pct, 2)
    utilised     = round(received * random.uniform(0.5, 1.0), 2)
    fund_rows.append({
        "funding_sk":         i,
        "funding_id":         f"FND-{str(i).zfill(5)}",
        "donor_sk":           donor_sk,
        "program_sk":         prog_sk,
        "location_sk":        random.randint(1,15),
        "time_sk":            (pledge_date - START).days + 1,
        "pledged_amount_usd": pledged,
        "received_amount_usd":received,
        "utilised_amount_usd":utilised,
        "balance_usd":        round(received - utilised, 2),
        "utilisation_rate_pct":round((utilised/received)*100,1) if received>0 else 0,
        "funding_type":       random.choice(["Grant","Loan","In-Kind","Pooled"]),
        "grant_code":         f"GRT-{random.randint(10000,99999)}",
        "reporting_deadline": fmt(pledge_date + timedelta(days=random.randint(90,365))),
        "compliance_status":  random.choices(["Compliant","At Risk","Non-Compliant"],[80,15,5])[0],
        "budget_code":        f"BC-{random.randint(100,999)}",
        "fiscal_year":        pledge_date.year if pledge_date.month >= 7 else pledge_date.year - 1,
        "currency":           "USD",
        "exchange_rate":      1.0
    })
with open("/home/claude/Fact_Funding.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=fund_rows[0].keys()); w.writeheader(); w.writerows(fund_rows)
print(f"Fact_Funding: {len(fund_rows)} rows")

# ── Fact_HealthServices ───────────────────────────────────────────────────────
CONDITIONS = ["Acute Malnutrition","Malaria","Diarrhoea","Respiratory Infection",
              "Trauma/Injury","Obstetric Emergency","Cholera","Skin Disease",
              "Anaemia","Psychosocial Disorder","Hypertension","Diabetes"]
OUTCOMES   = ["Recovered","Referred","Ongoing Treatment","Deceased","LAMA"]

health_rows = []
for i in range(1, 8001):
    visit_date = rand_date(START, END)
    condition  = random.choice(CONDITIONS)
    sev        = random.choices(["Mild","Moderate","Severe"],[50,35,15])[0]
    outcome    = random.choices(OUTCOMES,[65,15,12,3,5])[0]
    cost       = round(random.uniform(5, 300), 2)
    health_rows.append({
        "health_sk":            i,
        "health_id":            f"HLT-{str(i).zfill(6)}",
        "beneficiary_sk":       random.randint(1,5000),
        "location_sk":          random.randint(1,15),
        "program_sk":           random.choice([2,9]),
        "time_sk":              (visit_date - START).days + 1,
        "visit_type":           random.choice(["Outpatient","Inpatient","Emergency","Immunisation","ANC","PNC"]),
        "condition_diagnosed":  condition,
        "severity":             sev,
        "treatment_provided":   random.choice(["Medication","Surgery","Counselling","Referral","Nutrition Support"]),
        "outcome":              outcome,
        "days_in_treatment":    random.randint(1,30) if outcome not in ["Recovered"] else random.randint(1,7),
        "cost_per_patient_usd": cost,
        "staff_id":             f"MED-{random.randint(1,80):03d}",
        "facility_type":        random.choice(["Health Post","PHC","Hospital","Mobile Clinic"]),
        "referred_out":         1 if outcome == "Referred" else 0,
        "muac_cm":              round(random.uniform(9.5, 16.0),1) if "Malnutrition" in condition else None,
        "malnutrition_flag":    1 if "Malnutrition" in condition else 0,
        "vaccination_given":    random.choice([0,0,1]),
        "data_quality_flag":    random.choices([0,1],[95,5])[0]
    })
with open("/home/claude/Fact_HealthServices.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=health_rows[0].keys()); w.writeheader(); w.writerows(health_rows)
print(f"Fact_HealthServices: {len(health_rows)} rows")

# ── Data Quality issues file ───────────────────────────────────────────────────
# Inject intentional quality issues into a separate raw file for DQ demo
import copy, math

raw_rows = []
for r in random.sample(aid_rows, 500):
    bad = dict(r)
    issue = random.choice(["missing_ben","negative_qty","future_date","duplicate","null_status"])
    if issue == "missing_ben":      bad["beneficiary_sk"] = ""
    elif issue == "negative_qty":   bad["quantity_distributed"] = -abs(bad["quantity_distributed"])
    elif issue == "future_date":    bad["actual_date"] = "2027-01-15"
    elif issue == "duplicate":      bad["distribution_id"] = aid_rows[0]["distribution_id"]
    elif issue == "null_status":    bad["delivery_status"] = ""
    bad["injected_issue"] = issue
    raw_rows.append(bad)

raw_rows[0].setdefault("injected_issue","")
for r in aid_rows[:200]:
    clean = dict(r); clean["injected_issue"] = "none"; raw_rows.append(clean)

with open("/home/claude/Raw_AidDistribution_WithErrors.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(raw_rows[0].keys())); w.writeheader(); w.writerows(raw_rows)
print(f"Raw_AidDistribution_WithErrors: {len(raw_rows)} rows")

print("\n✅ All 8 data files generated successfully!")
