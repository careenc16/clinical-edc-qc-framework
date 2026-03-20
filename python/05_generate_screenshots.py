"""
============================================================
05_generate_screenshots.py
Purpose: Generate eCRF mockup visuals and QC summary graphics
         for GitHub README screenshots
Study:   XYZ-2026
Author:  Careen Chowrappa
============================================================
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import numpy as np

# ============================================================
# 1. DEMOGRAPHICS eCRF MOCKUP
# ============================================================
print("Generating Demographics eCRF mockup...")

fig, ax = plt.subplots(1, 1, figsize=(11, 13))
ax.set_xlim(0, 11)
ax.set_ylim(0, 16)
ax.axis('off')
fig.patch.set_facecolor('white')

# Header bar
ax.add_patch(patches.FancyBboxPatch((0.3, 14.5), 10.4, 1.2,
             boxstyle="round,pad=0.1", facecolor='#1a5276', edgecolor='none'))
ax.text(5.5, 15.1, 'STUDY XYZ-2026 — DEMOGRAPHICS (DM)', fontsize=15,
        ha='center', va='center', color='white', fontweight='bold')
ax.text(5.5, 14.7, 'Phase II Randomized Double-Blind Placebo-Controlled | Type 2 Diabetes',
        fontsize=8, ha='center', va='center', color='#aed6f1')

# Sub-header
ax.add_patch(patches.FancyBboxPatch((0.3, 13.8), 10.4, 0.5,
             boxstyle="round,pad=0.05", facecolor='#eaf2f8', edgecolor='#aed6f1'))
ax.text(0.6, 14.05, 'Visit: SCREENING    |    Form Status: INCOMPLETE    |    '
        'Queries: 2 OPEN', fontsize=8, va='center', color='#1a5276')

fields = [
    ('Subject ID *', 'XYZ-2026-003-0042', 'Text', 'Auto-generated at enrollment'),
    ('Site Number *', '003 — Lakeside Clinical Research', 'Coded', 'Select from list'),
    ('Informed Consent Date *', '2026-02-18', 'Date', 'YYYY-MM-DD | Must be ≤ today'),
    ('Date of Birth *', '1962-07-14', 'Date', 'YYYY-MM-DD'),
    ('Age at Consent *', '63', 'Integer', 'Range: 18-75 | Auto-checked vs DOB'),
    ('Sex *', '● Male  ○ Female', 'Coded', 'Required | M or F only'),
    ('Race *', '☑ White  ☐ Black or African American  ☐ Asian  ☐ Other', 'Coded',
     'Select all that apply'),
    ('Ethnicity *', '○ Hispanic or Latino  ● Not Hispanic or Latino', 'Coded',
     'Required'),
    ('Treatment Arm *', '[ BLINDED — Assigned by IXRS ]', 'Coded',
     'Auto-populated at randomization'),
    ('Date of First Study Drug *', '2026-03-01', 'Date',
     'Must be ≥ Consent Date'),
    ('Date of Last Study Drug', '', 'Date', 'Required at End of Study'),
    ('Death Flag', '○ Yes  ● No', 'Coded', 'If Yes → death date required'),
]

y = 13.2
for label, value, dtype, hint in fields:
    # Label
    ax.text(0.5, y, label, fontsize=9, va='center', fontweight='bold',
            color='#1a5276')
    # Input box
    box_color = '#fef9e7' if value == '' else '#f0f9f0'
    border_color = '#e74c3c' if value == '' else '#bdc3c7'
    ax.add_patch(patches.FancyBboxPatch((4.8, y - 0.22), 5.7, 0.44,
                 boxstyle="round,pad=0.05", facecolor=box_color,
                 edgecolor=border_color, linewidth=1))
    ax.text(5.0, y, value if value else '— required —',
            fontsize=8, va='center',
            color='#2c3e50' if value else '#e74c3c',
            style='italic' if not value else 'normal')
    # Data type badge
    type_colors = {'Text': '#3498db', 'Coded': '#9b59b6',
                   'Date': '#e67e22', 'Integer': '#27ae60'}
    ax.add_patch(patches.FancyBboxPatch((10.55, y - 0.12), 0.5, 0.24,
                 boxstyle="round,pad=0.03",
                 facecolor=type_colors.get(dtype, '#95a5a6'),
                 edgecolor='none'))
    # Hint text
    ax.text(0.5, y - 0.35, hint, fontsize=6, va='center', color='#7f8c8d',
            style='italic')
    y -= 0.95

# Footer
ax.add_patch(patches.FancyBboxPatch((0.3, 0.3), 10.4, 1.0,
             boxstyle="round,pad=0.1", facecolor='#fef9e7', edgecolor='#f39c12'))
ax.text(0.6, 1.0, '⚠ EDIT CHECKS ACTIVE:', fontsize=8, fontweight='bold',
        color='#e67e22')
ax.text(0.6, 0.7, 'EC-DM-001: Age 18-75  |  EC-DM-002: Dose ≥ Consent  |  '
        'EC-DM-004: Age = DOB calc  |  EC-DM-005: ID format  |  EC-DM-006: Required fields',
        fontsize=7, color='#7f8c8d')

ax.text(5.5, 0.05, '* = Required field  |  Study XYZ-2026  |  '
        'eCRF v1.0  |  Careen Chowrappa, QC Specialist',
        fontsize=7, ha='center', color='#bdc3c7')

plt.savefig('screenshots/demographics_ecrf.png', dpi=150, bbox_inches='tight',
            facecolor='white')
plt.close()
print("  ✅ screenshots/demographics_ecrf.png")


# ============================================================
# 2. ADVERSE EVENTS eCRF MOCKUP
# ============================================================
print("Generating Adverse Events eCRF mockup...")

fig, ax = plt.subplots(1, 1, figsize=(11, 11))
ax.set_xlim(0, 11)
ax.set_ylim(0, 13.5)
ax.axis('off')
fig.patch.set_facecolor('white')

# Header
ax.add_patch(patches.FancyBboxPatch((0.3, 12.2), 10.4, 1.0,
             boxstyle="round,pad=0.1", facecolor='#922b21', edgecolor='none'))
ax.text(5.5, 12.7, 'STUDY XYZ-2026 — ADVERSE EVENTS (AE)', fontsize=15,
        ha='center', va='center', color='white', fontweight='bold')
ax.text(5.5, 12.35, 'AE Sequence #3  |  Subject: XYZ-2026-003-0042',
        fontsize=8, ha='center', va='center', color='#f5b7b1')

ae_fields = [
    ('Reported Term (Verbatim) *', 'Nausea', ''),
    ('MedDRA Coded Term *', 'Nausea (PT)', 'MedDRA v27.0 — auto-coded'),
    ('System Organ Class', 'Gastrointestinal disorders', 'Auto-populated from MedDRA'),
    ('Start Date *', '2026-03-15', 'Must be ≥ consent date (2026-02-18)'),
    ('End Date', '2026-03-22', 'Required if Outcome = Recovered'),
    ('Severity *', '● Mild  ○ Moderate  ○ Severe', 'If Severe → verify Serious'),
    ('Serious? *', '○ Yes  ● No', 'ICH E2A criteria: death, hospitalization, disability'),
    ('Causality *', '○ Not Related  ● Possible  ○ Probable  ○ Definite',
     'Investigator assessment'),
    ('Outcome *', '● Recovered  ○ Recovering  ○ Not Recovered  ○ Fatal',
     'If Fatal → update DM death flag'),
    ('Action Taken *', '● None  ○ Dose Reduced  ○ Drug Interrupted  ○ Withdrawn',
     'Action with study drug'),
]

y = 11.5
for label, value, hint in ae_fields:
    ax.text(0.5, y, label, fontsize=9, va='center', fontweight='bold', color='#922b21')
    ax.add_patch(patches.FancyBboxPatch((4.8, y - 0.2), 5.7, 0.4,
                 boxstyle="round,pad=0.05", facecolor='#fdedec',
                 edgecolor='#d5a6a6', linewidth=1))
    ax.text(5.0, y, value, fontsize=8, va='center', color='#2c3e50')
    if hint:
        ax.text(0.5, y - 0.35, hint, fontsize=6, va='center',
                color='#7f8c8d', style='italic')
    y -= 0.88

# Edit checks footer
ax.add_patch(patches.FancyBboxPatch((0.3, 0.3), 10.4, 0.8,
             boxstyle="round,pad=0.1", facecolor='#fdedec', edgecolor='#e74c3c'))
ax.text(0.6, 0.85, '⚠ EDIT CHECKS ACTIVE:', fontsize=8, fontweight='bold',
        color='#c0392b')
ax.text(0.6, 0.55, 'EC-AE-001: Start ≥ Consent  |  EC-AE-002: End ≥ Start  |  '
        'EC-AE-003: Severe→Serious?  |  EC-AE-005: Coding complete  |  '
        'EC-AE-006: Valid severity',
        fontsize=7, color='#7f8c8d')

plt.savefig('screenshots/adverse_events_ecrf.png', dpi=150, bbox_inches='tight',
            facecolor='white')
plt.close()
print("  ✅ screenshots/adverse_events_ecrf.png")


# ============================================================
# 3. EDIT CHECK SUMMARY INFOGRAPHIC
# ============================================================
print("Generating Edit Check summary infographic...")

fig, ax = plt.subplots(1, 1, figsize=(12, 6))
ax.axis('off')
fig.patch.set_facecolor('white')

# Title
ax.text(0.5, 0.95, 'EDIT CHECK FRAMEWORK — 20 Checks Across 5 Domains',
        fontsize=16, fontweight='bold', ha='center', va='center',
        transform=ax.transAxes, color='#1a5276')

domains = [
    ('DM', 6, '#3498db', 'Demographics'),
    ('AE', 6, '#e74c3c', 'Adverse Events'),
    ('VS', 6, '#2ecc71', 'Vital Signs'),
    ('LB', 2, '#f39c12', 'Laboratory'),
]

x_start = 0.08
for code, count, color, name in domains:
    ax.add_patch(patches.FancyBboxPatch((x_start, 0.25), 0.18, 0.55,
                 boxstyle="round,pad=0.02", facecolor=color, alpha=0.15,
                 edgecolor=color, linewidth=2, transform=ax.transAxes))
    ax.text(x_start + 0.09, 0.7, code, fontsize=22, fontweight='bold',
            ha='center', va='center', transform=ax.transAxes, color=color)
    ax.text(x_start + 0.09, 0.55, name, fontsize=8, ha='center',
            va='center', transform=ax.transAxes, color='#2c3e50')
    ax.text(x_start + 0.09, 0.38, f'{count} checks', fontsize=11,
            fontweight='bold', ha='center', va='center',
            transform=ax.transAxes, color=color)
    x_start += 0.22

# Stats bar at bottom
ax.add_patch(patches.FancyBboxPatch((0.05, 0.05), 0.9, 0.12,
             boxstyle="round,pad=0.02", facecolor='#eaf2f8',
             edgecolor='#aed6f1', transform=ax.transAxes))
ax.text(0.5, 0.11, '16 HARD Checks (must fix)  |  4 SOFT Checks (review)  |  '
        '84 Queries Generated  |  14,329 Records Tested  |  100% Detection Rate',
        fontsize=9, ha='center', va='center', transform=ax.transAxes,
        color='#1a5276', fontweight='bold')

plt.savefig('screenshots/edit_check_summary.png', dpi=150, bbox_inches='tight',
            facecolor='white')
plt.close()
print("  ✅ screenshots/edit_check_summary.png")


# ============================================================
# 4. QUERY LIFECYCLE FLOW DIAGRAM
# ============================================================
print("Generating Query Lifecycle diagram...")

fig, ax = plt.subplots(1, 1, figsize=(12, 4))
ax.set_xlim(0, 12)
ax.set_ylim(0, 4)
ax.axis('off')
fig.patch.set_facecolor('white')

ax.text(6, 3.7, 'QUERY LIFECYCLE — Discrepancy Management Workflow',
        fontsize=14, fontweight='bold', ha='center', color='#1a5276')

stages = [
    (1.0, 'ERROR\nDETECTED', '#e74c3c', 'QC Engine\nflags issue'),
    (3.5, 'QUERY\nOPENED', '#f39c12', 'Auto-generated\nwith query text'),
    (6.0, 'SITE\nRESPONDS', '#3498db', 'Reviews source\ndocuments'),
    (8.5, 'RESOLUTION', '#9b59b6', 'Corrected or\nConfirmed'),
    (11.0, 'QUERY\nCLOSED', '#27ae60', 'Ready for\nDB lock'),
]

for x, label, color, desc in stages:
    # Circle
    circle = plt.Circle((x, 2.2), 0.6, facecolor=color, edgecolor='white',
                        linewidth=2, alpha=0.9)
    ax.add_patch(circle)
    ax.text(x, 2.2, label, fontsize=8, fontweight='bold', ha='center',
            va='center', color='white')
    ax.text(x, 1.2, desc, fontsize=7, ha='center', va='center', color='#7f8c8d')

# Arrows
for i in range(len(stages) - 1):
    x1 = stages[i][0] + 0.7
    x2 = stages[i + 1][0] - 0.7
    ax.annotate('', xy=(x2, 2.2), xytext=(x1, 2.2),
                arrowprops=dict(arrowstyle='->', color='#bdc3c7', lw=2))

# Stats
ax.text(6, 0.4, '84 Queries  →  33 Closed (39.3%)  |  21 Answered (25.0%)  |  '
        '30 Open (35.7%)  |  42 HARD Unresolved',
        fontsize=8, ha='center', color='#1a5276', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#eaf2f8',
                  edgecolor='#aed6f1'))

plt.savefig('screenshots/query_lifecycle.png', dpi=150, bbox_inches='tight',
            facecolor='white')
plt.close()
print("  ✅ screenshots/query_lifecycle.png")


# ============================================================
# 5. PRE-LOCK READINESS VISUAL
# ============================================================
print("Generating Pre-Lock Readiness visual...")

fig, ax = plt.subplots(1, 1, figsize=(8, 5))
ax.axis('off')
fig.patch.set_facecolor('white')

ax.text(0.5, 0.95, 'PRE-DATABASE LOCK READINESS ASSESSMENT',
        fontsize=14, fontweight='bold', ha='center', transform=ax.transAxes,
        color='#1a5276')
ax.text(0.5, 0.88, 'Study XYZ-2026  |  Assessment Date: March 2026',
        fontsize=9, ha='center', transform=ax.transAxes, color='#7f8c8d')

criteria = [
    ('All HARD queries resolved', False, '42 unresolved'),
    ('Overall closure rate ≥ 90%', False, '39.3% (target: 90%)'),
    ('No site with >70% open rate', False, 'Sites 002, 005 flagged'),
    ('All SAE queries resolved', True, 'Confirmed'),
]

y = 0.72
for criterion, passed, detail in criteria:
    icon = '✅' if passed else '❌'
    color = '#27ae60' if passed else '#e74c3c'
    bg = '#eafaf1' if passed else '#fdedec'

    ax.add_patch(patches.FancyBboxPatch((0.05, y - 0.04), 0.9, 0.1,
                 boxstyle="round,pad=0.02", facecolor=bg, edgecolor=color,
                 linewidth=1, transform=ax.transAxes))
    ax.text(0.08, y + 0.01, f'{icon}  {criterion}', fontsize=10,
            va='center', transform=ax.transAxes, color='#2c3e50',
            fontweight='bold')
    ax.text(0.92, y + 0.01, detail, fontsize=8, va='center', ha='right',
            transform=ax.transAxes, color=color)
    y -= 0.14

# Verdict
ax.add_patch(patches.FancyBboxPatch((0.15, 0.08), 0.7, 0.12,
             boxstyle="round,pad=0.02", facecolor='#e74c3c',
             edgecolor='none', transform=ax.transAxes))
ax.text(0.5, 0.14, '❌  DATABASE IS NOT READY FOR LOCK', fontsize=13,
        fontweight='bold', ha='center', va='center', transform=ax.transAxes,
        color='white')

plt.savefig('screenshots/lock_readiness.png', dpi=150, bbox_inches='tight',
            facecolor='white')
plt.close()
print("  ✅ screenshots/lock_readiness.png")

print("\n✅ All screenshots generated in screenshots/ folder")