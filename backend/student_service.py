"""
EduGuard AI - Student Management & Analytics Service
Handles student database operations, queries, batch processing, and KPI aggregations.
"""

from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
import sqlite3
from backend.database import get_connection
from ml.predict import predict_student, batch_predict
from ml.preprocessing import standardize_student_dataframe

def get_all_students_with_predictions(
    search_term: Optional[str] = None,
    risk_filter: Optional[str] = None,
    dept_filter: Optional[str] = None,
    sort_by: str = "risk_score",
    sort_ascending: bool = False
) -> pd.DataFrame:
    """
    Fetches all student records joined with their latest ML prediction results.
    Supports real-time search, multi-factor filtering, and sorting.
    """
    conn = get_connection()
    
    query = """
    SELECT 
        s.student_id,
        s.student_name,
        s.department,
        s.attendance,
        s.cgpa,
        s.lms_activity,
        s.fee_dues,
        s.semester,
        s.email,
        s.phone,
        COALESCE(p.risk_score, 50.0) AS risk_score,
        COALESCE(p.risk_level, 'Medium Risk') AS risk_level,
        p.prob_low,
        p.prob_medium,
        p.prob_high,
        p.contributing_factors,
        p.prediction_date
    FROM Students s
    LEFT JOIN Prediction_Results p ON s.student_id = p.student_id
    WHERE 1=1
    """
    params = []
    
    if search_term:
        clean_search = f"%{search_term.strip()}%"
        query += " AND (s.student_id LIKE ? OR s.student_name LIKE ? OR s.email LIKE ?)"
        params.extend([clean_search, clean_search, clean_search])
        
    if risk_filter and risk_filter != "All":
        query += " AND p.risk_level = ?"
        params.append(risk_filter)
        
    if dept_filter and dept_filter != "All":
        query += " AND s.department = ?"
        params.append(dept_filter)
        
    # Valid sort columns mapping
    valid_sorts = {
        "risk_score": "risk_score",
        "attendance": "s.attendance",
        "cgpa": "s.cgpa",
        "lms_activity": "s.lms_activity",
        "fee_dues": "s.fee_dues",
        "student_name": "s.student_name",
        "student_id": "s.student_id"
    }
    sort_col = valid_sorts.get(sort_by, "risk_score")
    direction = "ASC" if sort_ascending else "DESC"
    query += f" ORDER BY {sort_col} {direction}"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_student_profile(student_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves full student profile, ML prediction details, and intervention history."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        s.*,
        p.risk_score, p.risk_level, p.prob_low, p.prob_medium, p.prob_high,
        p.contributing_factors, p.prediction_date
    FROM Students s
    LEFT JOIN Prediction_Results p ON s.student_id = p.student_id
    WHERE s.student_id = ?;
    """, (student_id,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    student = dict(row)
    
    # Retrieve intervention logs
    cursor.execute("""
    SELECT 
        i.*, u.full_name as counselor_user_name
    FROM Intervention_Logs i
    LEFT JOIN Users u ON i.user_id = u.user_id
    WHERE i.student_id = ?
    ORDER BY i.intervention_date DESC;
    """, (student_id,))
    
    student["interventions"] = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return student

def add_student(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Inserts a new student and automatically calculates & persists ML prediction.
    """
    student_id = data.get("student_id", "").strip().upper()
    student_name = data.get("student_name", "").strip()
    department = data.get("department", "General Engineering").strip()
    attendance = float(data.get("attendance", 75.0))
    cgpa = float(data.get("cgpa", 7.0))
    lms_activity = float(data.get("lms_activity", 65.0))
    fee_dues = float(data.get("fee_dues", 0.0))
    semester = int(data.get("semester", 4))
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    
    if not student_id:
        return False, "Student ID cannot be empty."
    if not student_name:
        return False, "Student Name cannot be empty."
        
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check duplicate
    cursor.execute("SELECT student_id FROM Students WHERE student_id = ?;", (student_id,))
    if cursor.fetchone():
        conn.close()
        return False, f"Student ID '{student_id}' already exists in database."
        
    # Insert Student
    cursor.execute("""
    INSERT INTO Students (student_id, student_name, department, attendance, cgpa, lms_activity, fee_dues, semester, email, phone)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (student_id, student_name, department, attendance, cgpa, lms_activity, fee_dues, semester, email, phone))
    
    # Run ML Prediction
    pred = predict_student(attendance, cgpa, lms_activity, fee_dues)
    factors_summary = "; ".join([f["text"] for f in pred["factors"]])
    
    cursor.execute("""
    INSERT INTO Prediction_Results (student_id, risk_score, risk_level, prob_low, prob_medium, prob_high, contributing_factors)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (student_id, pred["risk_score"], pred["risk_level"], pred["prob_low"], pred["prob_medium"], pred["prob_high"], factors_summary))
    
    conn.commit()
    conn.close()
    return True, f"Student {student_name} ({student_id}) enrolled with predicted {pred['risk_level']}."

def update_student(student_id: str, data: Dict[str, Any]) -> Tuple[bool, str]:
    """Updates student records and refreshes the ML prediction in real time."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT student_id FROM Students WHERE student_id = ?;", (student_id,))
    if not cursor.fetchone():
        conn.close()
        return False, f"Student '{student_id}' not found."
        
    student_name = data.get("student_name", "").strip()
    department = data.get("department", "General Engineering").strip()
    attendance = float(data.get("attendance", 75.0))
    cgpa = float(data.get("cgpa", 7.0))
    lms_activity = float(data.get("lms_activity", 65.0))
    fee_dues = float(data.get("fee_dues", 0.0))
    semester = int(data.get("semester", 4))
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    
    cursor.execute("""
    UPDATE Students 
    SET student_name = ?, department = ?, attendance = ?, cgpa = ?, lms_activity = ?, fee_dues = ?, semester = ?, email = ?, phone = ?
    WHERE student_id = ?;
    """, (student_name, department, attendance, cgpa, lms_activity, fee_dues, semester, email, phone, student_id))
    
    # Re-run ML Prediction
    pred = predict_student(attendance, cgpa, lms_activity, fee_dues)
    factors_summary = "; ".join([f["text"] for f in pred["factors"]])
    
    cursor.execute("""
    UPDATE Prediction_Results
    SET risk_score = ?, risk_level = ?, prob_low = ?, prob_medium = ?, prob_high = ?, contributing_factors = ?, prediction_date = CURRENT_TIMESTAMP
    WHERE student_id = ?;
    """, (pred["risk_score"], pred["risk_level"], pred["prob_low"], pred["prob_medium"], pred["prob_high"], factors_summary, student_id))
    
    conn.commit()
    conn.close()
    return True, f"Student {student_name} ({student_id}) successfully updated. Re-evaluated as {pred['risk_level']}."

def delete_student(student_id: str) -> Tuple[bool, str]:
    """Deletes student record, cascade removes predictions and intervention logs."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT student_name FROM Students WHERE student_id = ?;", (student_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, f"Student '{student_id}' not found."
        
    name = row["student_name"]
    cursor.execute("DELETE FROM Students WHERE student_id = ?;", (student_id,))
    conn.commit()
    conn.close()
    return True, f"Record for {name} ({student_id}) permanently removed from system."

def batch_upload_students(df: pd.DataFrame) -> Tuple[int, int, List[str]]:
    """
    Processes uploaded dataframe, cleans features, runs ML inference,
    and upserts into SQLite database.
    """
    clean_df = standardize_student_dataframe(df)
    scored_df = batch_predict(clean_df)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    inserted = 0
    updated = 0
    errors = []
    
    for _, row in scored_df.iterrows():
        stu_id = str(row["student_id"]).strip().upper()
        name = str(row.get("student_name", "Student Record"))
        dept = str(row.get("department", "General Engineering"))
        att = float(row["attendance"])
        cgpa = float(row["cgpa"])
        lms = float(row["lms_activity"])
        fee = float(row["fee_dues"])
        sem = int(row.get("semester", 4))
        email = str(row.get("email", f"{stu_id.lower()}@eduguard.edu"))
        phone = str(row.get("phone", ""))
        
        score = float(row["risk_score"])
        level = str(row["risk_level"])
        p_l = float(row["prob_low"])
        p_m = float(row["prob_medium"])
        p_h = float(row["prob_high"])
        factors = f"Attendance: {att}%, CGPA: {cgpa}, LMS: {lms}%, Dues: ${fee:,.0f}"
        
        cursor.execute("SELECT student_id FROM Students WHERE student_id = ?;", (stu_id,))
        if cursor.fetchone():
            # Update
            cursor.execute("""
            UPDATE Students 
            SET student_name=?, department=?, attendance=?, cgpa=?, lms_activity=?, fee_dues=?, semester=?, email=?, phone=?
            WHERE student_id = ?;
            """, (name, dept, att, cgpa, lms, fee, sem, email, phone, stu_id))
            
            cursor.execute("""
            UPDATE Prediction_Results
            SET risk_score=?, risk_level=?, prob_low=?, prob_medium=?, prob_high=?, contributing_factors=?, prediction_date=CURRENT_TIMESTAMP
            WHERE student_id = ?;
            """, (score, level, p_l, p_m, p_h, factors, stu_id))
            updated += 1
        else:
            # Insert
            cursor.execute("""
            INSERT INTO Students (student_id, student_name, department, attendance, cgpa, lms_activity, fee_dues, semester, email, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (stu_id, name, dept, att, cgpa, lms, fee, sem, email, phone))
            
            cursor.execute("""
            INSERT INTO Prediction_Results (student_id, risk_score, risk_level, prob_low, prob_medium, prob_high, contributing_factors)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (stu_id, score, level, p_l, p_m, p_h, factors))
            inserted += 1
            
    conn.commit()
    conn.close()
    return inserted, updated, errors

def get_institutional_kpis() -> Dict[str, Any]:
    """Computes top-level institutional metrics dynamically from SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        COUNT(s.student_id) as total_students,
        AVG(s.attendance) as avg_attendance,
        AVG(s.cgpa) as avg_cgpa,
        AVG(s.lms_activity) as avg_lms,
        SUM(s.fee_dues) as total_fee_dues,
        SUM(CASE WHEN p.risk_level = 'High Risk' THEN 1 ELSE 0 END) as high_risk_count,
        SUM(CASE WHEN p.risk_level = 'Medium Risk' THEN 1 ELSE 0 END) as med_risk_count,
        SUM(CASE WHEN p.risk_level = 'Low Risk' THEN 1 ELSE 0 END) as low_risk_count
    FROM Students s
    LEFT JOIN Prediction_Results p ON s.student_id = p.student_id;
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    total = row["total_students"] or 0
    return {
        "total_students": total,
        "high_risk": row["high_risk_count"] or 0,
        "med_risk": row["med_risk_count"] or 0,
        "low_risk": row["low_risk_count"] or 0,
        "avg_attendance": round(float(row["avg_attendance"] or 0.0), 1),
        "avg_cgpa": round(float(row["avg_cgpa"] or 0.0), 2),
        "avg_lms": round(float(row["avg_lms"] or 0.0), 1),
        "total_fee_dues": float(row["total_fee_dues"] or 0.0)
    }

def get_risk_by_department() -> pd.DataFrame:
    """Aggregates student counts across departments and risk levels."""
    conn = get_connection()
    query = """
    SELECT 
        s.department,
        p.risk_level,
        COUNT(s.student_id) as count
    FROM Students s
    JOIN Prediction_Results p ON s.student_id = p.student_id
    GROUP BY s.department, p.risk_level
    ORDER BY s.department, p.risk_level;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_performance_trends() -> pd.DataFrame:
    """Computes semester performance trends from students."""
    conn = get_connection()
    query = """
    SELECT 
        s.semester,
        ROUND(AVG(s.attendance), 1) as avg_attendance,
        ROUND(AVG(s.cgpa), 2) as avg_cgpa,
        ROUND(AVG(s.lms_activity), 1) as avg_lms,
        COUNT(s.student_id) as student_count
    FROM Students s
    GROUP BY s.semester
    ORDER BY s.semester;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_all_departments() -> List[str]:
    """Returns list of distinct departments currently in database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT department FROM Students WHERE department IS NOT NULL ORDER BY department ASC;")
    rows = cursor.fetchall()
    conn.close()
    depts = [r["department"] for r in rows if r["department"]]
    return depts if depts else ["Computer Science", "AI & Data Science", "Information Technology", "Electronics"]
