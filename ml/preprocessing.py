"""
EduGuard AI - Machine Learning Preprocessing Utilities
Handles feature mapping, column normalization, and input sanitization.
"""

import pandas as pd
import numpy as np

FEATURE_COLUMNS = ["attendance", "cgpa", "lms_activity", "fee_dues"]
RISK_CLASSES = ["Low Risk", "Medium Risk", "High Risk"]
CLASS_TO_INT = {"Low Risk": 0, "Medium Risk": 1, "High Risk": 2}
INT_TO_CLASS = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}

COLUMN_SYNONYMS = {
    "attendance": ["attendance", "attendance_rate", "attendance_percentage", "attendance_pct", "attend"],
    "cgpa": ["cgpa", "gpa", "grade", "academic_score"],
    "lms_activity": ["lms_activity", "lms_activity_score", "lms", "lms_score", "lms_engagement", "lms_pct"],
    "fee_dues": ["fee_dues", "dues", "pending_dues", "pending_fee", "fee_pending", "fees"]
}

def standardize_student_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes column names of an uploaded or raw dataframe to standard schema.
    Returns cleaned dataframe with expected column names.
    """
    df_clean = df.copy()
    col_mapping = {}
    
    # Lowercase and clean input column names for fuzzy mapping
    clean_orig_cols = {col: col.strip().lower().replace(" ", "_") for col in df_clean.columns}
    
    for std_col, synonyms in COLUMN_SYNONYMS.items():
        for orig_col, cleaned_name in clean_orig_cols.items():
            if cleaned_name in synonyms:
                col_mapping[orig_col] = std_col
                break
                
    # Also handle ID and Name
    for orig_col, cleaned_name in clean_orig_cols.items():
        if cleaned_name in ["student_id", "id", "roll_no", "reg_no"]:
            col_mapping[orig_col] = "student_id"
        elif cleaned_name in ["student_name", "name", "full_name"]:
            col_mapping[orig_col] = "student_name"
        elif cleaned_name in ["department", "dept", "branch", "stream"]:
            col_mapping[orig_col] = "department"
            
    df_clean = df_clean.rename(columns=col_mapping)
    
    # Ensure numerical types
    for col in FEATURE_COLUMNS:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            
    # Handle missing values with sensible medians
    defaults = {
        "attendance": 75.0,
        "cgpa": 7.0,
        "lms_activity": 65.0,
        "fee_dues": 0.0,
        "department": "General Engineering",
        "student_name": "Student Record"
    }
    
    for col, default_val in defaults.items():
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(default_val)
        else:
            df_clean[col] = default_val
            
    # Clip ranges
    df_clean["attendance"] = df_clean["attendance"].clip(0.0, 100.0)
    df_clean["cgpa"] = df_clean["cgpa"].clip(0.0, 10.0)
    df_clean["lms_activity"] = df_clean["lms_activity"].clip(0.0, 100.0)
    df_clean["fee_dues"] = df_clean["fee_dues"].apply(lambda x: max(0.0, float(x)))
    
    if "student_id" not in df_clean.columns:
        df_clean["student_id"] = [f"STU{2000 + i}" for i in range(len(df_clean))]
        
    return df_clean

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts exactly the feature matrix required for ML modeling."""
    std_df = standardize_student_dataframe(df)
    return std_df[FEATURE_COLUMNS]
