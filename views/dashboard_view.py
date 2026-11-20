"""
EduGuard AI - Overview Institutional Dashboard View
Clean, modern, responsive executive intelligence dashboard:
balanced KPI metrics, interactive Plotly visualizations, and early alert banner.
"""

import streamlit as st
import pandas as pd
from backend.student_service import (
    get_institutional_kpis, get_all_students_with_predictions,
    get_risk_by_department, get_performance_trends, get_all_departments
)
from ml.model_evaluation import get_feature_importances
from utils.charts import (
    create_risk_distribution_pie, create_attendance_cgpa_scatter,
    create_department_risk_bar, create_semester_performance_line,
    create_feature_importance_bar
)
from utils.helpers import render_kpi_card, render_banner, format_currency

def render_dashboard_view():
    """Renders the executive institutional dashboard."""
    user = st.session_state.get("user") or {}
    user_role = "👑 Administrator" if user.get("role") == "admin" else "🎓 Faculty/Counselor"
    
    # Hero Header Banner
    st.markdown(
        render_banner(
            title="Institutional Retention & Dropout Risk Intelligence",
            subtitle="Machine Learning-driven predictive analytics for early student attrition prevention",
            role_badge=f"{user_role} · {user.get('full_name', 'Authorized Staff')}"
        ),
        unsafe_allow_html=True
    )
    
    # Fetch real-time data from SQLite
    all_students_df = get_all_students_with_predictions()
    departments = ["All Departments"] + get_all_departments()
    
    # Clean Filter Bar
    f_c1, f_c2, f_c3 = st.columns([2, 1.2, 1])
    with f_c1:
        selected_dept = st.selectbox("Academic Department Filter", departments, label_visibility="collapsed")
    with f_c2:
        semester_filter = st.selectbox(
            "Cohort Semester", 
            ["All Semesters", "Semester 2", "Semester 4", "Semester 6", "Semester 8"],
            label_visibility="collapsed"
        )
    with f_c3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
            
    # Filter dataset
    filtered_df = all_students_df.copy()
    if selected_dept != "All Departments":
        filtered_df = filtered_df[filtered_df["department"] == selected_dept]
    if semester_filter != "All Semesters":
        sem_num = int(semester_filter.replace("Semester ", ""))
        filtered_df = filtered_df[filtered_df["semester"] == sem_num]
        
    filtered_total = len(filtered_df)
    filtered_high = len(filtered_df[filtered_df["risk_level"] == "High Risk"])
    filtered_med = len(filtered_df[filtered_df["risk_level"] == "Medium Risk"])
    filtered_low = len(filtered_df[filtered_df["risk_level"] == "Low Risk"])
    filtered_att = filtered_df["attendance"].mean() if not filtered_df.empty else 0.0
    filtered_cgpa = filtered_df["cgpa"].mean() if not filtered_df.empty else 0.0
    
    # Eye-Catchy Early Alert Banner for High-Risk Students
    if filtered_high > 0:
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #FEF2F2 0%, #FFF1F2 100%);
            border-left: 5px solid #EF4444;
            border-radius: 12px;
            padding: 14px 20px;
            margin: 10px 0 20px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            box-shadow: 0 2px 8px rgba(239, 68, 68, 0.08);
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.6rem;">🚨</span>
                <div>
                    <div style="font-size: 0.98rem; font-weight: 700; color: #991B1B;">
                        Action Required: {filtered_high} High-Risk Students Detected in Selected Cohort
                    </div>
                    <div style="font-size: 0.84rem; color: #B91C1C; margin-top: 2px;">
                        Exhibiting severe deficits across attendance, academic standing, or pending tuition arrears.
                    </div>
                </div>
            </div>
            <div>
                <span style="background: #FEE2E2; color: #991B1B; font-size: 0.80rem; font-weight: 700; padding: 6px 14px; border-radius: 20px; border: 1px solid #FECACA;">
                    Prioritized Outreach Queue
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Clean 3x2 Balanced Metric Grid (Responsive & Highly Legible)
    high_pct = (filtered_high / filtered_total * 100) if filtered_total > 0 else 0
    med_pct = (filtered_med / filtered_total * 100) if filtered_total > 0 else 0
    low_pct = (filtered_low / filtered_total * 100) if filtered_total > 0 else 0
    
    # Row 1 of KPIs
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    with r1_c1:
        st.markdown(
            render_kpi_card("Total Students Monitored", str(filtered_total), f"Cohort Size ({selected_dept})", "blue"),
            unsafe_allow_html=True
        )
    with r1_c2:
        st.markdown(
            render_kpi_card("High-Risk Students", str(filtered_high), f"{high_pct:.1f}% of cohort · Immediate action", "red"),
            unsafe_allow_html=True
        )
    with r1_c3:
        st.markdown(
            render_kpi_card("Medium-Risk Watchlist", str(filtered_med), f"{med_pct:.1f}% of cohort · Preventative monitoring", "orange"),
            unsafe_allow_html=True
        )
        
    # Row 2 of KPIs
    r2_c1, r2_c2, r2_c3 = st.columns(3)
    with r2_c1:
        st.markdown(
            render_kpi_card("Low-Risk (On Track)", str(filtered_low), f"{low_pct:.1f}% of cohort · Healthy retention", "green"),
            unsafe_allow_html=True
        )
    with r2_c2:
        st.markdown(
            render_kpi_card("Cohort Avg Attendance", f"{filtered_att:.1f}%", "Regulatory minimum requirement: 75%", "teal"),
            unsafe_allow_html=True
        )
    with r2_c3:
        st.markdown(
            render_kpi_card("Cohort Avg CGPA", f"{filtered_cgpa:.2f}", "Grading scale: 0.00 – 10.00", "purple"),
            unsafe_allow_html=True
        )
        
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # Chart Row 1: Risk Distribution Donut & Attendance vs CGPA Scatter
    chart_r1_c1, chart_r1_c2 = st.columns([1.1, 1.9])
    with chart_r1_c1:
        st.subheader("📊 Student Risk Distribution")
        st.caption("Categorized by Random Forest into Low, Medium, and High Attrition Risk")
        pie_fig = create_risk_distribution_pie(filtered_df)
        st.plotly_chart(pie_fig, use_container_width=True)
        
    with chart_r1_c2:
        st.subheader("🎯 Attendance vs. Academic Performance (CGPA)")
        st.caption("Individual students plotted with 75% attendance threshold and 5.0 probation cutoff")
        scatter_fig = create_attendance_cgpa_scatter(filtered_df)
        st.plotly_chart(scatter_fig, use_container_width=True)
        
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    # Chart Row 2: Department Breakdown & Semester Trends
    chart_r2_c1, chart_r2_c2 = st.columns(2)
    with chart_r2_c1:
        st.subheader("🏢 Department-wise Risk Distribution")
        st.caption("Comparison of risk proportions across engineering disciplines")
        dept_risk_df = get_risk_by_department()
        dept_fig = create_department_risk_bar(dept_risk_df)
        st.plotly_chart(dept_fig, use_container_width=True)
        
    with chart_r2_c2:
        st.subheader("📈 Cohort Progression Across Semesters")
        st.caption("Historical trajectories of average attendance and cumulative GPA")
        trends_df = get_performance_trends()
        trends_fig = create_semester_performance_line(trends_df)
        st.plotly_chart(trends_fig, use_container_width=True)
        
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    # Chart Row 3: Explainable AI - Feature Importance
    st.subheader("🧠 Explainable AI: Key Risk Factors Influencing Attrition")
    st.caption("Feature importance contributions calculated from trained Random Forest ensemble trees")
    fi_dict = get_feature_importances()
    fi_fig = create_feature_importance_bar(fi_dict)
    st.plotly_chart(fi_fig, use_container_width=True)
