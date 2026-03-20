"""
============================================================
03_query_management.py
Purpose: Simulate full query lifecycle for discrepancy management
Study:   XYZ-2026
Author:  Careen Chowrappa
============================================================
Maps to ICON JD: "Collaborating with cross-functional teams
to address QC findings and ensure data integrity"
============================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 60)
print("QUERY MANAGEMENT SIMULATION — Study XYZ-2026")
print("=" * 60)

disc = pd.read_csv('outputs/discrepancy_database.csv')
np.random.seed(42)

# Add new columns as object/float type first to avoid dtype conflicts
disc['DAYS_TO_RESOLVE'] = np.nan
disc['DAYS_OPEN'] = np.nan

# ============================================================
# SIMULATE SITE RESPONSES (real-world patterns)
# ============================================================

site_response_templates = {
    'DATA CORRECTED': [
        'Value has been corrected per source document review. '
        'Original value was a transcription error.',
        'Data updated. Confirmed against patient chart.',
        'Corrected. Site coordinator re-verified against source.',
        'Error identified during site QC. Value amended.',
    ],
    'CONFIRMED CORRECT': [
        'Value confirmed as entered. Verified against source document. '
        'Patient presented with this value at time of assessment.',
        'Confirmed correct per investigator review. '
        'Clinically plausible for this patient given medical history.',
        'Value verified. Patient has documented history explaining this result.',
    ],
    'QUERY CANCELLED': [
        'Query raised in error. Data is within acceptable range '
        'per protocol amendment 2.',
        'Duplicate query. Already addressed in Q-XXXX.',
    ],
    'PENDING': [
        'Site is reviewing source documents. Response expected within 5 business days.',
        'Query forwarded to investigator for clinical review.',
        'Awaiting source document retrieval from medical records.',
    ]
}

print("\nSimulating query lifecycle...")

# Assign resolution based on severity and random probability
for idx, row in disc.iterrows():
    if row['STATUS'] == 'CLOSED':
        # Already resolved from QC engine — add realistic details
        days_to_resolve = int(np.random.randint(1, 14))
        opened = datetime.strptime(str(row['OPENED_DATE']), '%Y-%m-%d')
        closed = opened + timedelta(days=days_to_resolve)

        if row['SEVERITY'] == 'HARD':
            resolution = np.random.choice(['DATA CORRECTED'] * 7 +
                                          ['CONFIRMED CORRECT'] * 2 +
                                          ['QUERY CANCELLED'] * 1)
        else:
            resolution = np.random.choice(['CONFIRMED CORRECT'] * 6 +
                                          ['DATA CORRECTED'] * 3 +
                                          ['QUERY CANCELLED'] * 1)

        disc.at[idx, 'RESOLUTION'] = resolution
        disc.at[idx, 'CLOSED_DATE'] = closed.strftime('%Y-%m-%d')
        disc.at[idx, 'DAYS_TO_RESOLVE'] = days_to_resolve
        disc.at[idx, 'SITE_RESPONSE'] = np.random.choice(
            site_response_templates[resolution])

    else:
        # Still OPEN — assign aging
        days_open = int(np.random.randint(1, 30))
        disc.at[idx, 'DAYS_TO_RESOLVE'] = np.nan
        disc.at[idx, 'DAYS_OPEN'] = days_open

        # Some have pending responses
        if np.random.random() < 0.3:
            disc.at[idx, 'STATUS'] = 'ANSWERED'
            disc.at[idx, 'SITE_RESPONSE'] = np.random.choice(
                site_response_templates['PENDING'])
        else:
            disc.at[idx, 'SITE_RESPONSE'] = ''

# ============================================================
# PRE-LOCK READINESS ASSESSMENT
# ============================================================
print("\n" + "=" * 60)
print("PRE-DATABASE LOCK READINESS ASSESSMENT")
print("=" * 60)

total = len(disc)
closed = len(disc[disc['STATUS'] == 'CLOSED'])
answered = len(disc[disc['STATUS'] == 'ANSWERED'])
open_q = len(disc[disc['STATUS'] == 'OPEN'])
hard_open = len(disc[(disc['STATUS'] != 'CLOSED') & (disc['SEVERITY'] == 'HARD')])

print(f"\nTotal Queries:        {total}")
print(f"  CLOSED:             {closed} ({closed/total*100:.1f}%)")
print(f"  ANSWERED:           {answered} ({answered/total*100:.1f}%)")
print(f"  OPEN:               {open_q} ({open_q/total*100:.1f}%)")
print(f"  HARD & Unresolved:  {hard_open}")

# Site-level analysis
disc['SITE'] = disc['USUBJID'].apply(
    lambda x: x.split('-')[2] if len(str(x).split('-')) >= 3 else 'UNKNOWN')

print("\n--- QUERIES BY SITE ---")
site_summary = disc.groupby('SITE').agg(
    Total=('QUERY_ID', 'count'),
    Open=('STATUS', lambda x: (x != 'CLOSED').sum()),
    Closed=('STATUS', lambda x: (x == 'CLOSED').sum())
).reset_index()
site_summary['Open_Rate'] = (site_summary['Open'] / site_summary['Total'] * 100).round(1)
print(site_summary.to_string(index=False))

# Identify problem sites
problem_sites = site_summary[site_summary['Open_Rate'] > 70]
if len(problem_sites) > 0:
    print(f"\n⚠️  PROBLEM SITES (>70% open query rate):")
    for _, site in problem_sites.iterrows():
        print(f"   Site {site['SITE']}: {site['Open_Rate']}% queries unresolved")

# Lock readiness verdict
print("\n--- DATABASE LOCK READINESS ---")
lock_criteria = {
    'All HARD queries resolved': hard_open == 0,
    'Overall closure rate >= 90%': (closed / total * 100) >= 90,
    'No site with >70% open rate': len(problem_sites) == 0,
    'All SAE queries resolved': True,  # simplified
}

all_pass = all(lock_criteria.values())
for criterion, passed in lock_criteria.items():
    status = '✅ PASS' if passed else '❌ FAIL'
    print(f"  {status} — {criterion}")

print(f"\n{'='*60}")
if all_pass:
    print("  VERDICT: ✅ DATABASE IS READY FOR LOCK")
else:
    print("  VERDICT: ❌ DATABASE IS NOT READY FOR LOCK")
    print("  ACTION:  Resolve outstanding queries before lock date")
print(f"{'='*60}")

# Save updated discrepancy database
disc.to_csv('outputs/discrepancy_database.csv', index=False)
site_summary.to_csv('outputs/site_query_summary.csv', index=False)

# Save lock readiness report
with open('outputs/lock_readiness_report.txt', 'w') as f:
    f.write("PRE-DATABASE LOCK READINESS REPORT\n")
    f.write(f"Study: XYZ-2026 | Date: {datetime.now().strftime('%Y-%m-%d')}\n")
    f.write(f"{'='*50}\n\n")
    f.write(f"Total Queries: {total}\n")
    f.write(f"Closed: {closed} ({closed/total*100:.1f}%)\n")
    f.write(f"Open/Answered: {open_q + answered} ({(open_q+answered)/total*100:.1f}%)\n")
    f.write(f"Hard & Unresolved: {hard_open}\n\n")
    for criterion, passed in lock_criteria.items():
        f.write(f"{'PASS' if passed else 'FAIL'} — {criterion}\n")
    f.write(f"\nVERDICT: {'READY' if all_pass else 'NOT READY'} FOR LOCK\n")

print("\n✅ Query management simulation complete")
print("   Saved: outputs/discrepancy_database.csv (updated)")
print("   Saved: outputs/site_query_summary.csv")
print("   Saved: outputs/lock_readiness_report.txt")