"""
=============================================================================
Fitness Tracker & Personal Wellness Report Generator - Web Application
=============================================================================
Course: Computational Thinking and Programming (2026CSAE100)
Institution: Bennett University, School of Computer Science Engg. & Technology
Academic Year: 2026–27

Core Flask application file coordinating:
- HTTP request routing and template rendering
- User session state management
- Flash messaging for intuitive UX feedback
- Integration with fitness mathematics and CSV persistence layers
- Educational wellness report presentation and printable exports

Python Concepts Demonstrated:
- Modular architecture with clean separation of concerns
- Flask routing decorators (@app.route)
- HTTP methods (GET, POST) and form handling
- Session handling and state preservation
- Defensive programming with try-except blocks and input validation
=============================================================================
"""

import os
from datetime import date, datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify, abort
)

from fitness import (
    validate_profile_data,
    validate_activity_data,
    validate_goals_data,
    calculate_bmi,
    get_bmi_category,
    calculate_bmr,
    calculate_tdee,
    calculate_calories_burned,
    evaluate_fitness_profile,
    get_fitness_disclaimer,
    ACTIVITY_MULTIPLIERS,
    ACTIVITY_MET_VALUES
)

from csv_manager import (
    init_csv_files,
    load_profiles,
    get_profile,
    save_profile,
    load_activities,
    get_activity_by_id,
    get_activity_by_date,
    save_activity,
    delete_activity,
    calculate_user_statistics,
    seed_demo_data
)

from report_generator import (
    generate_weekly_activity_chart,
    generate_activity_distribution_chart,
    generate_hydration_trends_chart,
    generate_wellness_report_data
)

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "bennett_bu_cse_2026_fitness_tracker_secret")

# Academic metadata for Bennett University
ACADEMIC_INFO = {
    "university": "Bennett University",
    "school": "School of Computer Science Engineering and Technology",
    "course_name": "Computational Thinking and Programming",
    "course_code": "2026CSAE100",
    "academic_year": "2026–27",
    "project_title": "Fitness Tracker & Personal Wellness Report Generator"
}


# ---------------------------------------------------------------------------
# CONTEXT PROCESSOR & HELPER UTILITIES
# ---------------------------------------------------------------------------

@app.context_processor
def inject_global_template_vars():
    """
    Injects universal variables (academic info, current user, date) into all templates.
    """
    profiles = load_profiles()
    current_user_id = session.get("user_id")

    current_user = None
    if current_user_id:
        current_user = get_profile(current_user_id)

    # If no valid user in session, default to first existing profile
    if not current_user and profiles:
        current_user = profiles[0]
        session["user_id"] = current_user["id"]

    return {
        "academic": ACADEMIC_INFO,
        "current_user": current_user,
        "all_profiles": profiles,
        "today_str": date.today().strftime("%Y-%m-%d"),
        "now_year": datetime.now().year
    }


def get_active_user_id() -> str:
    """Helper to ensure an active profile exists; creates demo if none exist."""
    user_id = session.get("user_id")
    if not user_id or not get_profile(user_id):
        profiles = load_profiles()
        if not profiles:
            seed_demo_data()
            profiles = load_profiles()
        user_id = profiles[0]["id"]
        session["user_id"] = user_id
    return str(user_id)


# ---------------------------------------------------------------------------
# ROUTES & CONTROLLERS
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """
    Landing / Welcome Page.
    Introduces the system, academic context, and quick action pathways.
    """
    user_id = get_active_user_id()
    profile = get_profile(user_id)
    stats = calculate_user_statistics(user_id)
    return render_template("index.html", profile=profile, stats=stats)


@app.route("/dashboard")
def dashboard():
    """
    Main Modern Fitness Dashboard.
    Displays:
    - Welcome greeting (time-aware)
    - Profile summary & BMI status
    - Daily activity stats (latest log)
    - Personal goals with circular and bar progress meters
    - Weekly activity chart (generated via Matplotlib)
    - Recent activity history log
    """
    user_id = get_active_user_id()
    profile = get_profile(user_id)
    activities = load_activities(user_id)
    stats = calculate_user_statistics(user_id)

    # Greeting based on local hour
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # Latest logged day activity
    latest_activity = activities[-1] if activities else None

    # Step, Exercise, and Water progress for today / latest log
    step_goal = profile.get("step_goal", 10000)
    exercise_goal = profile.get("exercise_goal", 45)
    water_goal = profile.get("water_goal", 3.0)

    if latest_activity:
        today_steps = latest_activity["steps"]
        today_exercise = latest_activity["exercise_minutes"]
        today_water = latest_activity["water_litres"]
        today_calories = latest_activity["calories_burned"]
    else:
        today_steps = 0
        today_exercise = 0
        today_water = 0.0
        today_calories = 0

    step_progress_pct = min(100, round((today_steps / step_goal) * 100)) if step_goal > 0 else 0
    exercise_progress_pct = min(100, round((today_exercise / exercise_goal) * 100)) if exercise_goal > 0 else 0
    water_progress_pct = min(100, round((today_water / water_goal) * 100)) if water_goal > 0 else 0

    # Generate or refresh weekly chart
    weekly_chart_url = generate_weekly_activity_chart(activities, step_goal, user_id)

    # Health evaluation
    fitness_eval = evaluate_fitness_profile(profile)

    return render_template(
        "dashboard.html",
        profile=profile,
        fitness=fitness_eval,
        stats=stats,
        greeting=greeting,
        latest_activity=latest_activity,
        today_steps=today_steps,
        today_exercise=today_exercise,
        today_water=today_water,
        today_calories=today_calories,
        step_progress_pct=step_progress_pct,
        exercise_progress_pct=exercise_progress_pct,
        water_progress_pct=water_progress_pct,
        weekly_chart_url=weekly_chart_url,
        recent_activities=stats["recent_activities"]
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    """
    User Profile View & Editor:
    - Input fields: Name, Age, Height (cm), Weight (kg), Sex, Activity Level
    - Fitness Goals: Daily Step Goal, Daily Exercise Goal, Daily Water Goal
    - Comprehensive input validation with informative flash messages
    """
    user_id = get_active_user_id()
    user_profile = get_profile(user_id)

    if request.method == "POST":
        name = request.form.get("name", "")
        age = request.form.get("age", "")
        height = request.form.get("height", "")
        weight = request.form.get("weight", "")
        sex = request.form.get("sex", "")
        activity_level = request.form.get("activity_level", "")
        step_goal = request.form.get("step_goal", "")
        exercise_goal = request.form.get("exercise_goal", "")
        water_goal = request.form.get("water_goal", "")

        # 1. Validate physical metrics
        val_profile_ok, prof_err, cleaned_prof = validate_profile_data(
            name, age, height, weight, sex, activity_level
        )
        if not val_profile_ok:
            flash(prof_err, "danger")
            return render_template("profile.html", profile=user_profile)

        # 2. Validate goal metrics
        val_goals_ok, goal_err, cleaned_goals = validate_goals_data(
            step_goal, exercise_goal, water_goal
        )
        if not val_goals_ok:
            flash(goal_err, "danger")
            return render_template("profile.html", profile=user_profile)

        # Merge and save
        updated_data = {
            "id": user_id,
            **cleaned_prof,
            **cleaned_goals
        }

        try:
            save_profile(updated_data)
            flash("Profile and daily wellness goals updated successfully!", "success")
            return redirect(url_for("profile"))
        except Exception as e:
            flash(f"Error saving profile: {e}", "danger")

    fitness_eval = evaluate_fitness_profile(user_profile)
    return render_template("profile.html", profile=user_profile, fitness=fitness_eval)


@app.route("/profile/new", methods=["GET", "POST"])
def new_profile():
    """Creates a new user profile record."""
    if request.method == "POST":
        name = request.form.get("name", "")
        age = request.form.get("age", "")
        height = request.form.get("height", "")
        weight = request.form.get("weight", "")
        sex = request.form.get("sex", "")
        activity_level = request.form.get("activity_level", "")
        step_goal = request.form.get("step_goal", "10000")
        exercise_goal = request.form.get("exercise_goal", "45")
        water_goal = request.form.get("water_goal", "3.0")

        val_profile_ok, prof_err, cleaned_prof = validate_profile_data(
            name, age, height, weight, sex, activity_level
        )
        if not val_profile_ok:
            flash(prof_err, "danger")
            return render_template("profile.html", is_new=True, profile=None)

        val_goals_ok, goal_err, cleaned_goals = validate_goals_data(
            step_goal, exercise_goal, water_goal
        )
        if not val_goals_ok:
            flash(goal_err, "danger")
            return render_template("profile.html", is_new=True, profile=None)

        new_dict = {
            "id": "",  # Automatically generated in save_profile
            **cleaned_prof,
            **cleaned_goals
        }

        new_id = save_profile(new_dict)
        session["user_id"] = new_id
        flash(f"Welcome, {cleaned_prof['name']}! Your new profile has been created.", "success")
        return redirect(url_for("dashboard"))

    return render_template("profile.html", is_new=True, profile=None)


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    """
    Fitness Calculator Page:
    - Calculates BMI, BMR (Mifflin-St Jeor), and estimated TDEE.
    - Transparently reveals all mathematical formulas.
    - Features 1-click loading from active profile.
    - CRITICAL SAFEGUARD: For age < 18, hides adult BMI categories & calorie targets,
      displaying pediatric growth advisory instead.
    """
    user_id = get_active_user_id()
    user_profile = get_profile(user_id)

    # Initial default values (from user profile if available)
    calc_data = {
        "age": user_profile.get("age", 19) if user_profile else 19,
        "height": user_profile.get("height", 172.0) if user_profile else 172.0,
        "weight": user_profile.get("weight", 65.0) if user_profile else 65.0,
        "sex": user_profile.get("sex", "male") if user_profile else "male",
        "activity_level": user_profile.get("activity_level", "moderate") if user_profile else "moderate"
    }

    result = None

    if request.method == "POST":
        try:
            age = int(request.form.get("age", 19))
            height = float(request.form.get("height", 170.0))
            weight = float(request.form.get("weight", 65.0))
            sex = str(request.form.get("sex", "male")).strip().lower()
            activity_level = str(request.form.get("activity_level", "moderate")).strip()

            calc_data = {
                "age": age,
                "height": height,
                "weight": weight,
                "sex": sex,
                "activity_level": activity_level
            }

            # Validate
            val_ok, err_msg, cleaned = validate_profile_data(
                "Calculator User", age, height, weight, sex, activity_level
            )

            if not val_ok:
                flash(err_msg, "danger")
            else:
                bmi = calculate_bmi(cleaned["weight"], cleaned["height"])
                bmi_info = get_bmi_category(bmi, cleaned["age"])
                bmr = calculate_bmr(cleaned["weight"], cleaned["height"], cleaned["age"], cleaned["sex"])
                tdee_info = calculate_tdee(bmr, cleaned["activity_level"], cleaned["age"])

                result = {
                    "bmi": bmi,
                    "bmi_info": bmi_info,
                    "bmr": bmr,
                    "tdee": tdee_info["tdee"],
                    "tdee_info": tdee_info,
                    "disclaimer": get_fitness_disclaimer()
                }

        except (ValueError, TypeError) as e:
            flash(f"Invalid input provided: {e}", "danger")

    elif request.method == "GET" and user_profile:
        # Pre-compute with active profile for instant visualization
        bmi = calculate_bmi(user_profile["weight"], user_profile["height"])
        bmi_info = get_bmi_category(bmi, user_profile["age"])
        bmr = calculate_bmr(user_profile["weight"], user_profile["height"], user_profile["age"], user_profile["sex"])
        tdee_info = calculate_tdee(bmr, user_profile["activity_level"], user_profile["age"])

        result = {
            "bmi": bmi,
            "bmi_info": bmi_info,
            "bmr": bmr,
            "tdee": tdee_info["tdee"],
            "tdee_info": tdee_info,
            "disclaimer": get_fitness_disclaimer()
        }

    return render_template(
        "calculator.html",
        calc_data=calc_data,
        result=result,
        activity_levels=ACTIVITY_MULTIPLIERS,
        disclaimer=get_fitness_disclaimer()
    )


@app.route("/tracker", methods=["GET", "POST"])
def tracker():
    """
    Daily Activity Tracker:
    - Allows logging Date, Steps, Exercise Minutes, Water Litres, Activity Type, Notes.
    - Prevents duplicates for identical user & date unless update requested.
    - Displays chronological table of all logged activities.
    """
    user_id = get_active_user_id()
    user_profile = get_profile(user_id)
    weight = user_profile.get("weight", 65.0)

    if request.method == "POST":
        date_str = request.form.get("date", "")
        steps = request.form.get("steps", "")
        exercise_minutes = request.form.get("exercise_minutes", "")
        water_litres = request.form.get("water_litres", "")
        activity_type = request.form.get("activity_type", "Walking")
        notes = request.form.get("notes", "")
        allow_update = request.form.get("allow_update") == "yes"

        # Validate inputs
        val_ok, err_msg, cleaned = validate_activity_data(
            date_str, steps, exercise_minutes, water_litres, activity_type, notes
        )

        if not val_ok:
            flash(err_msg, "danger")
        else:
            # Check duplicate date
            existing = get_activity_by_date(user_id, cleaned["date"])
            if existing and not allow_update:
                flash(
                    f"A log for {cleaned['date']} already exists ({existing['steps']:,} steps, {existing['activity_type']}). "
                    "Check 'Update existing record if already present' or edit that entry directly below.",
                    "warning"
                )
            else:
                # Calculate estimated calories burned
                cals = calculate_calories_burned(
                    cleaned["activity_type"],
                    cleaned["exercise_minutes"],
                    weight
                )
                entry = {
                    "id": existing["id"] if existing else "",
                    "user_id": user_id,
                    "date": cleaned["date"],
                    "steps": cleaned["steps"],
                    "exercise_minutes": cleaned["exercise_minutes"],
                    "water_litres": cleaned["water_litres"],
                    "calories_burned": cals,
                    "activity_type": cleaned["activity_type"],
                    "notes": cleaned["notes"]
                }

                success, msg, act_id = save_activity(entry, allow_update=True)
                if success:
                    flash(msg, "success")
                    return redirect(url_for("tracker"))
                else:
                    flash(msg, "danger")

    activities = load_activities(user_id)
    # Reverse to show newest first in table
    activities_desc = sorted(activities, key=lambda a: a["date"], reverse=True)

    return render_template(
        "tracker.html",
        activities=activities_desc,
        activity_types=list(ACTIVITY_MET_VALUES.keys()),
        today=date.today().strftime("%Y-%m-%d")
    )


@app.route("/tracker/edit/<activity_id>", methods=["GET", "POST"])
def edit_activity(activity_id):
    """Edits a specific logged activity."""
    user_id = get_active_user_id()
    user_profile = get_profile(user_id)
    activity = get_activity_by_id(activity_id)

    if not activity or activity["user_id"] != user_id:
        flash("Activity entry not found or unauthorized.", "danger")
        return redirect(url_for("tracker"))

    if request.method == "POST":
        date_str = request.form.get("date", "")
        steps = request.form.get("steps", "")
        exercise_minutes = request.form.get("exercise_minutes", "")
        water_litres = request.form.get("water_litres", "")
        activity_type = request.form.get("activity_type", "Walking")
        notes = request.form.get("notes", "")

        val_ok, err_msg, cleaned = validate_activity_data(
            date_str, steps, exercise_minutes, water_litres, activity_type, notes
        )

        if not val_ok:
            flash(err_msg, "danger")
        else:
            cals = calculate_calories_burned(
                cleaned["activity_type"],
                cleaned["exercise_minutes"],
                user_profile.get("weight", 65.0)
            )
            activity["date"] = cleaned["date"]
            activity["steps"] = cleaned["steps"]
            activity["exercise_minutes"] = cleaned["exercise_minutes"]
            activity["water_litres"] = cleaned["water_litres"]
            activity["calories_burned"] = cals
            activity["activity_type"] = cleaned["activity_type"]
            activity["notes"] = cleaned["notes"]

            success, msg, _ = save_activity(activity, allow_update=True)
            if success:
                flash("Activity record updated successfully!", "success")
                return redirect(url_for("tracker"))
            else:
                flash(msg, "danger")

    return render_template(
        "tracker_edit.html",
        activity=activity,
        activity_types=list(ACTIVITY_MET_VALUES.keys())
    )


@app.route("/tracker/delete/<activity_id>", methods=["POST"])
def delete_activity_route(activity_id):
    """Deletes an activity entry."""
    user_id = get_active_user_id()
    activity = get_activity_by_id(activity_id)

    if activity and activity["user_id"] == user_id:
        delete_activity(activity_id)
        flash("Activity record deleted successfully.", "info")
    else:
        flash("Record could not be found or unauthorized.", "danger")

    return redirect(url_for("tracker"))


@app.route("/progress")
def progress():
    """
    Comprehensive Progress & Statistical Analysis:
    - Average Daily Steps, Exercise Duration, Water Intake
    - Total Days Logged & Active Streak
    - Goal Met Percentages
    - Matplotlib Charts: Weekly Dual-Axis, Exercise Type Donut, Hydration Trend
    - Activity breakdown
    """
    user_id = get_active_user_id()
    profile = get_profile(user_id)
    activities = load_activities(user_id)
    stats = calculate_user_statistics(user_id)

    step_goal = profile.get("step_goal", 10000)
    water_goal = profile.get("water_goal", 3.0)

    # Generate Matplotlib chart images
    weekly_chart = generate_weekly_activity_chart(activities, step_goal, user_id)
    dist_chart = generate_activity_distribution_chart(activities, user_id)
    hydration_chart = generate_hydration_trends_chart(activities, water_goal, user_id)

    return render_template(
        "progress.html",
        profile=profile,
        stats=stats,
        weekly_chart=weekly_chart,
        dist_chart=dist_chart,
        hydration_chart=hydration_chart
    )


@app.route("/report")
def report():
    """
    Personal Wellness Report Generator:
    - Formal printable & downloadable academic wellness report
    - Contains User Profile, Fitness Metrics, Activity Summary, Goal Completion,
      Embedded Progress Charts, Intelligent Observations, Academic CT Reflection,
      and Faculty Evaluation criteria for 2026CSAE100.
    """
    user_id = get_active_user_id()
    profile = get_profile(user_id)
    activities = load_activities(user_id)
    stats = calculate_user_statistics(user_id)

    report_data = generate_wellness_report_data(profile, activities, stats)

    return render_template(
        "report.html",
        report=report_data
    )


@app.route("/switch-user/<user_id>")
def switch_user(user_id):
    """Switches the active user profile."""
    prof = get_profile(user_id)
    if prof:
        session["user_id"] = str(user_id)
        flash(f"Switched active profile to: {prof['name']}", "info")
    else:
        flash("Selected user profile does not exist.", "warning")
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/seed-demo")
def seed_demo():
    """Populates or refreshes demo data for presentation."""
    seed_demo_data()
    profiles = load_profiles()
    if profiles:
        session["user_id"] = profiles[0]["id"]
    flash("Sample demonstration data loaded for Arjun Sharma (Bennett University CSE student).", "success")
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------------------------
# API ENDPOINTS FOR DYNAMIC FRONTEND FEATURES
# ---------------------------------------------------------------------------

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """
    JSON API for real-time calculation in the interactive calculator UI.
    """
    data = request.get_json() or {}
    try:
        age = int(data.get("age", 20))
        height = float(data.get("height", 170.0))
        weight = float(data.get("weight", 65.0))
        sex = str(data.get("sex", "male")).strip().lower()
        activity = str(data.get("activity_level", "moderate")).strip()

        val_ok, err, cleaned = validate_profile_data(
            "API User", age, height, weight, sex, activity
        )
        if not val_ok:
            return jsonify({"success": False, "error": err}), 400

        bmi = calculate_bmi(cleaned["weight"], cleaned["height"])
        bmi_info = get_bmi_category(bmi, cleaned["age"])
        bmr = calculate_bmr(cleaned["weight"], cleaned["height"], cleaned["age"], cleaned["sex"])
        tdee_info = calculate_tdee(bmr, cleaned["activity_level"], cleaned["age"])

        return jsonify({
            "success": True,
            "bmi": bmi,
            "bmi_category": bmi_info["category"],
            "bmi_description": bmi_info["description"],
            "is_pediatric": bmi_info.get("is_pediatric", False),
            "bmr": bmr,
            "tdee": tdee_info["tdee"],
            "activity_title": tdee_info["activity_title"],
            "calorie_guidance": tdee_info["calorie_guidance"],
            "recommended_ranges": tdee_info.get("recommended_ranges")
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ---------------------------------------------------------------------------
# APPLICATION ENTRYPOINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Ensure CSV data directory and demo records exist on startup
    init_csv_files()
    if not load_profiles():
        seed_demo_data()

    print("\n" + "=" * 70)
    print(" FITNESS TRACKER & PERSONAL WELLNESS REPORT GENERATOR")
    print(" Course: Computational Thinking & Programming (2026CSAE100)")
    print(" Bennett University - School of Computer Science Engg. & Technology")
    print("=" * 70)
    print(" Starting local development server at http://127.0.0.1:5001")
    print("=" * 70 + "\n")

    app.run(debug=True, host="127.0.0.1", port=5001)
