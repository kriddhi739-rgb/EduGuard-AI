"""
EduGuard AI - Data Visualization Suite
Generates modern, interactive Plotly charts with corporate EdTech styling.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any, List

COLOR_PALETTE = {
    "Low Risk": "#10B981",       # Emerald Green
    "Medium Risk": "#F59E0B",    # Amber Yellow
    "High Risk": "#EF4444",      # Rose Red
    "Primary Blue": "#2563EB",   # Vibrant Blue
    "Purple": "#6366F1",         # Royal Purple
    "Teal": "#0D9488",           # Deep Teal
    "Light Bg": "#F8FAFC",
    "Card Bg": "#FFFFFF"
}

CHART_LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, Inter, sans-serif", size=12, color="#1E293B"),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

def create_risk_distribution_pie(df: pd.DataFrame) -> go.Figure:
    """Creates a donut chart displaying student risk proportions."""
    if df.empty or "risk_level" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False, font=dict(size=14))
        return fig
        
    counts = df["risk_level"].value_counts().reset_index()
    counts.columns = ["Risk_Level", "Count"]
    
    # Ensure correct ordering
    order_map = {"Low Risk": 0, "Medium Risk": 1, "High Risk": 2}
    counts["Order"] = counts["Risk_Level"].map(order_map).fillna(3)
    counts = counts.sort_values("Order")
    
    colors = [COLOR_PALETTE.get(level, "#94A3B8") for level in counts["Risk_Level"]]
    
    fig = go.Figure(data=[go.Pie(
        labels=counts["Risk_Level"],
        values=counts["Count"],
        hole=0.58,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        textfont=dict(size=13, family="Plus Jakarta Sans", weight="bold")
    )])
    
    total_students = len(df)
    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        showlegend=False,
        annotations=[dict(
            text=f"<b style='font-size:22px; color:#0F172A;'>{total_students}</b><br><span style='font-size:11px; color:#64748B;'>STUDENTS</span>",
            x=0.5, y=0.5, font_size=13, showarrow=False
        )]
    )
    return fig

def create_attendance_cgpa_scatter(df: pd.DataFrame) -> go.Figure:
    """Creates a scatter plot showing relationship between Attendance and CGPA."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
        
    hover_cols = ["student_name", "student_id", "department"] if "student_name" in df.columns else None
    
    color_map = {
        "Low Risk": COLOR_PALETTE["Low Risk"],
        "Medium Risk": COLOR_PALETTE["Medium Risk"],
        "High Risk": COLOR_PALETTE["High Risk"]
    }
    
    fig = px.scatter(
        df,
        x="attendance",
        y="cgpa",
        color="risk_level",
        color_discrete_map=color_map,
        hover_name="student_name" if "student_name" in df.columns else None,
        hover_data={"attendance": ':.1f', "cgpa": ':.2f', "student_id": True, "department": True},
        labels={"attendance": "Attendance Percentage (%)", "cgpa": "CGPA (0 - 10)", "risk_level": "Risk Level"}
    )
    
    # Add regulatory warning threshold lines
    fig.add_vline(x=75.0, line_dash="dash", line_color="#94A3B8", 
                  annotation_text="75% Min. Attendance", annotation_position="top left", annotation_font_size=10)
    fig.add_hline(y=5.0, line_dash="dash", line_color="#F87171", 
                  annotation_text="5.0 Academic Probation", annotation_position="bottom right", annotation_font_size=10)
    
    fig.update_traces(marker=dict(size=9, opacity=0.85, line=dict(width=1, color="white")))
    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        xaxis=dict(gridcolor="#E2E8F0", zeroline=False, range=[20, 105]),
        yaxis=dict(gridcolor="#E2E8F0", zeroline=False, range=[1.5, 10.5])
    )
    return fig

def create_department_risk_bar(dept_df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart showing risk distribution per academic department."""
    if dept_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No department data", showarrow=False)
        return fig
        
    color_map = {
        "Low Risk": COLOR_PALETTE["Low Risk"],
        "Medium Risk": COLOR_PALETTE["Medium Risk"],
        "High Risk": COLOR_PALETTE["High Risk"]
    }
    
    fig = px.bar(
        dept_df,
        x="department",
        y="count",
        color="risk_level",
        barmode="group",
        color_discrete_map=color_map,
        labels={"department": "Academic Department", "count": "Student Count", "risk_level": "Risk Level"}
    )
    
    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        xaxis=dict(gridcolor="#E2E8F0", tickangle=-15),
        yaxis=dict(gridcolor="#E2E8F0")
    )
    return fig

def create_semester_performance_line(trends_df: pd.DataFrame) -> go.Figure:
    """Line chart showing cohort academic performance across semesters."""
    if trends_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No semester trend data", showarrow=False)
        return fig
        
    fig = go.Figure()
    
    # Attendance trace (secondary y or normalized)
    fig.add_trace(go.Scatter(
        x=[f"Sem {s}" for s in trends_df["semester"]],
        y=trends_df["avg_attendance"],
        name="Avg Attendance (%)",
        mode="lines+markers",
        line=dict(color=COLOR_PALETTE["Primary Blue"], width=3),
        marker=dict(size=8),
        yaxis="y1"
    ))
    
    # CGPA trace
    fig.add_trace(go.Scatter(
        x=[f"Sem {s}" for s in trends_df["semester"]],
        y=trends_df["avg_cgpa"],
        name="Avg CGPA (x10 scale)",
        mode="lines+markers",
        line=dict(color=COLOR_PALETTE["Purple"], width=3, dash="dot"),
        marker=dict(size=8),
        yaxis="y2"
    ))
    
    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        xaxis=dict(gridcolor="#E2E8F0"),
        yaxis=dict(title=dict(text="Attendance (%)", font=dict(color=COLOR_PALETTE["Primary Blue"])), 
                   tickfont=dict(color=COLOR_PALETTE["Primary Blue"]), gridcolor="#E2E8F0", range=[40, 100]),
        yaxis2=dict(title=dict(text="CGPA", font=dict(color=COLOR_PALETTE["Purple"])),
                    tickfont=dict(color=COLOR_PALETTE["Purple"]), overlaying="y", side="right", range=[2, 10])
    )
    return fig

def create_feature_importance_bar(feature_importances: Dict[str, float]) -> go.Figure:
    """Horizontal bar chart representing Random Forest feature weights."""
    feature_labels = {
        "attendance": "Attendance Percentage",
        "cgpa": "Cumulative GPA (CGPA)",
        "fee_dues": "Pending Fee Dues ($)",
        "lms_activity": "LMS Platform Activity"
    }
    
    data = []
    for k, v in feature_importances.items():
        data.append({"Feature": feature_labels.get(k, k.replace('_', ' ').title()), "Importance": v * 100})
        
    df = pd.DataFrame(data).sort_values("Importance", ascending=True)
    
    fig = px.bar(
        df,
        x="Importance",
        y="Feature",
        orientation="h",
        labels={"Importance": "Model Weight Contribution (%)", "Feature": ""},
        text=[f"{v:.1f}%" for v in df["Importance"]]
    )
    
    fig.update_traces(
        marker=dict(
            color=df["Importance"],
            colorscale=[[0, "#93C5FD"], [0.5, "#3B82F6"], [1, "#1D4ED8"]],
            line=dict(width=1, color="white")
        ),
        textposition="outside"
    )
    
    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        xaxis=dict(gridcolor="#E2E8F0", range=[0, max(df["Importance"]) * 1.25]),
        yaxis=dict(gridcolor="#E2E8F0")
    )
    return fig

def create_probability_breakdown_bar(prob_dict: Dict[str, float]) -> go.Figure:
    """Stacked probability bar showing Low, Medium, and High percentages."""
    p_low = prob_dict.get("Low Risk", 0.0) * 100
    p_med = prob_dict.get("Medium Risk", 0.0) * 100
    p_high = prob_dict.get("High Risk", 0.0) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=["Probability"], x=[p_low], name=f"Low Risk ({p_low:.1f}%)",
        orientation="h", marker=dict(color=COLOR_PALETTE["Low Risk"])
    ))
    fig.add_trace(go.Bar(
        y=["Probability"], x=[p_med], name=f"Medium Risk ({p_med:.1f}%)",
        orientation="h", marker=dict(color=COLOR_PALETTE["Medium Risk"])
    ))
    fig.add_trace(go.Bar(
        y=["Probability"], x=[p_high], name=f"High Risk ({p_high:.1f}%)",
        orientation="h", marker=dict(color=COLOR_PALETTE["High Risk"])
    ))
    
    fig.update_layout(
        barmode="stack",
        height=100,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 100]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

def create_confusion_matrix_heatmap(cm_matrix: List[List[int]], class_names: List[str]) -> go.Figure:
    """Heatmap displaying model confusion matrix on the test set."""
    fig = px.imshow(
        cm_matrix,
        x=class_names,
        y=class_names,
        labels=dict(x="Predicted Risk Level", y="Actual Ground Truth", color="Students"),
        color_continuous_scale="Blues",
        text_auto=True
    )
    
    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        xaxis=dict(side="bottom"),
        height=320
    )
    return fig
