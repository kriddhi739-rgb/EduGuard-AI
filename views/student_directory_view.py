"""
EduGuard AI - Student Risk Directory View
Complete student management module: search, filters, profile diagnostics,
CRUD operations, batch CSV ingestion, and multi-format exports.
"""

import streamlit as st
import pandas as pd
from backend.student_service import (
    get_all_students_with_predictions, get_student_profile,
    add_student, update_student, delete_student, batch_upload_students,
    get_all_departments, get_institutional_kpis
)
from utils.helpers import get_risk_badge_html, format_currency, format_percentage, render_banner
from utils.report_generator import generate_excel_report

def render_student_directory_view():
    """Renders the comprehensive Student Risk Directory."""
    user = st.session_state.get("user") or {}
    is_admin = user.get("role") == "admin"
    
    st.markdown(
        render_banner(
            title="Student Risk Directory & Records Management",
            subtitle="Search, analyze, edit, and export student profiles evaluated by EduGuard ML",
            role_badge="👑 Admin Full Access" if is_admin else "🎓 Faculty/Counselor Access"
        ),
        unsafe_allow_html=True
    )
    
    # Action Toolbar: Search, Filters, Sorting
    tb_c1, tb_c2, tb_c3, tb_c4 = st.columns([2, 1.2, 1.2, 1.2])
    with tb_c1:
        search_query = st.text_input("🔍 Search Student", placeholder="Search by Student ID, Name, or Email...")
    with tb_c2:
        risk_filter = st.selectbox("Risk Level", ["All", "High Risk", "Medium Risk", "Low Risk"])
    with tb_c3:
        dept_options = ["All"] + get_all_departments()
        dept_filter = st.selectbox("Department", dept_options)
    with tb_c4:
        sort_choice = st.selectbox(
            "Sort Records By",
            ["Highest Risk Score", "Lowest Risk Score", "Lowest Attendance", "Lowest CGPA", "Highest Fee Dues", "Student Name"]
        )
        
    # Map sort choice
    sort_mapping = {
        "Highest Risk Score": ("risk_score", False),
        "Lowest Risk Score": ("risk_score", True),
        "Lowest Attendance": ("attendance", True),
        "Lowest CGPA": ("cgpa", True),
        "Highest Fee Dues": ("fee_dues", False),
        "Student Name": ("student_name", True)
    }
    sort_col, sort_asc = sort_mapping.get(sort_choice, ("risk_score", False))
    
    # Query database
    df = get_all_students_with_predictions(
        search_term=search_query,
        risk_filter=risk_filter,
        dept_filter=dept_filter,
        sort_by=sort_col,
        sort_ascending=sort_asc
    )
    
    # Action buttons: Add Student, Batch Upload, Export
    action_c1, action_c2, action_c3 = st.columns([1.5, 1.5, 3])
    with action_c1:
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export CSV",
            data=csv_bytes,
            file_name=f"eduguard_students_{risk_filter.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with action_c2:
        kpis = get_institutional_kpis()
        excel_bytes = generate_excel_report(kpis, df)
        st.download_button(
            label="📊 Export Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"eduguard_students_register.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with action_c3:
        st.markdown(f"""
        <div style="text-align: right; padding-top: 8px; font-size: 0.88rem; color: #64748B;">
            Showing <b>{len(df)}</b> student records matching criteria
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # Main Directory Tabs: Register View | Add Student | Batch Upload (Admin)
    tab1, tab2, tab3 = st.tabs(["📋 Student Register Table", "➕ Enroll New Student", "📁 Batch CSV Upload (Admin)"])
    
    # ---------------- TAB 1: DATA TABLE & ACTIONS ----------------
    with tab1:
        if df.empty:
            st.info("No student records match the active search or filter criteria.")
        else:
            # Prepare formatted display table
            display_table = pd.DataFrame({
                "Student ID": df["student_id"],
                "Student Name": df["student_name"],
                "Department": df["department"],
                "Attendance (%)": df["attendance"].apply(lambda x: f"{x:.1f}%"),
                "CGPA": df["cgpa"].apply(lambda x: f"{x:.2f}"),
                "LMS Activity (%)": df["lms_activity"].apply(lambda x: f"{x:.1f}%"),
                "Fee Dues": df["fee_dues"].apply(format_currency),
                "Risk Score": df["risk_score"].apply(lambda x: f"{x:.1f} / 100"),
                "Risk Level": df["risk_level"]
            })
            
            st.dataframe(
                display_table,
                use_container_width=True,
                height=min(450, 45 + len(display_table) * 35)
            )
            
            # Interactive Action Selector
            st.markdown("---")
            st.subheader("🔍 Student Profile Diagnostics & Record Actions")
            
            sel_col1, sel_col2 = st.columns([2.5, 1.5])
            with sel_col1:
                student_options = [
                    f"{r['student_id']} - {r['student_name']} ({r['risk_level']})" 
                    for _, r in df.iterrows()
                ]
                selected_item = st.selectbox("Select Student to Inspect, Edit, or Intervene:", student_options)
                
            selected_id = selected_item.split(" - ")[0] if selected_item else None
            
            if selected_id:
                student_profile = get_student_profile(selected_id)
                if student_profile:
                    # Summary card
                    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
                    p_col1.metric("Student Name", student_profile.get("student_name", "N/A"))
                    p_col2.metric("Department", student_profile.get("department", "N/A"))
                    p_col3.metric("Current Semester", f"Sem {student_profile.get('semester', 4)}")
                    
                    risk_lvl = student_profile.get("risk_level", "Medium Risk")
                    risk_scr = student_profile.get("risk_score", 50.0)
                    p_col4.markdown(f"""
                    <div style="background: white; border: 1px solid #E2E8F0; padding: 10px 14px; border-radius: 10px;">
                        <div style="font-size: 0.75rem; color: #64748B; font-weight: 600;">RISK CLASSIFICATION</div>
                        <div style="margin-top: 4px;">{get_risk_badge_html(risk_lvl)}</div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-top: 4px;">Score: {risk_scr:.1f} / 100</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Diagnostic Factors Progress Bars
                    diag_c1, diag_c2 = st.columns(2)
                    with diag_c1:
                        att_val = float(student_profile.get("attendance", 0))
                        st.write(f"**Attendance Rate:** {att_val:.1f}% (Regulatory Threshold: 75%)")
                        st.progress(min(100, int(att_val)) / 100)
                        
                        cgpa_val = float(student_profile.get("cgpa", 0))
                        st.write(f"**Cumulative GPA:** {cgpa_val:.2f} / 10.0 (Probation Threshold: 5.0)")
                        st.progress(min(100, int(cgpa_val * 10)) / 100)
                        
                    with diag_c2:
                        lms_val = float(student_profile.get("lms_activity", 0))
                        st.write(f"**LMS Platform Engagement:** {lms_val:.1f}%")
                        st.progress(min(100, int(lms_val)) / 100)
                        
                        fee_val = float(student_profile.get("fee_dues", 0))
                        fee_status = "⚠️ Outstanding Tuition Arrears" if fee_val > 0 else "✓ Cleared (No Dues)"
                        st.write(f"**Tuition Status:** {format_currency(fee_val)} ({fee_status})")
                        st.progress(min(1.0, fee_val / 5000.0) if fee_val > 0 else 0.0)
                        
                    # Model Diagnostic Summary
                    st.info(f"💡 **AI Diagnostic Factors:** {student_profile.get('contributing_factors', 'Stable performance profile.')}")
                    
                    # Action Sub-Sections: Edit Record / Delete / Quick Intervene
                    with st.expander("✏️ Edit Student Record & Re-evaluate Risk"):
                        with st.form(f"edit_form_{selected_id}"):
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                edit_name = st.text_input("Full Name", value=student_profile.get("student_name", ""))
                                edit_dept = st.selectbox(
                                    "Department", 
                                    get_all_departments(), 
                                    index=get_all_departments().index(student_profile.get("department")) if student_profile.get("department") in get_all_departments() else 0
                                )
                                edit_sem = st.number_input("Semester", min_value=1, max_value=10, value=int(student_profile.get("semester", 4)))
                                edit_email = st.text_input("Email", value=student_profile.get("email", ""))
                            with ec2:
                                edit_att = st.slider("Attendance Rate (%)", 0.0, 100.0, float(student_profile.get("attendance", 75.0)), 0.1)
                                edit_cgpa = st.slider("CGPA (0 - 10)", 0.0, 10.0, float(student_profile.get("cgpa", 7.0)), 0.01)
                                edit_lms = st.slider("LMS Activity (%)", 0.0, 100.0, float(student_profile.get("lms_activity", 65.0)), 0.1)
                                edit_fee = st.number_input("Pending Fee Dues ($)", min_value=0.0, max_value=25000.0, value=float(student_profile.get("fee_dues", 0.0)), step=100.0)
                                
                            save_edit_btn = st.form_submit_button("💾 Save Changes & Recompute ML Prediction", use_container_width=True)
                            if save_edit_btn:
                                update_data = {
                                    "student_name": edit_name,
                                    "department": edit_dept,
                                    "semester": edit_sem,
                                    "email": edit_email,
                                    "attendance": edit_att,
                                    "cgpa": edit_cgpa,
                                    "lms_activity": edit_lms,
                                    "fee_dues": edit_fee,
                                    "phone": student_profile.get("phone", "")
                                }
                                success, msg = update_student(selected_id, update_data)
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                                    
                    # Admin Delete Record
                    if is_admin:
                        with st.expander("🗑️ Delete Student Record (Admin Only)"):
                            st.warning(f"Warning: Deleting student '{selected_id} - {student_profile.get('student_name')}' will also permanently delete all associated prediction results and intervention histories.")
                            confirm_delete = st.checkbox(f"Yes, I confirm permanent deletion of {selected_id}")
                            if st.button("Permanently Delete Student", disabled=not confirm_delete, type="primary"):
                                success, msg = delete_student(selected_id)
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                                    
    # ---------------- TAB 2: ADD NEW STUDENT ----------------
    with tab2:
        st.subheader("➕ Enroll New Student with Real-time ML Evaluation")
        st.markdown("Fill in the student academic and engagement metrics. The Random Forest model will evaluate risk immediately upon insertion.")
        
        with st.form("add_student_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                new_id = st.text_input("Student ID (Unique)", placeholder="e.g. EDU2045")
                new_name = st.text_input("Full Name", placeholder="e.g. Sophia Anderson")
                new_dept = st.selectbox("Academic Department", get_all_departments())
                new_sem = st.selectbox("Current Semester", [1, 2, 3, 4, 5, 6, 7, 8], index=3)
                new_email = st.text_input("Institutional Email", placeholder="e.g. sophia.a@eduguard.edu")
            with f2:
                new_att = st.slider("Attendance Percentage (%)", 0.0, 100.0, 80.0, 0.1)
                new_cgpa = st.slider("Cumulative CGPA (0 - 10)", 0.0, 10.0, 7.5, 0.01)
                new_lms = st.slider("LMS Activity Score (%)", 0.0, 100.0, 70.0, 0.1)
                new_fee = st.number_input("Pending Tuition Dues ($)", min_value=0.0, max_value=25000.0, value=0.0, step=100.0)
                new_phone = st.text_input("Phone Number", placeholder="+91-9876543210")
                
            submit_new = st.form_submit_button("🚀 Add Student & Compute Dropout Risk", use_container_width=True)
            if submit_new:
                if not new_id or not new_name:
                    st.error("Student ID and Full Name are mandatory fields.")
                else:
                    new_student_data = {
                        "student_id": new_id,
                        "student_name": new_name,
                        "department": new_dept,
                        "semester": new_sem,
                        "email": new_email,
                        "attendance": new_att,
                        "cgpa": new_cgpa,
                        "lms_activity": new_lms,
                        "fee_dues": new_fee,
                        "phone": new_phone
                    }
                    success, msg = add_student(new_student_data)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                        
    # ---------------- TAB 3: BATCH CSV UPLOAD (ADMIN) ----------------
    with tab3:
        st.subheader("📁 Batch Ingestion of Student Datasets")
        st.markdown("Upload an institutional CSV dataset. EduGuard AI's preprocessing engine automatically standardizes headers, executes batch ML predictions, and updates SQLite storage.")
        
        if not is_admin:
            st.warning("🔒 Batch dataset ingestion is restricted to Administrator accounts. Please contact an institutional administrator.")
        else:
            # Downloadable CSV template
            template_df = pd.DataFrame([{
                "Student_ID": "EDU9001",
                "Student_Name": "Sample Student",
                "Department": "Computer Science",
                "Attendance": 82.5,
                "CGPA": 7.8,
                "LMS_Activity": 74.0,
                "Fee_Dues": 0.0,
                "Semester": 4,
                "Email": "sample@eduguard.edu"
            }])
            template_csv = template_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Download Sample CSV Template",
                data=template_csv,
                file_name="eduguard_student_upload_template.csv",
                mime="text/csv"
            )
            
            uploaded_file = st.file_uploader("Upload Institutional CSV File", type=["csv"])
            if uploaded_file is not None:
                try:
                    raw_df = pd.read_csv(uploaded_file)
                    st.write(f"Uploaded **{len(raw_df)}** rows. Data preview:")
                    st.dataframe(raw_df.head(5), use_container_width=True)
                    
                    if st.button("⚡ Process Batch Predictions & Import to Database", use_container_width=True):
                        with st.spinner("Processing ML predictions and updating SQLite tables..."):
                            ins, upd, errs = batch_upload_students(raw_df)
                            st.success(f"Batch Processing Complete! Inserted: {ins} new records | Updated: {upd} existing records.")
                            st.rerun()
                except Exception as e:
                    st.error(f"Error parsing CSV file: {str(e)}")
