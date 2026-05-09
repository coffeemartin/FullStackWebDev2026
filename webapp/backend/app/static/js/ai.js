document.querySelectorAll("[data-training-exercise-form]").forEach((form) => {
  const editButton = form.querySelector("[data-training-edit]");
  const saveButton = form.querySelector(".training-save-btn");
  const viewBlocks = form.querySelectorAll("[data-training-view]");
  const editGrid = form.querySelector(".training-edit-grid");
  const editFields = form.querySelectorAll(".training-edit-field");

  if (!editButton || !saveButton || !editGrid) {
    return;
  }

  editButton.addEventListener("click", () => {
    viewBlocks.forEach((block) => block.classList.add("d-none"));
    editGrid.classList.remove("d-none");
    editFields.forEach((field) => {
      field.classList.remove("d-none");
      field.removeAttribute("readonly");
    });
    editButton.classList.add("d-none");
    saveButton.classList.remove("d-none");
    editFields[0]?.focus();
  });
});
