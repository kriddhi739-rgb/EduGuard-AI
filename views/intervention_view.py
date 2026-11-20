"""
EduGuard AI - Intervention Action Center View
Case management workflow for faculty and counselors to initiate, monitor,
and complete student retention interventions and track outcome histories.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from backend.intervention_service import (
    get_interventions, add_intervention, update_intervention_status,
    get_intervention_kpis, get_high_risk_students_requiring_intervention,
    INTERVENTION_TYPES, ACTION_STATUSES
)
from backend.student_service import get_all_students_with_predictions, get_student_profile
from backend.authentication import get_all_counselors
from utils.helpers import get_risk_badge_html, get_status_badge_html, render_kpi_card, render_banner

def render_intervention_view():
    """Renders the early intervention management center."""
    user = st.session_state.get("user") or {}
    user_id = user.get("user_id", 1)
    
    st.markdown(
        render_banner(
            title="Early Intervention & Case Action Center",
            subtitle="Coordinate structured retention advisories, counselor casework, and multi-stage student follow-ups",
            role_badge=f"Counseling Desk · {user.get('full_name', 'Faculty/Counselor')}"
        ),
        unsafe_allow_html=True
    )
    
    # Intervention KPIs
    kpi_dict = get_intervention_kpis()
    
    k_col1, k_col2, k_col3, k_col4 = st.columns(4)
    with k_col1:
        st.markdown(
            render_kpi_card("Total Interventions", str(kpi_dict["total"]), "All recorded cases", "blue"),
            unsafe_allow_html=True
        )
    with k_col2:
        st.markdown(
            render_kpi_card("Active In Progress", str(kpi_dict["in_progress"]), "Ongoing counselor outreach", "teal"),
            unsafe_allow_html=True
        )
    with k_col3:
        st.markdown(
            render_kpi_card("Scheduled Pending", str(kpi_dict["pending"]), "Upcoming initial consultations", "orange"),
            unsafe_allow_html=True
        )
    with k_col4:
        st.markdown(
            render_kpi_card("Completed Cases", str(kpi_dict["completed"]), "Successfully resolved cases", "green"),
            unsafe_allow_html=True
        )
        
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    # High-Risk Urgent Queue Check
    urgent_students = get_high_risk_students_requiring_intervention()
    unaddressed_high_risk = [s for s in urgent_students if s.get("intervention_count", 0) == 0]
    
    if unaddressed_high_risk:
        priority_alert_html = (
            '<div style="background: linear-gradient(90deg, #FEF2F2 0%, #FFF1F2 100%); border-left: 5px solid #EF4444; '
            'border-radius: 12px; padding: 14px 18px; margin-bottom: 18px; display: flex; align-items: center; '
            'justify-content: space-between; flex-wrap: wrap; gap: 10px; box-shadow: 0 2px 6px rgba(239, 68, 68, 0.08);">'
            '<div>'
            '<span style="font-weight: 700; color: #991B1B;">⚠️ Priority Alert:</span>'
            f'<span style="color: #7F1D1D; font-size: 0.90rem; margin-left: 6px;"><b>{len(unaddressed_high_risk)}</b> High-Risk students currently have no active retention intervention logged.</span>'
            '</div>'
            '<span style="background: #FEE2E2; color: #991B1B; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 20px;">Outreach Mandated</span>'
            '</div>'
        )
        st.markdown(priority_alert_html, unsafe_allow_html=True)
        
    # Main Tabs
    tab1, tab2, tab3 = st.tabs([
        "📂 Active Cases & Log History", 
        "➕ Initiate New Intervention Case", 
        "🚨 High-Risk Priority Queue"
    ])
    
    # ---------------- TAB 1: ACTIVE CASES & LOG ----------------
    with tab1:
        st.subheader("Intervention History & Case Workflow")
        
        fil_c1, _ = st.columns([1.8, 3])
        with fil_c1:
            status_filter = st.selectbox("Filter Casework by Status", ["All", "Pending", "In Progress", "Completed"])
            
        interventions = get_interventions(status_filter=status_filter)
        
        if not interventions:
            st.info("No intervention records found matching this status filter.")
        else:
            for item in interventions:
                case_id = item["intervention_id"]
                stu_id = item["student_id"]
                stu_name = item["student_name"]
                status = item["action_status"]
                inv_type = item["intervention_type"]
                risk_lvl = item.get("risk_level", "Medium Risk")
                counselor = item["assigned_counselor"]
                follow_up = item.get("follow_up_date") or "Not scheduled"
                date_logged = item.get("intervention_date", "")[:10]
                
                with st.expander(f"Case #{case_id}: {stu_name} ({stu_id}) — {inv_type} [{status}]", expanded=(status != "Completed")):
                    card_c1, card_c2 = st.columns([2.5, 1.5])
                    with card_c1:
                        st.write(f"**Student:** {stu_name} (`{stu_id}`) | **Department:** {item.get('department', 'N/A')}")
                        st.markdown(f"**Classification:** {get_risk_badge_html(risk_lvl)}", unsafe_allow_html=True)
                        st.info(f"**Action Advisory:**\n{item['advisory']}")
                        
                        if item.get("notes"):
                            st.write(f"**Counselor Notes:**\n```\n{item['notes']}\n```")
                            
                    with card_c2:
                        st.write(f"**Current Status:** {status}")
                        st.write(f"**Assigned Counselor:** {counselor}")
                        st.write(f"**Follow-up Date:** {follow_up}")
                        st.caption(f"Logged: {date_logged}")
                        
                        # In-place status updater
                        with st.form(f"update_status_form_{case_id}"):
                            new_status_val = st.selectbox(
                                "Update Action Status",
                                ACTION_STATUSES,
                                index=ACTION_STATUSES.index(status) if status in ACTION_STATUSES else 0
                            )
                            additional_note = st.text_area("Add Progress Note", height=65, placeholder="e.g. Student attended counseling session...")
                            submit_up = st.form_submit_button("Save Status Update", use_container_width=True)
                            
                            if submit_up:
                                succ, msg = update_intervention_status(case_id, new_status_val, additional_note)
                                if succ:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                                    
    # ---------------- TAB 2: INITIATE NEW INTERVENTION ----------------
    with tab2:
        st.subheader("➕ Launch Structured Student Early Intervention")
        st.caption("Assign a counselor or faculty mentor, set milestone follow-ups, and log actionable retention advisories.")
        
        all_students_df = get_all_students_with_predictions()
        
        prefill_id = st.session_state.pop("prefill_intervention_student_id", None)
        prefill_advisory = st.session_state.pop("prefill_intervention_advisory", None)
        
        # Order high risk first
        all_students_df["sort_key"] = all_students_df["risk_level"].map({"High Risk": 0, "Medium Risk": 1, "Low Risk": 2})
        sorted_students = all_students_df.sort_values(["sort_key", "risk_score"], ascending=[True, False])
        
        stu_options = []
        default_index = 0
        for idx, r in sorted_students.reset_index().iterrows():
            tag = "🔴 [HIGH RISK]" if r["risk_level"] == "High Risk" else ("🟡 [MED]" if r["risk_level"] == "Medium Risk" else "🟢 [LOW]")
            label = f"{r['student_id']} - {r['student_name']} {tag} (Score: {r['risk_score']:.1f})"
            stu_options.append(label)
            if prefill_id and str(r["student_id"]) == str(prefill_id):
                default_index = idx
                
        selected_stu_str = st.selectbox("Select Student Requiring Intervention:", stu_options, index=default_index)
        sel_student_id = selected_stu_str.split(" - ")[0] if selected_stu_str else None
        
        if sel_student_id:
            profile = get_student_profile(sel_student_id)
            if profile:
                s_c1, s_c2, s_c3, s_c4 = st.columns(4)
                s_c1.metric("Student Name", profile.get("student_name", "N/A"))
                s_c2.metric("Attendance", f"{float(profile.get('attendance', 0)):.1f}%")
                s_c3.metric("CGPA", f"{float(profile.get('cgpa', 0)):.2f}")
                s_c4.metric("Pending Dues", f"${float(profile.get('fee_dues', 0)):,.0f}")
                
                auto_advisory = prefill_advisory or (
                    f"Immediate intervention required for {profile.get('student_name')}. "
                    f"Focus areas: {profile.get('contributing_factors', 'Academic & attendance recovery plan.')}"
                )
                
                with st.form("new_intervention_form", clear_on_submit=True):
                    ic1, ic2 = st.columns(2)
                    with ic1:
                        inv_type_val = st.selectbox("Intervention Category", INTERVENTION_TYPES)
                        counselor_list = get_all_counselors()
                        current_user_name = user.get("full_name", counselor_list[0])
                        counselor_idx = counselor_list.index(current_user_name) if current_user_name in counselor_list else 0
                        assigned_counselor_val = st.selectbox("Assign Counselor / Faculty Mentor", counselor_list, index=counselor_idx)
                        status_val = st.selectbox("Initial Action Status", ["In Progress", "Pending"], index=0)
                    with ic2:
                        default_date = date.today() + timedelta(days=7)
                        follow_up_val = st.date_input("Scheduled Follow-up Date", value=default_date)
                        initial_notes_val = st.text_area("Initial Counselor Case Notes", placeholder="e.g. Initial counseling session scheduled. Parent notified.")
                        
                    advisory_val = st.text_area("Advisory & Remedial Action Strategy", value=auto_advisory, height=85)
                    
                    submit_inv = st.form_submit_button("🚀 Submit & Log Intervention Record", use_container_width=True, type="primary")
                    if submit_inv:
                        success, msg = add_intervention(
                            student_id=sel_student_id,
                            user_id=user_id,
                            advisory=advisory_val,
                            intervention_type=inv_type_val,
                            action_status=status_val,
                            assigned_counselor=assigned_counselor_val,
                            follow_up_date=str(follow_up_val),
                            notes=initial_notes_val
                        )
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                            
    # ---------------- TAB 3: HIGH RISK PRIORITY QUEUE ----------------
    with tab3:
        st.subheader("🚨 Prioritized High-Risk Students Queue")
        st.caption("All students evaluated as High Risk by the Random Forest model, sorted by highest attrition probability.")
        
        if not urgent_students:
            st.success("🎉 Zero students currently classified as High Risk.")
        else:
            urgent_table = pd.DataFrame([
                {
                    "Student ID": s["student_id"],
                    "Student Name": s["student_name"],
                    "Department": s["department"],
                    "Attendance": f"{s['attendance']:.1f}%",
                    "CGPA": f"{s['cgpa']:.2f}",
                    "LMS Score": f"{s['lms_activity']:.1f}%",
                    "Pending Fees": f"${s['fee_dues']:,.0f}",
                    "Risk Score": f"{s['risk_score']:.1f}/100",
                    "Past Interventions": s["intervention_count"]
                }
                for s in urgent_students
            ])
            
            st.dataframe(urgent_table, use_container_width=True)
