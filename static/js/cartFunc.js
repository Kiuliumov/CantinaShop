function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

function getCartFromCookie() {
  const cookie = getCookie('cart');
  if (!cookie) {
    return [];
  }
  try {
    const decoded = decodeURIComponent(cookie);
    return JSON.parse(decoded);
  } catch (e) {
    return [];
  }
}

function setCartToCookie(cart) {
  const path = '/';
  const maxAge = 60 * 60 * 24 * 7;

  if (!cart || cart.length === 0) {
    document.cookie = `cart=; path=${path}; max-age=0; SameSite=Lax`;
  } else {
    const json = JSON.stringify(cart);
    const encoded = encodeURIComponent(json);
    document.cookie = `cart=${encoded}; path=${path}; max-age=${maxAge}; SameSite=Lax`;
  }
}



function updateCartItem(slug, quantity) {
  let cart = getCartFromCookie();

  let found = false;
  cart = cart.map(item => {
    if (item.slug === slug) {
      found = true;
      return { slug, quantity };
    }
    return item;
  });

  if (!found && quantity > 0) {
    cart.push({ slug, quantity });
  }

  if (quantity <= 0) {
    cart = cart.filter(item => item.slug !== slug);

    const itemDiv = document.querySelector(`.cart-item[data-slug="${slug}"]`);
    if (itemDiv) {
      itemDiv.classList.add('opacity-0', 'scale-95', 'transition', 'duration-300');
      setTimeout(() => itemDiv.remove(), 300);
    }
    showRemoveToast();
  }

  setCartToCookie(cart);
}



function showRemoveToast() {
  const toast = document.getElementById('cart-remove-toast');
  if (!toast) return;
  toast.classList.remove('opacity-0', 'pointer-events-none');
  toast.classList.add('opacity-100');
  setTimeout(() => {
    toast.classList.remove('opacity-100');
    toast.classList.add('opacity-0', 'pointer-events-none');
  }, 3000);
}



document.addEventListener('DOMContentLoaded', () => {

  document.querySelectorAll('.quantity-increment').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const slug = btn.dataset.slug;
      const input = document.querySelector(`.quantity-input[data-slug="${slug}"]`);
      if (!input) return;
      let val = parseInt(input.value) || 0;
      val++;
      input.value = val;
      updateCartItem(slug, val);
    });
  });

  document.querySelectorAll('.quantity-decrement').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const slug = btn.dataset.slug;
      const input = document.querySelector(`.quantity-input[data-slug="${slug}"]`);
      if (!input) return;
      let val = parseInt(input.value) || 0;
      val = val > 0 ? val - 1 : 0;
      input.value = val;
      updateCartItem(slug, val);
    });
  });

  document.querySelectorAll('.quantity-input').forEach(input => {
    input.addEventListener('change', () => {
      const slug = input.dataset.slug;
      let val = parseInt(input.value);
      if (isNaN(val) || val < 0) val = 0;
      input.value = val;
      updateCartItem(slug, val);
    });
  });

  document.querySelectorAll('.remove-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const slug = btn.dataset.slug;
      updateCartItem(slug, 0);
    });
  });

  document.getElementById('remove-toast-close')?.addEventListener('click', () => {
    const toast = document.getElementById('cart-remove-toast');
    if (!toast) return;
    toast.classList.add('opacity-0', 'pointer-events-none');
  });
});
