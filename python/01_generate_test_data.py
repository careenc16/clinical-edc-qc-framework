"""
============================================================
01_generate_test_data.py
Purpose: Generate clinically realistic synthetic EDC test data
         with deliberately planted errors for QC validation (UAT)
Study:   XYZ-2026 Phase II Diabetes Trial
Author:  Careen Chowrappa
Date:    March 2026
============================================================
Clinical parameters calibrated against published trials:
- SURPASS-2 (NEJM 2021) — Tirzepatide vs Semaglutide in T2D
- DUAL VII (Frontiers Pharmacology 2022) — IDegLira in T2D
  Mean age: 55.6 (SD 10), HbA1c: 8.84 (SD 0.94)%,
  BMI: 29.68 (SD 4.79) kg/m²
============================================================
============================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

print("=" * 60)
print("SYNTHETIC TEST DATA GENERATOR — Study XYZ-2026")
print("Calibrated against published Phase II T2D trial parameters")
print("=" * 60)

# ============================================================
# STUDY PARAMETERS (from protocol)
# ============================================================
N_SUBJECTS = 200
SITES = {
    '001': 'Metro General Hospital',
    '002': 'University Medical Center',
    '003': 'Lakeside Clinical Research',
    '004': 'Downtown Diabetes Clinic',
    '005': 'Regional Health Institute'
}
ARMS = ['DRUG A 10MG', 'DRUG B 25MG', 'PLACEBO']
VISITS = ['SCREENING', 'BASELINE', 'WEEK 4', 'WEEK 8', 'WEEK 12', 'END OF STUDY']

# Clinical parameters from published trials (SURPASS-2, DUAL VII)
AGE_MEAN, AGE_SD = 55.6, 10.0       # Years
BMI_MEAN, BMI_SD = 29.68, 4.79      # kg/m²
HBA1C_MEAN, HBA1C_SD = 8.84, 0.94   # %
DIABETES_DUR_MEAN = 8.87             # Years
SBP_MEAN, SBP_SD = 132, 14          # mmHg
DBP_MEAN, DBP_SD = 79, 9            # mmHg
HR_MEAN, HR_SD = 74, 11             # bpm
TEMP_MEAN, TEMP_SD = 36.7, 0.3      # °C
WEIGHT_MEAN, WEIGHT_SD = 87, 16     # kg (derived from BMI ~30, height ~170)
HEIGHT_MEAN, HEIGHT_SD = 170, 9     # cm

# Lab reference ranges (central lab)
LAB_RANGES = {
    'GLUC':  {'mean': 154, 'sd': 42, 'unit': 'mg/dL', 'lo': 70, 'hi': 100},
    'HBA1C': {'mean': HBA1C_MEAN, 'sd': HBA1C_SD, 'unit': '%', 'lo': 4.0, 'hi': 5.6},
    'ALT':   {'mean': 28, 'sd': 15, 'unit': 'U/L', 'lo': 7, 'hi': 40},
    'AST':   {'mean': 25, 'sd': 12, 'unit': 'U/L', 'lo': 10, 'hi': 40},
    'CREAT': {'mean': 0.95, 'sd': 0.25, 'unit': 'mg/dL', 'lo': 0.6, 'hi': 1.2},
    'BUN':   {'mean': 15, 'sd': 5, 'unit': 'mg/dL', 'lo': 7, 'hi': 20},
    'CHOL':  {'mean': 195, 'sd': 38, 'unit': 'mg/dL', 'lo': 0, 'hi': 200},
    'TRIG':  {'mean': 165, 'sd': 80, 'unit': 'mg/dL', 'lo': 0, 'hi': 150},
    'HDL':   {'mean': 45, 'sd': 12, 'unit': 'mg/dL', 'lo': 40, 'hi': 999},
    'LDL':   {'mean': 110, 'sd': 34, 'unit': 'mg/dL', 'lo': 0, 'hi': 100},
}

# AE terms (common in diabetes trials)
AE_TERMS = [
    ('Nausea', 'Nausea', 'Gastrointestinal disorders'),
    ('Diarrhoea', 'Diarrhoea', 'Gastrointestinal disorders'),
    ('Vomiting', 'Vomiting', 'Gastrointestinal disorders'),
    ('Headache', 'Headache', 'Nervous system disorders'),
    ('Dizziness', 'Dizziness', 'Nervous system disorders'),
    ('Hypoglycaemia', 'Hypoglycaemia', 'Metabolism and nutrition disorders'),
    ('Decreased appetite', 'Decreased appetite', 'Metabolism and nutrition disorders'),
    ('Nasopharyngitis', 'Nasopharyngitis', 'Infections and infestations'),
    ('Injection site reaction', 'Injection site reaction', 'General disorders'),
    ('Fatigue', 'Fatigue', 'General disorders'),
    ('Back pain', 'Back pain', 'Musculoskeletal disorders'),
    ('Arthralgia', 'Arthralgia', 'Musculoskeletal disorders'),
    ('Urinary tract infection', 'Urinary tract infection', 'Infections and infestations'),
    ('Constipation', 'Constipation', 'Gastrointestinal disorders'),
    ('Abdominal pain', 'Abdominal pain upper', 'Gastrointestinal disorders'),
]

# Concomitant medications (common in T2D patients)
CM_MEDS = [
    ('Metformin', 'metformin hydrochloride', 1000, 'mg', 'ORAL', 'Type 2 diabetes mellitus'),
    ('Lisinopril', 'lisinopril', 10, 'mg', 'ORAL', 'Hypertension'),
    ('Atorvastatin', 'atorvastatin calcium', 20, 'mg', 'ORAL', 'Hyperlipidemia'),
    ('Aspirin', 'acetylsalicylic acid', 81, 'mg', 'ORAL', 'Cardiovascular prophylaxis'),
    ('Amlodipine', 'amlodipine besylate', 5, 'mg', 'ORAL', 'Hypertension'),
    ('Omeprazole', 'omeprazole', 20, 'mg', 'ORAL', 'Gastroesophageal reflux'),
    ('Glimepiride', 'glimepiride', 2, 'mg', 'ORAL', 'Type 2 diabetes mellitus'),
    ('Sitagliptin', 'sitagliptin phosphate', 100, 'mg', 'ORAL', 'Type 2 diabetes mellitus'),
    ('Losartan', 'losartan potassium', 50, 'mg', 'ORAL', 'Hypertension'),
    ('Gabapentin', 'gabapentin', 300, 'mg', 'ORAL', 'Diabetic neuropathy'),
]

# ============================================================
# GENERATE DEMOGRAPHICS (DM)
# ============================================================
print("\n--- Generating DM (Demographics) ---")
dm_records = []

for i in range(N_SUBJECTS):
    site = random.choice(list(SITES.keys()))
    subj = f"XYZ-2026-{site}-{str(i+1).zfill(4)}"

    # Consent date spread over 3-month enrollment window
    consent_date = datetime(2026, 1, 15) + timedelta(days=random.randint(0, 90))

    # Age from published distribution, clipped to protocol range 18-75
    age = int(np.clip(np.random.normal(AGE_MEAN, AGE_SD), 18, 75))
    birth_year = consent_date.year - age
    birth_date = datetime(birth_year, random.randint(1, 12), random.randint(1, 28))

    # First dose 1-14 days after consent (standard run-in period)
    first_dose = consent_date + timedelta(days=random.randint(1, 14))

    # Sex distribution ~55% male (typical for T2D trials)
    sex = np.random.choice(['M', 'F'], p=[0.55, 0.45])

    # Race distribution (approximate US clinical trial demographics)
    race = np.random.choice(
        ['WHITE', 'BLACK OR AFRICAN AMERICAN', 'ASIAN',
         'AMERICAN INDIAN OR ALASKA NATIVE', 'OTHER'],
        p=[0.65, 0.18, 0.10, 0.02, 0.05]
    )

    ethnicity = np.random.choice(
        ['HISPANIC OR LATINO', 'NOT HISPANIC OR LATINO'],
        p=[0.15, 0.85]
    )

    arm = random.choice(ARMS)

    dm_records.append({
        'USUBJID': subj, 'SITEID': site, 'SITENAME': SITES[site],
        'RFICDTC': consent_date.strftime('%Y-%m-%d'),
        'BRTHDTC': birth_date.strftime('%Y-%m-%d'),
        'AGE': age,
        'SEX': sex,
        'RACE': race,
        'ETHNIC': ethnicity,
        'ARM': arm,
        'RFSTDTC': first_dose.strftime('%Y-%m-%d'),
        'RFENDTC': (first_dose + timedelta(days=84)).strftime('%Y-%m-%d'),
        'DTHFL': 'N'
    })

dm = pd.DataFrame(dm_records)

# ---- PLANT DM ERRORS ----
print("   Planting DM errors...")

# Error Type 1: Age outside protocol range (18-75)
dm.loc[5, 'AGE'] = 82       # elderly beyond protocol
dm.loc[42, 'AGE'] = 16      # minor — protocol violation
dm.loc[188, 'AGE'] = -3     # impossible negative age

# Error Type 2: First dose BEFORE consent (serious protocol violation)
dm.loc[10, 'RFSTDTC'] = '2025-12-01'
dm.loc[77, 'RFSTDTC'] = '2025-11-15'
dm.loc[150, 'RFSTDTC'] = '2025-10-20'

# Error Type 3: Missing required fields
dm.loc[20, 'SEX'] = np.nan
dm.loc[55, 'RACE'] = np.nan
dm.loc[90, 'ETHNIC'] = np.nan
dm.loc[130, 'AGE'] = np.nan
dm.loc[170, 'ARM'] = np.nan

# Error Type 4: Invalid coded values
dm.loc[33, 'SEX'] = 'X'         # not M or F
dm.loc[99, 'SEX'] = 'MALE'      # should be M
dm.loc[145, 'SEX'] = 'Female'   # should be F

# Error Type 5: Invalid subject ID format
dm.loc[15, 'USUBJID'] = 'WRONG-FORMAT'
dm.loc[88, 'USUBJID'] = '12345'
dm.loc[165, 'USUBJID'] = 'XYZ-2026-01-001'  # site should be 3 digits

# Error Type 6: Age doesn't match DOB calculation
dm.loc[60, 'AGE'] = 25      # actual age from DOB will be ~56
dm.loc[120, 'AGE'] = 90     # actual age from DOB will be ~55

dm_error_count = 3 + 3 + 5 + 3 + 3 + 2  # = 19
print(f"   DM: {len(dm)} records | {dm_error_count} planted errors")

# ============================================================
# GENERATE ADVERSE EVENTS (AE)
# ============================================================
print("\n--- Generating AE (Adverse Events) ---")
ae_records = []

for i in range(N_SUBJECTS):
    # Average 1.8 AEs per subject (typical for Phase II diabetes)
    n_aes = np.random.poisson(1.8)
    for j in range(n_aes):
        subj = dm.loc[i, 'USUBJID']
        try:
            consent = datetime.strptime(dm.loc[i, 'RFICDTC'], '%Y-%m-%d')
        except:
            consent = datetime(2026, 2, 1)

        ae_start = consent + timedelta(days=random.randint(1, 120))
        ae_duration = random.randint(1, 30)
        ae_end = ae_start + timedelta(days=ae_duration)

        term, coded, bodsys = random.choice(AE_TERMS)

        # Severity weighted: mostly mild in Phase II
        severity = np.random.choice(
            ['MILD', 'MODERATE', 'SEVERE'], p=[0.55, 0.35, 0.10])

        relationship = np.random.choice(
            ['NOT RELATED', 'UNLIKELY', 'POSSIBLE', 'PROBABLE', 'DEFINITE'],
            p=[0.30, 0.20, 0.30, 0.15, 0.05])

        serious = 'Y' if (severity == 'SEVERE' and random.random() > 0.3) else 'N'

        outcome = np.random.choice(
            ['RECOVERED/RESOLVED', 'RECOVERING/RESOLVING',
             'NOT RECOVERED/NOT RESOLVED', 'RECOVERED WITH SEQUELAE',
             'UNKNOWN'],
            p=[0.50, 0.20, 0.15, 0.05, 0.10])

        action = np.random.choice(
            ['NONE', 'DOSE REDUCED', 'DRUG INTERRUPTED',
             'DRUG WITHDRAWN', 'NOT APPLICABLE'],
            p=[0.50, 0.15, 0.15, 0.10, 0.10])

        ae_records.append({
            'USUBJID': subj,
            'AESEQ': j + 1,
            'AETERM': term,
            'AEDECOD': coded,
            'AEBODSYS': bodsys,
            'AESTDTC': ae_start.strftime('%Y-%m-%d'),
            'AEENDTC': ae_end.strftime('%Y-%m-%d') if 'RECOVERED' in outcome else '',
            'AESEV': severity,
            'AESER': serious,
            'AEREL': relationship,
            'AEOUT': outcome,
            'AEACN': action
        })

ae = pd.DataFrame(ae_records)

# ---- PLANT AE ERRORS ----
print("   Planting AE errors...")

if len(ae) > 210:
    # Error Type 7: AE end date before start date
    for idx in [3, 50, 120, 200]:
        if idx < len(ae):
            ae.loc[idx, 'AEENDTC'] = '2025-01-01'

    # Error Type 8: AE start before consent
    for idx in [8, 75, 180]:
        if idx < len(ae):
            ae.loc[idx, 'AESTDTC'] = '2025-06-01'

    # Error Type 9: SEVERE but not SERIOUS
    for idx in [15, 45, 110]:
        if idx < len(ae):
            ae.loc[idx, 'AESEV'] = 'SEVERE'
            ae.loc[idx, 'AESER'] = 'N'

    # Error Type 10: Missing MedDRA coded term
    for idx in [22, 100, 140]:
        if idx < len(ae):
            ae.loc[idx, 'AEDECOD'] = ''

    # Error Type 11: RECOVERED but no end date
    for idx in [30, 60, 155]:
        if idx < len(ae):
            ae.loc[idx, 'AEOUT'] = 'RECOVERED/RESOLVED'
            ae.loc[idx, 'AEENDTC'] = ''

    # Error Type 12: Invalid severity value
    for idx in [90, 170]:
        if idx < len(ae):
            ae.loc[idx, 'AESEV'] = 'LIGHT'

ae_error_count = 4 + 3 + 3 + 3 + 3 + 2  # = 18
print(f"   AE: {len(ae)} records | {ae_error_count} planted errors")

# ============================================================
# GENERATE VITAL SIGNS (VS)
# ============================================================
print("\n--- Generating VS (Vital Signs) ---")
vs_records = []

for i in range(N_SUBJECTS):
    subj = dm.loc[i, 'USUBJID']
    try:
        consent = datetime.strptime(dm.loc[i, 'RFICDTC'], '%Y-%m-%d')
    except:
        consent = datetime(2026, 2, 1)

    # Baseline vitals (calibrated from published data)
    base_sbp = np.random.normal(SBP_MEAN, SBP_SD)
    base_dbp = np.random.normal(DBP_MEAN, DBP_SD)
    base_hr = np.random.normal(HR_MEAN, HR_SD)
    base_temp = np.random.normal(TEMP_MEAN, TEMP_SD)
    base_weight = np.random.normal(WEIGHT_MEAN, WEIGHT_SD)
    height = np.random.normal(HEIGHT_MEAN, HEIGHT_SD)

    for v_idx, visit in enumerate(VISITS):
        visit_date = consent + timedelta(days=v_idx * 28)

        # Add slight visit-to-visit variation
        sbp = round(base_sbp + np.random.normal(0, 5))
        dbp = round(base_dbp + np.random.normal(0, 3))
        hr = round(base_hr + np.random.normal(0, 4))
        temp = round(base_temp + np.random.normal(0, 0.2), 1)
        weight = round(base_weight + np.random.normal(0, 0.5), 1)

        record = {
            'USUBJID': subj,
            'VISITNUM': v_idx + 1,
            'VISIT': visit,
            'VSDTC': visit_date.strftime('%Y-%m-%d'),
            'SYSBP': sbp,
            'DIABP': dbp,
            'PULSE': hr,
            'TEMP': temp,
            'WEIGHT': weight,
        }
        # Height only at screening
        if visit == 'SCREENING':
            record['HEIGHT'] = round(height, 1)
        else:
            record['HEIGHT'] = np.nan

        vs_records.append(record)

vs = pd.DataFrame(vs_records)

# ---- PLANT VS ERRORS ----
print("   Planting VS errors...")

# Error Type 13: Systolic ≤ Diastolic
for idx in [5, 100, 300, 500]:
    if idx < len(vs):
        vs.loc[idx, 'SYSBP'] = 70
        vs.loc[idx, 'DIABP'] = 95

# Error Type 14: Impossible vital signs
impossible_vs = [(20, 'SYSBP', 310), (50, 'PULSE', 8),
                 (150, 'TEMP', 43.5), (250, 'DIABP', 200),
                 (400, 'PULSE', 220), (600, 'TEMP', 30.0)]
for idx, field, val in impossible_vs:
    if idx < len(vs):
        vs.loc[idx, field] = val

# Error Type 15: Missing required vitals
for idx in [30, 80, 180, 350, 550]:
    if idx < len(vs):
        field = random.choice(['SYSBP', 'DIABP', 'PULSE', 'TEMP'])
        vs.loc[idx, field] = np.nan

vs_error_count = 4 + 6 + 5  # = 15
print(f"   VS: {len(vs)} records | {vs_error_count} planted errors")

# ============================================================
# GENERATE LABORATORY DATA (LB)
# ============================================================
print("\n--- Generating LB (Laboratory) ---")
lb_records = []

lab_visits = ['SCREENING', 'BASELINE', 'WEEK 4', 'WEEK 8', 'WEEK 12', 'END OF STUDY']

for i in range(N_SUBJECTS):
    subj = dm.loc[i, 'USUBJID']
    try:
        consent = datetime.strptime(dm.loc[i, 'RFICDTC'], '%Y-%m-%d')
    except:
        consent = datetime(2026, 2, 1)

    for v_idx, visit in enumerate(lab_visits):
        visit_date = consent + timedelta(days=v_idx * 28)

        for test_code, params in LAB_RANGES.items():
            result = round(np.random.normal(params['mean'], params['sd']), 2)
            # Ensure non-negative
            result = max(result, 0.01)

            # Determine normal range indicator
            if result < params['lo']:
                nrind = 'LOW'
            elif result > params['hi']:
                nrind = 'HIGH'
            else:
                nrind = 'NORMAL'

            lb_records.append({
                'USUBJID': subj,
                'VISITNUM': v_idx + 1,
                'VISIT': visit,
                'LBDTC': visit_date.strftime('%Y-%m-%d'),
                'LBTESTCD': test_code,
                'LBTEST': {
                    'GLUC': 'Glucose', 'HBA1C': 'Hemoglobin A1C',
                    'ALT': 'Alanine Aminotransferase',
                    'AST': 'Aspartate Aminotransferase',
                    'CREAT': 'Creatinine', 'BUN': 'Blood Urea Nitrogen',
                    'CHOL': 'Cholesterol', 'TRIG': 'Triglycerides',
                    'HDL': 'HDL Cholesterol', 'LDL': 'LDL Cholesterol'
                }[test_code],
                'LBORRES': str(result),
                'LBORRESU': params['unit'],
                'LBSTRESN': result,
                'LBNRIND': nrind,
                'LBSTNRLO': params['lo'],
                'LBSTNRHI': params['hi']
            })

lb = pd.DataFrame(lb_records)

# ---- PLANT LB ERRORS ----
print("   Planting LB errors...")

# Error Type 16: HbA1c outside testable range
hba1c_rows = lb[lb['LBTESTCD'] == 'HBA1C'].index.tolist()
if len(hba1c_rows) >= 3:
    lb.loc[hba1c_rows[5], 'LBSTRESN'] = 25.0   # impossible
    lb.loc[hba1c_rows[5], 'LBORRES'] = '25.0'
    lb.loc[hba1c_rows[50], 'LBSTRESN'] = 1.5    # impossible
    lb.loc[hba1c_rows[50], 'LBORRES'] = '1.5'

# Error Type 17: ALT > 3x ULN (hepatotoxicity signal)
alt_rows = lb[lb['LBTESTCD'] == 'ALT'].index.tolist()
if len(alt_rows) >= 3:
    lb.loc[alt_rows[10], 'LBSTRESN'] = 185.0
    lb.loc[alt_rows[10], 'LBORRES'] = '185.0'
    lb.loc[alt_rows[10], 'LBNRIND'] = 'HIGH'
    lb.loc[alt_rows[30], 'LBSTRESN'] = 220.0
    lb.loc[alt_rows[30], 'LBORRES'] = '220.0'
    lb.loc[alt_rows[30], 'LBNRIND'] = 'HIGH'

lb_error_count = 2 + 2  # = 4
print(f"   LB: {len(lb)} records | {lb_error_count} planted errors")

# ============================================================
# GENERATE CONCOMITANT MEDICATIONS (CM)
# ============================================================
print("\n--- Generating CM (Concomitant Medications) ---")
cm_records = []

for i in range(N_SUBJECTS):
    subj = dm.loc[i, 'USUBJID']
    try:
        consent = datetime.strptime(dm.loc[i, 'RFICDTC'], '%Y-%m-%d')
    except:
        consent = datetime(2026, 2, 1)

    # Average 3.2 concomitant meds per T2D patient
    n_meds = max(1, int(np.random.poisson(3.2)))
    selected_meds = random.sample(CM_MEDS, min(n_meds, len(CM_MEDS)))

    for j, (name, coded, dose, unit, route, indication) in enumerate(selected_meds):
        # Most meds started before study (prior/concomitant)
        start_offset = random.randint(-365, 30)
        cm_start = consent + timedelta(days=start_offset)

        # Some meds are ongoing, some have end dates
        if random.random() < 0.4:
            cm_end = cm_start + timedelta(days=random.randint(30, 180))
            cm_end_str = cm_end.strftime('%Y-%m-%d')
        else:
            cm_end_str = ''  # ongoing

        cm_records.append({
            'USUBJID': subj,
            'CMSEQ': j + 1,
            'CMTRT': name,
            'CMDECOD': coded,
            'CMDOSE': dose,
            'CMDOSU': unit,
            'CMROUTE': route,
            'CMSTDTC': cm_start.strftime('%Y-%m-%d'),
            'CMENDTC': cm_end_str,
            'CMINDC': indication
        })

cm = pd.DataFrame(cm_records)

# ---- PLANT CM ERRORS ----
print("   Planting CM errors...")

# Error Type 18: Med end date before start date
for idx in [5, 40, 100]:
    if idx < len(cm):
        cm.loc[idx, 'CMENDTC'] = '2024-01-01'

# Error Type 19: Missing dose
for idx in [15, 60]:
    if idx < len(cm):
        cm.loc[idx, 'CMDOSE'] = np.nan

cm_error_count = 3 + 2  # = 5
print(f"   CM: {len(cm)} records | {cm_error_count} planted errors")

# ============================================================
# SAVE ALL DATA
# ============================================================
os.makedirs('data', exist_ok=True)
dm.to_csv('data/dm_test_data.csv', index=False)
ae.to_csv('data/ae_test_data.csv', index=False)
vs.to_csv('data/vs_test_data.csv', index=False)
lb.to_csv('data/lb_test_data.csv', index=False)
cm.to_csv('data/cm_test_data.csv', index=False)

# ============================================================
# SUMMARY
# ============================================================
total_errors = dm_error_count + ae_error_count + vs_error_count + lb_error_count + cm_error_count
total_records = len(dm) + len(ae) + len(vs) + len(lb) + len(cm)

print("\n" + "=" * 60)
print("DATA GENERATION SUMMARY")
print("=" * 60)
print(f"  Subjects:        {N_SUBJECTS}")
print(f"  Sites:           {len(SITES)}")
print(f"  Treatment Arms:  {len(ARMS)}")
print(f"")
print(f"  Domain   Records   Planted Errors")
print(f"  ------   -------   --------------")
print(f"  DM       {len(dm):>7}   {dm_error_count}")
print(f"  AE       {len(ae):>7}   {ae_error_count}")
print(f"  VS       {len(vs):>7}   {vs_error_count}")
print(f"  LB       {len(lb):>7}   {lb_error_count}")
print(f"  CM       {len(cm):>7}   {cm_error_count}")
print(f"  ------   -------   --------------")
print(f"  TOTAL    {total_records:>7}   {total_errors}")
print(f"")
print(f"  Clinical Parameters Source:")
print(f"  - SURPASS-2 (NEJM 2021) — Tirzepatide vs Semaglutide")
print(f"  - DUAL VII (Front Pharmacol 2022) — IDegLira in T2D")
print(f"  - Age: mean {AGE_MEAN} (SD {AGE_SD})")
print(f"  - HbA1c: mean {HBA1C_MEAN}% (SD {HBA1C_SD})")
print(f"  - BMI: mean {BMI_MEAN} (SD {BMI_SD})")
print(f"")
print(f"All data saved to data/ folder ✅")
