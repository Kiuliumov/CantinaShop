document.addEventListener('DOMContentLoaded', () => {
  const orderLink = document.querySelector('.order-link');
  const quantityInput = document.getElementById('quantity-input');

  if (orderLink && quantityInput) {
    orderLink.addEventListener('click', (e) => {
      e.preventDefault();

      const baseHref = orderLink.getAttribute('href').split('?')[0];
      const quantity = parseInt(quantityInput.value, 10) || 1;
        window.location.href = `${baseHref}?quantity=${quantity}`;
    });
  }
});
