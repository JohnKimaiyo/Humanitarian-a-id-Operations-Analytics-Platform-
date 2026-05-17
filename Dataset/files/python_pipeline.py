"""
HAOAP - Python Data Pipeline
Cleans, validates, and transforms raw humanitarian data
"""

import csv, re, logging, json
from datetime import datetime, date
from pathlib import Path
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/home/claude/pipeline.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("HAOAP-Pipeline")

# ─── CONFIG ──────────────────────────────────────────────────────────────────
DATA_DIR   = Path("/home/claude")
TODAY      = date.today()
MAX_FUTURE = date(2026, 12, 31)
VALID_STATUSES = {"Completed","Delayed","Partial","Failed","In Transit"}
VALID_AID_TYPES = {
    "Food Ration","Cash Transfer","NFI Kit","Medical Supplies",
    "Shelter Kit","WASH Kit","Education Kit","Winterization Kit"
}

# ─── VALIDATION REPORT ────────────────────────────────────────────────────────
class QualityReport:
    def __init__(self, table):
        self.table     = table
        self.total     = 0
        self.issues    = defaultdict(list)
        self.dupes     = 0
        self.nulls     = 0
        self.out_range = 0
        self.type_errs = 0

    def flag(self, row_id, issue_type, detail):
        self.issues[issue_type].append({"row": row_id, "detail": detail})

    def summary(self):
        all_issues = sum(len(v) for v in self.issues.values())
        quality_score = round(100 * (1 - all_issues / max(self.total, 1)), 2)
        return {
            "table":            self.table,
            "total_records":    self.total,
            "total_issues":     all_issues,
            "quality_score_pct":quality_score,
            "issue_breakdown":  {k: len(v) for k, v in self.issues.items()},
            "sample_issues":    {k: v[:3] for k, v in self.issues.items()}
        }

# ─── VALIDATORS ───────────────────────────────────────────────────────────────
def is_valid_date(s):
    try:
        d = datetime.strptime(s, "%Y-%m-%d").date()
        return True, d
    except Exception:
        return False, None

def clean_numeric(val, allow_negative=False):
    try:
        n = float(str(val).replace(",","").strip())
        if not allow_negative and n < 0:
            return None, "negative_value"
        return n, None
    except Exception:
        return None, "non_numeric"

def validate_beneficiary_id(bid):
    return bool(re.match(r"^BEN-\d{5}$", str(bid).strip()))

# ─── PIPELINE FUNCTIONS ───────────────────────────────────────────────────────
def validate_aid_distribution(path):
    log.info(f"▶ Validating {path.name}")
    report   = QualityReport("Fact_AidDistribution")
    clean    = []
    seen_ids = set()

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            report.total += 1
            rid = row.get("distribution_id","?")
            issues_this_row = []

            # Duplicate check
            if rid in seen_ids:
                report.flag(rid, "duplicate_id", f"ID {rid} appears more than once")
                report.dupes += 1
                issues_this_row.append("duplicate")
            seen_ids.add(rid)

            # Null / empty checks on critical fields
            for field in ["beneficiary_sk","location_sk","aid_type","delivery_status"]:
                if not str(row.get(field,"")).strip():
                    report.flag(rid, "null_critical_field", f"Field '{field}' is empty")
                    report.nulls += 1
                    issues_this_row.append(f"null_{field}")

            # Numeric range
            qty, err = clean_numeric(row.get("quantity_distributed",""), allow_negative=False)
            if err:
                report.flag(rid, "invalid_quantity", f"qty={row.get('quantity_distributed')}")
                issues_this_row.append("bad_qty")
            elif qty is not None and qty > 1000:
                report.flag(rid, "quantity_outlier", f"qty={qty} exceeds threshold 1000")
                issues_this_row.append("qty_outlier")

            cost, err2 = clean_numeric(row.get("total_cost_usd",""), allow_negative=False)
            if err2:
                report.flag(rid, "invalid_cost", f"cost={row.get('total_cost_usd')}")
                issues_this_row.append("bad_cost")

            # Date validation
            for df in ["planned_date","actual_date"]:
                ok, dt = is_valid_date(row.get(df,""))
                if not ok:
                    report.flag(rid, "invalid_date", f"{df}='{row.get(df)}'")
                    issues_this_row.append(f"bad_{df}")
                elif dt and dt > MAX_FUTURE:
                    report.flag(rid, "future_date_anomaly", f"{df}={dt} > {MAX_FUTURE}")
                    issues_this_row.append(f"future_{df}")

            # Domain check
            if row.get("aid_type") not in VALID_AID_TYPES:
                report.flag(rid, "invalid_aid_type", f"aid_type='{row.get('aid_type')}'")
                issues_this_row.append("bad_aid_type")

            if row.get("delivery_status") and row.get("delivery_status") not in VALID_STATUSES:
                report.flag(rid, "invalid_status", f"status='{row.get('delivery_status')}'")
                issues_this_row.append("bad_status")

            # Mark quality flag and append to clean output
            row["data_quality_flag"]   = 1 if issues_this_row else 0
            row["quality_issue_codes"] = "|".join(issues_this_row)
            row["processed_at"]        = str(datetime.now())
            clean.append(row)

    return report, clean


def validate_beneficiaries(path):
    log.info(f"▶ Validating {path.name}")
    report = QualityReport("Dim_Beneficiary")
    clean  = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            report.total += 1
            bid = row.get("beneficiary_id","?")
            issues = []

            if not validate_beneficiary_id(bid):
                report.flag(bid, "invalid_id_format", f"id='{bid}'")
                issues.append("bad_id_format")

            age_raw = row.get("age","")
            age, err = clean_numeric(age_raw)
            if err:
                report.flag(bid, "invalid_age", f"age='{age_raw}'")
                issues.append("bad_age")
            elif age is not None and (age < 0 or age > 110):
                report.flag(bid, "age_out_of_range", f"age={age}")
                issues.append("age_range")

            hh, err2 = clean_numeric(row.get("household_size",""))
            if err2 or (hh is not None and (hh < 1 or hh > 30)):
                report.flag(bid, "household_size_anomaly", f"hh_size={row.get('household_size')}")
                issues.append("hh_size_anomaly")

            ok, _ = is_valid_date(row.get("date_of_birth",""))
            if not ok:
                report.flag(bid, "invalid_dob", f"dob='{row.get('date_of_birth')}'")
                issues.append("bad_dob")

            row["validation_flag"]   = 1 if issues else 0
            row["validation_codes"]  = "|".join(issues)
            row["processed_at"]      = str(datetime.now())
            clean.append(row)

    return report, clean


def validate_funding(path):
    log.info(f"▶ Validating {path.name}")
    report = QualityReport("Fact_Funding")
    clean  = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            report.total += 1
            fid    = row.get("funding_id","?")
            issues = []

            pledged,  e1 = clean_numeric(row.get("pledged_amount_usd",""))
            received, e2 = clean_numeric(row.get("received_amount_usd",""))
            utilised, e3 = clean_numeric(row.get("utilised_amount_usd",""))

            if e1 or e2 or e3:
                report.flag(fid,"invalid_amounts",f"pledge={row.get('pledged_amount_usd')}")
                issues.append("bad_amounts")
            else:
                if received and pledged and received > pledged * 1.05:
                    report.flag(fid,"received_exceeds_pledge",f"rcvd={received}>pledged={pledged}")
                    issues.append("received_gt_pledged")
                if utilised and received and utilised > received * 1.02:
                    report.flag(fid,"utilised_exceeds_received",f"util={utilised}>rcvd={received}")
                    issues.append("utilised_gt_received")

            row["validation_flag"]  = 1 if issues else 0
            row["validation_codes"] = "|".join(issues)
            row["processed_at"]     = str(datetime.now())
            clean.append(row)

    return report, clean


def write_clean(rows, out_path):
    if not rows:
        return
    with open(out_path,"w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    log.info(f"  ✅ Wrote {len(rows):,} rows → {out_path.name}")


def write_quality_report(reports, out_path):
    combined = [r.summary() for r in reports]
    with open(out_path,"w") as f:
        json.dump(combined, f, indent=2, default=str)
    log.info(f"  📋 Quality report → {out_path.name}")
    for r in combined:
        log.info(f"     {r['table']:35s}  score={r['quality_score_pct']}%  issues={r['total_issues']}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("=" * 60)
    log.info("HAOAP Data Pipeline  |  started")
    log.info("=" * 60)

    reports = []

    # Aid Distribution (raw WITH errors file)
    rpt1, clean1 = validate_aid_distribution(DATA_DIR / "Raw_AidDistribution_WithErrors.csv")
    write_clean(clean1, DATA_DIR / "Clean_AidDistribution.csv")
    reports.append(rpt1)

    # Beneficiaries
    rpt2, clean2 = validate_beneficiaries(DATA_DIR / "Dim_Beneficiary.csv")
    write_clean(clean2, DATA_DIR / "Clean_Beneficiary.csv")
    reports.append(rpt2)

    # Funding
    rpt3, clean3 = validate_funding(DATA_DIR / "Fact_Funding.csv")
    write_clean(clean3, DATA_DIR / "Clean_Funding.csv")
    reports.append(rpt3)

    write_quality_report(reports, DATA_DIR / "data_quality_report.json")

    log.info("Pipeline complete ✅")
