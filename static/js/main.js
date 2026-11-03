const resumeInput = document.getElementById("resume");
if (resumeInput) {
  resumeInput.addEventListener("change", function () {
    const label = document.getElementById("fileLabel");
    if (this.files.length) label.textContent = this.files[0].name;
  });
}
function confirmDelete() {
  return window.confirm("Delete this candidate record permanently?");
}
