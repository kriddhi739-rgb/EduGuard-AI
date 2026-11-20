"""
EduGuard AI - Early Intervention & Case Management Service
Manages intervention logging, advisory generation, case assignment, and status workflows.
"""

from typing import Optional, Dict, Any, List, Tuple
import sqlite3
from datetime import datetime
from backend.database import get_connection

INTERVENTION_TYPES = [
    "Academic Counseling",
    "Attendance Improvement",
    "Financial Assistance",
    "Personal Guidance",
    "Academic Mentoring"
]

ACTION_STATUSES = ["Pending", "In Progress", "Completed"]

def get_interventions(status_filter: Optional[str] = None, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches interventions with student name, department, and risk level."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        i.intervention_id,
        i.student_id,
        s.student_name,
        s.department,
        p.risk_level,
        p.risk_score,
        i.advisory,
        i.intervention_type,
        i.action_status,
        i.assigned_counselor,
        i.follow_up_date,
        i.notes,
        i.intervention_date,
        u.username as logged_by
    FROM Intervention_Logs i
    JOIN Students s ON i.student_id = s.student_id
    LEFT JOIN Prediction_Results p ON s.student_id = p.student_id
    LEFT JOIN Users u ON i.user_id = u.user_id
    WHERE 1=1
    """
    params = []
    
    if status_filter and status_filter != "All":
        query += " AND i.action_status = ?"
        params.append(status_filter)
        
    if student_id:
        query += " AND i.student_id = ?"
        params.append(student_id)
        
    query += " ORDER BY i.intervention_date DESC;"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_intervention(
    student_id: str,
    user_id: Optional[int],
    advisory: str,
    intervention_type: str,
    action_status: str,
    assigned_counselor: str,
    follow_up_date: str,
    notes: str
) -> Tuple[bool, str]:
    """Logs a new intervention record for a student."""
    if not student_id:
        return False, "Student selection is required."
    if not advisory:
        return False, "Advisory recommendations cannot be empty."
    if intervention_type not in INTERVENTION_TYPES:
        intervention_type = "Academic Counseling"
    if action_status not in ACTION_STATUSES:
        action_status = "In Progress"
        
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT student_name FROM Students WHERE student_id = ?;", (student_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, f"Student '{student_id}' does not exist."
        
    student_name = row["student_name"]
    
    cursor.execute("""
    INSERT INTO Intervention_Logs (
        student_id, user_id, advisory, intervention_type, 
        action_status, assigned_counselor, follow_up_date, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (student_id, user_id, advisory, intervention_type, action_status, assigned_counselor, follow_up_date, notes))
    
    conn.commit()
    conn.close()
    return True, f"Intervention successfully initiated for {student_name} ({student_id})."

def update_intervention_status(
    intervention_id: int, 
    new_status: str, 
    updated_notes: Optional[str] = None
) -> Tuple[bool, str]:
    """Updates action status and appends updated counselor notes."""
    if new_status not in ACTION_STATUSES:
        return False, f"Invalid status '{new_status}'."
        
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT intervention_id, notes FROM Intervention_Logs WHERE intervention_id = ?;", (intervention_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, f"Intervention ID {intervention_id} not found."
        
    existing_notes = row["notes"] or ""
    if updated_notes and updated_notes.strip():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_note_entry = f"\n[{timestamp} Update]: {updated_notes.strip()}"
        combined_notes = existing_notes + new_note_entry
    else:
        combined_notes = existing_notes
        
    cursor.execute("""
    UPDATE Intervention_Logs
    SET action_status = ?, notes = ?
    WHERE intervention_id = ?;
    """, (new_status, combined_notes, intervention_id))
    
    conn.commit()
    conn.close()
    return True, f"Intervention #{intervention_id} updated to '{new_status}'."

def get_intervention_kpis() -> Dict[str, Any]:
    """Aggregates intervention status metrics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        COUNT(intervention_id) as total_interventions,
        SUM(CASE WHEN action_status = 'Pending' THEN 1 ELSE 0 END) as pending_cases,
        SUM(CASE WHEN action_status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_cases,
        SUM(CASE WHEN action_status = 'Completed' THEN 1 ELSE 0 END) as completed_cases
    FROM Intervention_Logs;
    """)
    row = cursor.fetchone()
    
    # Also find how many High-Risk students do NOT have any intervention logged yet
    cursor.execute("""
    SELECT COUNT(s.student_id) as high_risk_awaiting
    FROM Students s
    JOIN Prediction_Results p ON s.student_id = p.student_id
    WHERE p.risk_level = 'High Risk'
      AND s.student_id NOT IN (SELECT DISTINCT student_id FROM Intervention_Logs);
    """)
    high_risk_awaiting = cursor.fetchone()[0] or 0
    
    conn.close()
    return {
        "total": row["total_interventions"] or 0,
        "pending": row["pending_cases"] or 0,
        "in_progress": row["in_progress_cases"] or 0,
        "completed": row["completed_cases"] or 0,
        "high_risk_awaiting": high_risk_awaiting
    }

def get_high_risk_students_requiring_intervention() -> List[Dict[str, Any]]:
    """Fetches high-risk students prioritized by highest risk score."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        s.student_id,
        s.student_name,
        s.department,
        s.attendance,
        s.cgpa,
        s.lms_activity,
        s.fee_dues,
        p.risk_score,
        p.risk_level,
        p.contributing_factors,
        (SELECT COUNT(*) FROM Intervention_Logs i WHERE i.student_id = s.student_id) as intervention_count
    FROM Students s
    JOIN Prediction_Results p ON s.student_id = p.student_id
    WHERE p.risk_level = 'High Risk'
    ORDER BY p.risk_score DESC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
