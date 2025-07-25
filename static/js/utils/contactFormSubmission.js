  const form = document.getElementById('contact-form');
  const successPopup = document.getElementById('form-popup-success');
  const closeBtn = document.getElementById('popup-success-close');
  const okBtn = document.getElementById('popup-success-ok');

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(form);
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: formData
      });
      if (response.ok) {
        form.reset();
        successPopup.classList.remove('opacity-0', 'pointer-events-none');
        successPopup.classList.add('opacity-100');
        setTimeout(() => {
          successPopup.classList.add('opacity-0', 'pointer-events-none');
          successPopup.classList.remove('opacity-100');
        }, 5000);
      } else {
        alert('There was a problem with your submission.');
      }
    } catch (error) {
      alert('Network error occurred.');
    }
  });

  function hideSuccessPopup() {
    successPopup.classList.add('opacity-0', 'pointer-events-none');
    successPopup.classList.remove('opacity-100');
  }

  closeBtn.addEventListener('click', hideSuccessPopup);
  okBtn.addEventListener('click', hideSuccessPopup);