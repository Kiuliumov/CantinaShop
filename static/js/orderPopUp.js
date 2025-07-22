document.addEventListener('DOMContentLoaded', function () {
  const orderLink = document.getElementById('order-link');

  const successPopup = document.getElementById('cart-popup-success');
  const successCloseBtn = document.getElementById('popup-success-close');
  const successOkBtn = document.getElementById('popup-success-ok');

  const errorPopup = document.getElementById('cart-popup-error');
  const errorCloseBtn = document.getElementById('popup-error-close');
  const errorOkBtn = document.getElementById('popup-error-ok');

  function showPopup(popup) {
    popup.classList.remove('opacity-0', 'pointer-events-none');
    popup.classList.add('opacity-100');

    setTimeout(() => {
      popup.classList.add('opacity-0', 'pointer-events-none');
    }, 4000);
  }

  function hidePopup(popup) {
    popup.classList.add('opacity-0', 'pointer-events-none');
  }

  if (orderLink) {
    orderLink.addEventListener('click', async function (e) {
      e.preventDefault();
      const url = orderLink.getAttribute('data-url');

      try {
        const response = await fetch(url, {
          method: 'GET',
          credentials: 'same-origin',
        });

        if (response.ok) {
          showPopup(successPopup);
        } else {
          showPopup(errorPopup);
          console.error('Failed to add to cart:', response.status);
        }
      } catch (err) {
        showPopup(errorPopup);
        console.error('Error:', err);
      }
    });
  }

  if (successCloseBtn) successCloseBtn.addEventListener('click', () => hidePopup(successPopup));
  if (successOkBtn) successOkBtn.addEventListener('click', () => hidePopup(successPopup));

  if (errorCloseBtn) errorCloseBtn.addEventListener('click', () => hidePopup(errorPopup));
  if (errorOkBtn) errorOkBtn.addEventListener('click', () => hidePopup(errorPopup));
});
