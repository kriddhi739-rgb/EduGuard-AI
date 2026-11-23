"""
EduGuard AI - Database Connection & Schema Management
Uses SQLite with complete schema definitions and automated initial seeding.
"""

import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "eduguard.db")

def get_connection():
    """Returns a SQLite connection with foreign key support enabled."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def hash_password(password: str) -> str:
    """Hashes password using SHA-256 with a salt."""
    salt = "eduguard_secure_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def init_database():
    """Initializes all database tables and seeds demo data if empty."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'counselor')),
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        department TEXT DEFAULT 'Academic Affairs',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 2. Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        student_id TEXT PRIMARY KEY,
        student_name TEXT NOT NULL,
        department TEXT NOT NULL,
        attendance REAL NOT NULL CHECK(attendance >= 0 AND attendance <= 100),
        cgpa REAL NOT NULL CHECK(cgpa >= 0 AND cgpa <= 10),
        lms_activity REAL NOT NULL CHECK(lms_activity >= 0 AND lms_activity <= 100),
        fee_dues REAL NOT NULL DEFAULT 0.0,
        semester INTEGER DEFAULT 4,
        email TEXT,
        phone TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 3. Prediction Results Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Prediction_Results (
        prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        risk_score REAL NOT NULL,
        risk_level TEXT NOT NULL CHECK(risk_level IN ('Low Risk', 'Medium Risk', 'High Risk')),
        prob_low REAL DEFAULT 0.0,
        prob_medium REAL DEFAULT 0.0,
        prob_high REAL DEFAULT 0.0,
        contributing_factors TEXT,
        prediction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
    );
    """)
    
    # 4. Intervention Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Intervention_Logs (
        intervention_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        user_id INTEGER,
        advisory TEXT NOT NULL,
        intervention_type TEXT NOT NULL,
        action_status TEXT NOT NULL CHECK(action_status IN ('Pending', 'In Progress', 'Completed')),
        assigned_counselor TEXT NOT NULL,
        follow_up_date TEXT,
        notes TEXT,
        intervention_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL
    );
    """)
    
    conn.commit()
    
    # Seed default users if empty
    cursor.execute("SELECT COUNT(*) FROM Users;")
    if cursor.fetchone()[0] == 0:
        seed_users(conn)
        
    conn.close()

def seed_users(conn):
    """Seed initial administrator and faculty/counselor credentials."""
    users = [
        ("admin", hash_password("admin123"), "admin", "Dr. Sarah Jenkins", "admin@eduguard.edu", "Institutional Administration"),
        ("counselor", hash_password("counselor123"), "counselor", "Elena Vance, M.Ed.", "counselor@eduguard.edu", "Student Support Center"),
        ("prof_sharma", hash_password("faculty123"), "counselor", "Prof. Rajesh Sharma", "sharma@eduguard.edu", "Computer Science & Engineering")
    ]
    cursor = conn.cursor()
    cursor.executemany("""
    INSERT INTO Users (username, password_hash, role, full_name, email, department)
    VALUES (?, ?, ?, ?, ?, ?);
    """, users)
    conn.commit()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully at:", DB_PATH)
