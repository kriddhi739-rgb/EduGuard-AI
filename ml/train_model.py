"""
EduGuard AI - Machine Learning Model Training Pipeline
Trains a Scikit-Learn Random Forest Classifier on realistic student data,
evaluates genuine performance metrics, saves model artifacts, and seeds database.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import joblib
from datetime import datetime

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.preprocessing import FEATURE_COLUMNS, RISK_CLASSES, CLASS_TO_INT, INT_TO_CLASS
from backend.database import get_connection, init_database

ARTIFACTS_PATH = os.path.join(BASE_DIR, "data", "model_artifacts.joblib")
LEGACY_MODEL_PATH = os.path.join(BASE_DIR, "dropout_model.pkl")
SAMPLE_CSV_PATH = os.path.join(BASE_DIR, "data", "sample_students.csv")

def generate_synthetic_training_data(n_samples: int = 1500, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates realistic synthetic student academic & financial records.
    Reflects educational attrition risk dynamics with natural statistical variance.
    """
    np.random.seed(random_seed)
    
    # 1. Base latent academic capability & engagement factor (z)
    z = np.random.normal(loc=0.0, scale=1.0, size=n_samples)
    
    # 2. Features influenced by academic engagement
    # Attendance: mean 76%, std 15%
    attendance = 76.0 + 13.0 * z + np.random.normal(0, 7.0, size=n_samples)
    attendance = np.clip(attendance, 15.0, 99.5).round(1)
    
    # CGPA: scale 0-10, strongly correlated with attendance & capability
    cgpa = 7.1 + 1.35 * z + 0.015 * (attendance - 76.0) + np.random.normal(0, 0.6, size=n_samples)
    cgpa = np.clip(cgpa, 2.2, 9.95).round(2)
    
    # LMS Activity Score: scale 0-100%
    lms_activity = 68.0 + 15.0 * z + np.random.normal(0, 10.0, size=n_samples)
    lms_activity = np.clip(lms_activity, 5.0, 100.0).round(1)
    
    # Fee Dues: Financial stress factor (currency amount)
    # Higher risk students have higher pending dues probability
    base_dues = np.random.exponential(scale=600.0, size=n_samples)
    financial_stress = np.where(z < -0.4, np.random.uniform(1500, 5500, size=n_samples), 0.0)
    fee_dues = np.where(np.random.rand(n_samples) < 0.35, base_dues + financial_stress, 0.0)
    fee_dues = np.clip(fee_dues, 0.0, 7500.0).round(0)
    
    # 3. Ground truth Risk Score calculation (Educational Risk Index)
    # Weights based on institutional dropout studies:
    # Attendance (< 65% critical, > 80% safe)
    att_risk = np.where(attendance < 60, 40, np.where(attendance < 75, 20, 5))
    # CGPA (< 5.5 critical, < 6.8 warning)
    cgpa_risk = np.where(cgpa < 5.2, 35, np.where(cgpa < 6.8, 18, 5))
    # LMS engagement (< 40 critical)
    lms_risk = np.where(lms_activity < 35, 20, np.where(lms_activity < 60, 10, 2))
    # Financial dues (> 2000 critical)
    fee_risk = np.where(fee_dues > 2500, 25, np.where(fee_dues > 800, 12, 0))
    
    # Continuous risk index + subtle noise
    risk_index = att_risk + cgpa_risk + lms_risk + fee_risk + np.random.normal(0, 6.0, size=n_samples)
    risk_index = np.clip(risk_index, 0, 100)
    
    # Discretize into 3 classes
    labels = []
    for score in risk_index:
        if score >= 55:
            labels.append("High Risk")
        elif score >= 28:
            labels.append("Medium Risk")
        else:
            labels.append("Low Risk")
            
    df = pd.DataFrame({
        "attendance": attendance,
        "cgpa": cgpa,
        "lms_activity": lms_activity,
        "fee_dues": fee_dues,
        "risk_level": labels,
        "risk_target": [CLASS_TO_INT[l] for l in labels]
    })
    
    return df

def train_and_evaluate_model():
    """Trains the Random Forest model and saves artifacts & metrics."""
    print("=" * 60)
    print("EduGuard AI: Training Random Forest Dropout Risk Model")
    print("=" * 60)
    
    # 1. Generate realistic dataset
    df = generate_synthetic_training_data(n_samples=1800, random_seed=42)
    print(f"Dataset generated: {len(df)} records.")
    print("Risk Level Breakdown:")
    print(df["risk_level"].value_counts())
    
    X = df[FEATURE_COLUMNS]
    y = df["risk_target"]
    
    # 2. Train-test split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    # 3. Train Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=160,
        max_depth=9,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    
    # 4. Genuine Model Evaluation
    y_pred = rf_model.predict(X_test)
    y_prob = rf_model.predict_proba(X_test)
    
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, average="weighted"))
    rec = float(recall_score(y_test, y_pred, average="weighted"))
    f1 = float(f1_score(y_test, y_pred, average="weighted"))
    
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, target_names=RISK_CLASSES, output_dict=True)
    
    feature_importances = {
        col: float(imp) for col, imp in zip(FEATURE_COLUMNS, rf_model.feature_importances_)
    }
    
    print("\n--- Genuine Test Set Evaluation ---")
    print(f"Overall Accuracy:  {acc * 100:.2f}%")
    print(f"Weighted Precision: {prec * 100:.2f}%")
    print(f"Weighted Recall:    {rec * 100:.2f}%")
    print(f"Weighted F1 Score:  {f1 * 100:.2f}%")
    print("\nFeature Importances:")
    for feat, imp in sorted(feature_importances.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {feat.capitalize()}: {imp * 100:.1f}%")
        
    # 5. Save Artifacts Bundle
    os.makedirs(os.path.dirname(ARTIFACTS_PATH), exist_ok=True)
    bundle = {
        "model": rf_model,
        "features": FEATURE_COLUMNS,
        "classes": RISK_CLASSES,
        "metrics": {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "confusion_matrix": cm,
            "classification_report": report,
            "test_samples": len(y_test),
            "train_samples": len(y_train)
        },
        "feature_importances": feature_importances,
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    joblib.dump(bundle, ARTIFACTS_PATH)
    # Save standalone model for backward compatibility
    joblib.dump(rf_model, LEGACY_MODEL_PATH)
    print(f"\nArtifacts successfully saved to: {ARTIFACTS_PATH}")
    
    # 6. Generate and save realistic Sample Students CSV & Seed Database
    seed_sample_students_data(rf_model)
    
    return bundle

def seed_sample_students_data(model):
    """Generates 120 rich sample student profiles and populates SQLite database."""
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if students already exist
    cursor.execute("SELECT COUNT(*) FROM Students;")
    count = cursor.fetchone()[0]
    
    first_names = ["Aarav", "Ananya", "Rohan", "Sneha", "Vikram", "Pooja", "Arjun", "Diya",
                   "Karthik", "Ishaan", "Meera", "Kabir", "Neha", "Aditya", "Rhea", "Siddharth",
                   "Tanvi", "Varun", "Anika", "Dev", "Alia", "Nikhil", "Bhavna", "Gaurav", "Simran"]
    last_names = ["Sharma", "Verma", "Patel", "Reddy", "Iyer", "Mehta", "Singh", "Nair",
                  "Gupta", "Deshmukh", "Chopra", "Joshi", "Bose", "Kulkarni", "Malhotra"]
    departments = ["Computer Science", "AI & Data Science", "Information Technology", 
                   "Electronics & Comm.", "Mechanical Engineering"]
    
    np.random.seed(101)
    n_students = 120
    students_data = []
    csv_rows = []
    
    for i in range(n_students):
        stu_id = f"EDU{1000 + i + 1}"
        fn = np.random.choice(first_names)
        ln = np.random.choice(last_names)
        name = f"{fn} {ln}"
        dept = np.random.choice(departments)
        sem = int(np.random.choice([2, 4, 6, 8], p=[0.25, 0.35, 0.25, 0.15]))
        email = f"{fn.lower()}.{ln.lower()}{i+1}@eduguard.edu"
        phone = f"+91-98{np.random.randint(10000000, 99999999)}"
        
        # Cluster realistic student profiles
        archetype = np.random.choice(["thriving", "average", "at_risk", "financial_hardship"], p=[0.40, 0.30, 0.18, 0.12])
        if archetype == "thriving":
            att = round(np.random.uniform(82.0, 98.0), 1)
            cgpa = round(np.random.uniform(7.8, 9.8), 2)
            lms = round(np.random.uniform(75.0, 98.0), 1)
            fee = 0.0
        elif archetype == "average":
            att = round(np.random.uniform(68.0, 83.0), 1)
            cgpa = round(np.random.uniform(6.0, 7.8), 2)
            lms = round(np.random.uniform(50.0, 75.0), 1)
            fee = float(np.random.choice([0.0, 500.0, 1200.0], p=[0.6, 0.25, 0.15]))
        elif archetype == "at_risk":
            att = round(np.random.uniform(35.0, 62.0), 1)
            cgpa = round(np.random.uniform(3.5, 5.8), 2)
            lms = round(np.random.uniform(15.0, 45.0), 1)
            fee = float(np.random.choice([0.0, 1500.0, 3200.0, 4800.0], p=[0.2, 0.3, 0.3, 0.2]))
        else: # financial hardship
            att = round(np.random.uniform(60.0, 78.0), 1)
            cgpa = round(np.random.uniform(5.5, 7.2), 2)
            lms = round(np.random.uniform(40.0, 68.0), 1)
            fee = round(float(np.random.uniform(2500.0, 6500.0)), 0)
            
        students_data.append((stu_id, name, dept, att, cgpa, lms, fee, sem, email, phone))
        csv_rows.append({
            "Student_ID": stu_id,
            "Student_Name": name,
            "Department": dept,
            "Attendance": att,
            "CGPA": cgpa,
            "LMS_Activity": lms,
            "Fee_Dues": fee,
            "Semester": sem,
            "Email": email
        })
        
    # Save CSV
    pd.DataFrame(csv_rows).to_csv(SAMPLE_CSV_PATH, index=False)
    # Also write to root sample_students.csv for convenience
    pd.DataFrame(csv_rows).to_csv(os.path.join(BASE_DIR, "sample_students.csv"), index=False)
    print(f"Sample students exported to: {SAMPLE_CSV_PATH}")
    
    if count == 0:
        cursor.executemany("""
        INSERT INTO Students (student_id, student_name, department, attendance, cgpa, lms_activity, fee_dues, semester, email, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, students_data)
        
        # Compute and insert predictions for all seeded students
        X_df = pd.DataFrame([
            {"attendance": s[3], "cgpa": s[4], "lms_activity": s[5], "fee_dues": s[6]}
            for s in students_data
        ])
        
        pred_probs = model.predict_proba(X_df)
        pred_classes = model.predict(X_df)
        
        pred_records = []
        for i, s in enumerate(students_data):
            stu_id = s[0]
            p_low = float(pred_probs[i][0])
            p_med = float(pred_probs[i][1])
            p_high = float(pred_probs[i][2])
            
            # Risk score continuous: 0 - 100
            risk_score = round(float(p_med * 45.0 + p_high * 100.0), 1)
            risk_level = INT_TO_CLASS[pred_classes[i]]
            
            factors = []
            if s[3] < 70:
                factors.append(f"Low Attendance ({s[3]}%)")
            if s[4] < 6.0:
                factors.append(f"Low CGPA ({s[4]})")
            if s[5] < 45:
                factors.append(f"Weak LMS Engagement ({s[5]}%)")
            if s[6] > 1500:
                factors.append(f"High Pending Dues (${s[6]:,.0f})")
            if not factors:
                factors.append("Consistent Academic & Attendance Performance")
                
            factors_str = "; ".join(factors)
            pred_records.append((stu_id, risk_score, risk_level, p_low, p_med, p_high, factors_str))
            
        cursor.executemany("""
        INSERT INTO Prediction_Results (student_id, risk_score, risk_level, prob_low, prob_medium, prob_high, contributing_factors)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, pred_records)
        
        # Seed several active interventions for demonstration
        cursor.execute("SELECT user_id FROM Users WHERE role='counselor' LIMIT 1;")
        counselor_user = cursor.fetchone()
        counselor_id = counselor_user[0] if counselor_user else 1
        
        initial_interventions = [
            ("EDU1003", counselor_id, 
             "Immediate attendance recovery plan and remedial tutoring in core engineering subjects.",
             "Academic Counseling", "In Progress", "Elena Vance, M.Ed.", "2026-11-28",
             "Student expressed difficulty commuting and balancing family commitments. Bi-weekly check-in scheduled."),
            ("EDU1012", counselor_id,
             "Installment payment plan authorization and student emergency aid application.",
             "Financial Assistance", "Pending", "Dr. Sarah Jenkins", "2026-12-05",
             "Finance office notified. Student awaiting scholarship review."),
            ("EDU1019", counselor_id,
             "Weekly LMS study schedule and peer mentor pairing for algorithmic problem solving.",
             "Academic Mentoring", "Completed", "Prof. Rajesh Sharma", "2026-11-15",
             "Student showed 22% improvement in quiz completion rates over last 3 weeks."),
            ("EDU1024", counselor_id,
             "Attendance contract signed. Faculty notifications sent for missed laboratory sessions.",
             "Attendance Improvement", "In Progress", "Elena Vance, M.Ed.", "2026-11-30",
             "Student agreed to log in daily and submit weekly laboratory work on time.")
        ]
        
        cursor.executemany("""
        INSERT INTO Intervention_Logs (student_id, user_id, advisory, intervention_type, action_status, assigned_counselor, follow_up_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, initial_interventions)
        
        conn.commit()
        print(f"Seeded {len(students_data)} students with predictions & demo interventions.")
        
    conn.close()

if __name__ == "__main__":
    train_and_evaluate_model()
