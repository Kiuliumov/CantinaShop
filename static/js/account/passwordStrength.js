document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  if (!form) return;

  const passwordInput = form.querySelector('input[type="password"]');
  const strengthMessage = document.getElementById('password-strength');
  const progressBar = document.getElementById('password-strength-bar');

  if (!passwordInput || !strengthMessage || !progressBar) return;

  passwordInput.addEventListener('input', () => {
    const val = passwordInput.value;
    let strength = 0;

    const lengthRequirement = val.length >= 8;
    const hasUpper = /[A-Z]/.test(val);
    const hasLower = /[a-z]/.test(val);
    const hasNumber = /\d/.test(val);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(val);

    if(lengthRequirement) strength++;
    if(hasUpper) strength++;
    if(hasLower) strength++;
    if(hasNumber) strength++;
    if(hasSpecial) strength++;

    if (val.length === 0) {
      strengthMessage.textContent = '';
      strengthMessage.className = '';
      progressBar.style.width = '0';
      progressBar.style.backgroundColor = 'transparent';
      return;
    }

    if (strength <= 2) {
      strengthMessage.textContent = 'Weak password';
      strengthMessage.className = 'mt-2 text-sm font-semibold text-red-500';
      progressBar.style.backgroundColor = '#f87171';
    } else if (strength === 3 || strength === 4) {
      strengthMessage.textContent = 'Medium strength password';
      strengthMessage.className = 'mt-2 text-sm font-semibold text-yellow-400';
      progressBar.style.backgroundColor = '#fbbf24';
    } else if (strength === 5) {
      strengthMessage.textContent = 'Strong password';
      strengthMessage.className = 'mt-2 text-sm font-semibold text-green-500';
      progressBar.style.backgroundColor = '#34d399';
    }

    const widthPercent = (strength / 5) * 100;
    progressBar.style.width = widthPercent + '%';
  });
});
