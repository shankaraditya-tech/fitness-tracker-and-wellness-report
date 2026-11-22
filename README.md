# Fitness Tracker & Personal Wellness Report Generator
### Computational Thinking and Programming (Course Code: 2026CSAE100)
**School of Computer Science Engineering and Technology (SCSET)**  
**Bennett University, Greater Noida**  
**Academic Year:** 2026–27  

---

## 1. Project Introduction
The **Fitness Tracker & Personal Wellness Report Generator** is a full-stack, modular Python web application built for first-year Computer Science Engineering students. It provides an intuitive, high-tech interface for tracking daily physical activity, estimating metabolic parameters using established clinical equations, evaluating adherence to fitness goals, storing historical logs persistently in CSV spreadsheets, and rendering analytical charts with Matplotlib.

---

## 2. Problem Statement
First-year college students often struggle to balance demanding academic schedules (lectures, programming lab sessions, assignments) with adequate physical activity, regular sleep, and healthy hydration. Most commercial fitness tools are either locked behind subscription paywalls, store private health data on unverified cloud servers, or present complex metrics without explaining the underlying computational or mathematical models.

There is a clear need for a transparent, locally run wellness management tool that:
1. Keeps all personal fitness logs private and accessible in transparent CSV format.
2. Explains the exact mathematical models (Mifflin-St Jeor equation, WHO BMI indices, MET activity values) rather than treating them as a black box.
3. Incorporates important ethical safeguards (such as pediatric safety warnings for individuals under 18).
4. Demonstrates fundamental computational thinking pillars (Decomposition, Pattern Recognition, Abstraction, and Algorithm Design) in Python.

---

## 3. Project Objectives
- **Modularity:** Separate business logic (`fitness.py`), persistent storage (`csv_manager.py`), visual chart synthesis (`report_generator.py`), and web routing (`app.py`).
- **Data Integrity:** Prevent accidental duplicate logs on identical dates while permitting explicit edits and updates.
- **Accurate Calculations:** Implement the Mifflin-St Jeor BMR equation, BMI formula, and TDEE activity multipliers with edge-case validation.
- **Visual Analytics:** Use Python's Matplotlib library in a headless environment to generate dual-axis activity charts, modality distributions, and hydration progressions.
- **Academic Reporting:** Generate a comprehensive, printable Personal Wellness Report with faculty grading rubrics for project viva evaluation.

---

## 4. Technologies Used
| Technology | Role in Project |
| :--- | :--- |
| **Python 3 (3.10+)** | Core programming language for data structures, algorithms, and business logic |
| **Flask (3.1+)** | Lightweight Python WSGI web application framework and routing engine |
| **Jinja2** | Template rendering engine for dynamic HTML generation |
| **Matplotlib (3.11+)** | Scientific visualization library for generating high-resolution charts |
| **CSV (Built-in)** | Structured file persistence using `csv.DictReader` and `csv.DictWriter` |
| **HTML5 & CSS3** | Modern semantic structure and dark/light fitness-tech user interface |
| **JavaScript (ES6)** | Theme switching (`localStorage`), mobile navigation drawer, and dynamic live calculation |

---

## 5. Project Directory Structure
```
fitness_tracker/
├── app.py                  # Core Flask controller and route handlers
├── fitness.py              # Mathematical formulas, validations, and metabolic logic
├── csv_manager.py          # CSV persistence, duplicate handling, and statistical queries
├── report_generator.py     # Matplotlib headless chart rendering and report aggregation
├── requirements.txt        # Python package dependencies
├── README.md               # Complete project documentation and viva guide
├── data/
│   ├── profiles.csv        # Persistent user biometric profiles and fitness goals
│   └── activity.csv        # Daily logged fitness records
├── static/
│   ├── css/
│   │   └── style.css       # Premium fitness-tech design system (dark/light themes)
│   ├── js/
│   │   └── script.js       # Client-side theme toggle, live calculator, and UI helpers
│   └── images/
│       └── charts/         # Headless Matplotlib charts saved dynamically
└── templates/
    ├── base.html           # Master layout with sidebar navigation & topbar
    ├── index.html          # Academic project overview & Computational Thinking guide
    ├── dashboard.html      # Main fitness dashboard with daily metrics & charts
    ├── profile.html        # User profile creator/editor & goal configuration
    ├── tracker.html        # Daily activity logger & records table
    ├── tracker_edit.html   # Activity editing form
    ├── calculator.html     # Interactive BMI, BMR, and TDEE calculator
    ├── progress.html       # Statistical averages, streak tracking, & Matplotlib charts
    └── report.html         # Downloadable / printable Personal Wellness Report
```

---

## 6. Core Features & Capabilities

### 1. Modern Dashboard
- Time-aware personalized greeting ("Good morning", "Good afternoon", "Good evening").
- Real-time KPI cards for Daily Steps, Exercise Minutes, Water Intake, and Calories Burned.
- Animated progress bars displaying percentage completion against personal goals.
- Dual-axis weekly activity chart embedded directly from Matplotlib.
- Active logging streak counter and recent activity history table.

### 2. User Profile & Goal Customization
- Validates Name, Age (10–120), Height (50–250 cm), Weight (20–300 kg), Biological Sex, and Activity Level.
- Custom daily fitness targets: Step Goal (e.g. 10,000), Workout Goal (e.g. 45 min), Hydration Goal (e.g. 3.0 L).
- Multi-user support with quick-switching dropdown in the top navigation bar.

### 3. Fitness & Metabolic Calculator
- **BMI Calculation:** $\text{BMI} = \frac{\text{weight in kg}}{(\text{height in m})^2}$
- **BMR (Mifflin-St Jeor):**
  - **Male:** $10 \times \text{weight} + 6.25 \times \text{height} - 5 \times \text{age} + 5$
  - **Female:** $10 \times \text{weight} + 6.25 \times \text{height} - 5 \times \text{age} - 161$
- **TDEE (Total Daily Energy Expenditure):** Multiplies BMR by physical activity factor (1.20 to 1.90).
- **Pediatric Safeguard:** For users under 18, adult BMI categories and adult deficit/surplus calorie recommendations are suppressed and replaced by a clinical pediatric growth advisory notice.
- **Educational Notice:** Explicitly reminds students that all metrics are educational approximations and not medical prescriptions.

### 4. Daily Activity Logger & CSV Persistence
- Date picker, steps input, exercise duration, water volume in litres, activity selection, and personal notes.
- **Duplicate Prevention:** Prevents accidental overwriting of past logs on the same date unless explicitly requested.
- **MET Calorie Estimation:** Estimates workout calories burned using Metabolic Equivalent of Task values:
  $\text{Calories} = \frac{\text{MET} \times 3.5 \times \text{weight (kg)}}{200} \times \text{duration (min)}$

### 5. Progress Analytics & Matplotlib Charts
- Dynamic headless rendering using `matplotlib.use('Agg')`.
- Dual-axis bar and line chart of steps vs target line.
- Donut chart depicting breakdown of workouts (Gym, Running, Cycling, Yoga, Swimming, etc.).
- Area progression graph of daily water intake.
- Summary statistics: mean steps, mean workout minutes, mean hydration, best single day, and active streaks.

### 6. Personal Wellness Report
- Printable, downloadable academic wellness report.
- Includes institutional branding for Bennett University, candidate profile, computed biometrics, activity breakdown, Matplotlib figures, automated observations, and Computational Thinking reflections.
- Print-optimized CSS (`@media print`) hides navigation bars for clean paper or PDF printing.
- Includes a faculty evaluation rubric with score allocations for 2026CSAE100.

---

## 7. Python Concepts Demonstrated (Viva Preparation Guide)

When demonstrating this project to faculty, reference these foundational programming concepts:

### 1. Variables and Data Types
- **Integers:** Used for steps count, exercise duration (minutes), age, and loop indices.
- **Floats:** Used for height (cm), weight (kg), water intake (litres), and BMI calculations.
- **Strings:** Used for names, dates (`YYYY-MM-DD`), activity types, and notes.
- **Booleans:** Used for validation flags (`is_valid`, `is_pediatric`, `allow_update`).

### 2. Conditional Branching (`if / elif / else`)
- Validating inputs (e.g. checking if height is between 50 and 250 cm).
- Determining BMI categories (Underweight $< 18.5$, Normal $18.5–24.9$, Overweight $25–29.9$, Obese $\ge 30$).
- Selecting sex-specific formula adjustments in the Mifflin-St Jeor formula ($+5$ for males, $-161$ for females).
- Enforcing pediatric safety rules when `age < 18`.

### 3. Loops and Iteration (`for` and `while`)
- Iterating through CSV records using `for row in reader:`.
- Calculating active streaks by traversing chronologically sorted activity records backwards.
- Computing totals and averages using list comprehensions and generators.

### 4. Lists and List Comprehensions
- Extracting date strings: `dates = [e["date"][5:] for e in recent_entries]`
- Filtering activities: `user_activities = [a for a in all_activities if a["user_id"] == target_user]`
- Sorting records chronologically by date: `activities.sort(key=lambda item: item["date"])`

### 5. Dictionaries and Key-Value Mapping
- Storing structured activity logs (`date`, `steps`, `exercise_minutes`, `water_litres`, `notes`).
- Mapping activity levels to their numeric multipliers:
  ```python
  ACTIVITY_MULTIPLIERS = {
      "sedentary": {"factor": 1.20, "title": "Sedentary"},
      "light": {"factor": 1.375, "title": "Lightly Active"},
      "moderate": {"factor": 1.55, "title": "Moderately Active"},
      ...
  }
  ```

### 6. Modular Functions & Type Hinting
- Every task is broken into reusable functions with type annotations and docstrings:
  ```python
  def calculate_bmi(weight_kg: float, height_cm: float) -> float:
  ```
- Separating presentation (`app.py`), mathematics (`fitness.py`), and storage (`csv_manager.py`).

### 7. Exception Handling (`try / except / finally`)
- Preventing program crashes when users enter invalid text into numeric fields (`ValueError`).
- Gracefully handling missing CSV files (`FileNotFoundError`, `OSError`) by automatically re-creating files with proper headers.

### 8. CSV File Handling (`csv.DictReader` & `csv.DictWriter`)
- Reading and writing comma-separated files with headers:
  ```python
  with open(ACTIVITY_CSV, mode="r", newline="", encoding="utf-8") as f:
      reader = csv.DictReader(f)
  ```

---

## 8. Installation & Setup Instructions

### Prerequisites
- Python 3.10 or higher installed on your computer.
- Terminal / Command Prompt or VS Code / Antigravity terminal.

### Step 1: Navigate to Project Directory
```bash
cd "/Users/adityashankar/Desktop/python project/fitness_tracker"
```

### Step 2: Install Required Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies: `Flask>=3.0.0` and `matplotlib>=3.8.0`)*

### Step 3: Run the Application
```bash
python3 app.py
```

### Step 4: Access in Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
*(Or `http://localhost:5000`)*

---

## 9. Faculty Demonstration Checklist

Follow this sequence when presenting your project in the evaluation viva:

1. **Project Overview (`/`):**
   - Show the academic header for Bennett University, Course 2026CSAE100.
   - Explain how the 4 pillars of Computational Thinking are embodied in the design.
2. **Dashboard (`/dashboard`):**
   - Point out the time-aware greeting and the candidate profile summary.
   - Show the live KPI cards and animated goal progress meters.
   - Point to the weekly activity chart generated dynamically by Python Matplotlib.
3. **Log a New Activity (`/tracker`):**
   - Fill in today's steps, workout minutes, water intake, and a workout note.
   - Submit the form and verify that the new entry appears immediately in the table and updates the dashboard totals.
   - Demonstrate duplicate prevention: try entering another log for the same date without checking the update box.
4. **Fitness Calculator (`/calculator`):**
   - Demonstrate the Mifflin-St Jeor formula and BMI computation.
   - **Crucial Viva Test:** Change the age to **16** and demonstrate how the pediatric safeguard automatically suppresses adult categories and displays the pediatric growth advisory notice!
   - Change age back to **19** to show adult maintenance calorie guidelines.
5. **Progress & Matplotlib Analytics (`/progress`):**
   - Show the 3 Matplotlib charts: Dual-Axis Weekly Target, Exercise Modality Donut, and Hydration Progression.
   - Explain how `matplotlib.use('Agg')` allows headless server-side rendering without pop-up windows.
6. **Wellness Report & Print Preview (`/report`):**
   - Click "Print / Save as PDF" to demonstrate how clean `@media print` CSS formats the document for official submission.
   - Show the faculty grading rubric section at the bottom of the report.
7. **Code Walkthrough:**
   - Open `fitness.py`, `csv_manager.py`, and `app.py` in VS Code to explain your modular architecture, list comprehensions, and exception handling.

---

## 10. Academic Honor Code Statement
This project was developed by a first-year student of the School of Computer Science Engineering and Technology, Bennett University, for the Computational Thinking and Programming course (2026CSAE100), Academic Year 2026–27. All logic, validation routines, and documentation have been crafted to adhere to the highest academic integrity standards.
