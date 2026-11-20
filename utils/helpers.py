"""
EduGuard AI - UI Helpers, HTML Formatters & Badge Generators
"""

from typing import Optional

def get_risk_badge_html(risk_level: str) -> str:
    """Generates a styled HTML badge pill for risk levels."""
    risk_level = str(risk_level).strip()
    
    if "Low" in risk_level:
        bg = "#ECFDF5"
        color = "#065F46"
        border = "#A7F3D0"
        icon = "🟢"
    elif "Med" in risk_level:
        bg = "#FFFBEB"
        color = "#92400E"
        border = "#FDE68A"
        icon = "🟡"
    else:  # High Risk
        bg = "#FEF2F2"
        color = "#991B1B"
        border = "#FECACA"
        icon = "🔴"
        
    return f"""
    <span style="
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: {bg};
        color: {color};
        border: 1px solid {border};
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        white-space: nowrap;
    ">
        <span>{icon}</span> {risk_level}
    </span>
    """

def get_status_badge_html(status: str) -> str:
    """Generates a styled badge for intervention action statuses."""
    status = str(status).strip()
    
    if status == "Completed":
        bg = "#ECFDF5"
        color = "#065F46"
        border = "#A7F3D0"
        icon = "✓"
    elif status == "In Progress":
        bg = "#EFF6FF"
        color = "#1E40AF"
        border = "#BFDBFE"
        icon = "⏳"
    else:  # Pending
        bg = "#FFFBEB"
        color = "#92400E"
        border = "#FDE68A"
        icon = "⚠"
        
    return f"""
    <span style="
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background-color: {bg};
        color: {color};
        border: 1px solid {border};
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.80rem;
        font-weight: 600;
        white-space: nowrap;
    ">
        <span>{icon}</span> {status}
    </span>
    """

def format_currency(amount: float) -> str:
    """Formats numeric amount as currency string."""
    try:
        val = float(amount)
        return f"${val:,.0f}"
    except (ValueError, TypeError):
        return "$0"

def format_percentage(val: float) -> str:
    """Formats numeric value as percentage."""
    try:
        return f"{float(val):.1f}%"
    except (ValueError, TypeError):
        return "0.0%"

def render_kpi_card(title: str, value: str, subtitle: str = "", theme: str = "blue") -> str:
    """
    Renders modern HTML KPI card with top colored accent line.
    Theme: 'blue', 'purple', 'teal', 'green', 'orange', 'red'
    """
    return f"""
    <div class="kpi-card {theme}">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-subtitle">{subtitle}</div>' if subtitle else ''}
    </div>
    """

def render_banner(title: str, subtitle: str, role_badge: str = "") -> str:
    """Renders top hero banner."""
    badge_html = f'<div class="user-pill">{role_badge}</div>' if role_badge else ''
    return f"""
    <div class="eduguard-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
            {badge_html}
        </div>
    </div>
    """
