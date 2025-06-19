// Authentication Animations
document.addEventListener('DOMContentLoaded', function() {
    initializePasswordReveal();
    initializeFormValidation();
    initializeLoginAnimations();
});

// Password reveal functionality
function initializePasswordReveal() {
    const passwordToggles = document.querySelectorAll('.password-toggle-btn');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const passwordField = this.parentElement.querySelector('input[type="password"], input[type="text"]');
            const icon = this.querySelector('i[data-feather]');
            
            if (passwordField.type === 'password') {
                // Show password
                passwordField.type = 'text';
                icon.setAttribute('data-feather', 'eye-off');
                
                // Add reveal animation
                passwordField.classList.add('password-revealed');
                
                // Animate the toggle button
                if (typeof gsap !== 'undefined') {
                    gsap.to(this, {
                        duration: 0.2,
                        scale: 1.2,
                        ease: "power2.out",
                        onComplete: () => {
                            gsap.to(this, {
                                duration: 0.2,
                                scale: 1,
                                ease: "power2.out"
                            });
                        }
                    });
                }
            } else {
                // Hide password
                passwordField.type = 'password';
                icon.setAttribute('data-feather', 'eye');
                
                passwordField.classList.remove('password-revealed');
                
                // Animate the toggle button
                if (typeof gsap !== 'undefined') {
                    gsap.to(this, {
                        duration: 0.2,
                        scale: 0.8,
                        ease: "power2.out",
                        onComplete: () => {
                            gsap.to(this, {
                                duration: 0.2,
                                scale: 1,
                                ease: "power2.out"
                            });
                        }
                    });
                }
            }
            
            // Re-initialize feather icons
            if (typeof feather !== 'undefined') {
                feather.replace();
            }
        });
    });
}

// Form validation with error animations
function initializeFormValidation() {
    const forms = document.querySelectorAll('#login-form, #register-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
            
            // Add loading animation to submit button
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.classList.add('btn-loading');
                
                // GSAP loading animation
                if (typeof gsap !== 'undefined') {
                    gsap.to(submitButton, {
                        duration: 0.3,
                        scale: 0.95,
                        ease: "power2.out"
                    });
                }
            }
            
            // Check for validation errors
            const errorFields = form.querySelectorAll('.form-control:invalid, .form-control[aria-invalid="true"]');
            if (errorFields.length > 0) {
                e.preventDefault();
                triggerErrorShake(form);
                
                // Remove loading state
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.classList.remove('btn-loading');
                    
                    if (typeof gsap !== 'undefined') {
                        gsap.to(submitButton, {
                            duration: 0.3,
                            scale: 1,
                            ease: "power2.out"
                        });
                    }
                }
            }
        });
        
        // Real-time validation feedback
        const inputs = form.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                // Remove error state when user starts typing
                if (this.classList.contains('form-error')) {
                    this.classList.remove('form-error');
                    this.classList.remove('shake-error');
                }
            });
        });
    });
}

// Trigger error shake animation
function triggerErrorShake(form) {
    const card = form.closest('.card');
    
    // Add shake animation to the form card
    if (card) {
        card.classList.add('shake-error');
        
        // Remove the class after animation completes
        setTimeout(() => {
            card.classList.remove('shake-error');
        }, 600);
    }
    
    // GSAP shake animation for individual error fields
    const errorFields = form.querySelectorAll('.form-control:invalid, .form-control[aria-invalid="true"]');
    errorFields.forEach((field, index) => {
        field.classList.add('form-error');
        
        if (typeof gsap !== 'undefined') {
            gsap.to(field, {
                duration: 0.1,
                x: -5,
                repeat: 5,
                yoyo: true,
                ease: "power2.inOut",
                delay: index * 0.1,
                onComplete: () => {
                    gsap.set(field, { x: 0 });
                }
            });
        }
    });
}

// Validate individual field
function validateField(field) {
    const isValid = field.checkValidity();
    
    if (isValid) {
        field.classList.remove('form-error');
        field.classList.add('form-success');
        
        // Success animation
        if (typeof gsap !== 'undefined') {
            gsap.to(field, {
                duration: 0.3,
                borderColor: "#28a745",
                ease: "power2.out"
            });
        }
    } else {
        field.classList.remove('form-success');
        field.classList.add('form-error');
        
        // Error animation
        if (typeof gsap !== 'undefined') {
            gsap.to(field, {
                duration: 0.3,
                borderColor: "#dc3545",
                ease: "power2.out"
            });
        }
    }
}

// Login-specific animations
function initializeLoginAnimations() {
    // Check for flash messages that indicate login errors
    const alerts = document.querySelectorAll('.alert-danger');
    if (alerts.length > 0) {
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            // Trigger shake animation for login errors
            setTimeout(() => {
                triggerErrorShake(loginForm);
            }, 100);
        }
    }
    
    // Success animations for login/registration
    const successAlerts = document.querySelectorAll('.alert-success');
    if (successAlerts.length > 0) {
        successAlerts.forEach(alert => {
            if (typeof gsap !== 'undefined') {
                gsap.from(alert, {
                    duration: 0.5,
                    y: -20,
                    opacity: 0,
                    ease: "power2.out"
                });
            }
        });
    }
}

// Handle form submission success/error states
function handleAuthResponse(success, message) {
    if (success) {
        // Success animation
        const form = document.querySelector('#login-form, #register-form');
        if (form && typeof gsap !== 'undefined') {
            gsap.to(form, {
                duration: 0.5,
                opacity: 0,
                y: -20,
                ease: "power2.out",
                onComplete: () => {
                    // Show success message or redirect
                    if (window.gsapAnimations && window.gsapAnimations.showNotification) {
                        window.gsapAnimations.showNotification(message, 'success');
                    }
                }
            });
        }
    } else {
        // Error animation
        const form = document.querySelector('#login-form, #register-form');
        if (form) {
            triggerErrorShake(form);
            
            if (window.gsapAnimations && window.gsapAnimations.showNotification) {
                window.gsapAnimations.showNotification(message, 'danger');
            }
        }
    }
}

// Export functions for external use
window.authAnimations = {
    triggerErrorShake,
    validateField,
    handleAuthResponse
};