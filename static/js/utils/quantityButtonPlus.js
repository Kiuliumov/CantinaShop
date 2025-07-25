document.addEventListener('DOMContentLoaded', () => {
  const qtyInput = document.getElementById('quantity-input');
  const incrementBtn = document.getElementById('quantity-increment');
  const decrementBtn = document.getElementById('quantity-decrement');

  incrementBtn.addEventListener('click', () => {
    qtyInput.value = parseInt(qtyInput.value) + 1;
  });

  decrementBtn.addEventListener('click', () => {
    let val = parseInt(qtyInput.value);
    if (val > 1) {
      qtyInput.value = val - 1;
    }
  });

  qtyInput.addEventListener('input', () => {
    if (!qtyInput.value || qtyInput.value < 1) {
      qtyInput.value = 1;
    }
  });
});

