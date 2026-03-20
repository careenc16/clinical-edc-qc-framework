/************************************************************
* Program:  01_qc_cross_validation.sas
* Purpose:  Cross-validate Python QC engine findings using SAS
* Study:    XYZ-2026 Phase II Diabetes Trial
* Author:   Careen Chowrappa
* Date:     March 2026

************************************************************/

options nocenter linesize=120 pagesize=60;
title1 "Study XYZ-2026 — SAS Cross-Validation of Python QC Findings";
title2 "Configuration & QC Specialist: Careen Chowrappa";
footnote "Generated: &sysdate | SAS &sysver | Cross-validation against Python QC Engine";

/*----------------------------------------------------------
  STEP 1: IMPORT ALL CSV DATA FILES
----------------------------------------------------------*/

%let datapath = /home/&sysuserid/clinical-edc-qc-framework/data;

proc import datafile="&datapath/dm_test_data.csv"
    out=dm dbms=csv replace;
    guessingrows=max;
run;

proc import datafile="&datapath/ae_test_data.csv"
    out=ae dbms=csv replace;
    guessingrows=max;
run;

proc import datafile="&datapath/vs_test_data.csv"
    out=vs dbms=csv replace;
    guessingrows=max;
run;

proc import datafile="&datapath/lb_test_data.csv"
    out=lb dbms=csv replace;
    guessingrows=max;
run;

proc import datafile="&datapath/cm_test_data.csv"
    out=cm dbms=csv replace;
    guessingrows=max;
run;

/* Verify data loaded correctly */
title3 "Data Load Verification";
proc sql;
    select 'DM' as Domain, count(*) as Records from dm
    union all
    select 'AE', count(*) from ae
    union all
    select 'VS', count(*) from vs
    union all
    select 'LB', count(*) from lb
    union all
    select 'CM', count(*) from cm;
quit;


/*==========================================================
  STEP 2: DM DOMAIN EDIT CHECKS
==========================================================*/
title2 "DM DOMAIN EDIT CHECKS";

/* EC-DM-001: Age outside protocol range (18-75) */
title3 "EC-DM-001: Age Outside Protocol Range (18-75)";
proc sql;
    select USUBJID, SITEID, AGE,
           'HARD' as Severity,
           'Age outside protocol range' as Finding
    from dm
    where AGE is not missing and (AGE < 18 or AGE > 75);
quit;

proc sql noprint;
    select count(*) into :dm001_count
    from dm
    where AGE is not missing and (AGE < 18 or AGE > 75);
quit;
%put NOTE: EC-DM-001 findings: &dm001_count;


/* EC-DM-002: First dose before consent */
title3 "EC-DM-002: First Dose Date Before Informed Consent";
data dm_dates;
    set dm;
    consent_dt = input(RFICDTC, yymmdd10.);
    dose_dt = input(RFSTDTC, yymmdd10.);
    format consent_dt dose_dt yymmdd10.;
    if dose_dt < consent_dt then output;
run;

proc print data=dm_dates noobs label;
    var USUBJID SITEID RFICDTC RFSTDTC;
    label RFICDTC = 'Consent Date'
          RFSTDTC = 'First Dose Date';
run;

proc sql noprint;
    select count(*) into :dm002_count from dm_dates;
quit;
%put NOTE: EC-DM-002 findings: &dm002_count;


/* EC-DM-003: Invalid sex values */
title3 "EC-DM-003: Invalid Sex Values (not M or F)";
proc sql;
    select USUBJID, SEX,
           'HARD' as Severity
    from dm
    where SEX is not missing
      and SEX not in ('M', 'F');
quit;

proc sql noprint;
    select count(*) into :dm003_count
    from dm
    where SEX is not missing and SEX not in ('M', 'F');
quit;
%put NOTE: EC-DM-003 findings: &dm003_count;


/* EC-DM-004: Age does not match DOB calculation */
title3 "EC-DM-004: Reported Age Does Not Match Calculated Age from DOB";
data dm_age_check;
    set dm;
    dob_dt = input(BRTHDTC, yymmdd10.);
    consent_dt = input(RFICDTC, yymmdd10.);
    calc_age = intck('year', dob_dt, consent_dt);
    age_diff = abs(AGE - calc_age);
    if AGE is not missing and age_diff > 1 then output;
    format dob_dt consent_dt yymmdd10.;
run;

proc print data=dm_age_check noobs;
    var USUBJID AGE calc_age age_diff;
    title4 "Subjects with age discrepancy > 1 year";
run;

proc sql noprint;
    select count(*) into :dm004_count from dm_age_check;
quit;
%put NOTE: EC-DM-004 findings: &dm004_count;


/* EC-DM-005: Invalid Subject ID format */
title3 "EC-DM-005: Invalid Subject ID Format";
proc sql;
    select USUBJID,
           'HARD' as Severity,
           'ID format violation' as Finding
    from dm
    where not prxmatch('/^XYZ-2026-\d{3}-\d{4}$/', strip(USUBJID));
quit;

proc sql noprint;
    select count(*) into :dm005_count
    from dm
    where not prxmatch('/^XYZ-2026-\d{3}-\d{4}$/', strip(USUBJID));
quit;
%put NOTE: EC-DM-005 findings: &dm005_count;


/* EC-DM-006: Missing required DM fields */
title3 "EC-DM-006: Missing Required DM Fields";
proc sql;
    select USUBJID,
           case when AGE is missing then 'AGE' else '' end as Missing_AGE,
           case when SEX = '' or SEX is missing then 'SEX' else '' end as Missing_SEX,
           case when RACE = '' or RACE is missing then 'RACE' else '' end as Missing_RACE,
           case when ETHNIC = '' or ETHNIC is missing then 'ETHNIC' else '' end as Missing_ETHNIC,
           case when ARM = '' or ARM is missing then 'ARM' else '' end as Missing_ARM
    from dm
    where AGE is missing
       or SEX = '' or SEX is missing
       or RACE = '' or RACE is missing
       or ETHNIC = '' or ETHNIC is missing
       or ARM = '' or ARM is missing;
quit;

proc sql noprint;
    select count(*) into :dm006_count
    from dm
    where AGE is missing
       or SEX = '' or SEX is missing
       or RACE = '' or RACE is missing
       or ETHNIC = '' or ETHNIC is missing
       or ARM = '' or ARM is missing;
quit;
%put NOTE: EC-DM-006 findings: &dm006_count;


/*==========================================================
  STEP 3: AE DOMAIN EDIT CHECKS
==========================================================*/
title2 "AE DOMAIN EDIT CHECKS";

/* EC-AE-002: AE end date before start date */
title3 "EC-AE-002: AE End Date Before Start Date";
data ae_date_check;
    set ae;
    if AEENDTC ne '' then do;
        start_dt = input(AESTDTC, yymmdd10.);
        end_dt = input(AEENDTC, yymmdd10.);
        if end_dt < start_dt then output;
    end;
    format start_dt end_dt yymmdd10.;
run;

proc print data=ae_date_check noobs;
    var USUBJID AETERM AESTDTC AEENDTC;
run;

proc sql noprint;
    select count(*) into :ae002_count from ae_date_check;
quit;
%put NOTE: EC-AE-002 findings: &ae002_count;


/* EC-AE-003: SEVERE but not SERIOUS */
title3 "EC-AE-003: AE is SEVERE but Not Marked SERIOUS";
proc sql;
    select USUBJID, AETERM, AESEV, AESER
    from ae
    where strip(AESEV) = 'SEVERE' and strip(AESER) = 'N';
quit;

proc sql noprint;
    select count(*) into :ae003_count
    from ae where strip(AESEV) = 'SEVERE' and strip(AESER) = 'N';
quit;
%put NOTE: EC-AE-003 findings: &ae003_count;


/* EC-AE-005: Missing MedDRA coded term */
title3 "EC-AE-005: Verbatim Term Present but Coded Term Missing";
proc sql;
    select USUBJID, AETERM, AEDECOD
    from ae
    where strip(AETERM) ne ''
      and (AEDECOD = '' or AEDECOD is missing);
quit;

proc sql noprint;
    select count(*) into :ae005_count
    from ae
    where strip(AETERM) ne ''
      and (AEDECOD = '' or AEDECOD is missing);
quit;
%put NOTE: EC-AE-005 findings: &ae005_count;


/* EC-AE-006: Invalid severity value */
title3 "EC-AE-006: Invalid Severity Value";
proc sql;
    select USUBJID, AETERM, AESEV
    from ae
    where strip(AESEV) not in ('MILD', 'MODERATE', 'SEVERE')
      and AESEV is not missing
      and strip(AESEV) ne '';
quit;

proc sql noprint;
    select count(*) into :ae006_count
    from ae
    where strip(AESEV) not in ('MILD', 'MODERATE', 'SEVERE')
      and AESEV is not missing and strip(AESEV) ne '';
quit;
%put NOTE: EC-AE-006 findings: &ae006_count;


/*==========================================================
  STEP 4: VS DOMAIN EDIT CHECKS
==========================================================*/
title2 "VS DOMAIN EDIT CHECKS";

/* EC-VS-001: Systolic BP outside range */
title3 "EC-VS-001: Systolic BP Outside Range (70-250 mmHg)";
proc sql;
    select USUBJID, VISIT, SYSBP
    from vs
    where SYSBP is not missing and (SYSBP < 70 or SYSBP > 250);
quit;

proc sql noprint;
    select count(*) into :vs001_count
    from vs where SYSBP is not missing and (SYSBP < 70 or SYSBP > 250);
quit;
%put NOTE: EC-VS-001 findings: &vs001_count;


/* EC-VS-002: Diastolic BP outside range */
title3 "EC-VS-002: Diastolic BP Outside Range (40-150 mmHg)";
proc sql;
    select USUBJID, VISIT, DIABP
    from vs
    where DIABP is not missing and (DIABP < 40 or DIABP > 150);
quit;

proc sql noprint;
    select count(*) into :vs002_count
    from vs where DIABP is not missing and (DIABP < 40 or DIABP > 150);
quit;
%put NOTE: EC-VS-002 findings: &vs002_count;


/* EC-VS-003: Systolic <= Diastolic */
title3 "EC-VS-003: Systolic BP <= Diastolic BP";
proc sql;
    select USUBJID, VISIT, SYSBP, DIABP
    from vs
    where SYSBP is not missing
      and DIABP is not missing
      and SYSBP <= DIABP;
quit;

proc sql noprint;
    select count(*) into :vs003_count
    from vs
    where SYSBP is not missing and DIABP is not missing and SYSBP <= DIABP;
quit;
%put NOTE: EC-VS-003 findings: &vs003_count;


/* EC-VS-004: Heart rate outside range */
title3 "EC-VS-004: Heart Rate Outside Range (40-180 bpm)";
proc sql;
    select USUBJID, VISIT, PULSE
    from vs
    where PULSE is not missing and (PULSE < 40 or PULSE > 180);
quit;

proc sql noprint;
    select count(*) into :vs004_count
    from vs where PULSE is not missing and (PULSE < 40 or PULSE > 180);
quit;
%put NOTE: EC-VS-004 findings: &vs004_count;


/* EC-VS-005: Temperature outside range */
title3 "EC-VS-005: Temperature Outside Range (35.0-40.0 C)";
proc sql;
    select USUBJID, VISIT, TEMP
    from vs
    where TEMP is not missing and (TEMP < 35.0 or TEMP > 40.0);
quit;

proc sql noprint;
    select count(*) into :vs005_count
    from vs where TEMP is not missing and (TEMP < 35.0 or TEMP > 40.0);
quit;
%put NOTE: EC-VS-005 findings: &vs005_count;


/*==========================================================
  STEP 5: LB DOMAIN EDIT CHECKS
==========================================================*/
title2 "LB DOMAIN EDIT CHECKS";

/* EC-LB-001: HbA1c outside testable range */
title3 "EC-LB-001: HbA1c Outside Testable Range (3.0-20.0%)";
proc sql;
    select USUBJID, VISIT, LBSTRESN as HBA1C_VALUE, LBORRESU
    from lb
    where LBTESTCD = 'HBA1C'
      and LBSTRESN is not missing
      and (LBSTRESN < 3.0 or LBSTRESN > 20.0);
quit;

proc sql noprint;
    select count(*) into :lb001_count
    from lb
    where LBTESTCD = 'HBA1C' and LBSTRESN is not missing
      and (LBSTRESN < 3.0 or LBSTRESN > 20.0);
quit;
%put NOTE: EC-LB-001 findings: &lb001_count;


/* EC-LB-002: ALT > 3x ULN (hepatotoxicity signal) */
title3 "EC-LB-002: ALT > 3x ULN (>120 U/L) — Potential Hy's Law Signal";
proc sql;
    select USUBJID, VISIT, LBSTRESN as ALT_VALUE, LBORRESU
    from lb
    where LBTESTCD = 'ALT'
      and LBSTRESN is not missing
      and LBSTRESN > 120;
quit;

proc sql noprint;
    select count(*) into :lb002_count
    from lb where LBTESTCD = 'ALT' and LBSTRESN is not missing and LBSTRESN > 120;
quit;
%put NOTE: EC-LB-002 findings: &lb002_count;


/*==========================================================
  STEP 6: CM DOMAIN EDIT CHECKS
==========================================================*/
title2 "CM DOMAIN EDIT CHECKS";

/* EC-CM-001: Med end date before start date */
title3 "EC-CM-001: Medication End Date Before Start Date";
data cm_date_check;
    set cm;
    if CMENDTC ne '' then do;
        start_dt = input(CMSTDTC, yymmdd10.);
        end_dt = input(CMENDTC, yymmdd10.);
        if end_dt < start_dt then output;
    end;
    format start_dt end_dt yymmdd10.;
run;

proc print data=cm_date_check noobs;
    var USUBJID CMTRT CMSTDTC CMENDTC;
run;

proc sql noprint;
    select count(*) into :cm001_count from cm_date_check;
quit;
%put NOTE: EC-CM-001 findings: &cm001_count;


/*==========================================================
  STEP 7: CROSS-VALIDATION SUMMARY TABLE
  Compare SAS counts with Python QC engine counts
==========================================================*/
title2 "CROSS-VALIDATION SUMMARY: SAS vs Python QC Counts";

data xval_summary;
    length Check_ID $12 Domain $4 Description $60;
    infile datalines delimiter='|' truncover;
    input Check_ID $ Domain $ Description $ SAS_Count;
    datalines;
EC-DM-001|DM|Age outside protocol range (18-75)|&dm001_count
EC-DM-002|DM|First dose before consent|&dm002_count
EC-DM-003|DM|Invalid sex values|&dm003_count
EC-DM-004|DM|Age vs DOB mismatch|&dm004_count
EC-DM-005|DM|Invalid Subject ID format|&dm005_count
EC-DM-006|DM|Missing required DM fields|&dm006_count
EC-AE-002|AE|AE end date before start|&ae002_count
EC-AE-003|AE|SEVERE but not SERIOUS|&ae003_count
EC-AE-005|AE|Missing coded term|&ae005_count
EC-AE-006|AE|Invalid severity value|&ae006_count
EC-VS-001|VS|Systolic BP outside range|&vs001_count
EC-VS-002|VS|Diastolic BP outside range|&vs002_count
EC-VS-003|VS|Systolic <= Diastolic|&vs003_count
EC-VS-004|VS|Heart rate outside range|&vs004_count
EC-VS-005|VS|Temperature outside range|&vs005_count
EC-LB-001|LB|HbA1c outside range|&lb001_count
EC-LB-002|LB|ALT > 3x ULN|&lb002_count
EC-CM-001|CM|Med end before start|&cm001_count
;
run;

proc print data=xval_summary noobs label;
    var Check_ID Domain Description SAS_Count;
    label Check_ID = 'Edit Check'
          Domain = 'Domain'
          Description = 'Check Description'
          SAS_Count = 'SAS Count';
    title3 "Compare these counts with Python 02_qc_engine.py output";
    title4 "If all counts match = 100% cross-validation PASS";
run;


/*==========================================================
  STEP 8: DESCRIPTIVE STATISTICS (Bonus — shows SAS skills)
==========================================================*/
title2 "DESCRIPTIVE STATISTICS — Study XYZ-2026";

/* Demographics by Treatment Arm */
title3 "Table 14.1.1: Demographics Summary by Treatment Arm";
proc means data=dm n mean std min max maxdec=1;
    class ARM;
    var AGE;
run;

proc freq data=dm;
    tables ARM * SEX / nocol nopercent chisq;
    title3 "Sex Distribution by Treatment Arm";
run;

proc freq data=dm;
    tables ARM * RACE / nocol nopercent;
    title3 "Race Distribution by Treatment Arm";
run;

/* AE Summary */
title3 "Adverse Event Summary by Severity and Seriousness";
proc freq data=ae;
    tables AESEV * AESER / nocol nopercent;
run;

proc freq data=ae order=freq;
    tables AEBODSYS / nocum;
    title3 "AEs by System Organ Class (Frequency Order)";
run;

/* Vital Signs Summary */
title3 "Vital Signs Summary Statistics Across All Visits";
proc means data=vs n mean std min max maxdec=1;
    var SYSBP DIABP PULSE TEMP WEIGHT;
run;

/* Lab Summary — Key Diabetes Markers */
title3 "Laboratory: HbA1c and Glucose Summary by Visit";
proc means data=lb(where=(LBTESTCD in ('HBA1C', 'GLUC')))
    n mean std min max maxdec=2;
    class LBTESTCD VISIT;
    var LBSTRESN;
run;

/* Lab — ALT/AST for hepatotoxicity monitoring */
title3 "Laboratory: Liver Function (ALT/AST) Summary";
proc means data=lb(where=(LBTESTCD in ('ALT', 'AST')))
    n mean std min max maxdec=1;
    class LBTESTCD;
    var LBSTRESN;
run;

title;
footnote;
%put NOTE: ============================================;
%put NOTE: SAS CROSS-VALIDATION COMPLETE;
%put NOTE: Compare SAS counts with Python QC output;
%put NOTE: If all counts match = validation PASSED;
%put NOTE: ============================================;
