"""
============================================================
02_qc_engine.py
Purpose: Automated QC Engine — runs all edit checks against
         test data and generates discrepancy database
Study:   XYZ-2026 Phase II Diabetes Trial
Author:  Careen Chowrappa
Date:    March 2026
============================================================
Runs 20 edit checks across 5 SDTM domains (DM, AE, VS, LB, CM)
Generates a discrepancy database with auto-classified queries
============================================================
Maps to ICON JD: "Performing quality control (QC) checks on
clinical trial data and study documentation to identify
discrepancies, inconsistencies, and data entry errors"
============================================================
"""

import pandas as pd
import numpy as np
import re
import os
from datetime import datetime

# ============================================================
# LOAD TEST DATA
# ============================================================
print("=" * 60)
print("QC ENGINE — Study XYZ-2026")
print("Automated Edit Check Framework")
print("=" * 60)

dm = pd.read_csv('data/dm_test_data.csv')
ae = pd.read_csv('data/ae_test_data.csv')
vs = pd.read_csv('data/vs_test_data.csv')
lb = pd.read_csv('data/lb_test_data.csv')
cm = pd.read_csv('data/cm_test_data.csv')

print(f"\nData loaded:")
print(f"  DM: {len(dm)} records")
print(f"  AE: {len(ae)} records")
print(f"  VS: {len(vs)} records")
print(f"  LB: {len(lb)} records")
print(f"  CM: {len(cm)} records")
print(f"  Total: {len(dm)+len(ae)+len(vs)+len(lb)+len(cm)} records")

# ============================================================
# DISCREPANCY TRACKER
# ============================================================
discrepancies = []
query_id = 1

def add_query(domain, subjid, field, check_id, severity, message):
    """Add a query to the discrepancy database."""
    global query_id
    discrepancies.append({
        'QUERY_ID': f'Q-{str(query_id).zfill(4)}',
        'CHECK_ID': check_id,
        'DOMAIN': domain,
        'USUBJID': str(subjid),
        'FIELD': field,
        'SEVERITY': severity,
        'QUERY_TEXT': message,
        'STATUS': 'OPEN',
        'OPENED_DATE': datetime.now().strftime('%Y-%m-%d'),
        'SITE_RESPONSE': '',
        'CLOSED_DATE': '',
        'RESOLUTION': ''
    })
    query_id += 1

# ============================================================
# DM DOMAIN CHECKS
# ============================================================
print("\n" + "-" * 40)
print("Running DM Domain Checks...")
print("-" * 40)
dm_start = query_id

# EC-DM-001: Age must be 18-75 (protocol inclusion criteria)
for idx, row in dm.iterrows():
    if pd.notna(row['AGE']):
        age = int(row['AGE'])
        if age < 18 or age > 75:
            add_query('DM', row['USUBJID'], 'AGE', 'EC-DM-001', 'HARD',
                      f"Subject age {age} is outside protocol-specified "
                      f"range (18-75). Please verify against source document.")

# EC-DM-002: First dose date >= consent date
for idx, row in dm.iterrows():
    try:
        consent = datetime.strptime(str(row['RFICDTC']), '%Y-%m-%d')
        dose = datetime.strptime(str(row['RFSTDTC']), '%Y-%m-%d')
        if dose < consent:
            add_query('DM', row['USUBJID'], 'RFSTDTC', 'EC-DM-002', 'HARD',
                      f"First dose date ({row['RFSTDTC']}) is before informed "
                      f"consent date ({row['RFICDTC']}). This is a protocol "
                      f"violation. Please review.")
    except (ValueError, TypeError):
        pass

# EC-DM-003: Sex must be M or F
for idx, row in dm.iterrows():
    if pd.notna(row['SEX']) and str(row['SEX']).strip() not in ['M', 'F']:
        add_query('DM', row['USUBJID'], 'SEX', 'EC-DM-003', 'HARD',
                  f"Invalid sex value '{row['SEX']}'. Expected M or F "
                  f"per CDISC controlled terminology.")

# EC-DM-004: Age must match DOB calculation
for idx, row in dm.iterrows():
    try:
        dob = datetime.strptime(str(row['BRTHDTC']), '%Y-%m-%d')
        consent = datetime.strptime(str(row['RFICDTC']), '%Y-%m-%d')
        calc_age = (consent - dob).days // 365
        if pd.notna(row['AGE']) and abs(int(row['AGE']) - calc_age) > 1:
            add_query('DM', row['USUBJID'], 'AGE', 'EC-DM-004', 'HARD',
                      f"Reported age ({int(row['AGE'])}) does not match "
                      f"calculated age from DOB ({calc_age}). "
                      f"Discrepancy of {abs(int(row['AGE']) - calc_age)} years. "
                      f"Please verify.")
    except (ValueError, TypeError):
        pass

# EC-DM-005: Subject ID format XYZ-2026-SSS-PPPP
for idx, row in dm.iterrows():
    if not re.match(r'^XYZ-2026-\d{3}-\d{4}$', str(row['USUBJID'])):
        add_query('DM', row['USUBJID'], 'USUBJID', 'EC-DM-005', 'HARD',
                  f"Subject ID '{row['USUBJID']}' does not follow expected "
                  f"format XYZ-2026-SSS-PPPP. Please correct.")

# EC-DM-006: Missing required DM fields
required_dm = ['USUBJID', 'SITEID', 'RFICDTC', 'AGE', 'SEX', 'RACE',
               'ETHNIC', 'ARM', 'RFSTDTC']
for idx, row in dm.iterrows():
    for field in required_dm:
        val = row.get(field)
        if pd.isna(val) or str(val).strip() == '':
            add_query('DM', row['USUBJID'], field, 'EC-DM-006', 'HARD',
                      f"{field} is missing. This field is required per "
                      f"protocol CRF completion guidelines.")

dm_queries = query_id - dm_start
print(f"  DM checks complete: {dm_queries} queries generated")

# ============================================================
# AE DOMAIN CHECKS
# ============================================================
print("\n" + "-" * 40)
print("Running AE Domain Checks...")
print("-" * 40)
ae_start = query_id

# Build consent date lookup
dm_consent = {}
for _, row in dm.iterrows():
    try:
        dm_consent[str(row['USUBJID'])] = datetime.strptime(
            str(row['RFICDTC']), '%Y-%m-%d')
    except:
        pass

# EC-AE-001: AE start date >= consent date
for idx, row in ae.iterrows():
    try:
        subj = str(row['USUBJID'])
        if subj in dm_consent:
            ae_start_dt = datetime.strptime(str(row['AESTDTC']), '%Y-%m-%d')
            if ae_start_dt < dm_consent[subj]:
                add_query('AE', subj, 'AESTDTC', 'EC-AE-001', 'HARD',
                          f"AE start date ({row['AESTDTC']}) is before "
                          f"informed consent. Pre-consent events should not "
                          f"be in AE log unless pre-existing. Please verify.")
    except (ValueError, TypeError):
        pass

# EC-AE-002: AE end date >= AE start date
for idx, row in ae.iterrows():
    try:
        end_str = str(row['AEENDTC']).strip()
        if end_str and end_str != '' and end_str != 'nan':
            start_dt = datetime.strptime(str(row['AESTDTC']), '%Y-%m-%d')
            end_dt = datetime.strptime(end_str, '%Y-%m-%d')
            if end_dt < start_dt:
                add_query('AE', row['USUBJID'], 'AEENDTC', 'EC-AE-002', 'HARD',
                          f"AE end date ({row['AEENDTC']}) is before start "
                          f"date ({row['AESTDTC']}). Temporal impossibility. "
                          f"Please review dates.")
    except (ValueError, TypeError):
        pass

# EC-AE-003: SEVERE but not SERIOUS
for idx, row in ae.iterrows():
    if str(row['AESEV']).strip() == 'SEVERE' and str(row['AESER']).strip() == 'N':
        add_query('AE', row['USUBJID'], 'AESER', 'EC-AE-003', 'SOFT',
                  f"AE is graded SEVERE but not marked as Serious. Per "
                  f"ICH E2A, please confirm this AE does not meet any "
                  f"SAE criteria.")

# EC-AE-004: RECOVERED but no end date
for idx, row in ae.iterrows():
    outcome = str(row['AEOUT']).strip()
    end = str(row['AEENDTC']).strip()
    if 'RECOVERED' in outcome and (end == '' or end == 'nan'):
        add_query('AE', row['USUBJID'], 'AEENDTC', 'EC-AE-004', 'SOFT',
                  f"Outcome is '{outcome}' but no end date provided. "
                  f"Please enter resolution date.")

# EC-AE-005: Verbatim term present but coded term missing
for idx, row in ae.iterrows():
    term = str(row['AETERM']).strip()
    coded = str(row['AEDECOD']).strip()
    if term and term != 'nan' and (not coded or coded == '' or coded == 'nan'):
        add_query('AE', row['USUBJID'], 'AEDECOD', 'EC-AE-005', 'SOFT',
                  f"AE verbatim term '{term}' is entered but MedDRA coded "
                  f"term is missing. Please complete medical coding.")

# EC-AE-006: Invalid severity value
valid_sev = ['MILD', 'MODERATE', 'SEVERE']
for idx, row in ae.iterrows():
    sev = str(row['AESEV']).strip()
    if sev and sev != 'nan' and sev not in valid_sev:
        add_query('AE', row['USUBJID'], 'AESEV', 'EC-AE-006', 'HARD',
                  f"Invalid severity value '{sev}'. Expected MILD, "
                  f"MODERATE, or SEVERE per CDISC controlled terminology.")

ae_queries = query_id - ae_start
print(f"  AE checks complete: {ae_queries} queries generated")

# ============================================================
# VS DOMAIN CHECKS
# ============================================================
print("\n" + "-" * 40)
print("Running VS Domain Checks...")
print("-" * 40)
vs_start = query_id

for idx, row in vs.iterrows():
    subj = row['USUBJID']
    visit = row['VISIT']

    # EC-VS-001: Systolic BP range (70-250)
    if pd.notna(row['SYSBP']):
        val = float(row['SYSBP'])
        if val < 70 or val > 250:
            add_query('VS', subj, 'SYSBP', 'EC-VS-001', 'HARD',
                      f"Systolic BP {int(val)} mmHg is outside physiological "
                      f"range (70-250) at {visit}. Please verify against source.")

    # EC-VS-002: Diastolic BP range (40-150)
    if pd.notna(row['DIABP']):
        val = float(row['DIABP'])
        if val < 40 or val > 150:
            add_query('VS', subj, 'DIABP', 'EC-VS-002', 'HARD',
                      f"Diastolic BP {int(val)} mmHg is outside physiological "
                      f"range (40-150) at {visit}. Please verify.")

    # EC-VS-003: Systolic must be > Diastolic
    if pd.notna(row['SYSBP']) and pd.notna(row['DIABP']):
        if float(row['SYSBP']) <= float(row['DIABP']):
            add_query('VS', subj, 'SYSBP/DIABP', 'EC-VS-003', 'HARD',
                      f"Systolic ({int(row['SYSBP'])}) is ≤ Diastolic "
                      f"({int(row['DIABP'])}) at {visit}. Physiologically "
                      f"impossible. Please verify both values.")

    # EC-VS-004: Heart rate range (40-180)
    if pd.notna(row['PULSE']):
        val = float(row['PULSE'])
        if val < 40 or val > 180:
            add_query('VS', subj, 'PULSE', 'EC-VS-004', 'HARD',
                      f"Heart rate {int(val)} bpm is outside range (40-180) "
                      f"at {visit}. Please verify.")

    # EC-VS-005: Temperature range (35.0-40.0)
    if pd.notna(row['TEMP']):
        val = float(row['TEMP'])
        if val < 35.0 or val > 40.0:
            add_query('VS', subj, 'TEMP', 'EC-VS-005', 'HARD',
                      f"Temperature {val}°C is outside expected range "
                      f"(35.0-40.0) at {visit}. Please verify measurement "
                      f"and units.")

    # EC-VS-006: Missing required vitals
    for field in ['SYSBP', 'DIABP', 'PULSE', 'TEMP']:
        if pd.isna(row[field]):
            add_query('VS', subj, field, 'EC-VS-006', 'HARD',
                      f"{field} is missing for {visit}. All vitals are "
                      f"required per protocol Section 8.2.")

vs_queries = query_id - vs_start
print(f"  VS checks complete: {vs_queries} queries generated")

# ============================================================
# LB DOMAIN CHECKS
# ============================================================
print("\n" + "-" * 40)
print("Running LB Domain Checks...")
print("-" * 40)
lb_start = query_id

# EC-LB-001: HbA1c range (3.0-20.0%)
hba1c = lb[lb['LBTESTCD'] == 'HBA1C']
for idx, row in hba1c.iterrows():
    if pd.notna(row['LBSTRESN']):
        val = float(row['LBSTRESN'])
        if val < 3.0 or val > 20.0:
            add_query('LB', row['USUBJID'], 'HBA1C', 'EC-LB-001', 'HARD',
                      f"HbA1c value {val}% is outside testable range "
                      f"(3.0-20.0) at {row['VISIT']}. Please verify "
                      f"with central lab.")

# EC-LB-002: ALT > 3x ULN (>120 U/L) — hepatotoxicity signal
alt_data = lb[lb['LBTESTCD'] == 'ALT']
for idx, row in alt_data.iterrows():
    if pd.notna(row['LBSTRESN']):
        val = float(row['LBSTRESN'])
        if val > 120:
            add_query('LB', row['USUBJID'], 'ALT', 'EC-LB-002', 'SOFT',
                      f"ALT value {val} U/L exceeds 3x ULN (>120 U/L) "
                      f"at {row['VISIT']}. Potential Hy's Law signal. "
                      f"Medical monitor review recommended.")

lb_queries = query_id - lb_start
print(f"  LB checks complete: {lb_queries} queries generated")

# ============================================================
# CM DOMAIN CHECKS
# ============================================================
print("\n" + "-" * 40)
print("Running CM Domain Checks...")
print("-" * 40)
cm_start = query_id

# EC-CM-001: Med end date >= start date
for idx, row in cm.iterrows():
    try:
        end_str = str(row['CMENDTC']).strip()
        if end_str and end_str != '' and end_str != 'nan':
            start_dt = datetime.strptime(str(row['CMSTDTC']), '%Y-%m-%d')
            end_dt = datetime.strptime(end_str, '%Y-%m-%d')
            if end_dt < start_dt:
                add_query('CM', row['USUBJID'], 'CMENDTC', 'EC-CM-001', 'HARD',
                          f"Medication end date ({row['CMENDTC']}) is before "
                          f"start date ({row['CMSTDTC']}) for {row['CMTRT']}. "
                          f"Please correct.")
    except (ValueError, TypeError):
        pass

# EC-CM-002: Missing dose
for idx, row in cm.iterrows():
    if pd.isna(row['CMDOSE']):
        add_query('CM', row['USUBJID'], 'CMDOSE', 'EC-CM-002', 'HARD',
                  f"Dose is missing for {row['CMTRT']}. Required per "
                  f"protocol medication logging guidelines.")

cm_queries = query_id - cm_start
print(f"  CM checks complete: {cm_queries} queries generated")

# ============================================================
# BUILD DISCREPANCY DATABASE
# ============================================================
print("\n" + "=" * 60)
print("BUILDING DISCREPANCY DATABASE")
print("=" * 60)

disc_db = pd.DataFrame(discrepancies)

# Simulate partial query resolution (40% resolved)
n_resolved = int(len(disc_db) * 0.4)
resolved_idx = disc_db.sample(n=n_resolved, random_state=42).index

for idx in resolved_idx:
    disc_db.loc[idx, 'STATUS'] = 'CLOSED'
    disc_db.loc[idx, 'CLOSED_DATE'] = datetime.now().strftime('%Y-%m-%d')
    if disc_db.loc[idx, 'SEVERITY'] == 'HARD':
        disc_db.loc[idx, 'SITE_RESPONSE'] = \
            'Data corrected per source document review.'
        disc_db.loc[idx, 'RESOLUTION'] = 'DATA CORRECTED'
    else:
        disc_db.loc[idx, 'SITE_RESPONSE'] = \
            'Confirmed as entered. Verified against source document.'
        disc_db.loc[idx, 'RESOLUTION'] = 'CONFIRMED CORRECT'

# Save
os.makedirs('outputs', exist_ok=True)
disc_db.to_csv('outputs/discrepancy_database.csv', index=False)

# ============================================================
# QC SUMMARY REPORT
# ============================================================
total = len(disc_db)
hard = len(disc_db[disc_db['SEVERITY'] == 'HARD'])
soft = len(disc_db[disc_db['SEVERITY'] == 'SOFT'])
open_q = len(disc_db[disc_db['STATUS'] == 'OPEN'])
closed = len(disc_db[disc_db['STATUS'] == 'CLOSED'])

print(f"\n{'='*60}")
print(f"QC SUMMARY REPORT — Study XYZ-2026")
print(f"{'='*60}")
print(f"")
print(f"  Total queries generated:    {total}")
print(f"  ┌─ HARD (must fix):         {hard}")
print(f"  └─ SOFT (review):           {soft}")
print(f"")
print(f"  Query Status:")
print(f"  ┌─ OPEN:                    {open_q} ({open_q/total*100:.1f}%)")
print(f"  └─ CLOSED:                  {closed} ({closed/total*100:.1f}%)")
print(f"")

# By domain
print(f"  Queries by Domain:")
domain_counts = disc_db['DOMAIN'].value_counts()
for domain, count in domain_counts.items():
    bar = '█' * (count // 2) + '░' * ((max(domain_counts) // 2) - (count // 2))
    print(f"    {domain:4s}  {bar}  {count}")

print(f"")

# By check ID (top 10)
print(f"  Top 10 Failing Edit Checks:")
top_checks = disc_db['CHECK_ID'].value_counts().head(10)
for check, count in top_checks.items():
    print(f"    {check:12s}  {'█' * count} {count}")

# By site
print(f"\n  Queries by Site:")
disc_db['SITE'] = disc_db['USUBJID'].apply(
    lambda x: x.split('-')[2] if len(str(x).split('-')) >= 3 else 'UNK')
site_counts = disc_db.groupby('SITE').agg(
    Total=('QUERY_ID', 'count'),
    Open=('STATUS', lambda x: (x == 'OPEN').sum()),
    Closed=('STATUS', lambda x: (x == 'CLOSED').sum())
).reset_index()
site_counts['Open_Rate'] = (site_counts['Open'] / site_counts['Total'] * 100).round(1)

print(f"    {'Site':<6} {'Total':<8} {'Open':<8} {'Closed':<8} {'Open%':<8}")
print(f"    {'─'*6} {'─'*7} {'─'*7} {'─'*7} {'─'*7}")
for _, row in site_counts.iterrows():
    flag = ' ⚠️' if row['Open_Rate'] > 70 else ''
    print(f"    {row['SITE']:<6} {int(row['Total']):<8} {int(row['Open']):<8} "
          f"{int(row['Closed']):<8} {row['Open_Rate']:<7}%{flag}")

# Save summary
summary = disc_db.groupby(['DOMAIN', 'CHECK_ID', 'SEVERITY']).agg(
    Total_Queries=('QUERY_ID', 'count'),
    Open=('STATUS', lambda x: (x == 'OPEN').sum()),
    Closed=('STATUS', lambda x: (x == 'CLOSED').sum())
).reset_index()
summary.to_csv('outputs/qc_summary_report.csv', index=False)
site_counts.to_csv('outputs/site_query_summary.csv', index=False)

print(f"\n{'='*60}")
print(f"FILES SAVED:")
print(f"  ✅ outputs/discrepancy_database.csv  ({total} queries)")
print(f"  ✅ outputs/qc_summary_report.csv")
print(f"  ✅ outputs/site_query_summary.csv")
print(f"{'='*60}")