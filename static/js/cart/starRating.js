document.addEventListener("DOMContentLoaded", () => {
  const starsContainer = document.getElementById("star-rating");
  if (!starsContainer) return;

  const stars = Array.from(starsContainer.querySelectorAll("label"));
  const radios = Array.from(starsContainer.querySelectorAll("input[type='radio']"));

  stars.forEach((star, index) => {
    star.addEventListener("mouseenter", () => {
      highlightStars(index);
    });

    star.addEventListener("mouseleave", () => {
      resetStars();
    });

    star.addEventListener("click", () => {
      setRating(index);
    });
  });

  function highlightStars(index) {
    stars.forEach((star, i) => {
      if (i <= index) {
        star.classList.add("text-yellow-500");
        star.classList.remove("text-yellow-400", "text-gray-400");
      } else {
        star.classList.remove("text-yellow-500", "text-yellow-400");
        star.classList.add("text-gray-400");
      }
    });
  }

  function resetStars() {
    const checkedIndex = radios.findIndex(radio => radio.checked);
    stars.forEach((star, i) => {
      if (i <= checkedIndex) {
        star.classList.add("text-yellow-400");
        star.classList.remove("text-yellow-500", "text-gray-400");
      } else {
        star.classList.remove("text-yellow-400", "text-yellow-500");
        star.classList.add("text-gray-400");
      }
    });
  }

  function setRating(index) {
    radios.forEach((radio, i) => {
      radio.checked = i === index;
    });
    resetStars();
  }

  resetStars();
});
