"""
EduGuard AI - UI Helpers, HTML Formatters & Badge Generators
"""

from typing import Optional

def get_risk_badge_html(risk_level: str) -> str:
    """Generates a styled HTML badge pill for risk levels."""
    risk_level = str(risk_level).strip()
    
    if "Low" in risk_level:
        bg, color, border, icon = "#ECFDF5", "#065F46", "#A7F3D0", "🟢"
    elif "Med" in risk_level:
        bg, color, border, icon = "#FFFBEB", "#92400E", "#FDE68A", "🟡"
    else:  # High Risk
        bg, color, border, icon = "#FEF2F2", "#991B1B", "#FECACA", "🔴"
        
    return (
        f'<span style="display: inline-flex; align-items: center; gap: 6px; background-color: {bg}; '
        f'color: {color}; border: 1px solid {border}; padding: 3px 10px; border-radius: 9999px; '
        f'font-size: 0.82rem; font-weight: 700; letter-spacing: 0.02em; white-space: nowrap;">'
        f'<span>{icon}</span> {risk_level}'
        f'</span>'
    )

def get_status_badge_html(status: str) -> str:
    """Generates a styled badge for intervention action statuses."""
    status = str(status).strip()
    
    if status == "Completed":
        bg, color, border, icon = "#ECFDF5", "#065F46", "#A7F3D0", "✓"
    elif status == "In Progress":
        bg, color, border, icon = "#EFF6FF", "#1E40AF", "#BFDBFE", "⏳"
    else:  # Pending
        bg, color, border, icon = "#FFFBEB", "#92400E", "#FDE68A", "⚠"
        
    return (
        f'<span style="display: inline-flex; align-items: center; gap: 5px; background-color: {bg}; '
        f'color: {color}; border: 1px solid {border}; padding: 3px 10px; border-radius: 6px; '
        f'font-size: 0.80rem; font-weight: 600; white-space: nowrap;">'
        f'<span>{icon}</span> {status}'
        f'</span>'
    )

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
    sub_html = f'<div class="kpi-subtitle">{subtitle}</div>' if subtitle else ''
    return (
        f'<div class="kpi-card {theme}">'
        f'<div class="kpi-title">{title}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{sub_html}'
        f'</div>'
    )

def render_banner(title: str, subtitle: str, role_badge: str = "") -> str:
    """Renders top hero banner."""
    badge_html = f'<div class="user-pill">{role_badge}</div>' if role_badge else ''
    return (
        '<div class="eduguard-header">'
        '<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">'
        '<div>'
        f'<h1>{title}</h1>'
        f'<p>{subtitle}</p>'
        '</div>'
        f'{badge_html}'
        '</div>'
        '</div>'
    )
