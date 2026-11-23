"""
Comprehensive Render Deployment Verification Suite for EduGuard AI
Tests database, ML model, predictions, charts, reports, assets, and environmental variables.
"""

import os
import sys

# Ensure root directory is on Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def run_checks():
    print("=" * 60)
    print("[DEPLOYMENT AUDIT] RUNNING EDUGUARD AI DEPLOYMENT VERIFICATION")
    print("=" * 60)

    # 1. Check Assets
    print("[1/8] Checking Assets & CSS Files...")
    css_path = os.path.join(BASE_DIR, "assets", "styles.css")
    assert os.path.exists(css_path), f"CSS file missing at {css_path}"
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()
    assert len(css) > 100, "CSS file is empty"
    print("  [OK] CSS stylesheet verified.")

    # 2. Check Database Initialization
    print("[2/8] Checking SQLite Database Schema & Tables...")
    from backend.database import init_database, get_connection
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    for table in ["Users", "Students", "Prediction_Results", "Intervention_Logs"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        cnt = cursor.fetchone()[0]
        print(f"  [OK] Table '{table}' verified (records: {cnt}).")
    conn.close()

    # 3. Check Authentication
    print("[3/8] Checking Authentication Service...")
    from backend.authentication import authenticate_user, get_all_counselors
    user = authenticate_user("admin", "admin123")
    assert user is not None and user["role"] == "admin", "Admin authentication failed"
    counselor = authenticate_user("counselor", "counselor123")
    assert counselor is not None and counselor["role"] == "counselor", "Counselor auth failed"
    print("  [OK] Authentication workflows functioning properly.")

    # 4. Check ML Model & Inference
    print("[4/8] Checking ML Model Artifacts & Inference Pipeline...")
    from ml.predict import get_model_bundle, predict_student, batch_predict
    bundle = get_model_bundle()
    assert bundle is not None and "model" in bundle, "ML bundle invalid"
    metrics = bundle.get("metrics", {})
    print(f"  [OK] Random Forest loaded. Accuracy: {metrics.get('accuracy', 0)*100:.2f}%, F1: {metrics.get('f1_score', 0)*100:.2f}%")

    pred = predict_student(attendance=55.0, cgpa=4.8, lms_activity=30.0, fee_dues=2500.0)
    assert pred["risk_level"] in ["Low Risk", "Medium Risk", "High Risk"], "Prediction failed"
    assert 0 <= pred["risk_score"] <= 100, "Risk score out of bounds"
    assert len(pred["factors"]) > 0, "No diagnostic factors generated"
    assert len(pred["advisory"]) > 10, "Advisory missing"
    print(f"  [OK] Single student prediction test passed: Risk={pred['risk_level']}, Score={pred['risk_score']:.1f}")

    # 5. Check Student & Intervention Services
    print("[5/8] Checking Backend Student & Intervention Services...")
    from backend.student_service import (
        get_all_students_with_predictions, get_institutional_kpis,
        get_risk_by_department, get_performance_trends
    )
    from backend.intervention_service import get_interventions, get_intervention_kpis

    kpis = get_institutional_kpis()
    assert kpis["total_students"] > 0, "No students monitored in KPIs"
    students_df = get_all_students_with_predictions()
    assert len(students_df) > 0, "Students dataframe empty"

    inv_kpis = get_intervention_kpis()
    assert inv_kpis["total"] >= 0, "Intervention KPIs error"
    print(f"  [OK] Services verified: Monitored Students={kpis['total_students']}, Interventions={inv_kpis['total']}")

    # 6. Check Plotly Visualizations
    print("[6/8] Checking Plotly Chart Builders...")
    from utils.charts import (
        create_risk_distribution_pie, create_attendance_cgpa_scatter,
        create_department_risk_bar, create_semester_performance_line,
        create_feature_importance_bar, create_probability_breakdown_bar,
        create_confusion_matrix_heatmap
    )
    from ml.model_evaluation import get_feature_importances, get_model_metrics

    pie = create_risk_distribution_pie(students_df)
    scatter = create_attendance_cgpa_scatter(students_df)
    bar = create_department_risk_bar(get_risk_by_department())
    line = create_semester_performance_line(get_performance_trends())
    fi = create_feature_importance_bar(get_feature_importances())
    prob = create_probability_breakdown_bar(pred["probabilities"])
    cm = create_confusion_matrix_heatmap(get_model_metrics()["confusion_matrix"], ["Low", "Med", "High"])
    print("  [OK] All 7 Plotly interactive chart builders validated successfully.")

    # 7. Check Multi-Format Export Generators (PDF, Excel, CSV)
    print("[7/8] Checking PDF, Excel, and CSV Generators...")
    from utils.report_generator import generate_pdf_report, generate_excel_report, generate_student_pdf_dossier

    pdf_bytes = generate_pdf_report(kpis, students_df)
    assert len(pdf_bytes) > 500 and isinstance(pdf_bytes, bytes), "PDF generation failed"

    excel_bytes = generate_excel_report(kpis, students_df)
    assert len(excel_bytes) > 500 and isinstance(excel_bytes, bytes), "Excel generation failed"

    first_profile = students_df.iloc[0].to_dict()
    first_profile["interventions"] = []
    dossier_pdf = generate_student_pdf_dossier(first_profile)
    assert len(dossier_pdf) > 500 and isinstance(dossier_pdf, bytes), "Dossier PDF failed"
    print(f"  [OK] Exports validated: PDF ({len(pdf_bytes)} B), Excel ({len(excel_bytes)} B), Dossier ({len(dossier_pdf)} B)")

    # 8. Check Streamlit and Render configuration
    print("[8/8] Checking Render Environment Compatibility & Config...")
    import re
    config_path = os.path.join(BASE_DIR, ".streamlit", "config.toml")
    assert os.path.exists(config_path), "Streamlit config missing"
    with open(config_path, "r", encoding="utf-8") as f:
        streamlit_config = f.read()
    assert re.search(r"(?m)^enableCORS\s*=\s*true\s*$", streamlit_config), "Streamlit CORS protection must be enabled"
    assert re.search(r"(?m)^enableXsrfProtection\s*=\s*true\s*$", streamlit_config), "Streamlit XSRF protection must be enabled"

    render_path = os.path.join(BASE_DIR, "render.yaml")
    assert os.path.exists(render_path), "Render Blueprint missing"
    with open(render_path, "r", encoding="utf-8") as f:
        render_config = f.read()
    assert re.search(r"(?m)^\s*plan:\s*free\s*$", render_config), "Render service plan must match the selected Free tier"
    assert "pip install -r requirements.txt" in render_config, "Render dependency installation command missing"
    assert "--server.port $PORT" in render_config, "Render start command must use the assigned PORT"
    assert re.search(r'(?m)^\s*value:\s*"true"\s*$', render_config), "Render protection settings must be enabled"

    version_path = os.path.join(BASE_DIR, ".python-version")
    assert os.path.exists(version_path), "Python version pin missing"
    with open(version_path, "r", encoding="utf-8") as f:
        python_version = f.read().strip()
    assert python_version == "3.11.9", "Render Python version pin does not match the documented runtime"

    print(f"  [OK] Render Blueprint, Streamlit protections, and Python {python_version} pin verified.")
    print("=" * 60)
    print("[SUCCESS] ALL 8 AUDIT GATES PASSED! APPLICATION READY FOR RENDER.")
    print("=" * 60)

if __name__ == "__main__":
    run_checks()
