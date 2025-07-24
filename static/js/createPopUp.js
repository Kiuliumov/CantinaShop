document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('successModal');
  const closeBtn = document.getElementById('successClose');

  if (localStorage.getItem('showSuccessModal') === 'true') {
    modal.classList.remove('hidden');
    localStorage.removeItem('showSuccessModal');

    setTimeout(() => {
      modal.classList.add('hidden');
    }, 6000);
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
    localStorage.removeItem('showSuccessModal');
    });
  }
});
