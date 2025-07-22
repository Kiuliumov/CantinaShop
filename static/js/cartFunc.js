function getCartFromCookie() {
  const cookie = document.cookie.split("; ").find(row => row.startsWith("cart="));
  if (!cookie) return [];
  try {
    return JSON.parse(decodeURIComponent(cookie.split("=")[1]));
  } catch {
    return [];
  }
}

function setCartToCookie(cart) {
  if (!cart || cart.length === 0) {
    document.cookie = "cart=; path=/; max-age=0; samesite=lax";
  } else {
    document.cookie = `cart=${encodeURIComponent(JSON.stringify(cart))}; path=/; max-age=${60 * 60 * 24 * 7}; samesite=lax`;
  }
}

function updateCartItem(slug, quantity) {
  let cart = getCartFromCookie();
  let updated = false;

  cart = cart.map(item => {
    if (item.slug === slug) {
      updated = true;
      return { slug: slug, quantity: quantity };
    }
    return item;
  });

  if (!updated && quantity > 0) {
    cart.push({ slug: slug, quantity: quantity });
  }

  if (quantity <= 0) {
    cart = cart.filter(item => item.slug !== slug);
    const itemDiv = document.querySelector(`[data-slug="${slug}"]`);
    if (itemDiv) {
      itemDiv.classList.add("opacity-0", "scale-95", "transition", "duration-300");
      setTimeout(() => itemDiv.remove(), 300);
    }
    showRemoveToast();
  }

  setCartToCookie(cart);
}

function showRemoveToast() {
  const toast = document.getElementById("cart-remove-toast");
  toast.classList.remove("opacity-0", "pointer-events-none");
  toast.classList.add("opacity-100");

  setTimeout(() => {
    toast.classList.remove("opacity-100");
    toast.classList.add("opacity-0", "pointer-events-none");
  }, 3000);
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".quantity-increment").forEach(btn => {
    btn.addEventListener("click", () => {
      const slug = btn.dataset.slug;
      const input = document.querySelector(`.quantity-input[data-slug="${slug}"]`);
      const val = parseInt(input.value) || 0;
      input.value = val + 1;
      updateCartItem(slug, val + 1);
    });
  });

  document.querySelectorAll(".quantity-decrement").forEach(btn => {
    btn.addEventListener("click", () => {
      const slug = btn.dataset.slug;
      const input = document.querySelector(`.quantity-input[data-slug="${slug}"]`);
      const val = parseInt(input.value) || 0;
      const newVal = val - 1;
      input.value = newVal < 0 ? 0 : newVal;
      updateCartItem(slug, newVal);
    });
  });

  document.querySelectorAll(".quantity-input").forEach(input => {
    input.addEventListener("change", () => {
      const slug = input.dataset.slug;
      let val = parseInt(input.value);
      if (isNaN(val) || val < 0) val = 0;
      input.value = val;
      updateCartItem(slug, val);
    });
  });

  document.querySelectorAll(".remove-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const slug = btn.dataset.slug;
      updateCartItem(slug, 0);
    });
  });

  document.getElementById("remove-toast-ok")?.addEventListener("click", () => {
    const toast = document.getElementById("cart-remove-toast");
    toast.classList.add("opacity-0", "pointer-events-none");
  });

  document.getElementById("remove-toast-close")?.addEventListener("click", () => {
    const toast = document.getElementById("cart-remove-toast");
    toast.classList.add("opacity-0", "pointer-events-none");
  });
});
