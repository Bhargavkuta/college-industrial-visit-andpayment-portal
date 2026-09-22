/**
 * Payment checkout integration script
 * Supports both Razorpay Standard Checkout & Development Mock Payment Gateway
 */

function initiateRazorpayPayment(options) {
  if (typeof Razorpay === 'undefined') {
    alert('Razorpay SDK failed to load. Please check your internet connection or use Dev Mock Gateway.');
    return;
  }

  const rzp = new Razorpay({
    key: options.key_id,
    amount: options.amount_paise,
    currency: options.currency || 'INR',
    name: options.college_name,
    description: options.description,
    image: options.logo_url || '',
    order_id: options.order_id,
    handler: function (response) {
      // Create hidden form and submit to verification endpoint
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = options.verify_url;

      // Add CSRF Token
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrf_token';
      csrfInput.value = options.csrf_token;
      form.appendChild(csrfInput);

      // Add Registration ID
      const regInput = document.createElement('input');
      regInput.type = 'hidden';
      regInput.name = 'registration_id';
      regInput.value = options.registration_id;
      form.appendChild(regInput);

      // Add Razorpay Response Params
      const payIdInput = document.createElement('input');
      payIdInput.type = 'hidden';
      payIdInput.name = 'razorpay_payment_id';
      payIdInput.value = response.razorpay_payment_id;
      form.appendChild(payIdInput);

      const orderIdInput = document.createElement('input');
      orderIdInput.type = 'hidden';
      orderIdInput.name = 'razorpay_order_id';
      orderIdInput.value = response.razorpay_order_id;
      form.appendChild(orderIdInput);

      const sigInput = document.createElement('input');
      sigInput.type = 'hidden';
      sigInput.name = 'razorpay_signature';
      sigInput.value = response.razorpay_signature;
      form.appendChild(sigInput);

      document.body.appendChild(form);
      form.submit();
    },
    prefill: {
      name: options.student_name,
      email: options.student_email,
      contact: options.student_phone
    },
    notes: {
      registration_id: options.registration_id,
      roll_number: options.student_roll
    },
    theme: {
      color: '#1e3a8a'
    }
  });

  rzp.on('payment.failed', function (response) {
    alert('Payment Failed: ' + response.error.description);
  });

  rzp.open();
}
