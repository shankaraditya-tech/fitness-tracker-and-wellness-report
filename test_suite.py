"""
=============================================================================
Automated Test Suite for Fitness Tracker & Report Generator
=============================================================================
Course: Computational Thinking and Programming (2026CSAE100)
Bennett University (SCSET)

Tests all modules, routes, calculations, CSV operations, and Matplotlib charts.
=============================================================================
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fitness import (
    calculate_bmi,
    get_bmi_category,
    calculate_bmr,
    calculate_tdee,
    calculate_calories_burned,
    validate_profile_data,
    validate_activity_data,
    validate_goals_data
)
from csv_manager import (
    init_csv_files,
    seed_demo_data,
    load_profiles,
    get_profile,
    save_profile,
    load_activities,
    get_activity_by_id,
    save_activity,
    delete_activity,
    calculate_user_statistics
)
from report_generator import (
    generate_weekly_activity_chart,
    generate_activity_distribution_chart,
    generate_hydration_trends_chart,
    generate_wellness_report_data
)
from app import app


def test_fitness_calculations():
    print("[1/5] Testing Mathematical Calculations & Pediatric Safeguards...")

    # 1. BMI calculation: 70kg, 175cm -> 70 / (1.75^2) = 70 / 3.0625 = 22.86
    bmi = calculate_bmi(70.0, 175.0)
    assert abs(bmi - 22.86) < 0.05, f"Expected ~22.86, got {bmi}"

    # Adult BMI category
    adult_cat = get_bmi_category(bmi, age=20)
    assert adult_cat["is_pediatric"] is False
    assert adult_cat["category"] == "Normal weight"

    # Pediatric BMI category (< 18)
    child_cat = get_bmi_category(bmi, age=16)
    assert child_cat["is_pediatric"] is True
    assert "Pediatric" in child_cat["category"]

    # 2. Mifflin-St Jeor BMR:
    # Male: 10*70 + 6.25*175 - 5*20 + 5 = 700 + 1093.75 - 100 + 5 = 1698.75 -> 1698.8
    bmr_m = calculate_bmr(70.0, 175.0, 20, "male")
    assert abs(bmr_m - 1698.8) < 0.5, f"Expected ~1698.8, got {bmr_m}"

    # Female: 10*60 + 6.25*165 - 5*22 - 161 = 600 + 1031.25 - 110 - 161 = 1360.25 -> 1360.2
    bmr_f = calculate_bmr(60.0, 165.0, 22, "female")
    assert abs(bmr_f - 1360.2) < 0.5, f"Expected ~1360.2, got {bmr_f}"

    # 3. TDEE with moderate activity (1.55)
    tdee_adult = calculate_tdee(bmr_m, "moderate", age=20)
    assert tdee_adult["is_pediatric"] is False
    assert tdee_adult["recommended_ranges"] is not None

    # TDEE for age < 18 (Adult calorie ranges should be None)
    tdee_minor = calculate_tdee(bmr_m, "moderate", age=15)
    assert tdee_minor["is_pediatric"] is True
    assert tdee_minor["recommended_ranges"] is None

    # 4. MET Calories calculation: Running for 30 min at 70kg (MET 9.8)
    # Calories = 9.8 * 3.5 * 70 / 200 * 30 = 360.15 -> 360
    cals = calculate_calories_burned("Running", 30, 70.0)
    assert abs(cals - 360) <= 2, f"Expected ~360, got {cals}"

    print("  ✓ All mathematical calculations & pediatric safeguards passed!")


def test_csv_persistence():
    print("[2/5] Testing CSV File Handling & Duplicate Prevention...")

    init_csv_files()
    seed_demo_data()

    profiles = load_profiles()
    assert len(profiles) >= 1, "Profiles should not be empty after seeding."
    user1 = get_profile("1")
    assert user1 is not None
    assert user1["name"] == "Arjun Sharma"

    activities = load_activities("1")
    assert len(activities) >= 10, "Should have seeded 14 demonstration days."

    # Test duplicate prevention / update logic
    test_entry = {
        "id": "",
        "user_id": "1",
        "date": "2026-11-20",
        "steps": 12000,
        "exercise_minutes": 55,
        "water_litres": 3.5,
        "calories_burned": 450,
        "activity_type": "Gym/Strength",
        "notes": "Test Duplicate Handling"
    }

    # Save once
    ok1, msg1, id1 = save_activity(test_entry, allow_update=True)
    assert ok1 is True

    # Save again on same date with allow_update=False
    ok2, msg2, id2 = save_activity(test_entry, allow_update=False)
    assert ok2 is False, "Duplicate entry should be blocked when allow_update is False"

    # Save again on same date with allow_update=True
    test_entry["steps"] = 13500
    ok3, msg3, id3 = save_activity(test_entry, allow_update=True)
    assert ok3 is True
    updated_act = get_activity_by_id(id3)
    assert updated_act["steps"] == 13500, "Record steps should have updated"

    # Test user statistics calculation
    stats = calculate_user_statistics("1")
    assert stats["total_days"] > 0
    assert stats["avg_steps"] > 0
    assert stats["step_goal_completion_pct"] > 0

    print("  ✓ CSV persistence, duplicate prevention, and statistics passed!")


def test_matplotlib_charts():
    print("[3/5] Testing Matplotlib Headless Chart Generation...")

    activities = load_activities("1")
    user_profile = get_profile("1")

    # Generate weekly activity chart
    c1 = generate_weekly_activity_chart(activities, user_profile["step_goal"], "1")
    assert c1 is not None and os.path.exists(os.path.join(os.path.dirname(__file__), "static", c1))

    # Generate distribution chart
    c2 = generate_activity_distribution_chart(activities, "1")
    assert c2 is not None and os.path.exists(os.path.join(os.path.dirname(__file__), "static", c2))

    # Generate hydration chart
    c3 = generate_hydration_trends_chart(activities, user_profile["water_goal"], "1")
    assert c3 is not None and os.path.exists(os.path.join(os.path.dirname(__file__), "static", c3))

    # Generate full report data
    stats = calculate_user_statistics("1")
    rep = generate_wellness_report_data(user_profile, activities, stats)
    assert "report_id" in rep
    assert len(rep["observations"]) > 0
    assert "Computational Thinking" in rep["ct_reflection"]

    print("  ✓ Matplotlib charts generated and saved successfully!")


def test_flask_routes():
    print("[4/5] Testing Flask Web Application Routes...")

    client = app.test_client()

    routes_to_test = [
        ("/", 200),
        ("/dashboard", 200),
        ("/profile", 200),
        ("/profile/new", 200),
        ("/calculator", 200),
        ("/tracker", 200),
        ("/progress", 200),
        ("/report", 200),
        ("/seed-demo", 302)  # Redirects to /dashboard
    ]

    for route, expected_status in routes_to_test:
        response = client.get(route, follow_redirects=(expected_status == 200))
        assert response.status_code == expected_status, f"Route {route} returned status {response.status_code}, expected {expected_status}"

    # Test API calculate endpoint for Adult
    api_resp_adult = client.post("/api/calculate", json={
        "age": 20,
        "height": 175,
        "weight": 70,
        "sex": "male",
        "activity_level": "moderate"
    })
    assert api_resp_adult.status_code == 200
    res_data = api_resp_adult.get_json()
    assert res_data["success"] is True
    assert res_data["is_pediatric"] is False
    assert "recommended_ranges" in res_data

    # Test API calculate endpoint for Minor (< 18)
    api_resp_minor = client.post("/api/calculate", json={
        "age": 16,
        "height": 165,
        "weight": 55,
        "sex": "female",
        "activity_level": "light"
    })
    assert api_resp_minor.status_code == 200
    res_minor_data = api_resp_minor.get_json()
    assert res_minor_data["is_pediatric"] is True
    assert res_minor_data["recommended_ranges"] is None

    print("  ✓ All Flask routes and JSON API endpoints returned HTTP 200 OK!")


def run_all():
    print("=" * 65)
    print("RUNNING COMPLETE AUTOMATED TEST SUITE (2026CSAE100)")
    print("=" * 65)
    test_fitness_calculations()
    test_csv_persistence()
    test_matplotlib_charts()
    test_flask_routes()
    print("=" * 65)
    print("ALL TESTS PASSED WITH 100% SUCCESS! APPLICATION IS READY.")
    print("=" * 65)


if __name__ == "__main__":
    run_all()
