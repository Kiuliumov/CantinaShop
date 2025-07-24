document.addEventListener('DOMContentLoaded', () => {
  const successPopup = document.getElementById('cart-popup-success');
  const errorPopup = document.getElementById('cart-popup-error');

  const showPopup = (popup) => {
    popup.classList.remove('opacity-0', 'pointer-events-none');
    popup.classList.add('opacity-100');
  };

  const hidePopup = (popup) => {
    popup.classList.add('opacity-0', 'pointer-events-none');
    popup.classList.remove('opacity-100');
  };

  const successCloseBtn = document.getElementById('popup-success-close');
  const successOkBtn = document.getElementById('popup-success-ok');
  const errorCloseBtn = document.getElementById('popup-error-close');
  const errorOkBtn = document.getElementById('popup-error-ok');

  if (successCloseBtn) successCloseBtn.addEventListener('click', () => hidePopup(successPopup));
  if (successOkBtn) successOkBtn.addEventListener('click', () => hidePopup(successPopup));
  if (errorCloseBtn) errorCloseBtn.addEventListener('click', () => hidePopup(errorPopup));
  if (errorOkBtn) errorOkBtn.addEventListener('click', () => hidePopup(errorPopup));

  const hideAllPopups = () => {
    hidePopup(successPopup);
    hidePopup(errorPopup);
  };

  if (localStorage.getItem('addedToCartSuccess') === 'true') {
    showPopup(successPopup);
    localStorage.removeItem('addedToCartSuccess');

    setTimeout(() => {
      hidePopup(successPopup);
    }, 3000);
  }

  if (localStorage.getItem('addedToCartError') === 'true') {
    showPopup(errorPopup);
    localStorage.removeItem('addedToCartError');

    setTimeout(() => {
      hidePopup(errorPopup);
    }, 3000);
  }

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      hideAllPopups();
    }
  });

  window.addEventListener('beforeunload', () => {
    hideAllPopups();
  });

  const orderLink = document.querySelector('.order-link');
  if (orderLink) {
    orderLink.addEventListener('click', (e) => {
      e.preventDefault();
      localStorage.setItem('addedToCartSuccess', 'true');
      window.location.href = orderLink.href;
    });
  }
});
