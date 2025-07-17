document.addEventListener('DOMContentLoaded', () => {
  const deleteButtons = document.querySelectorAll('.delete-btn');
  const modal = document.getElementById('confirmModal');
  const confirmYes = document.getElementById('confirmYes');
  const confirmNo = document.getElementById('confirmNo');
  let formToSubmit = null;
  let linkToFollow = null;

  deleteButtons.forEach(button => {
    button.addEventListener('click', event => {
      event.preventDefault();

      formToSubmit = null;
      linkToFollow = null;

      if (button.tagName === 'BUTTON' && button.closest('form')) {
        formToSubmit = button.closest('form');
      } else if (button.tagName === 'A') {
        linkToFollow = button.href;
      }

      modal.classList.remove('hidden');
    });
  });

  confirmYes.addEventListener('click', () => {
    modal.classList.add('hidden');
    if (formToSubmit) {
      formToSubmit.submit();
    } else if (linkToFollow) {
      window.location.href = linkToFollow;
    }
  });

  confirmNo.addEventListener('click', () => {
    modal.classList.add('hidden');
    formToSubmit = null;
    linkToFollow = null;
  });
});
