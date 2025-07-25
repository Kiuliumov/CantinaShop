document.addEventListener('DOMContentLoaded', () => {
  const successPopup = document.getElementById('form-popup-success');
  const closeBtn = document.getElementById('popup-success-close');
  const okBtn = document.getElementById('popup-success-ok');
  const editBtn = document.querySelector('.edit-btn');

  if (localStorage.getItem('isEditedSuccessfully') === 'true') {
    showSuccessPopup();
    localStorage.removeItem('isEditedSuccessfully');
  }

  if (editBtn) {
    editBtn.addEventListener('click', () => {
      localStorage.setItem('isEditedSuccessfully', 'true');
    });
  }

  function showSuccessPopup() {
    if (!successPopup) return;
    successPopup.classList.remove('opacity-0', 'pointer-events-none');

    setTimeout(() => {
      hideSuccessPopup();
    }, 3000);
  }

  function hideSuccessPopup() {
    if (!successPopup) return;
    successPopup.classList.add('opacity-0', 'pointer-events-none');
  }
});
