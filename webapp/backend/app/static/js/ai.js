function setExerciseEditableState(form, editing) {
  const viewBlocks = form.querySelectorAll("[data-training-view]");
  const editGrid = form.querySelector(".training-edit-grid");
  const editFields = form.querySelectorAll(".training-edit-field");
  const removeButton = form.querySelector("[data-training-remove-exercise]");

  if (!editGrid) return;

  if (editing) {
    viewBlocks.forEach((block) => block.classList.add("d-none"));
    editGrid.classList.remove("d-none");
    editFields.forEach((field) => {
      field.classList.remove("d-none");
      field.removeAttribute("readonly");
    });
    if (removeButton) removeButton.classList.remove("d-none");
  } else {
    viewBlocks.forEach((block) => block.classList.remove("d-none"));
    editGrid.classList.add("d-none");
    editFields.forEach((field) => {
      field.classList.add("d-none");
      field.setAttribute("readonly", "readonly");
    });
    if (removeButton) removeButton.classList.add("d-none");
  }
}

function createExerciseForm(dayIndex, exercise = {}) {
  const li = document.createElement("li");
  li.className = "training-exercise-item";

  li.innerHTML = `
    <form method="post" class="training-exercise-form" data-training-exercise-form>
      <input type="hidden" name="day_index" value="${dayIndex}" />
      <input type="hidden" name="exercise_index" value="" />
      <div class="training-exercise-title-row">
        <strong class="training-view-value d-none" data-training-view="name"></strong>
        <input type="text" class="form-control form-control-sm training-edit-field" name="name" value="" readonly placeholder="Exercise name" />
        <div class="training-card-actions">
          <button type="button" class="btn btn-outline-danger btn-sm d-none training-remove-exercise-btn" data-training-remove-exercise aria-label="Remove exercise">-</button>
        </div>
      </div>
      <div class="training-exercise-meta training-view-meta d-none" data-training-view="meta"></div>
      <div class="training-edit-grid d-none">
        <div>
          <label class="form-label form-label-sm">Sets</label>
          <input type="text" class="form-control form-control-sm training-edit-field" name="sets" value="" readonly />
        </div>
        <div>
          <label class="form-label form-label-sm">Reps</label>
          <input type="text" class="form-control form-control-sm training-edit-field" name="reps" value="" readonly />
        </div>
        <div>
          <label class="form-label form-label-sm">Duration</label>
          <input type="text" class="form-control form-control-sm training-edit-field" name="duration_minutes" value="" readonly />
        </div>
        <div class="training-edit-notes">
          <label class="form-label form-label-sm">Notes</label>
          <textarea class="form-control form-control-sm training-edit-field" name="notes" rows="2" readonly></textarea>
        </div>
      </div>
      <div class="training-exercise-notes d-none" data-training-view="notes"></div>
    </form>
  `;

  const name = li.querySelector('input[name="name"]');
  const sets = li.querySelector('input[name="sets"]');
  const reps = li.querySelector('input[name="reps"]');
  const duration = li.querySelector('input[name="duration_minutes"]');
  const notes = li.querySelector('textarea[name="notes"]');
  if (exercise.name) name.value = exercise.name;
  if (exercise.sets) sets.value = exercise.sets;
  if (exercise.reps) reps.value = exercise.reps;
  if (exercise.duration_minutes) duration.value = exercise.duration_minutes;
  if (exercise.notes) notes.value = exercise.notes;

  return li;
}

// Give the main AI button a short "charging" phase before submitting.
const generateMagicBtn = document.querySelector(".ai-generate-btn");
if (generateMagicBtn) {
  const generateForm = generateMagicBtn.closest("form");
  let isCharging = false;
  const bodyEl = document.body;

  // Recover cleanly if browser restores this page from cache.
  window.addEventListener("pageshow", () => {
    isCharging = false;
    bodyEl?.classList.remove("ai-page-loading");
    generateMagicBtn.classList.remove("is-charging");
    generateMagicBtn.disabled = false;
    generateMagicBtn.removeAttribute("aria-busy");
  });

  const startChargingAndSubmit = (event) => {
    if (!generateForm || isCharging) return;

    event.preventDefault();
    isCharging = true;
    bodyEl?.classList.add("ai-page-loading");
    generateMagicBtn.classList.add("is-charging");
    generateMagicBtn.disabled = true;
    generateMagicBtn.setAttribute("aria-busy", "true");
    generateMagicBtn.textContent = "Forging Your Plan...";

    window.setTimeout(() => {
      if (typeof generateForm.requestSubmit === "function") {
        generateForm.requestSubmit();
      } else {
        generateForm.submit();
      }
    }, 220);
  };

  if (generateForm) {
    generateForm.addEventListener("submit", (event) => {
      if (!isCharging) {
        startChargingAndSubmit(event);
      }
    });
  }
}

// Global edit toggle: show edit fields across all exercise forms
const globalEditBtn = document.getElementById("training-global-edit");
if (globalEditBtn) {
  let globalEditing = false;
  globalEditBtn.addEventListener("click", () => {
    globalEditing = !globalEditing;
    globalEditBtn.textContent = globalEditing ? "Cancel" : "Save Plan";
    const topSaveBtn = document.getElementById("training-save-all-btn");
    document.querySelectorAll("[data-training-day-card]").forEach((card) => {
      const addBtn = card.querySelector("[data-training-add-exercise]");
      const forms = card.querySelectorAll("[data-training-exercise-form]");
      if (addBtn) addBtn.classList.toggle("d-none", !globalEditing);
      forms.forEach((form) => setExerciseEditableState(form, globalEditing));
    });

    if (topSaveBtn) {
      if (globalEditing) topSaveBtn.classList.remove("d-none");
      else topSaveBtn.classList.add("d-none");
    }
  });
}

// Profile edit toggle: show/hide profile edit fields and update button states
const profileEditBtn = document.getElementById("profile-edit-toggle");
const profileCancelBtn = document.getElementById("profile-edit-cancel");
// The data-profile-form attribute is on the <form> element in the profile section,
// which contains both the view and edit fields. This allows us to easily toggle between them.
const profileForm = document.querySelector("[data-profile-form]");
const profileViewPanel = document.getElementById("ai-profile-view");
if (profileEditBtn && profileForm) {
  let profileEditing = false;

  // Toggle between the stat-chip view panel and the edit form
  const setProfileEditableState = (editing) => {
    // Toggle the read-only view chips panel
    if (profileViewPanel) profileViewPanel.classList.toggle("d-none", editing);
    // Toggle the edit form
    profileForm.classList.toggle("d-none", !editing);

    if (profileCancelBtn) {
      profileCancelBtn.classList.toggle("d-none", !editing);
    }
    profileEditBtn.textContent = editing ? "Save Changes" : "Edit Profile";
    profileEditBtn.classList.toggle("btn-outline-secondary", !editing);
    profileEditBtn.classList.toggle("btn-success", editing);
  };

  setProfileEditableState(false);

  if (profileCancelBtn) {
    profileCancelBtn.addEventListener("click", () => {
      profileEditing = false;
      profileForm.reset();
      setProfileEditableState(false);
    });
  }
  profileEditBtn.addEventListener("click", () => {
    if (!profileEditing) {
      profileEditing = true;
      setProfileEditableState(true);
      return;
    }
    const formAction = profileForm.querySelector('input[name="form_action"]');
    if (formAction) formAction.value = "update_profile";
    profileForm.submit();
  });
}

document.querySelectorAll("[data-training-add-exercise]").forEach((button) => {
  button.addEventListener("click", () => {
    const card = button.closest("[data-training-day-card]");
    const list = card?.querySelector("[data-training-exercise-list]");
    if (!card || !list) return;

    const dayIndex = Array.from(
      document.querySelectorAll("[data-training-day-card]"),
    ).indexOf(card);
    const newExercise = createExerciseForm(dayIndex, {});
    newExercise
      .querySelector('[data-training-view="name"]')
      ?.classList.add("d-none");
    list.appendChild(newExercise);
    setExerciseEditableState(newExercise.querySelector("form"), true);
    const input = newExercise.querySelector('input[name="name"]');
    input?.focus();
  });
});

document.addEventListener("click", (event) => {
  const removeBtn = event.target.closest("[data-training-remove-exercise]");
  if (!removeBtn) return;

  const form = removeBtn.closest("[data-training-exercise-form]");
  const item = removeBtn.closest(".training-exercise-item");
  if (!form || !item) return;

  const card = form.closest("[data-training-day-card]");
  const list = card?.querySelector("[data-training-exercise-list]");
  const dayIndex = Array.from(
    document.querySelectorAll("[data-training-day-card]"),
  ).indexOf(card);
  item.remove();

  if (
    list &&
    list.querySelectorAll("[data-training-exercise-form]").length === 0
  ) {
    list.appendChild(createExerciseForm(dayIndex < 0 ? 0 : dayIndex, {}));
    const newForm = list.querySelector("[data-training-exercise-form]");
    if (newForm) setExerciseEditableState(newForm, true);
  }
});

// Save all edits handler: build plan from forms and submit hidden form
const saveAllBtn = document.getElementById("training-save-all-btn");
const saveAllForm = document.getElementById("training-save-all-form");
const trainingPlanInput = document.getElementById("training-plan-json-input");

if (saveAllBtn && saveAllForm) {
  saveAllBtn.addEventListener("click", () => {
    const base = [];

    document.querySelectorAll("[data-training-day-card]").forEach((card) => {
      const dayName =
        card.querySelector("[data-training-day-name]")?.textContent?.trim() ||
        "Day";
      const dayFocus =
        card.querySelector("[data-training-day-focus]")?.textContent?.trim() ||
        "";
      const day = { day: dayName, focus: dayFocus, exercises: [] };

      card.querySelectorAll("[data-training-exercise-form]").forEach((form) => {
        const nameEl = form.querySelector('input[name="name"]');
        const setsEl = form.querySelector('input[name="sets"]');
        const repsEl = form.querySelector('input[name="reps"]');
        const durEl = form.querySelector('input[name="duration_minutes"]');
        const notesEl = form.querySelector('textarea[name="notes"]');

        day.exercises.push({
          name: nameEl ? nameEl.value.trim() : "",
          sets: setsEl ? setsEl.value.trim() : "",
          reps: repsEl ? repsEl.value.trim() : "",
          duration_minutes: durEl ? durEl.value.trim() : "",
          notes: notesEl ? notesEl.value.trim() : "",
        });
      });

      base.push(day);
    });

    trainingPlanInput.value = JSON.stringify(base);
    saveAllForm.submit();
  });
}

/* Recommendation details rendering moved from inline template to JS */
function renderTraining(plan) {
  if (!plan || !plan.length) return "<p>No training plan.</p>";
  var html = [
    '<div class="table-responsive"><table class="table table-sm table-borderless text-white mb-0"><thead><tr><th>Day</th><th>Focus</th><th>Exercises</th></tr></thead><tbody>',
  ];
  plan.forEach(function (day) {
    var exercises = (day.exercises || [])
      .map(function (ex) {
        var meta = [];
        if (ex.sets) meta.push("Sets: " + ex.sets);
        if (ex.reps) meta.push("Reps: " + ex.reps);
        if (ex.duration_minutes)
          meta.push("Duration: " + ex.duration_minutes + "m");
        var notes = ex.notes
          ? '<div class="text-muted small">' + ex.notes + "</div>"
          : "";
        return (
          "<div><strong>" +
          (ex.name || "") +
          "</strong><div>" +
          meta.join(" · ") +
          "</div>" +
          notes +
          "</div>"
        );
      })
      .join('<hr class="my-2"/>');
    html.push(
      "<tr><td>" +
        (day.day || "") +
        "</td><td>" +
        (day.focus || "") +
        "</td><td>" +
        exercises +
        "</td></tr>",
    );
  });
  html.push("</tbody></table></div>");
  return html.join("");
}

function renderNutrition(nutrition) {
  if (!nutrition || !nutrition.length)
    return "<p>No nutrition recommendations.</p>";
  var html = ['<ul class="list-group list-group-flush">'];
  nutrition.forEach(function (item) {
    html.push(
      '<li class="list-group-item bg-transparent text-white"><strong>' +
        (item.goal || "") +
        '</strong><div class="text-muted">' +
        (item.suggestion || "") +
        "</div></li>",
    );
  });
  html.push("</ul>");
  return html.join("");
}

document.addEventListener("DOMContentLoaded", function () {
  var tempSlider = document.getElementById("temperature-slider");
  var tempValue = document.getElementById("temperature-value");
  if (tempSlider && tempValue) {
    var formatTemp = function (v) {
      return parseFloat(v).toFixed(2);
    };
    tempValue.textContent = formatTemp(tempSlider.value || 0);
    tempSlider.addEventListener("input", function (e) {
      tempValue.textContent = formatTemp(e.target.value || 0);
    });
  }

  var detailsPanel = document.getElementById("recommendation-details");
  document.querySelectorAll(".view-reco-btn").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      var tr = e.target.closest("tr");
      if (!tr) return;
      var training = tr.getAttribute("data-reco-training");
      var nutrition = tr.getAttribute("data-reco-nutrition");
      var summary = tr.getAttribute("data-reco-summary");
      try {
        training = JSON.parse(training);
      } catch (err) {
        training = null;
      }
      try {
        nutrition = JSON.parse(nutrition);
      } catch (err) {
        nutrition = null;
      }

      var detailsExercise = document.getElementById("details-exercise");
      var detailsNutrition = document.getElementById("details-nutrition");
      if (detailsExercise) detailsExercise.innerHTML = renderTraining(training);
      if (detailsNutrition)
        detailsNutrition.innerHTML = renderNutrition(nutrition);
      if (detailsPanel) {
        detailsPanel.classList.remove("d-none");
        detailsPanel.scrollIntoView({ behavior: "smooth" });
      }
    });
  });

  // Delete recommendation handler
  document.querySelectorAll(".set-current-btn").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      var tr = e.target.closest("tr");
      if (!tr) return;
      var recoId = tr.getAttribute("data-reco-id");
      if (!recoId) return;

      var csrfInput = document.querySelector('input[name="csrf_token"]');
      var token = csrfInput ? csrfInput.value : null;

      var fd = new FormData();
      if (token) fd.append("csrf_token", token);
      fd.append("recommendation_id", recoId);

      fetch("/AI/set-current", { method: "POST", body: fd })
        .then(function (resp) {
          if (!resp.ok) throw new Error("Request failed");
          return resp.json();
        })
        .then(function (data) {
          if (data && data.success) {
            window.location.reload();
          } else {
            alert((data && data.error) || "Could not set current plan.");
          }
        })
        .catch(function (err) {
          console.error(err);
          alert("Could not set current plan.");
        });
    });
  });

  document.querySelectorAll(".delete-reco-btn").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      var tr = e.target.closest("tr");
      if (!tr) return;
      var recoId = tr.getAttribute("data-reco-id");
      if (!recoId) return;

      if (!confirm("Delete this saved plan? This cannot be undone.")) return;

      var csrfInput = document.querySelector('input[name="csrf_token"]');
      var token = csrfInput ? csrfInput.value : null;

      var fd = new FormData();
      if (token) fd.append("csrf_token", token);
      fd.append("recommendation_id", recoId);

      fetch("/AI/delete-reco", { method: "POST", body: fd })
        .then(function (resp) {
          if (!resp.ok) throw new Error("Request failed");
          return resp.json();
        })
        .then(function (data) {
          if (data && data.success) {
            // remove the row
            tr.remove();
            // hide details panel if it was showing this reco
            var detailsPanel = document.getElementById(
              "recommendation-details",
            );
            if (
              detailsPanel &&
              detailsPanel.classList.contains("d-none") === false
            ) {
              detailsPanel.classList.add("d-none");
            }
          } else {
            alert((data && data.error) || "Could not delete recommendation.");
          }
        })
        .catch(function (err) {
          console.error(err);
          alert("Could not delete recommendation.");
        });
    });
  });
});
