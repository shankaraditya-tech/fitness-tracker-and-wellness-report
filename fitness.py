"""
=============================================================================
Fitness & Wellness Mathematics Module
=============================================================================
Course: Computational Thinking and Programming (2026CSAE100)
Institution: Bennett University, School of Computer Science Engg. & Technology
Academic Year: 2026–27

This module contains modular, well-documented Python functions for:
1. Input validation (Profiles, Daily Activity, Goals)
2. Body Mass Index (BMI) calculation & categorical analysis
3. Basal Metabolic Rate (BMR) using the Mifflin-St Jeor equation
4. Total Daily Energy Expenditure (TDEE) using activity multipliers
5. Metabolic Equivalent of Task (MET) calories burned estimation
6. Educational disclaimers and pediatric/under-18 safety safeguards

Python Concepts Demonstrated:
- Primitive data types (int, float, str, bool)
- Conditional branching (if / elif / else)
- Mathematical operators and type conversion
- Robust dictionary-based return structures
- Clear defensive programming with custom validation checks
=============================================================================
"""

from typing import Tuple, Dict, Any, Optional


def get_fitness_disclaimer() -> str:
    """
    Returns the standard educational disclaimer.
    Emphasizes that formulas are educational estimates, not medical prescriptions.
    """
    return (
        "EDUCATIONAL NOTICE: These calculations are estimates based on standard "
        "mathematical models (Mifflin-St Jeor formula and WHO BMI metrics) implemented "
        "for the Bennett University Computational Thinking and Programming course. "
        "They do NOT constitute medical diagnoses, clinical assessments, or personalized "
        "dietary prescriptions. Consult a licensed physician or registered dietitian before "
        "initiating any rigorous physical or nutritional program."
    )


# ---------------------------------------------------------------------------
# 1. INPUT VALIDATION FUNCTIONS
# ---------------------------------------------------------------------------

def validate_profile_data(
    name: str,
    age: Any,
    height: Any,
    weight: Any,
    sex: str,
    activity_level: str
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates user profile input fields.

    Parameters:
        name (str): Full name of the user (2 to 50 characters).
        age (int or str): Age in years (must be between 10 and 120).
        height (float or str): Height in centimetres (must be between 50 and 250 cm).
        weight (float or str): Weight in kilograms (must be between 20 and 300 kg).
        sex (str): 'male' or 'female' required by the Mifflin-St Jeor equation.
        activity_level (str): One of the predefined physical activity tiers.

    Returns:
        Tuple[bool, str, Dict[str, Any]]: (is_valid, error_message, cleaned_data_dict)
    """
    # 1. Validate Name
    cleaned_name = str(name).strip() if name else ""
    if not cleaned_name:
        return False, "Please enter your name.", {}
    if len(cleaned_name) < 2 or len(cleaned_name) > 60:
        return False, "Name must be between 2 and 60 characters in length.", {}

    # 2. Validate Age
    try:
        age_int = int(age)
        if age_int < 10 or age_int > 120:
            return False, "Age must be a realistic number between 10 and 120 years.", {}
    except (ValueError, TypeError):
        return False, "Please provide a valid whole number for age.", {}

    # 3. Validate Height (in cm)
    try:
        height_float = float(height)
        if height_float < 50.0 or height_float > 260.0:
            return False, "Height must be between 50.0 cm and 260.0 cm.", {}
    except (ValueError, TypeError):
        return False, "Please provide a valid numeric value for height in centimetres.", {}

    # 4. Validate Weight (in kg)
    try:
        weight_float = float(weight)
        if weight_float < 20.0 or weight_float > 350.0:
            return False, "Weight must be between 20.0 kg and 350.0 kg.", {}
    except (ValueError, TypeError):
        return False, "Please provide a valid numeric value for weight in kilograms.", {}

    # 5. Validate Sex (Mifflin-St Jeor requires biological sex parameter)
    cleaned_sex = str(sex).strip().lower() if sex else ""
    if cleaned_sex not in ("male", "female"):
        return False, "Please select biological sex ('male' or 'female') as required by the Mifflin-St Jeor BMR equation.", {}

    # 6. Validate Activity Level
    valid_levels = ("sedentary", "light", "moderate", "very_active", "extra_active")
    cleaned_activity = str(activity_level).strip().lower() if activity_level else ""
    if cleaned_activity not in valid_levels:
        return False, f"Invalid activity level selected. Choose from: {', '.join(valid_levels)}.", {}

    # Return sanitized and strongly typed data dictionary
    cleaned_data = {
        "name": cleaned_name,
        "age": age_int,
        "height": round(height_float, 1),
        "weight": round(weight_float, 1),
        "sex": cleaned_sex,
        "activity_level": cleaned_activity
    }
    return True, "", cleaned_data


def validate_activity_data(
    date_str: str,
    steps: Any,
    exercise_minutes: Any,
    water_litres: Any,
    activity_type: str,
    notes: str = ""
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates daily logged activity entries.

    Parameters:
        date_str (str): Date in YYYY-MM-DD format.
        steps (int or str): Number of walking/running steps (0 to 120,000).
        exercise_minutes (int or str): Duration of intentional exercise (0 to 1440 min).
        water_litres (float or str): Water consumed in litres (0.0 to 25.0 L).
        activity_type (str): Type of physical exercise.
        notes (str): Optional dietary or workout notes.

    Returns:
        Tuple[bool, str, Dict[str, Any]]: (is_valid, error_message, cleaned_activity_dict)
    """
    # 1. Validate Date format (basic string check & length)
    import re
    cleaned_date = str(date_str).strip() if date_str else ""
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", cleaned_date):
        return False, "Please select a valid date in YYYY-MM-DD format.", {}

    # 2. Validate Steps
    try:
        steps_int = int(steps)
        if steps_int < 0 or steps_int > 120000:
            return False, "Daily steps must be between 0 and 120,000.", {}
    except (ValueError, TypeError):
        return False, "Steps must be a valid non-negative integer.", {}

    # 3. Validate Exercise Duration
    try:
        exercise_int = int(exercise_minutes)
        if exercise_int < 0 or exercise_int > 1440:
            return False, "Exercise duration must be between 0 and 1440 minutes (24 hours).", {}
    except (ValueError, TypeError):
        return False, "Exercise duration must be a valid whole number in minutes.", {}

    # 4. Validate Water Intake
    try:
        water_float = float(water_litres)
        if water_float < 0.0 or water_float > 25.0:
            return False, "Water intake must be between 0.0 and 25.0 litres.", {}
    except (ValueError, TypeError):
        return False, "Water intake must be a valid numeric quantity in litres (e.g. 2.5).", {}

    # 5. Activity Type
    valid_types = [
        "Walking", "Running", "Cycling", "Gym/Strength",
        "Yoga", "Swimming", "Sports", "HIIT", "Other"
    ]
    cleaned_type = str(activity_type).strip() if activity_type else "Walking"
    # Find case-insensitive match or default
    matched_type = next((t for t in valid_types if t.lower() == cleaned_type.lower()), "Other")

    cleaned_notes = str(notes).strip() if notes else ""
    if len(cleaned_notes) > 300:
        cleaned_notes = cleaned_notes[:300]

    return True, "", {
        "date": cleaned_date,
        "steps": steps_int,
        "exercise_minutes": exercise_int,
        "water_litres": round(water_float, 2),
        "activity_type": matched_type,
        "notes": cleaned_notes
    }


def validate_goals_data(
    step_goal: Any,
    exercise_goal: Any,
    water_goal: Any
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates user-defined daily fitness goals.
    """
    try:
        steps_g = int(step_goal)
        if steps_g < 500 or steps_g > 100000:
            return False, "Daily step goal should be between 500 and 100,000 steps.", {}
    except (ValueError, TypeError):
        return False, "Please enter a valid number for step goal.", {}

    try:
        exer_g = int(exercise_goal)
        if exer_g < 0 or exer_g > 720:
            return False, "Daily exercise goal should be between 0 and 720 minutes.", {}
    except (ValueError, TypeError):
        return False, "Please enter a valid number of minutes for exercise goal.", {}

    try:
        water_g = float(water_goal)
        if water_g < 0.5 or water_g > 15.0:
            return False, "Daily water goal should be between 0.5 and 15.0 litres.", {}
    except (ValueError, TypeError):
        return False, "Please enter a valid decimal number for water goal (e.g. 3.0).", {}

    return True, "", {
        "step_goal": steps_g,
        "exercise_goal": exer_g,
        "water_goal": round(water_g, 2)
    }


# ---------------------------------------------------------------------------
# 2. BODY MASS INDEX (BMI)
# ---------------------------------------------------------------------------

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Calculates Body Mass Index (BMI).

    Formula:
        height_meters = height_cm / 100
        BMI = weight_kg / (height_meters ** 2)

    Returns:
        float: Calculated BMI rounded to 2 decimal places.
    """
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def get_bmi_category(bmi: float, age: int) -> Dict[str, Any]:
    """
    Determines BMI category and provides educational context.

    SPECIAL REQUIREMENT:
    For users under 18, standard adult WHO categories are NOT displayed.
    Instead, a pediatric guidance message is returned.

    Adult WHO Categories (Age >= 18):
    - BMI < 18.5: Underweight
    - 18.5 <= BMI < 25.0: Normal weight
    - 25.0 <= BMI < 30.0: Overweight
    - BMI >= 30.0: Obese
    """
    if age < 18:
        return {
            "is_pediatric": True,
            "category": "Pediatric / Adolescent",
            "badge_class": "badge-info",
            "description": (
                "For individuals under 18 years, standard adult BMI categories and adult "
                "weight cut-offs do not apply. Adolescents experience dynamic hormonal "
                "changes, skeletal growth, and shifting muscle-to-fat ratios. Growth percentiles "
                "(CDC / WHO age-and-sex specific charts) are used clinically instead. "
                "Please consult a pediatrician for developmental growth evaluations."
            ),
            "recommendation": "Consult pediatric growth percentile charts with a healthcare professional."
        }

    # Adult Evaluation (Age >= 18)
    if bmi < 18.5:
        return {
            "is_pediatric": False,
            "category": "Underweight",
            "badge_class": "badge-warning",
            "color": "#38bdf8",
            "description": "BMI is below the standard recommended adult range (< 18.5 kg/m²).",
            "recommendation": "Focus on nutrient-dense whole foods and strength resistance exercises."
        }
    elif 18.5 <= bmi < 25.0:
        return {
            "is_pediatric": False,
            "category": "Normal weight",
            "badge_class": "badge-success",
            "color": "#10b981",
            "description": "BMI is within the standard healthy adult reference range (18.5 - 24.9 kg/m²).",
            "recommendation": "Maintain your active routine and balanced wholesome nutrition."
        }
    elif 25.0 <= bmi < 30.0:
        return {
            "is_pediatric": False,
            "category": "Overweight",
            "badge_class": "badge-amber",
            "color": "#f59e0b",
            "description": "BMI is slightly above the standard healthy adult range (25.0 - 29.9 kg/m²).",
            "recommendation": "Incorporate daily moderate cardiovascular exercise and mindful portion control."
        }
    else:
        return {
            "is_pediatric": False,
            "category": "Obese",
            "badge_class": "badge-danger",
            "color": "#ef4444",
            "description": "BMI is 30.0 kg/m² or higher.",
            "recommendation": "Consult with a physician or certified fitness coach for a tailored, safe fitness plan."
        }


# ---------------------------------------------------------------------------
# 3. BASAL METABOLIC RATE (BMR) - MIFFLIN-ST JEOR FORMULA
# ---------------------------------------------------------------------------

def calculate_bmr(weight_kg: float, height_cm: float, age_years: int, sex: str) -> float:
    """
    Calculates Basal Metabolic Rate (BMR) in kilocalories/day using the
    internationally recognized Mifflin-St Jeor equation.

    Formulas:
        Male:   BMR = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        Female: BMR = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    Parameters:
        weight_kg (float): Weight in kilograms.
        height_cm (float): Height in centimetres.
        age_years (int): Age in years.
        sex (str): Biological sex ('male' or 'female').

    Returns:
        float: BMR in kcal/day rounded to 1 decimal place.
    """
    base_term = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age_years)

    if sex.strip().lower() == "male":
        bmr = base_term + 5.0
    else:
        bmr = base_term - 161.0

    return max(0.0, round(bmr, 1))


# ---------------------------------------------------------------------------
# 4. TOTAL DAILY ENERGY EXPENDITURE (TDEE)
# ---------------------------------------------------------------------------

ACTIVITY_MULTIPLIERS = {
    "sedentary": {
        "factor": 1.2,
        "title": "Sedentary",
        "description": "Little or no regular exercise; desk job / sedentary study routine."
    },
    "light": {
        "factor": 1.375,
        "title": "Lightly Active",
        "description": "Light physical exercise or sports 1 to 3 days per week."
    },
    "moderate": {
        "factor": 1.55,
        "title": "Moderately Active",
        "description": "Moderate exercise or fitness sessions 3 to 5 days per week."
    },
    "very_active": {
        "factor": 1.725,
        "title": "Very Active",
        "description": "Hard exercise or demanding athletics 6 to 7 days per week."
    },
    "extra_active": {
        "factor": 1.9,
        "title": "Extra Active",
        "description": "Very intense training twice daily or physically strenuous labor."
    }
}


def calculate_tdee(bmr: float, activity_level: str, age: int) -> Dict[str, Any]:
    """
    Calculates Total Daily Energy Expenditure (TDEE).

    Formula:
        TDEE = BMR * Activity Multiplier

    SPECIAL SAFEGUARD:
    For users under 18, adult calorie goals (deficit / surplus targets) are omitted
    to adhere strictly to pediatric safety requirements.

    Returns:
        Dict[str, Any] containing TDEE value, activity info, and educational notes.
    """
    level_key = activity_level.strip().lower() if activity_level else "sedentary"
    config = ACTIVITY_MULTIPLIERS.get(level_key, ACTIVITY_MULTIPLIERS["sedentary"])

    multiplier = config["factor"]
    tdee = round(bmr * multiplier, 1)

    is_minor = (age < 18)

    if is_minor:
        calorie_guidance = (
            "Special Note for Adolescents (< 18): Fixed calorie surplus/deficit diets "
            "are not advised. Adolescent energy needs fluctuate significantly with growth "
            "spurts and brain/organ development. Focus on balanced wholesome nutrition and "
            "staying physically active rather than calorie restriction."
        )
        recommended_ranges = None
    else:
        calorie_guidance = (
            "Adult Maintenance Energy: This represents the estimated daily calories "
            "required to maintain your current body weight at your declared activity level."
        )
        recommended_ranges = {
            "maintenance": int(round(tdee)),
            "mild_weight_loss": int(round(tdee - 300)),
            "weight_loss": int(round(tdee - 500)),
            "mild_weight_gain": int(round(tdee + 300)),
            "weight_gain": int(round(tdee + 500))
        }

    return {
        "tdee": tdee,
        "bmr": bmr,
        "activity_level_key": level_key,
        "activity_title": config["title"],
        "activity_description": config["description"],
        "multiplier": multiplier,
        "is_pediatric": is_minor,
        "calorie_guidance": calorie_guidance,
        "recommended_ranges": recommended_ranges
    }


# ---------------------------------------------------------------------------
# 5. EXERCISE CALORIE ESTIMATION (MET Formula)
# ---------------------------------------------------------------------------

ACTIVITY_MET_VALUES = {
    "Walking": 3.5,
    "Running": 9.8,
    "Cycling": 7.5,
    "Gym/Strength": 5.0,
    "Yoga": 3.0,
    "Swimming": 7.0,
    "Sports": 6.5,
    "HIIT": 8.0,
    "Other": 4.5
}


def calculate_calories_burned(
    activity_type: str,
    duration_minutes: int,
    weight_kg: float
) -> int:
    """
    Estimates calories burned using the standard exercise physiology MET equation.

    Formula:
        Calories = (MET * 3.5 * weight_kg / 200) * duration_minutes

    Parameters:
        activity_type (str): Name of exercise.
        duration_minutes (int): Minutes spent exercising.
        weight_kg (float): Body weight in kilograms.

    Returns:
        int: Estimated calories burned rounded to whole integer.
    """
    if duration_minutes <= 0 or weight_kg <= 0:
        return 0

    met = ACTIVITY_MET_VALUES.get(activity_type, 4.5)
    # Standard formula for kcal: MET * 3.5 * kg / 200 * minutes
    calories = (met * 3.5 * weight_kg / 200.0) * duration_minutes
    return int(round(calories))


# ---------------------------------------------------------------------------
# 6. COMPREHENSIVE FITNESS PROFILE EVALUATOR
# ---------------------------------------------------------------------------

def evaluate_fitness_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregates full fitness metrics for a given user profile.
    Takes a dictionary containing: name, age, height, weight, sex, activity_level.
    Returns calculated BMI, BMR, TDEE, categories, and educational notes.
    """
    name = profile.get("name", "Student")
    age = int(profile.get("age", 19))
    height = float(profile.get("height", 170.0))
    weight = float(profile.get("weight", 65.0))
    sex = str(profile.get("sex", "male"))
    activity_level = str(profile.get("activity_level", "moderate"))

    bmi = calculate_bmi(weight, height)
    bmi_info = get_bmi_category(bmi, age)
    bmr = calculate_bmr(weight, height, age, sex)
    tdee_info = calculate_tdee(bmr, activity_level, age)

    return {
        "name": name,
        "age": age,
        "height": height,
        "weight": weight,
        "sex": sex,
        "activity_level": activity_level,
        "bmi": bmi,
        "bmi_info": bmi_info,
        "bmr": bmr,
        "tdee": tdee_info["tdee"],
        "tdee_info": tdee_info,
        "disclaimer": get_fitness_disclaimer()
    }
