"""
EduGuard AI Branding and Icons
"""

def get_logo_svg(width=48, height=48):
    """Returns clean, unindented SVG representation of EduGuard AI shield logo"""
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<defs>'
        '<linearGradient id="shieldGrad" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">'
        '<stop offset="0%" stop-color="#3B82F6"/>'
        '<stop offset="50%" stop-color="#2563EB"/>'
        '<stop offset="100%" stop-color="#4F46E5"/>'
        '</linearGradient>'
        '<linearGradient id="capGrad" x1="20" y1="20" x2="80" y2="80" gradientUnits="userSpaceOnUse">'
        '<stop offset="0%" stop-color="#FACC15"/>'
        '<stop offset="100%" stop-color="#F59E0B"/>'
        '</linearGradient>'
        '</defs>'
        '<path d="M50 8L86 22V50C86 73 70.5 90 50 96C29.5 90 14 73 14 50V22L50 8Z" fill="url(#shieldGrad)" stroke="#60A5FA" stroke-width="3" stroke-linejoin="round"/>'
        '<path d="M50 14L80 26V50C80 69.5 67 84 50 89C33 84 20 69.5 20 50V26L50 14Z" stroke="white" stroke-opacity="0.25" stroke-width="2"/>'
        '<polygon points="50,30 74,42 50,54 26,42" fill="white"/>'
        '<path d="M34 46V56C34 62 41 66 50 66C59 66 66 62 66 56V46L50 54L34 46Z" fill="#E2E8F0"/>'
        '<path d="M70 44V60C70 62 68 64 68 66" stroke="url(#capGrad)" stroke-width="2.5" stroke-linecap="round"/>'
        '<circle cx="68" cy="67" r="2.5" fill="#F59E0B"/>'
        '</svg>'
    )

def get_sidebar_brand_html():
    svg = get_logo_svg(40, 40)
    return (
        '<div style="display: flex; align-items: center; gap: 12px; padding: 10px 4px; margin-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.12);">'
        f'<div>{svg}</div>'
        '<div>'
        '<div style="font-size: 1.25rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em; line-height: 1.1;">EduGuard <span style="color: #60A5FA;">AI</span></div>'
        '<div style="font-size: 0.72rem; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px;">Retention Platform</div>'
        '</div>'
        '</div>'
    )
