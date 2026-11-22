/**
 * ==============================================================================
 * FITNESS TRACKER & WELLNESS REPORT GENERATOR - CLIENT-SIDE SCRIPT
 * Course: Computational Thinking & Programming (2026CSAE100)
 * Bennett University (SCSET)
 * ==============================================================================
 */

document.addEventListener("DOMContentLoaded", function () {
  initThemeToggle();
  initMobileMenu();
  initLiveCalculator();
  initAlertDismissal();
});

/**
 * 1. Dark / Light Theme Toggle with LocalStorage persistence
 */
function initThemeToggle() {
  const toggleBtn = document.getElementById("themeToggleBtn");
  const themeIcon = document.getElementById("themeIcon");
  const themeLabel = document.getElementById("themeLabel");

  // Read saved preference or system preference
  const savedTheme = localStorage.getItem("bu_fitness_theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeButtonUI(savedTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener("click", function () {
      const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
      const newTheme = currentTheme === "dark" ? "light" : "dark";

      document.documentElement.setAttribute("data-theme", newTheme);
      localStorage.setItem("bu_fitness_theme", newTheme);
      updateThemeButtonUI(newTheme);
    });
  }

  function updateThemeButtonUI(theme) {
    if (!themeIcon || !themeLabel) return;
    if (theme === "light") {
      themeIcon.textContent = "🌙";
      themeLabel.textContent = "Dark Mode";
    } else {
      themeIcon.textContent = "☀️";
      themeLabel.textContent = "Light Mode";
    }
  }
}

/**
 * 2. Mobile Responsive Sidebar Drawer Toggle
 */
function initMobileMenu() {
  const menuBtn = document.getElementById("mobileMenuBtn");
  const sidebar = document.querySelector(".app-sidebar");

  if (menuBtn && sidebar) {
    menuBtn.addEventListener("click", function () {
      sidebar.classList.toggle("mobile-open");
    });

    // Close when clicking outside on mobile
    document.addEventListener("click", function (event) {
      if (
        sidebar.classList.contains("mobile-open") &&
        !sidebar.contains(event.target) &&
        !menuBtn.contains(event.target)
      ) {
        sidebar.classList.remove("mobile-open");
      }
    });
  }
}

/**
 * 3. Interactive Real-Time Calculator (API Integration)
 */
function initLiveCalculator() {
  const calcForm = document.getElementById("liveCalcForm");
  if (!calcForm) return;

  const ageInput = document.getElementById("calcAge");
  const heightInput = document.getElementById("calcHeight");
  const weightInput = document.getElementById("calcWeight");
  const sexInputs = document.querySelectorAll('input[name="sex"]');
  const activitySelect = document.getElementById("calcActivity");

  // Output elements
  const bmiVal = document.getElementById("resBmiVal");
  const bmiBadge = document.getElementById("resBmiBadge");
  const bmiDesc = document.getElementById("resBmiDesc");
  const bmrVal = document.getElementById("resBmrVal");
  const tdeeVal = document.getElementById("resTdeeVal");
  const pediatricNotice = document.getElementById("resPediatricNotice");
  const adultCalorieTable = document.getElementById("resAdultCalorieTable");

  function triggerCalculation() {
    const age = parseInt(ageInput?.value || 20);
    const height = parseFloat(heightInput?.value || 170);
    const weight = parseFloat(weightInput?.value || 65);
    let sex = "male";
    sexInputs.forEach((input) => {
      if (input.checked) sex = input.value;
    });
    const activity = activitySelect?.value || "moderate";

    if (!age || !height || !weight) return;

    fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        age: age,
        height: height,
        weight: weight,
        sex: sex,
        activity_level: activity,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (!data.success) return;

        // Update BMI
        if (bmiVal) bmiVal.textContent = data.bmi.toFixed(1);
        if (bmiBadge) {
          bmiBadge.textContent = data.bmi_category;
          bmiBadge.className = `badge-status ${
            data.is_pediatric
              ? "badge-info"
              : data.bmi < 18.5
              ? "badge-warning"
              : data.bmi < 25
              ? "badge-success"
              : data.bmi < 30
              ? "badge-amber"
              : "badge-danger"
          }`;
        }
        if (bmiDesc) bmiDesc.textContent = data.bmi_description;

        // Update BMR & TDEE
        if (bmrVal) bmrVal.textContent = Math.round(data.bmr) + " kcal";
        if (tdeeVal) tdeeVal.textContent = Math.round(data.tdee) + " kcal";

        // Safeguard for Under 18
        if (data.is_pediatric) {
          if (pediatricNotice) pediatricNotice.style.display = "flex";
          if (adultCalorieTable) adultCalorieTable.style.display = "none";
        } else {
          if (pediatricNotice) pediatricNotice.style.display = "none";
          if (adultCalorieTable) {
            adultCalorieTable.style.display = "block";
            // Populate table values if present
            const maint = document.getElementById("calMaintenance");
            const mildLoss = document.getElementById("calMildLoss");
            const loss = document.getElementById("calLoss");
            const gain = document.getElementById("calGain");

            if (maint && data.recommended_ranges) {
              maint.textContent = data.recommended_ranges.maintenance + " kcal";
              if (mildLoss) mildLoss.textContent = data.recommended_ranges.mild_weight_loss + " kcal";
              if (loss) loss.textContent = data.recommended_ranges.weight_loss + " kcal";
              if (gain) gain.textContent = data.recommended_ranges.mild_weight_gain + " kcal";
            }
          }
        }
      })
      .catch((err) => console.log("Calculation error:", err));
  }

  // Attach event listeners for real-time calculation
  [ageInput, heightInput, weightInput, activitySelect].forEach((el) => {
    if (el) {
      el.addEventListener("input", triggerCalculation);
      el.addEventListener("change", triggerCalculation);
    }
  });

  sexInputs.forEach((r) => r.addEventListener("change", triggerCalculation));
}

/**
 * 4. Dismissible Flash Message Alerts
 */
function initAlertDismissal() {
  const closeBtns = document.querySelectorAll(".alert-close");
  closeBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const alert = this.closest(".alert-card");
      if (alert) {
        alert.style.opacity = "0";
        alert.style.transform = "translateY(-8px)";
        alert.style.transition = "all 0.2s ease";
        setTimeout(() => alert.remove(), 200);
      }
    });
  });
}
