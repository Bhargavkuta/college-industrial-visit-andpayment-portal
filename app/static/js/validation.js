/**
 * Client-side validation and live password strength indicator
 */

document.addEventListener('DOMContentLoaded', () => {
  const passwordInput = document.getElementById('password');
  const strengthBar = document.getElementById('password-strength-bar');
  const strengthText = document.getElementById('password-strength-text');

  if (passwordInput && strengthBar && strengthText) {
    passwordInput.addEventListener('input', () => {
      const val = passwordInput.value;
      let score = 0;
      let feedback = [];

      if (val.length >= 8) score += 1;
      else feedback.push('Min 8 chars');

      if (/\d/.test(val)) score += 1;
      else feedback.push('At least 1 number');

      if (/[!@#$%^&*(),.?":{}|<>\-_+=\[\]\\/`~]/.test(val)) score += 1;
      else feedback.push('At least 1 special char');

      if (/[A-Z]/.test(val) && /[a-z]/.test(val)) score += 1;

      // Update UI
      if (val.length === 0) {
        strengthBar.style.width = '0%';
        strengthBar.className = 'progress-bar';
        strengthText.textContent = '';
      } else if (score <= 1) {
        strengthBar.style.width = '25%';
        strengthBar.className = 'progress-bar bg-danger';
        strengthText.textContent = 'Weak: ' + feedback.join(', ');
        strengthText.className = 'form-text text-danger';
      } else if (score === 2) {
        strengthBar.style.width = '50%';
        strengthBar.className = 'progress-bar bg-warning';
        strengthText.textContent = 'Moderate: ' + feedback.join(', ');
        strengthText.className = 'form-text text-warning';
      } else if (score === 3) {
        strengthBar.style.width = '75%';
        strengthBar.className = 'progress-bar bg-info';
        strengthText.textContent = 'Strong: Good password';
        strengthText.className = 'form-text text-info';
      } else {
        strengthBar.style.width = '100%';
        strengthBar.className = 'progress-bar bg-success';
        strengthText.textContent = 'Very Strong: Excellent password';
        strengthText.className = 'form-text text-success';
      }
    });
  }

  // Password confirmation matcher
  const confirmPasswordInput = document.getElementById('confirm_password');
  const matchText = document.getElementById('password-match-text');

  if (passwordInput && confirmPasswordInput && matchText) {
    confirmPasswordInput.addEventListener('input', () => {
      if (confirmPasswordInput.value.length > 0) {
        if (confirmPasswordInput.value === passwordInput.value) {
          matchText.textContent = '✓ Passwords match';
          matchText.className = 'form-text text-success';
        } else {
          matchText.textContent = '✕ Passwords do not match';
          matchText.className = 'form-text text-danger';
        }
      } else {
        matchText.textContent = '';
      }
    });
  }
});
