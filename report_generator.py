"""
=============================================================================
Wellness Report & Matplotlib Chart Generation Engine
=============================================================================
Course: Computational Thinking and Programming (2026CSAE100)
Institution: Bennett University, School of Computer Science Engg. & Technology
Academic Year: 2026–27

This module utilizes Matplotlib to generate high-resolution, modern progress
visualizations and compiles comprehensive academic Personal Wellness Reports.

Python Concepts Demonstrated:
- Non-GUI backend rendering (`matplotlib.use('Agg')`)
- Figure, Subplots, and Dual-axis data visualization
- Color styling, custom annotations, and formatting
- Data aggregation and pattern recognition logic
- String formatting, conditional feedback algorithms, and modular design
=============================================================================
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Set Matplotlib cache dir to /tmp to avoid permission warnings
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

# Configure Matplotlib for headless server execution before importing pyplot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Base directories configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE_DIR, "static", "images", "charts")


def ensure_charts_dir():
    """Creates the charts storage directory if it does not already exist."""
    os.makedirs(CHARTS_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. MATPLOTLIB VISUALIZATION GENERATORS
# ---------------------------------------------------------------------------

def generate_weekly_activity_chart(
    activities: List[Dict[str, Any]],
    step_goal: int = 10000,
    user_id: str = "1"
) -> Optional[str]:
    """
    Generates a dual-axis weekly progress chart:
    - Primary Y-axis: Bar chart of Daily Steps with a horizontal Goal Target line.
    - Secondary Y-axis: Line plot of Exercise Minutes with highlighted marker points.

    Returns:
        str: Relative web URL to the generated image file, or None if no data.
    """
    ensure_charts_dir()

    if not activities:
        return None

    # Take up to the last 7 recorded entries
    recent_entries = activities[-7:] if len(activities) >= 7 else activities

    dates = [e["date"][5:] for e in recent_entries]  # Format as MM-DD
    steps = [e["steps"] for e in recent_entries]
    exercise = [e["exercise_minutes"] for e in recent_entries]

    # Set up dark modern styling
    plt.style.use("dark_background")
    fig, ax1 = plt.subplots(figsize=(8.5, 4.4), dpi=140)
    fig.patch.set_facecolor("#0f172a")  # Slate 900
    ax1.set_facecolor("#0f172a")

    # Bar chart for steps
    x_positions = range(len(dates))
    bars = ax1.bar(
        x_positions,
        steps,
        width=0.45,
        color="#10b981",  # Emerald
        alpha=0.88,
        label="Daily Steps",
        edgecolor="#34d399",
        linewidth=1.2,
        zorder=3
    )

    # Step Goal target line
    ax1.axhline(
        y=step_goal,
        color="#38bdf8",  # Sky blue
        linestyle="--",
        linewidth=1.8,
        alpha=0.9,
        label=f"Goal ({step_goal:,} steps)",
        zorder=4
    )

    ax1.set_ylabel("Steps Count", color="#10b981", fontsize=11, fontweight="600")
    ax1.tick_params(axis="y", labelcolor="#10b981", labelsize=9)
    ax1.tick_params(axis="x", labelcolor="#e2e8f0", labelsize=9)
    ax1.set_xticks(list(x_positions))
    ax1.set_xticklabels(dates, rotation=0, fontweight="500")
    ax1.grid(axis="y", linestyle=":", alpha=0.2, color="#94a3b8")

    # Secondary Y-axis for Exercise Minutes
    ax2 = ax1.twinx()
    ax2.set_facecolor("none")
    line = ax2.plot(
        x_positions,
        exercise,
        color="#f59e0b",  # Amber/Orange
        marker="o",
        linewidth=2.4,
        markersize=6,
        label="Exercise (min)",
        zorder=5
    )
    ax2.set_ylabel("Exercise (Minutes)", color="#f59e0b", fontsize=11, fontweight="600")
    ax2.tick_params(axis="y", labelcolor="#f59e0b", labelsize=9)

    # Annotate step values above bars
    for bar in bars:
        h = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            h + (max(steps) * 0.02),
            f"{int(h):,}",
            ha="center",
            va="bottom",
            color="#f1f5f9",
            fontsize=8,
            fontweight="bold"
        )

    # Title & Legends
    plt.title("Weekly Activity & Target Tracking (Last 7 Days)", fontsize=13, fontweight="bold", color="#f8fafc", pad=14)

    # Unified Legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", framealpha=0.2, facecolor="#1e293b", edgecolor="#334155", fontsize=9)

    plt.tight_layout()

    filename = f"weekly_chart_user_{user_id}.png"
    filepath = os.path.join(CHARTS_DIR, filename)
    plt.savefig(filepath, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    return f"images/charts/{filename}"


def generate_activity_distribution_chart(
    activities: List[Dict[str, Any]],
    user_id: str = "1"
) -> Optional[str]:
    """
    Generates a donut chart displaying the distribution of exercise types.
    """
    ensure_charts_dir()

    if not activities:
        return None

    # Count frequencies of each activity type
    counts = {}
    for a in activities:
        atype = a.get("activity_type", "Walking")
        counts[atype] = counts.get(atype, 0) + 1

    if not counts:
        return None

    labels = list(counts.keys())
    values = list(counts.values())

    # Premium color palette
    palette = ["#10b981", "#06b6d4", "#6366f1", "#f59e0b", "#ec4899", "#8b5cf6", "#14b8a6", "#f43f5e"]
    colors = palette[:len(labels)]

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(5.5, 4.4), dpi=140)
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.78,
        wedgeprops=dict(width=0.45, edgecolor="#0f172a", linewidth=2.5)
    )

    # Style labels and percentages
    for text in texts:
        text.set_color("#cbd5e1")
        text.set_fontsize(9)
        text.set_fontweight("500")
    for autotext in autotexts:
        autotext.set_color("#ffffff")
        autotext.set_fontsize(8.5)
        autotext.set_fontweight("bold")

    plt.title("Exercise Modality Distribution", fontsize=12, fontweight="bold", color="#f8fafc", pad=12)
    plt.tight_layout()

    filename = f"distribution_chart_user_{user_id}.png"
    filepath = os.path.join(CHARTS_DIR, filename)
    plt.savefig(filepath, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    return f"images/charts/{filename}"


def generate_hydration_trends_chart(
    activities: List[Dict[str, Any]],
    water_goal: float = 3.0,
    user_id: str = "1"
) -> Optional[str]:
    """
    Generates a trend chart of daily water intake (Litres) vs water goal.
    """
    ensure_charts_dir()

    if not activities:
        return None

    recent_entries = activities[-10:] if len(activities) >= 10 else activities
    dates = [e["date"][5:] for e in recent_entries]
    water = [e["water_litres"] for e in recent_entries]

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(8.5, 3.8), dpi=140)
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")

    x_positions = range(len(dates))
    ax.fill_between(x_positions, water, color="#06b6d4", alpha=0.25)
    ax.plot(x_positions, water, color="#06b6d4", marker="o", linewidth=2.5, markersize=6, label="Water Intake (L)")

    # Target water line
    ax.axhline(
        y=water_goal,
        color="#38bdf8",
        linestyle="--",
        linewidth=1.8,
        label=f"Hydration Goal ({water_goal:.1f} L)"
    )

    ax.set_ylabel("Water (Litres)", color="#38bdf8", fontsize=11, fontweight="600")
    ax.tick_params(axis="y", labelcolor="#38bdf8", labelsize=9)
    ax.tick_params(axis="x", labelcolor="#e2e8f0", labelsize=9)
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(dates, fontweight="500")
    ax.grid(axis="y", linestyle=":", alpha=0.2, color="#94a3b8")

    # Annotate points
    for i, txt in enumerate(water):
        ax.annotate(
            f"{txt:.1f}L",
            (x_positions[i], water[i]),
            textcoords="offset points",
            xytext=(0, 7),
            ha="center",
            fontsize=8,
            color="#f1f5f9",
            fontweight="bold"
        )

    plt.title("Hydration Progression Over Time", fontsize=12, fontweight="bold", color="#f8fafc", pad=12)
    ax.legend(loc="upper left", framealpha=0.2, facecolor="#1e293b", edgecolor="#334155", fontsize=9)
    plt.tight_layout()

    filename = f"hydration_chart_user_{user_id}.png"
    filepath = os.path.join(CHARTS_DIR, filename)
    plt.savefig(filepath, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    return f"images/charts/{filename}"


# ---------------------------------------------------------------------------
# 2. PERSONAL WELLNESS REPORT COMPILER
# ---------------------------------------------------------------------------

def generate_wellness_report_data(
    profile: Dict[str, Any],
    activities: List[Dict[str, Any]],
    statistics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compiles full structured data for the downloadable Personal Wellness Report:
    - User Profile & Physical Metrics
    - Fitness Metrics (BMI, BMR, TDEE)
    - Activity Summary & Averages
    - Goal Completion Percentages
    - Matplotlib Chart Filepaths
    - Intelligent Pattern Observations & Academic CT Analysis
    """
    from fitness import (
        calculate_bmi,
        get_bmi_category,
        calculate_bmr,
        calculate_tdee,
        get_fitness_disclaimer
    )

    user_id = str(profile.get("id", "1"))
    age = int(profile.get("age", 20))
    height = float(profile.get("height", 170.0))
    weight = float(profile.get("weight", 65.0))
    sex = str(profile.get("sex", "male"))
    activity_level = str(profile.get("activity_level", "moderate"))
    step_goal = int(profile.get("step_goal", 10000))
    water_goal = float(profile.get("water_goal", 3.0))

    # Calculate core fitness metrics
    bmi = calculate_bmi(weight, height)
    bmi_info = get_bmi_category(bmi, age)
    bmr = calculate_bmr(weight, height, age, sex)
    tdee_info = calculate_tdee(bmr, activity_level, age)

    # Generate visual charts
    weekly_chart_path = generate_weekly_activity_chart(activities, step_goal, user_id)
    dist_chart_path = generate_activity_distribution_chart(activities, user_id)
    hydration_chart_path = generate_hydration_trends_chart(activities, water_goal, user_id)

    # Synthesize intelligent feedback observations
    observations = []

    # Step Consistency Observation
    avg_steps = statistics.get("avg_steps", 0)
    step_pct = statistics.get("step_goal_completion_pct", 0)
    if avg_steps >= step_goal:
        observations.append({
            "title": "Aerobic Stamina & Step Target",
            "type": "positive",
            "text": f"Your average daily step count of {avg_steps:,} successfully surpasses your target ({step_goal:,} steps). You achieved your step target on {step_pct}% of logged days, demonstrating consistent aerobic conditioning."
        })
    else:
        diff = step_goal - avg_steps
        observations.append({
            "title": "Daily Step Progress",
            "type": "neutral",
            "text": f"You are averaging {avg_steps:,} steps/day, which is within {diff:,} steps of your daily goal. Incorporating short brisk walks between classes will help bridge this gap."
        })

    # Hydration Observation
    avg_water = statistics.get("avg_water_litres", 0.0)
    water_pct = statistics.get("water_goal_completion_pct", 0)
    if avg_water >= water_goal:
        observations.append({
            "title": "Optimal Fluid Balance",
            "type": "positive",
            "text": f"Excellent hydration habits! You consumed an average of {avg_water:.2f} L of water daily, meeting your goal on {water_pct}% of days to support cellular recovery and cognitive alertness."
        })
    else:
        observations.append({
            "title": "Hydration Reminder",
            "type": "advisory",
            "text": f"Your average hydration is {avg_water:.2f} L/day compared to your target of {water_goal:.1f} L. Keeping a reusable water bottle during laboratory lectures will maintain sustained mental focus."
        })

    # Exercise Variety & Modality
    activity_counts = statistics.get("activity_counts", {})
    if len(activity_counts) >= 3:
        observations.append({
            "title": "Exercise Diversity",
            "type": "positive",
            "text": f"Great cross-training! You engaged in {len(activity_counts)} different training modalities ({', '.join(activity_counts.keys())}), fostering multi-planar mobility and reducing overuse injury risk."
        })
    elif len(activity_counts) == 1:
        single_type = list(activity_counts.keys())[0]
        observations.append({
            "title": "Cross-Training Recommendation",
            "type": "neutral",
            "text": f"Most of your logged sessions belong to '{single_type}'. Adding a secondary modality like swimming, bodyweight resistance, or yoga can enhance functional balance."
        })

    # Computational Thinking Reflection for Bennett University Course
    ct_reflection = (
        "Computational Thinking Analysis: This project applies the four foundational pillars "
        "of Computational Thinking: (1) Decomposition — breaking down personal wellness into discrete "
        "sub-problems (biometrics, hydration, energy balance); (2) Pattern Recognition — identifying "
        "activity spikes, rest-day dips, and habit streaks; (3) Abstraction — modeling complex physiological "
        "processes with established mathematical equations (Mifflin-St Jeor & MET indices); and "
        "(4) Algorithm Design — implementing deterministic validation, file storage, and statistical aggregation."
    )

    report_timestamp = datetime.now().strftime("%B %d, %Y - %I:%M %p")

    return {
        "report_id": f"WR-{user_id}-{datetime.now().strftime('%Y%m%d%H%M')}",
        "generated_at": report_timestamp,
        "academic_context": {
            "university": "Bennett University",
            "school": "School of Computer Science Engineering and Technology",
            "course": "Computational Thinking and Programming",
            "course_code": "2026CSAE100",
            "academic_year": "2026–27"
        },
        "profile": profile,
        "bmi": bmi,
        "bmi_info": bmi_info,
        "bmr": bmr,
        "tdee_info": tdee_info,
        "statistics": statistics,
        "charts": {
            "weekly_chart": weekly_chart_path,
            "distribution_chart": dist_chart_path,
            "hydration_chart": hydration_chart_path
        },
        "observations": observations,
        "ct_reflection": ct_reflection,
        "disclaimer": get_fitness_disclaimer()
    }
