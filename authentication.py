"""
EduGuard AI - Authentication & User Management Service
Handles secure authentication, role-based access control, and credential management.
"""

from typing import Optional, Dict, Any, List, Tuple
from backend.database import get_connection, hash_password

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Validates username and password.
    Returns user dictionary if valid, None otherwise.
    """
    if not username or not password:
        return None
        
    conn = get_connection()
    cursor = conn.cursor()
    
    pwd_hash = hash_password(password.strip())
    cursor.execute("""
        SELECT user_id, username, role, full_name, email, department, created_at
        FROM Users
        WHERE (LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)) 
          AND password_hash = ?;
    """, (username.strip(), username.strip(), pwd_hash))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "user_id": row["user_id"],
            "username": row["username"],
            "role": row["role"],
            "full_name": row["full_name"],
            "email": row["email"],
            "department": row["department"],
            "created_at": row["created_at"]
        }
    return None

def change_password(username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    """Changes password for an existing user after validating old password."""
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."
        
    conn = get_connection()
    cursor = conn.cursor()
    
    old_hash = hash_password(old_password.strip())
    cursor.execute("SELECT user_id FROM Users WHERE username = ? AND password_hash = ?;", (username, old_hash))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return False, "Current password is incorrect."
        
    new_hash = hash_password(new_password.strip())
    cursor.execute("UPDATE Users SET password_hash = ? WHERE username = ?;", (new_hash, username))
    conn.commit()
    conn.close()
    return True, "Password successfully updated!"

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves user profile by user_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, role, full_name, email, department, created_at
        FROM Users WHERE user_id = ?;
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_all_counselors() -> List[str]:
    """Retrieves list of active counselors/faculty names for dropdowns."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM Users ORDER BY full_name ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [r["full_name"] for r in rows] or ["Dr. Sarah Jenkins", "Elena Vance, M.Ed.", "Prof. Rajesh Sharma"]
