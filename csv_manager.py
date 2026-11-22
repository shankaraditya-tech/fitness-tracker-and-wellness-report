"""
=============================================================================
CSV Data Management & Analytics Engine
=============================================================================
Course: Computational Thinking and Programming (2026CSAE100)
Institution: Bennett University, School of Computer Science Engg. & Technology
Academic Year: 2026–27

This module handles all persistent file storage using Python's built-in `csv` module.
It demonstrates:
- CSV file creation, reading, and writing using DictReader & DictWriter
- Robust error handling for missing directories and corrupted rows
- Prevention of duplicate logs for identical user & date
- Aggregation, statistical calculations (mean, totals, rates, trends)
- Demonstration dataset seeding for academic viva presentation
=============================================================================
"""

import os
import csv
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

# Base directories configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

PROFILES_CSV = os.path.join(DATA_DIR, "profiles.csv")
ACTIVITY_CSV = os.path.join(DATA_DIR, "activity.csv")

# Standard CSV Headers
PROFILE_HEADERS = [
    "id",
    "name",
    "age",
    "height",
    "weight",
    "sex",
    "activity_level",
    "step_goal",
    "exercise_goal",
    "water_goal",
    "created_at",
    "updated_at"
]

ACTIVITY_HEADERS = [
    "id",
    "user_id",
    "date",
    "steps",
    "exercise_minutes",
    "water_litres",
    "calories_burned",
    "activity_type",
    "notes",
    "created_at"
]


# ---------------------------------------------------------------------------
# 1. INITIALIZATION & FILE INTEGRITY
# ---------------------------------------------------------------------------

def init_csv_files() -> None:
    """
    Ensures that data directory and CSV files exist with proper headers.
    Demonstrates: os.makedirs, os.path.exists, and csv.writer.
    """
    try:
        os.makedirs(DATA_DIR, exist_ok=True)

        # Check and initialize profiles.csv
        if not os.path.exists(PROFILES_CSV) or os.path.getsize(PROFILES_CSV) == 0:
            with open(PROFILES_CSV, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(PROFILE_HEADERS)

        # Check and initialize activity.csv
        if not os.path.exists(ACTIVITY_CSV) or os.path.getsize(ACTIVITY_CSV) == 0:
            with open(ACTIVITY_CSV, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(ACTIVITY_HEADERS)

    except OSError as err:
        print(f"[Error in init_csv_files]: Unable to initialize data files: {err}")


# ---------------------------------------------------------------------------
# 2. PROFILE MANAGEMENT FUNCTIONS
# ---------------------------------------------------------------------------

def load_profiles() -> List[Dict[str, Any]]:
    """
    Reads all user profiles from profiles.csv into a list of dictionaries.
    Demonstrates: csv.DictReader, type casting, and exception handling.
    """
    init_csv_files()
    profiles = []

    try:
        with open(PROFILES_CSV, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row or not row.get("id"):
                    continue
                try:
                    profile = {
                        "id": str(row.get("id", "").strip()),
                        "name": str(row.get("name", "User")).strip(),
                        "age": int(row.get("age", 20)),
                        "height": float(row.get("height", 170.0)),
                        "weight": float(row.get("weight", 65.0)),
                        "sex": str(row.get("sex", "male")).strip().lower(),
                        "activity_level": str(row.get("activity_level", "moderate")).strip(),
                        "step_goal": int(row.get("step_goal", 10000)),
                        "exercise_goal": int(row.get("exercise_goal", 45)),
                        "water_goal": float(row.get("water_goal", 3.0)),
                        "created_at": row.get("created_at", ""),
                        "updated_at": row.get("updated_at", "")
                    }
                    profiles.append(profile)
                except (ValueError, TypeError) as parse_err:
                    print(f"[Warning]: Skipping corrupted profile record {row}: {parse_err}")
                    continue

    except FileNotFoundError:
        init_csv_files()
    except Exception as e:
        print(f"[Error loading profiles]: {e}")

    return profiles


def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single user profile matching user_id.
    Returns None if not found.
    """
    profiles = load_profiles()
    for p in profiles:
        if p["id"] == str(user_id):
            return p
    return None


def save_profile(profile_dict: Dict[str, Any]) -> str:
    """
    Saves a user profile. If user_id exists, updates the record;
    otherwise assigns a new unique ID and appends the new record.

    Returns:
        str: user_id of the saved profile.
    """
    init_csv_files()
    profiles = load_profiles()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user_id = str(profile_dict.get("id", "")).strip()
    is_update = False

    if user_id:
        for i, existing in enumerate(profiles):
            if existing["id"] == user_id:
                # Update existing profile
                profile_dict["created_at"] = existing.get("created_at", now_str)
                profile_dict["updated_at"] = now_str
                profiles[i] = profile_dict
                is_update = True
                break

    if not is_update:
        # Generate new integer-based or timestamped ID
        if not user_id:
            user_id = str(len(profiles) + 1)
        profile_dict["id"] = user_id
        profile_dict["created_at"] = now_str
        profile_dict["updated_at"] = now_str
        profiles.append(profile_dict)

    # Write all back to CSV safely
    try:
        with open(PROFILES_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=PROFILE_HEADERS)
            writer.writeheader()
            for p in profiles:
                # Ensure all headers exist in dict
                row = {h: p.get(h, "") for h in PROFILE_HEADERS}
                writer.writerow(row)
    except Exception as e:
        print(f"[Error saving profile]: {e}")
        raise

    return user_id


# ---------------------------------------------------------------------------
# 3. DAILY ACTIVITY TRACKING & PREVENTING DUPLICATES
# ---------------------------------------------------------------------------

def load_activities(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Loads daily activity logs, optionally filtered by user_id.
    Sorted in chronological order by date (oldest to newest).
    """
    init_csv_files()
    activities = []

    try:
        with open(ACTIVITY_CSV, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row or not row.get("id"):
                    continue

                row_user = str(row.get("user_id", "")).strip()
                if user_id is not None and row_user != str(user_id):
                    continue

                try:
                    act = {
                        "id": str(row.get("id", "")).strip(),
                        "user_id": row_user,
                        "date": str(row.get("date", "")).strip(),
                        "steps": int(row.get("steps", 0)),
                        "exercise_minutes": int(row.get("exercise_minutes", 0)),
                        "water_litres": float(row.get("water_litres", 0.0)),
                        "calories_burned": int(row.get("calories_burned", 0)),
                        "activity_type": str(row.get("activity_type", "Walking")).strip(),
                        "notes": str(row.get("notes", "")).strip(),
                        "created_at": str(row.get("created_at", ""))
                    }
                    activities.append(act)
                except (ValueError, TypeError) as parse_err:
                    print(f"[Warning]: Skipping corrupted activity row: {parse_err}")
                    continue

    except FileNotFoundError:
        init_csv_files()
    except Exception as e:
        print(f"[Error loading activities]: {e}")

    # Sort chronologically by date
    activities.sort(key=lambda item: item["date"])
    return activities


def get_activity_by_date(user_id: str, date_str: str) -> Optional[Dict[str, Any]]:
    """
    Finds if an activity entry already exists for a specific user and date.
    Used to prevent accidental duplicates.
    """
    records = load_activities(user_id)
    for act in records:
        if act["date"] == date_str:
            return act
    return None


def get_activity_by_id(activity_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a specific activity record by its unique ID.
    """
    records = load_activities()
    for act in records:
        if act["id"] == str(activity_id):
            return act
    return None


def save_activity(
    activity_dict: Dict[str, Any],
    allow_update: bool = True
) -> Tuple[bool, str, str]:
    """
    Saves an activity record.

    DUPLICATE PREVENTION LOGIC:
    - Checks if a record already exists for the same user_id and date.
    - If a record exists and allow_update is True, it updates the existing record.
    - If allow_update is False, it rejects with an informative error message.

    Returns:
        Tuple[bool, str, str]: (success_flag, message, record_id)
    """
    init_csv_files()
    all_activities = load_activities()  # All records across all users
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Work on a copy of the input dictionary
    record = dict(activity_dict)
    target_user = str(record.get("user_id", "")).strip()
    target_date = str(record.get("date", "")).strip()
    act_id = str(record.get("id", "")).strip()

    # Search for an existing record with identical user and date
    existing_index = None
    for index, act in enumerate(all_activities):
        if act["user_id"] == target_user and act["date"] == target_date:
            existing_index = index
            break

    # If updating an existing ID specifically
    id_index = None
    if act_id:
        for index, act in enumerate(all_activities):
            if act["id"] == act_id:
                id_index = index
                break

    # If editing by explicit ID
    if id_index is not None:
        # Check if the date was changed to another date that already has a record
        if existing_index is not None and existing_index != id_index and not allow_update:
            return False, f"A record for {target_date} already exists.", ""
        record["id"] = act_id
        record["created_at"] = all_activities[id_index].get("created_at", now_str)
        all_activities[id_index] = record
        final_id = act_id
        action_msg = f"Activity for {target_date} successfully updated!"
    elif existing_index is not None:
        # Existing entry with the same date found
        if not allow_update:
            return False, f"A record for {target_date} already exists. Please choose a different date or edit the existing record.", ""
        # Overwrite/update existing date record
        record["id"] = all_activities[existing_index]["id"]
        record["created_at"] = all_activities[existing_index].get("created_at", now_str)
        all_activities[existing_index] = record
        final_id = record["id"]
        action_msg = f"Existing entry for {target_date} updated with new metrics."
    else:
        # Create brand new record
        if not act_id:
            max_id = 0
            for act in all_activities:
                try:
                    val = int(act["id"])
                    if val > max_id:
                        max_id = val
                except ValueError:
                    pass
            final_id = str(max_id + 1)
        else:
            final_id = act_id

        record["id"] = final_id
        record["created_at"] = now_str
        all_activities.append(record)
        action_msg = f"Activity for {target_date} successfully logged!"

    # Write all records back to CSV
    try:
        with open(ACTIVITY_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=ACTIVITY_HEADERS)
            writer.writeheader()
            for item in all_activities:
                row = {h: item.get(h, "") for h in ACTIVITY_HEADERS}
                writer.writerow(row)
    except Exception as e:
        return False, f"Failed to save record to CSV file: {e}", ""

    return True, action_msg, final_id


def delete_activity(activity_id: str) -> bool:
    """
    Deletes an activity record by its ID.
    """
    all_activities = load_activities()
    filtered = [a for a in all_activities if a["id"] != str(activity_id)]

    if len(filtered) == len(all_activities):
        return False  # Record was not present

    try:
        with open(ACTIVITY_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=ACTIVITY_HEADERS)
            writer.writeheader()
            for item in filtered:
                row = {h: item.get(h, "") for h in ACTIVITY_HEADERS}
                writer.writerow(row)
        return True
    except Exception as e:
        print(f"[Error deleting activity]: {e}")
        return False


# ---------------------------------------------------------------------------
# 4. STATISTICAL AGGREGATION & PROGRESS METRICS
# ---------------------------------------------------------------------------

def calculate_user_statistics(user_id: str) -> Dict[str, Any]:
    """
    Generates comprehensive summary statistics for a user:
    - Average daily steps
    - Average exercise duration
    - Average water intake
    - Total logged days
    - Goal completion rates (% of days meeting step, exercise, and water goals)
    - Activity breakdowns and streaks

    Demonstrates Python lists, dictionary counters, and math calculations.
    """
    profile = get_profile(user_id)
    activities = load_activities(user_id)

    # Defaults if profile is missing
    step_goal = profile["step_goal"] if profile else 10000
    exercise_goal = profile["exercise_goal"] if profile else 45
    water_goal = profile["water_goal"] if profile else 3.0

    total_days = len(activities)

    if total_days == 0:
        return {
            "total_days": 0,
            "avg_steps": 0,
            "avg_exercise_minutes": 0,
            "avg_water_litres": 0.0,
            "total_steps": 0,
            "total_exercise_minutes": 0,
            "total_water_litres": 0.0,
            "total_calories_burned": 0,
            "step_goal_completion_pct": 0,
            "exercise_goal_completion_pct": 0,
            "water_goal_completion_pct": 0,
            "step_goal_met_days": 0,
            "exercise_goal_met_days": 0,
            "water_goal_met_days": 0,
            "current_streak": 0,
            "best_steps_day": None,
            "activity_counts": {},
            "recent_activities": []
        }

    # Aggregate totals
    total_steps = sum(a["steps"] for a in activities)
    total_exercise = sum(a["exercise_minutes"] for a in activities)
    total_water = sum(a["water_litres"] for a in activities)
    total_calories = sum(a["calories_burned"] for a in activities)

    # Goal tracking counts
    step_met_days = sum(1 for a in activities if a["steps"] >= step_goal)
    exercise_met_days = sum(1 for a in activities if a["exercise_minutes"] >= exercise_goal)
    water_met_days = sum(1 for a in activities if a["water_litres"] >= water_goal)

    # Averages
    avg_steps = round(total_steps / total_days)
    avg_exercise = round(total_exercise / total_days, 1)
    avg_water = round(total_water / total_days, 2)

    # Percentages
    step_pct = round((step_met_days / total_days) * 100, 1)
    exercise_pct = round((exercise_met_days / total_days) * 100, 1)
    water_pct = round((water_met_days / total_days) * 100, 1)

    # Activity type distribution
    activity_counts = {}
    for a in activities:
        atype = a["activity_type"]
        activity_counts[atype] = activity_counts.get(atype, 0) + 1

    # Best day by steps
    best_steps = max(activities, key=lambda a: a["steps"])

    # Calculate active logging streak
    # Check backwards from latest activity
    sorted_by_date_desc = sorted(activities, key=lambda a: a["date"], reverse=True)
    streak = 0
    if sorted_by_date_desc:
        ref_date = datetime.strptime(sorted_by_date_desc[0]["date"], "%Y-%m-%d").date()
        # Today or yesterday check
        today = date.today()
        if (today - ref_date).days <= 1:
            streak = 1
            curr_date = ref_date
            for act in sorted_by_date_desc[1:]:
                act_date = datetime.strptime(act["date"], "%Y-%m-%d").date()
                if curr_date - act_date == timedelta(days=1):
                    streak += 1
                    curr_date = act_date
                else:
                    break

    return {
        "total_days": total_days,
        "avg_steps": avg_steps,
        "avg_exercise_minutes": avg_exercise,
        "avg_water_litres": avg_water,
        "total_steps": total_steps,
        "total_exercise_minutes": total_exercise,
        "total_water_litres": round(total_water, 1),
        "total_calories_burned": total_calories,
        "step_goal_completion_pct": step_pct,
        "exercise_goal_completion_pct": exercise_pct,
        "water_goal_completion_pct": water_pct,
        "step_goal_met_days": step_met_days,
        "exercise_goal_met_days": exercise_met_days,
        "water_goal_met_days": water_met_days,
        "current_streak": streak,
        "best_steps_day": best_steps,
        "activity_counts": activity_counts,
        "recent_activities": sorted_by_date_desc[:7]  # Last 7 records
    }


# ---------------------------------------------------------------------------
# 5. SAMPLE DEMONSTRATION DATA SEEDING
# ---------------------------------------------------------------------------

def seed_demo_data() -> None:
    """
    Seeds realistic demonstration data for a Bennett University student:
    - Profile: Arjun Sharma (19 yrs, 1st Year B.Tech CSE, Bennett University)
    - 14 days of realistic logs (gym, running, campus walking, football, etc.)
    """
    init_csv_files()

    # Create demo profile
    demo_profile = {
        "id": "1",
        "name": "Arjun Sharma",
        "age": 19,
        "height": 176.0,
        "weight": 68.5,
        "sex": "male",
        "activity_level": "moderate",
        "step_goal": 10000,
        "exercise_goal": 45,
        "water_goal": 3.0,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Import exercise calorie calculator from fitness module
    from fitness import calculate_calories_burned

    today = date.today()

    demo_activities = [
        {"day_offset": 13, "steps": 10540, "exercise": 50, "water": 3.2, "type": "Gym/Strength", "notes": "Upper body workout at Bennett Gym"},
        {"day_offset": 12, "steps": 9200, "exercise": 40, "water": 2.8, "type": "Running", "notes": "Evening sprint laps around academic block"},
        {"day_offset": 11, "steps": 11300, "exercise": 60, "water": 3.5, "type": "Sports", "notes": "Badminton match with hostel wing-mates"},
        {"day_offset": 10, "steps": 8450, "exercise": 30, "water": 2.5, "type": "Walking", "notes": "Walk to library and dining hall"},
        {"day_offset": 9, "steps": 12400, "exercise": 55, "water": 3.4, "type": "Cycling", "notes": "Cycling around Greater Noida expressway trail"},
        {"day_offset": 8, "steps": 9800, "exercise": 45, "water": 3.0, "type": "Gym/Strength", "notes": "Leg day and core circuits"},
        {"day_offset": 7, "steps": 10100, "exercise": 40, "water": 3.1, "type": "Swimming", "notes": "Swimming laps at university indoor pool"},
        {"day_offset": 6, "steps": 11200, "exercise": 50, "water": 3.3, "type": "Running", "notes": "Morning jog before 9 AM data structures class"},
        {"day_offset": 5, "steps": 8900, "exercise": 35, "water": 2.7, "type": "Yoga", "notes": "Relaxing flexibility and breathwork session"},
        {"day_offset": 4, "steps": 10800, "exercise": 45, "water": 3.2, "type": "Walking", "notes": "Evening campus walk with study group"},
        {"day_offset": 3, "steps": 13150, "exercise": 70, "water": 3.8, "type": "Sports", "notes": "Inter-hostel football tournament match"},
        {"day_offset": 2, "steps": 10400, "exercise": 50, "water": 3.2, "type": "Gym/Strength", "notes": "Chest & shoulders workout; hydration goal met"},
        {"day_offset": 1, "steps": 9650, "exercise": 40, "water": 2.9, "type": "Running", "notes": "Interval sprints on sports track"},
        {"day_offset": 0, "steps": 10850, "exercise": 45, "water": 3.1, "type": "Walking", "notes": "Active day across lab sessions and sports complex"}
    ]

    # Save demo profile
    save_profile(demo_profile)

    # Save demo activities
    for idx, sample in enumerate(demo_activities, start=1):
        log_date = (today - timedelta(days=sample["day_offset"])).strftime("%Y-%m-%d")
        cal_burned = calculate_calories_burned(
            sample["type"],
            sample["exercise"],
            demo_profile["weight"]
        )
        act_entry = {
            "id": str(idx),
            "user_id": "1",
            "date": log_date,
            "steps": sample["steps"],
            "exercise_minutes": sample["exercise"],
            "water_litres": sample["water"],
            "calories_burned": cal_burned,
            "activity_type": sample["type"],
            "notes": sample["notes"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_activity(act_entry, allow_update=True)

    print("[Info]: Seed demonstration data generated successfully.")
