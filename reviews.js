document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".review-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const card = btn.closest(".review-card, .strategy-card");
      const details = card ? card.querySelector(".review-card__details, .review-details") : null;
      if (!details) return;
      const isOpen = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!isOpen));
      if (isOpen) {
        details.style.maxHeight = null;
        details.classList.remove("is-open");
        btn.textContent = "Detailed Review";
      } else {
        details.style.maxHeight = details.scrollHeight + "px";
        details.classList.add("is-open");
        btn.textContent = "Hide Review";
      }
    });
  });
});
