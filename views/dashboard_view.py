"""
EduGuard AI - Overview Institutional Dashboard View
Displays real-time KPIs, multi-factor correlation charts, risk distribution,
and explainable ML feature importance metrics.
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
    
    # Fetch dynamic data from SQLite
    kpis = get_institutional_kpis()
    all_students_df = get_all_students_with_predictions()
    departments = ["All Departments"] + get_all_departments()
    
    # Filter Row
    f_col1, f_col2, f_col3 = st.columns([2, 1.2, 1.2])
    with f_col1:
        selected_dept = st.selectbox("Filter Institutional View by Academic Department", departments)
    with f_col2:
        semester_filter = st.selectbox("Cohort Semester", ["All Semesters", "Semester 2", "Semester 4", "Semester 6", "Semester 8"])
    with f_col3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
            
    # Apply Department & Semester Filters to Dataset
    filtered_df = all_students_df.copy()
    if selected_dept != "All Departments":
        filtered_df = filtered_df[filtered_df["department"] == selected_dept]
    if semester_filter != "All Semesters":
        sem_num = int(semester_filter.replace("Semester ", ""))
        filtered_df = filtered_df[filtered_df["semester"] == sem_num]
        
    # Recompute local metrics for filtered view
    filtered_total = len(filtered_df)
    filtered_high = len(filtered_df[filtered_df["risk_level"] == "High Risk"])
    filtered_med = len(filtered_df[filtered_df["risk_level"] == "Medium Risk"])
    filtered_low = len(filtered_df[filtered_df["risk_level"] == "Low Risk"])
    filtered_att = filtered_df["attendance"].mean() if not filtered_df.empty else 0.0
    filtered_cgpa = filtered_df["cgpa"].mean() if not filtered_df.empty else 0.0
    
    # High-Risk Alert Banner
    if filtered_high > 0:
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #FEF2F2 0%, #FFF1F2 100%);
            border-left: 5px solid #EF4444;
            border-radius: 10px;
            padding: 14px 20px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            box-shadow: 0 2px 6px rgba(239, 68, 68, 0.08);
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.6rem;">⚠️</span>
                <div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #991B1B;">
                        Immediate Attention Required: {filtered_high} High-Risk Students Detected
                    </div>
                    <div style="font-size: 0.83rem; color: #B91C1C;">
                        Identified by Random Forest Classifier exhibiting critical deficits in attendance, CGPA, or tuition arrears.
                    </div>
                </div>
            </div>
            <div>
                <span style="font-size: 0.82rem; font-weight: 600; color: #991B1B; background: #FEE2E2; padding: 6px 12px; border-radius: 6px;">
                    Priority Outreach Queue
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # 6 KPI Metric Cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
    
    with kpi_col1:
        st.markdown(
            render_kpi_card(
                title="Total Monitored",
                value=str(filtered_total),
                subtitle="Active Enrolled Cohort",
                theme="blue"
            ),
            unsafe_allow_html=True
        )
    with kpi_col2:
        high_pct = (filtered_high / filtered_total * 100) if filtered_total > 0 else 0
        st.markdown(
            render_kpi_card(
                title="High-Risk",
                value=str(filtered_high),
                subtitle=f"{high_pct:.1f}% of cohort",
                theme="red"
            ),
            unsafe_allow_html=True
        )
    with kpi_col3:
        med_pct = (filtered_med / filtered_total * 100) if filtered_total > 0 else 0
        st.markdown(
            render_kpi_card(
                title="Medium-Risk",
                value=str(filtered_med),
                subtitle=f"{med_pct:.1f}% watchlist",
                theme="orange"
            ),
            unsafe_allow_html=True
        )
    with kpi_col4:
        low_pct = (filtered_low / filtered_total * 100) if filtered_total > 0 else 0
        st.markdown(
            render_kpi_card(
                title="Low-Risk",
                value=str(filtered_low),
                subtitle=f"{low_pct:.1f}% on track",
                theme="green"
            ),
            unsafe_allow_html=True
        )
    with kpi_col5:
        st.markdown(
            render_kpi_card(
                title="Avg Attendance",
                value=f"{filtered_att:.1f}%",
                subtitle="Regulatory Min: 75%",
                theme="teal"
            ),
            unsafe_allow_html=True
        )
    with kpi_col6:
        st.markdown(
            render_kpi_card(
                title="Avg CGPA",
                value=f"{filtered_cgpa:.2f}",
                subtitle="Scale of 10.0",
                theme="purple"
            ),
            unsafe_allow_html=True
        )
        
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    
    # Main Chart Row 1: Risk Distribution (Donut) & Attendance vs CGPA (Scatter)
    c1, c2 = st.columns([1.1, 1.9])
    with c1:
        st.markdown("""
        <div class="eduguard-card" style="margin-bottom: 0;">
            <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 4px;">
                📊 Student Risk Distribution
            </div>
            <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">
                Classified by Random Forest into Low, Medium, and High Attrition Risk
            </div>
        </div>
        """, unsafe_allow_html=True)
        pie_fig = create_risk_distribution_pie(filtered_df)
        st.plotly_chart(pie_fig, use_container_width=True)
        
    with c2:
        st.markdown("""
        <div class="eduguard-card" style="margin-bottom: 0;">
            <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 4px;">
                🎯 Attendance vs. Academic Performance (CGPA)
            </div>
            <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">
                Individual students mapped with 75% attendance line and 5.0 CGPA threshold
            </div>
        </div>
        """, unsafe_allow_html=True)
        scatter_fig = create_attendance_cgpa_scatter(filtered_df)
        st.plotly_chart(scatter_fig, use_container_width=True)
        
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    
    # Main Chart Row 2: Department Breakdown & Semester Trends
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.markdown("""
        <div class="eduguard-card" style="margin-bottom: 0;">
            <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 4px;">
                🏢 Department-wise Risk Distribution
            </div>
            <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">
                Comparison of high, medium, and low-risk cohorts across academic disciplines
            </div>
        </div>
        """, unsafe_allow_html=True)
        dept_risk_df = get_risk_by_department()
        dept_fig = create_department_risk_bar(dept_risk_df)
        st.plotly_chart(dept_fig, use_container_width=True)
        
    with row2_col2:
        st.markdown("""
        <div class="eduguard-card" style="margin-bottom: 0;">
            <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 4px;">
                📈 Student Performance Trends Across Semesters
            </div>
            <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">
                Historical progression of average attendance and cumulative GPA
            </div>
        </div>
        """, unsafe_allow_html=True)
        trends_df = get_performance_trends()
        trends_fig = create_semester_performance_line(trends_df)
        st.plotly_chart(trends_fig, use_container_width=True)
        
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    
    # Main Chart Row 3: Explainable AI - Feature Importance
    st.markdown("""
    <div class="eduguard-card" style="margin-bottom: 0;">
        <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 4px;">
            🧠 Explainable AI: Key Risk Factors Influencing Model Predictions
        </div>
        <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">
            Feature importance scores calculated from trained Random Forest ensemble trees
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fi_dict = get_feature_importances()
    fi_fig = create_feature_importance_bar(fi_dict)
    st.plotly_chart(fi_fig, use_container_width=True)
