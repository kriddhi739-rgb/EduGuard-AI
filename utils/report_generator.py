"""
EduGuard AI - Report Generation Engine
Exports institutional and individual student reports to PDF, Excel (.xlsx), and CSV.
"""

import io
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
from fpdf import FPDF

class EduGuardPDFReport(FPDF):
    """Custom FPDF class with EduGuard AI corporate styling, headers and footers."""
    
    def __init__(self, title_text: str = "Institutional Dropout Risk & Analytics Report"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.title_text = title_text
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        # Header background bar
        self.set_fill_color(37, 99, 235) # Vibrant Blue
        self.rect(0, 0, 210, 16, "F")
        
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 3)
        self.cell(0, 10, "EduGuard AI - Student Risk Prediction & Early Intervention System", ln=False)
        
        self.set_font("Helvetica", "", 9)
        self.set_xy(150, 3)
        self.cell(50, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align="R")
        self.ln(6)
        
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 8, f"Confidential Academic Report | Page {self.page_no()}", align="C")

def generate_pdf_report(
    kpi_dict: Dict[str, Any], 
    students_df: pd.DataFrame, 
    report_type: str = "Institutional Risk Report"
) -> bytes:
    """Generates a professional multi-page PDF summary report."""
    pdf = EduGuardPDFReport(title_text=report_type)
    pdf.add_page()
    
    # Report Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(15, 23, 42) # Dark Slate
    pdf.cell(0, 12, report_type, ln=True)
    
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 6, f"Generated on {datetime.now().strftime('%B %d, %Y - %H:%M')} | Institutional Assessment", ln=True)
    pdf.ln(4)
    
    # Executive Summary Box
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(10, pdf.get_y(), 190, 26, "DF")
    
    pdf.set_xy(14, pdf.get_y() + 3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, "Key Performance Indicators (Executive Summary)", ln=True)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(14)
    total = kpi_dict.get("total_students", len(students_df))
    high = kpi_dict.get("high_risk", 0)
    med = kpi_dict.get("med_risk", 0)
    low = kpi_dict.get("low_risk", 0)
    att = kpi_dict.get("avg_attendance", 0.0)
    cgpa = kpi_dict.get("avg_cgpa", 0.0)
    
    summary_text = (
        f"Total Students Monitored: {total}   |   "
        f"High Risk: {high} ({(high/total*100 if total else 0):.1f}%)   |   "
        f"Medium Risk: {med}   |   "
        f"Low Risk: {low}\n"
        f"Institutional Avg Attendance: {att}%   |   "
        f"Avg CGPA: {cgpa} / 10.0   |   "
        f"Total Pending Arrears: ${kpi_dict.get('total_fee_dues', 0):,.0f}"
    )
    pdf.multi_cell(182, 5, summary_text)
    pdf.ln(10)
    
    # Student Records Table Section
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(15, 23, 42)
    table_heading = "Prioritized High-Risk Students" if "High-Risk" in report_type else "Student Evaluation Records"
    pdf.cell(0, 8, table_heading, ln=True)
    pdf.ln(2)
    
    # Table Header
    headers = [("ID", 22), ("Name", 40), ("Department", 42), ("Att %", 18), ("CGPA", 18), ("Dues", 24), ("Risk Level", 26)]
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(15, 23, 42)
    
    for h_name, w in headers:
        pdf.cell(w, 8, h_name, border=1, fill=True, align="C" if w < 30 else "L")
    pdf.ln()
    
    # Filter or limit rows for printable view
    display_df = students_df
    if "High-Risk" in report_type:
        display_df = students_df[students_df["risk_level"] == "High Risk"]
        
    pdf.set_font("Helvetica", "", 8)
    for idx, row in display_df.head(45).iterrows():
        # Highlight high risk with light red tint
        risk_level = str(row.get("risk_level", "Medium Risk"))
        if "High" in risk_level:
            pdf.set_fill_color(254, 242, 242)
            pdf.set_text_color(153, 27, 27)
        elif "Med" in risk_level:
            pdf.set_fill_color(255, 251, 235)
            pdf.set_text_color(146, 64, 14)
        else:
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(30, 41, 59)
            
        pdf.cell(22, 6, str(row.get("student_id", "")), border=1, fill=True, align="C")
        pdf.cell(40, 6, str(row.get("student_name", ""))[:22], border=1, fill=True)
        pdf.cell(42, 6, str(row.get("department", ""))[:22], border=1, fill=True)
        pdf.cell(18, 6, f"{float(row.get('attendance', 0)):.1f}%", border=1, fill=True, align="C")
        pdf.cell(18, 6, f"{float(row.get('cgpa', 0)):.2f}", border=1, fill=True, align="C")
        pdf.cell(24, 6, f"${float(row.get('fee_dues', 0)):,.0f}", border=1, fill=True, align="R")
        pdf.cell(26, 6, risk_level, border=1, fill=True, align="C")
        pdf.ln()
        
    return pdf.output()

def generate_student_pdf_dossier(student_dict: Dict[str, Any]) -> bytes:
    """Generates an individual student comprehensive prediction and intervention dossier in PDF."""
    pdf = EduGuardPDFReport(title_text=f"Student Profile Dossier - {student_dict.get('student_name', '')}")
    pdf.add_page()
    
    stu_name = student_dict.get("student_name", "Student")
    stu_id = student_dict.get("student_id", "")
    risk_level = student_dict.get("risk_level", "Medium Risk")
    risk_score = student_dict.get("risk_score", 50.0)
    
    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, f"Individual Student Risk & Intervention Dossier", ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 6, f"Student: {stu_name} | ID: {stu_id} | Department: {student_dict.get('department', 'N/A')}", ln=True)
    pdf.ln(6)
    
    # Risk Badge Card
    if "High" in risk_level:
        pdf.set_fill_color(254, 242, 242)
        pdf.set_draw_color(254, 202, 202)
        badge_text_color = (153, 27, 27)
    elif "Med" in risk_level:
        pdf.set_fill_color(255, 251, 235)
        pdf.set_draw_color(253, 230, 138)
        badge_text_color = (146, 64, 14)
    else:
        pdf.set_fill_color(236, 253, 245)
        pdf.set_draw_color(167, 243, 208)
        badge_text_color = (6, 95, 70)
        
    pdf.rect(10, pdf.get_y(), 190, 22, "DF")
    pdf.set_xy(14, pdf.get_y() + 4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*badge_text_color)
    pdf.cell(0, 6, f"AI PREDICTED STATUS: {risk_level.upper()} (Risk Index: {risk_score:.1f} / 100)", ln=True)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(14)
    prob_text = f"Class Probabilities: Low Risk {student_dict.get('prob_low', 0)*100:.1f}% | Medium Risk {student_dict.get('prob_medium', 0)*100:.1f}% | High Risk {student_dict.get('prob_high', 0)*100:.1f}%"
    pdf.cell(0, 5, prob_text, ln=True)
    pdf.ln(8)
    
    # Multi-factor Academic Indicators Box
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "Academic & Engagement Indicators", ln=True)
    
    metrics = [
        ("Attendance Rate", f"{float(student_dict.get('attendance', 0)):.1f}%"),
        ("Cumulative GPA (CGPA)", f"{float(student_dict.get('cgpa', 0)):.2f} / 10.0"),
        ("LMS Activity Score", f"{float(student_dict.get('lms_activity', 0)):.1f}%"),
        ("Pending Tuition Arrears", f"${float(student_dict.get('fee_dues', 0)):,.0f}"),
        ("Current Semester", f"Semester {student_dict.get('semester', 4)}"),
        ("Student Email", str(student_dict.get('email', 'N/A')))
    ]
    
    pdf.set_font("Helvetica", "", 9)
    for label, val in metrics:
        pdf.set_text_color(100, 116, 139)
        pdf.cell(60, 6, label + ":", border="B")
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(130, 6, val, border="B", ln=True)
        pdf.set_font("Helvetica", "", 9)
        
    pdf.ln(6)
    
    # Contributing Factors & Explainability
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "Machine Learning Factor Diagnostic", ln=True)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    factors_str = student_dict.get("contributing_factors", "No factor breakdown available.")
    for f in factors_str.split("; "):
        pdf.cell(6, 6, "-", align="R")
        pdf.multi_cell(184, 6, f)
        
    pdf.ln(6)
    
    # Intervention History
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "Recorded Counseling & Intervention History", ln=True)
    
    interventions = student_dict.get("interventions", [])
    if not interventions:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 6, "No prior counseling logs recorded for this student.", ln=True)
    else:
        for idx, item in enumerate(interventions, 1):
            pdf.set_fill_color(248, 250, 252)
            pdf.set_draw_color(226, 232, 240)
            pdf.rect(10, pdf.get_y(), 190, 22, "DF")
            
            pdf.set_xy(14, pdf.get_y() + 2)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(37, 99, 235)
            pdf.cell(0, 5, f"Case #{item.get('intervention_id')}: {item.get('intervention_type')} | Status: {item.get('action_status')}", ln=True)
            
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(51, 65, 85)
            pdf.set_x(14)
            pdf.multi_cell(182, 4, f"Advisory: {item.get('advisory')}\nCounselor: {item.get('assigned_counselor')} | Follow-up: {item.get('follow_up_date', 'N/A')}")
            pdf.ln(4)
            
    return pdf.output()

def generate_excel_report(kpi_dict: Dict[str, Any], students_df: pd.DataFrame) -> bytes:
    """Generates an Excel workbook with Summary sheet and Full Student Register."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Sheet 1: Summary Sheet
        summary_data = {
            "Metric": [
                "Report Generation Date",
                "Total Students Monitored",
                "High-Risk Student Count",
                "Medium-Risk Student Count",
                "Low-Risk Student Count",
                "Average Attendance Percentage",
                "Average CGPA (Scale 0-10)",
                "Total Outstanding Tuition Arrears ($)"
            ],
            "Value": [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                kpi_dict.get("total_students", len(students_df)),
                kpi_dict.get("high_risk", 0),
                kpi_dict.get("med_risk", 0),
                kpi_dict.get("low_risk", 0),
                f"{kpi_dict.get('avg_attendance', 0):.1f}%",
                f"{kpi_dict.get('avg_cgpa', 0):.2f}",
                f"${kpi_dict.get('total_fee_dues', 0):,.2f}"
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Institutional Summary", index=False)
        
        # Sheet 2: All Student Records
        export_df = students_df.copy()
        export_cols = [
            "student_id", "student_name", "department", "attendance", "cgpa",
            "lms_activity", "fee_dues", "risk_score", "risk_level", "semester", "email"
        ]
        available_cols = [c for c in export_cols if c in export_df.columns]
        export_df[available_cols].to_excel(writer, sheet_name="Student Register", index=False)
        
        # Sheet 3: High Risk Students Only
        if "risk_level" in export_df.columns:
            high_risk_df = export_df[export_df["risk_level"] == "High Risk"]
            high_risk_df[available_cols].to_excel(writer, sheet_name="High Risk Action List", index=False)
            
    return output.getvalue()
