"""Deterministic synthetic Contoso HR data generator.

Emits a single wide fact table (`fact_employee`) plus an access map
(`hr_access`) as parquet + CSV into ``data/``. Fixed seeds make the output
byte-stable and safe to commit.

100% FICTIONAL. No real people. Design reference only (not downloaded):
IBM HR Analytics Employee Attrition (CC0) — kaggle pavansubhasht/ibm-hr-analytics-attrition-dataset.

Run directly to (re)generate and self-check:
    python data/generate_hr.py
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

SEED = 42
SNAPSHOT_DATE = date(2026, 7, 1)  # ponytail: fixed snapshot so re-runs are deterministic
N_TARGET = 5000
EMP_ID_START = 100000
OUT_DIR = Path(__file__).resolve().parent

REGIONS = ["NA", "EMEA", "APAC", "LATAM"]
REGION_WEIGHTS = [0.40, 0.28, 0.22, 0.10]
REGION_FACTOR = {"NA": 1.00, "EMEA": 0.95, "APAC": 0.85, "LATAM": 0.80}
REGION_CITIES = {
    "NA": ["Redmond, WA", "Austin, TX", "Toronto, ON", "New York, NY"],
    "EMEA": ["Dublin, IE", "London, UK", "Amsterdam, NL", "Munich, DE"],
    "APAC": ["Singapore, SG", "Sydney, AU", "Bengaluru, IN", "Tokyo, JP"],
    "LATAM": ["Sao Paulo, BR", "Mexico City, MX", "Bogota, CO", "Buenos Aires, AR"],
}

# team -> (org, department). Region is assigned independently (teams span regions).
TEAM_CATALOG = {
    "Azure Data": ("Engineering", "Data & AI"),
    "Azure Core": ("Engineering", "Cloud Platform"),
    "Security Platform": ("Engineering", "Security"),
    "Developer Tools": ("Engineering", "Developer Division"),
    "Field Sales": ("Sales", "Enterprise Sales"),
    "Inside Sales": ("Sales", "SMB Sales"),
    "Solution Engineering": ("Sales", "Presales"),
    "Brand Marketing": ("Marketing", "Brand"),
    "Product Marketing": ("Marketing", "Product Marketing"),
    "FP&A": ("Finance", "Financial Planning"),
    "Controllership": ("Finance", "Accounting"),
    "Talent Acquisition": ("HumanResources", "Recruiting"),
    "People Operations": ("HumanResources", "HR Operations"),
    "Supply Chain": ("Operations", "Supply Chain"),
    "Customer Support": ("Operations", "Support"),
}
TEAM_NAMES = list(TEAM_CATALOG)
HOT_TEAMS = {"Azure Data", "Field Sales", "Customer Support"}  # elevated attrition

TITLE_BY_LEVEL = {
    6: "Chief Executive Officer",
    5: "Senior Vice President",
    4: "Director",
    3: "Senior Manager",
    2: "Specialist",
    1: "Associate",
}
INCOME_BASE = {1: 4200, 2: 6000, 3: 8500, 4: 12500, 5: 19000, 6: 30000}

# Two demo HR business partners, each scoped to their region. allowed_team NULL = all teams.
PERSONAS = [
    {"user_upn": "emea.hrbp@contoso.com", "allowed_region": "EMEA", "allowed_team": None},
    {"user_upn": "apac.hrbp@contoso.com", "allowed_region": "APAC", "allowed_team": None},
]


def _build_org_tree(regions: np.ndarray, ids: np.ndarray) -> tuple[list, list]:
    """Balanced ~1:8 tree per region, regional heads report to the global root.

    Guarantees manager_id < employee_id for every node, so depth is a single pass.
    """
    manager_ids: list[int | None] = [None] * len(ids)
    root_id = int(ids[0])
    for r in REGIONS:
        members = [int(ids[i]) for i in range(len(ids)) if regions[i] == r]
        for j, emp in enumerate(members):
            if j == 0:  # regional head
                manager_ids[emp - EMP_ID_START] = None if emp == root_id else root_id
            else:
                manager_ids[emp - EMP_ID_START] = members[(j - 1) // 8]
    depths = [0] * len(ids)
    for idx in range(len(ids)):
        mgr = manager_ids[idx]
        depths[idx] = 0 if mgr is None else depths[mgr - EMP_ID_START] + 1
    return manager_ids, depths


def generate() -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEED)
    fake = Faker("en_US")
    Faker.seed(SEED)

    ids = np.arange(EMP_ID_START, EMP_ID_START + N_TARGET)
    regions = rng.choice(REGIONS, size=N_TARGET, p=REGION_WEIGHTS)
    # Force the global root into a region so members_r[0] logic is stable.
    regions[0] = "NA"

    manager_ids, depths = _build_org_tree(regions, ids)
    levels = [max(1, 6 - min(d, 5)) for d in depths]

    rows = []
    seen_emails: dict[str, int] = {}
    for i in range(N_TARGET):
        emp_id = int(ids[i])
        region = str(regions[i])
        level = levels[i]

        full_name = fake.name()
        base = "".join(c for c in full_name.lower().replace(" ", ".") if c.isalnum() or c == ".")
        n = seen_emails.get(base, 0)
        seen_emails[base] = n + 1
        email = f"{base}{'' if n == 0 else n}@contoso.com"

        if level >= 5:  # execs sit outside functional teams
            team, org, dept = "Executive Leadership", "Executive", "Executive"
        else:
            team = TEAM_NAMES[int(rng.integers(0, len(TEAM_NAMES)))]
            org, dept = TEAM_CATALOG[team]

        title = "Chief Executive Officer" if level == 6 else f"{org} {TITLE_BY_LEVEL[level]}"
        office = REGION_CITIES[region][int(rng.integers(0, 4))]

        hire_days_ago = int(rng.integers(30, 15 * 365))
        hire_date = SNAPSHOT_DATE - timedelta(days=hire_days_ago)
        tenure_years = round(hire_days_ago / 365.25, 1)
        years_in_role = round(min(tenure_years, tenure_years * float(rng.uniform(0.3, 1.0))), 1)

        age = int(np.clip(22 + tenure_years + rng.integers(0, 18), 22, 64))
        gender = str(rng.choice(["Female", "Male", "Non-binary"], p=[0.47, 0.50, 0.03]))
        overtime = str(rng.choice(["Yes", "No"], p=[0.30, 0.70]))
        job_sat = int(rng.integers(1, 5))
        env_sat = int(rng.integers(1, 5))
        perf = int(rng.choice([1, 2, 3, 4], p=[0.05, 0.20, 0.55, 0.20]))
        distance = int(rng.integers(1, 30))
        education = int(rng.integers(1, 6))
        num_companies = int(rng.integers(0, 9))
        travel = str(
            rng.choice(["Non-Travel", "Travel_Rarely", "Travel_Frequently"], p=[0.20, 0.55, 0.25])
        )
        emp_type = str(rng.choice(["Full-Time", "Part-Time", "Contract"], p=[0.85, 0.08, 0.07]))

        income = INCOME_BASE[level] * REGION_FACTOR[region] * float(rng.normal(1.0, 0.12))
        monthly_income = int(np.clip(round(income, -2), 2500, 60000))
        salary_band = f"Band {level}"

        # Baked-in attrition correlations.
        p = 0.10
        p += 0.15 if overtime == "Yes" else 0.0
        p += 0.12 if tenure_years < 2 else 0.0
        p += 0.05 if job_sat <= 2 else 0.0
        p += 0.05 if job_sat == 1 else 0.0
        p += 0.06 if distance > 20 else 0.0
        p += 0.12 if team in HOT_TEAMS else 0.0
        p += 0.05 if travel == "Travel_Frequently" else 0.0
        p -= 0.05 if job_sat == 4 else 0.0
        p = float(np.clip(p, 0.02, 0.85))
        attrition = int(rng.random() < p)

        if attrition and level < 6:  # never terminate the CEO
            max_days = min(365, max(2, hire_days_ago - 1))
            term_date = SNAPSHOT_DATE - timedelta(days=int(rng.integers(1, max_days + 1)))
            active_status, termination_date = "Terminated", term_date.isoformat()
        else:
            attrition = 0 if level == 6 else attrition
            active_status, termination_date = "Active", None
            attrition = 0  # active employees have not attrited in this snapshot

        rows.append(
            {
                "employee_id": emp_id,
                "full_name": full_name,
                "work_email": email,
                "manager_id": manager_ids[i],
                "job_title": title,
                "department": dept,
                "team": team,
                "org": org,
                "region": region,
                "office_location": office,
                "hire_date": hire_date.isoformat(),
                "employment_type": emp_type,
                "active_status": active_status,
                "termination_date": termination_date,
                "age": age,
                "gender": gender,
                "tenure_years": tenure_years,
                "years_in_role": years_in_role,
                "attrition_flag": attrition,
                "monthly_income": monthly_income,
                "salary_band": salary_band,
                "overtime": overtime,
                "job_satisfaction": job_sat,
                "environment_satisfaction": env_sat,
                "performance_rating": perf,
                "distance_from_home": distance,
                "education_level": education,
                "num_companies_worked": num_companies,
                "business_travel": travel,
            }
        )

    fact = pd.DataFrame(rows)
    fact["manager_id"] = fact["manager_id"].astype("Int64")
    access = pd.DataFrame(PERSONAS)
    return fact, access


def self_check(fact: pd.DataFrame, access: pd.DataFrame) -> None:
    assert len(fact) == N_TARGET, f"expected {N_TARGET} rows, got {len(fact)}"
    assert fact["employee_id"].is_unique, "employee_id not unique"
    assert fact["work_email"].is_unique, "work_email not unique"

    nulls = fact["manager_id"].isna().sum()
    assert nulls == 1, f"expected exactly one root (null manager), got {nulls}"
    valid_ids = set(fact["employee_id"])
    resolved = fact["manager_id"].dropna().isin(valid_ids).all()
    assert resolved, "some manager_id does not resolve to an employee"

    rate = fact["attrition_flag"].mean()
    assert 0.05 <= rate <= 0.45, f"implausible overall attrition {rate:.2%}"
    for region in ["EMEA", "APAC"]:
        r_rate = fact.loc[fact.region == region, "attrition_flag"].mean()
        assert 0.02 <= r_rate <= 0.6, f"{region} attrition {r_rate:.2%} implausible"

    upns = set(access["user_upn"])
    assert {"emea.hrbp@contoso.com", "apac.hrbp@contoso.com"} <= upns, "personas missing"

    # Metrics/roster reconciliation for one scope: active EMEA headcount two ways.
    scope = (fact.region == "EMEA") & (fact.active_status == "Active")
    agg = int(fact.loc[scope].shape[0])
    roster = len(fact[scope]["employee_id"].tolist())
    assert agg == roster, "aggregate vs roster count mismatch"

    # Hot team should out-attrite the overall rate (correlation actually landed).
    hot = fact[fact.team.isin(HOT_TEAMS)]["attrition_flag"].mean()
    assert hot > rate, f"hot-team attrition {hot:.2%} not above overall {rate:.2%}"
    print("self_check: OK")


def main() -> None:
    fact, access = generate()
    self_check(fact, access)
    fact.to_parquet(OUT_DIR / "fact_employee.parquet", index=False)
    fact.to_csv(OUT_DIR / "fact_employee.csv", index=False)
    access.to_parquet(OUT_DIR / "hr_access.parquet", index=False)
    access.to_csv(OUT_DIR / "hr_access.csv", index=False)
    print(f"wrote {len(fact)} employees, {len(access)} access rows to {OUT_DIR}")
    print(f"overall attrition: {fact['attrition_flag'].mean():.2%}")
    for r in REGIONS:
        sub = fact[fact.region == r]
        print(f"  {r:5s} n={len(sub):4d} attrition={sub['attrition_flag'].mean():.2%}")


if __name__ == "__main__":
    main()
