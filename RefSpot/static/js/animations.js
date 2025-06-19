// GSAP Animations for Professional Network Platform
// Register ScrollTrigger plugin if GSAP is available
if (typeof gsap !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize instant navigation first for zero delay
    initializeInstantNavigation();
    
    // Initialize icon animations (works without GSAP)
    initializeIconAnimations();
    
    // Initialize GSAP animations if available
    if (typeof gsap !== 'undefined') {
        setTimeout(() => {
            initializePageAnimations();
            initializeCardAnimations();
            initializeNavigationAnimations();
            initializeFormAnimations();
            initializeMessageAnimations();
            initializeProfileAnimations();
            initializeMagneticEffect();
            initializeBreathingEffect();
            initializeStaggeredAnimations();
        }, 100);
    }
});

// Page entrance animations (instant mode)
function initializePageAnimations() {
    // Skip entrance animations for instant loading
    const elements = document.querySelectorAll('.container > .row > div, .hero-section h1, .hero-section p, .hero-section .card');
    elements.forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
    });
}

// Card hover and entrance animations
function initializeCardAnimations() {
    // Card entrance with scroll trigger
    gsap.utils.toArray('.card').forEach(card => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: "top 80%",
                toggleActions: "play none none reverse"
            },
            duration: 0.6,
            y: 30,
            opacity: 0,
            ease: "power2.out"
        });

        // Card hover effects
        card.addEventListener('mouseenter', () => {
            gsap.to(card, {
                duration: 0.3,
                y: -5,
                boxShadow: "0 10px 30px rgba(0,0,0,0.15)",
                ease: "power2.out"
            });
        });

        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                duration: 0.3,
                y: 0,
                boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
                ease: "power2.out"
            });
        });
    });
}

// Navigation animations
function initializeNavigationAnimations() {
    // Navbar slide down on page load
    gsap.from('.navbar', {
        duration: 0.8,
        y: -100,
        opacity: 0,
        ease: "power2.out"
    });

    // Navigation item hover effects
    gsap.utils.toArray('.nav-item').forEach(item => {
        const icon = item.querySelector('i[data-feather]');
        const text = item.querySelector('.nav-text');

        item.addEventListener('mouseenter', () => {
            gsap.timeline()
                .to(icon, {
                    duration: 0.2,
                    scale: 1.1,
                    rotation: 5,
                    ease: "power2.out"
                })
                .to(text, {
                    duration: 0.2,
                    color: "#404658",
                    ease: "power2.out"
                }, "-=0.1");
        });

        item.addEventListener('mouseleave', () => {
            gsap.timeline()
                .to(icon, {
                    duration: 0.2,
                    scale: 1,
                    rotation: 0,
                    ease: "power2.out"
                })
                .to(text, {
                    duration: 0.2,
                    color: "#6c757d",
                    ease: "power2.out"
                }, "-=0.1");
        });
    });
}

// Form and button animations
function initializeFormAnimations() {
    // Button hover effects
    gsap.utils.toArray('.btn').forEach(button => {
        button.addEventListener('mouseenter', () => {
            gsap.to(button, {
                duration: 0.2,
                scale: 1.05,
                ease: "power2.out"
            });
        });

        button.addEventListener('mouseleave', () => {
            gsap.to(button, {
                duration: 0.2,
                scale: 1,
                ease: "power2.out"
            });
        });
    });

    // Form field focus animations
    gsap.utils.toArray('.form-control').forEach(field => {
        field.addEventListener('focus', () => {
            gsap.to(field, {
                duration: 0.3,
                borderColor: "#404658",
                boxShadow: "0 0 0 0.2rem rgba(64, 70, 88, 0.25)",
                ease: "power2.out"
            });
        });

        field.addEventListener('blur', () => {
            gsap.to(field, {
                duration: 0.3,
                borderColor: "#dee2e6",
                boxShadow: "none",
                ease: "power2.out"
            });
        });
    });

    // Loading animation for form submissions
    document.addEventListener('submit', function(e) {
        const submitButton = e.target.querySelector('button[type="submit"]');
        if (submitButton) {
            gsap.to(submitButton, {
                duration: 0.3,
                scale: 0.95,
                opacity: 0.7,
                ease: "power2.out"
            });
        }
    });
}

// Message and conversation animations
function initializeMessageAnimations() {
    // Message bubble entrance
    gsap.utils.toArray('.message-bubble').forEach((bubble, index) => {
        gsap.from(bubble, {
            duration: 0.5,
            x: bubble.classList.contains('message-sent') ? 50 : -50,
            opacity: 0,
            delay: index * 0.1,
            ease: "power2.out"
        });
    });

    // Message hover effects
    gsap.utils.toArray('.message-bubble').forEach(bubble => {
        bubble.addEventListener('mouseenter', () => {
            gsap.to(bubble, {
                duration: 0.2,
                scale: 1.02,
                ease: "power2.out"
            });
        });

        bubble.addEventListener('mouseleave', () => {
            gsap.to(bubble, {
                duration: 0.2,
                scale: 1,
                ease: "power2.out"
            });
        });
    });

    // Typing indicator animation
    if (document.querySelector('.typing-indicator')) {
        gsap.to('.typing-indicator .dot', {
            duration: 0.6,
            y: -10,
            repeat: -1,
            yoyo: true,
            stagger: 0.2,
            ease: "power2.inOut"
        });
    }
}

// Profile and user interaction animations
function initializeProfileAnimations() {
    // Profile photo hover effect
    gsap.utils.toArray('.profile-avatar').forEach(avatar => {
        avatar.addEventListener('mouseenter', () => {
            gsap.to(avatar, {
                duration: 0.3,
                scale: 1.1,
                rotation: 5,
                ease: "power2.out"
            });
        });

        avatar.addEventListener('mouseleave', () => {
            gsap.to(avatar, {
                duration: 0.3,
                scale: 1,
                rotation: 0,
                ease: "power2.out"
            });
        });
    });

    // Skill tags animation
    gsap.utils.toArray('.skill-tag').forEach((tag, index) => {
        gsap.from(tag, {
            scrollTrigger: {
                trigger: tag,
                start: "top 90%",
                toggleActions: "play none none reverse"
            },
            duration: 0.4,
            scale: 0,
            opacity: 0,
            delay: index * 0.05,
            ease: "back.out(1.7)"
        });

        tag.addEventListener('mouseenter', () => {
            gsap.to(tag, {
                duration: 0.2,
                scale: 1.05,
                ease: "power2.out"
            });
        });

        tag.addEventListener('mouseleave', () => {
            gsap.to(tag, {
                duration: 0.2,
                scale: 1,
                ease: "power2.out"
            });
        });
    });

    // Connection status animations
    gsap.utils.toArray('.status-indicator').forEach(indicator => {
        gsap.from(indicator, {
            duration: 0.6,
            scale: 0,
            opacity: 0,
            ease: "back.out(1.7)"
        });
    });
}

// Page transition effects
// Instant page transitions with preloading
let preloadedPages = new Set();
let isNavigating = false;

function animatePageTransition(url) {
    if (isNavigating) return;
    window.location.href = url;
}

// Initialize instant navigation system
function initializeInstantNavigation() {
    const links = document.querySelectorAll('a[href^="/"], a[href^="' + window.location.origin + '"]');
    
    links.forEach(link => {
        // Skip file downloads and external links
        if (link.href.includes('download') || link.href.includes('.pdf') || link.target === '_blank') {
            return;
        }
        
        // Preload on hover
        link.addEventListener('mouseenter', () => {
            preloadPage(link.href);
        });
        
        // Preload on touch for mobile
        link.addEventListener('touchstart', () => {
            preloadPage(link.href);
        });
        
        // Instant navigation on click
        link.addEventListener('click', (e) => {
            if (e.ctrlKey || e.metaKey || e.shiftKey) return; // Allow new tabs
            
            e.preventDefault();
            navigateInstantly(link.href);
        });
    });
    
    // Preload critical pages immediately
    setTimeout(() => {
        const criticalPages = ['/connections', '/messages', '/jobs', '/search'];
        criticalPages.forEach(page => preloadPage(page));
    }, 1000);
}

function preloadPage(url) {
    if (preloadedPages.has(url) || url === window.location.href) return;
    
    // Use link prefetch for instant loading
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    document.head.appendChild(link);
    
    preloadedPages.add(url);
}

function navigateInstantly(url) {
    if (isNavigating || url === window.location.href) return;
    
    isNavigating = true;
    window.location.href = url;
}

// Notification animations
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        opacity: 0;
        transform: translateX(100%);
    `;
    
    document.body.appendChild(notification);
    
    gsap.timeline()
        .to(notification, {
            duration: 0.5,
            opacity: 1,
            x: 0,
            ease: "power2.out"
        })
        .to(notification, {
            duration: 0.5,
            opacity: 0,
            x: 100,
            ease: "power2.in",
            delay: 3,
            onComplete: () => notification.remove()
        });
}

// Progress bar animations
function animateProgressBar(element, targetWidth) {
    gsap.to(element, {
        duration: 1,
        width: targetWidth + '%',
        ease: "power2.out"
    });
}

// Scroll-based animations for long content
function initializeScrollAnimations() {
    gsap.utils.toArray('.fade-in-up').forEach(element => {
        gsap.from(element, {
            scrollTrigger: {
                trigger: element,
                start: "top 80%",
                toggleActions: "play none none reverse"
            },
            duration: 0.8,
            y: 50,
            opacity: 0,
            ease: "power2.out"
        });
    });
}

// Initialize scroll animations
initializeScrollAnimations();

// Icon Animation System
function initializeIconAnimations() {
    // Enhanced button icon hover effects
    const buttons = document.querySelectorAll('.btn, .nav-link, .dropdown-item');
    
    buttons.forEach((button, index) => {
        const icon = button.querySelector('i[data-feather]');
        if (!icon) return;
        
        // Set CSS custom property for staggered animations
        button.style.setProperty('--i', index);
        
        // Use CSS animations as primary method with GSAP enhancement if available
        button.addEventListener('mouseenter', function() {
            const iconType = icon.getAttribute('data-feather');
            
            // Add CSS class for immediate effect
            icon.classList.add('icon-hover');
            
            // Enhance with GSAP if available
            if (typeof gsap !== 'undefined') {
                animateIconHover(icon, iconType, true);
            }
        });
        
        button.addEventListener('mouseleave', function() {
            const iconType = icon.getAttribute('data-feather');
            
            // Remove CSS class
            icon.classList.remove('icon-hover');
            
            // Enhance with GSAP if available
            if (typeof gsap !== 'undefined') {
                animateIconHover(icon, iconType, false);
            }
        });
        
        // Enhanced click animations with micro-interactions
        button.addEventListener('mousedown', function() {
            icon.classList.add('icon-click');
            button.classList.add('clicked');
            
            // Add click feedback class for immediate response
            button.classList.add('btn-clicking');
            
            if (typeof gsap !== 'undefined') {
                gsap.to(icon, {
                    duration: 0.1,
                    scale: 0.9,
                    ease: "power2.out"
                });
            }
        });
        
        button.addEventListener('mouseup', function() {
            icon.classList.remove('icon-click');
            button.classList.remove('clicked');
            
            // Remove click feedback after animation
            setTimeout(() => {
                button.classList.remove('btn-clicking');
            }, 300);
            
            if (typeof gsap !== 'undefined') {
                gsap.to(icon, {
                    duration: 0.2,
                    scale: 1.1,
                    ease: "back.out(1.7)"
                });
            }
        });
        
        // Handle click completion feedback
        button.addEventListener('click', function(e) {
            const iconType = icon.getAttribute('data-feather');
            
            // Special feedback for different action types
            if (this.type === 'submit' || this.matches('[type="submit"]')) {
                handleSubmitClick(this, icon, iconType);
            } else if (iconType === 'save' || iconType === 'check') {
                handleSuccessClick(this, icon);
            }
        });
    });
}

// Handle submit button clicks with loading state
function handleSubmitClick(button, icon, iconType) {
    // Add loading state
    button.classList.add('loading');
    button.disabled = true;
    
    // Store original text
    const originalContent = button.innerHTML;
    
    // Show loading state
    if (iconType === 'send') {
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Sending...';
    } else {
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    }
    
    // Reset after form submission (or timeout)
    setTimeout(() => {
        if (button.classList.contains('loading')) {
            button.classList.remove('loading');
            button.disabled = false;
            button.innerHTML = originalContent;
            
            // Re-initialize feather icons
            if (typeof feather !== 'undefined') {
                feather.replace();
            }
        }
    }, 3000);
}

// Handle success actions with visual feedback
function handleSuccessClick(button, icon) {
    button.classList.add('success-flash');
    
    // Remove success class after animation
    setTimeout(() => {
        button.classList.remove('success-flash');
    }, 600);
}

// Ripple effect for enhanced click feedback
function createRippleEffect(button, event) {
    // Check if reduced motion is preferred
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }
    
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: rippleEffect 0.6s ease-out;
        pointer-events: none;
        z-index: 0;
    `;
    
    button.appendChild(ripple);
    
    // Remove ripple after animation
    setTimeout(() => {
        if (ripple.parentNode) {
            ripple.parentNode.removeChild(ripple);
        }
    }, 600);
}

// Add ripple CSS animation if not already present
if (!document.querySelector('#ripple-styles')) {
    const style = document.createElement('style');
    style.id = 'ripple-styles';
    style.textContent = `
        @keyframes rippleEffect {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

function animateIconHover(icon, iconType, isHover) {
    if (!icon || !gsap) return;
    
    // Kill existing animations
    gsap.killTweensOf(icon);
    
    if (isHover) {
        // Specific icon behaviors with GSAP
        switch(iconType) {
            case 'send':
            case 'message-circle':
            case 'mail':
                // Paper plane effect
                gsap.timeline()
                    .to(icon, {
                        duration: 0.3,
                        x: 5,
                        scale: 1.15,
                        ease: "power2.out"
                    })
                    .to(icon, {
                        duration: 0.2,
                        x: 3,
                        scale: 1.1,
                        ease: "power2.out"
                    });
                break;
                
            case 'user-plus':
            case 'users':
                // Wiggle effect
                gsap.to(icon, {
                    duration: 0.5,
                    rotation: "5_ccw",
                    scale: 1.1,
                    ease: "elastic.out(1, 0.5)",
                    transformOrigin: "center"
                });
                break;
                
            case 'search':
                // Tilt and scale
                gsap.to(icon, {
                    duration: 0.3,
                    rotation: 15,
                    scale: 1.15,
                    ease: "back.out(1.7)"
                });
                break;
                
            case 'edit':
            case 'edit-2':
            case 'edit-3':
                // Draw line effect
                gsap.timeline()
                    .to(icon, {
                        duration: 0.2,
                        x: 2,
                        rotation: -10,
                        scale: 1.1,
                        ease: "power2.out"
                    })
                    .to(icon, {
                        duration: 0.2,
                        x: 0,
                        rotation: 0,
                        ease: "power2.out"
                    });
                break;
                
            case 'upload':
            case 'upload-cloud':
                // Bounce up
                gsap.to(icon, {
                    duration: 0.5,
                    y: -4,
                    scale: 1.15,
                    ease: "bounce.out"
                });
                break;
                
            case 'download':
            case 'download-cloud':
                // Bounce down
                gsap.to(icon, {
                    duration: 0.5,
                    y: 4,
                    scale: 1.15,
                    ease: "bounce.out"
                });
                break;
                
            case 'trash':
            case 'trash-2':
            case 'x':
                // Shake effect
                gsap.to(icon, {
                    duration: 0.4,
                    x: "random(-3, 3)",
                    scale: 1.1,
                    ease: "elastic.out(1, 0.5)",
                    repeat: 3,
                    yoyo: true
                });
                break;
                
            case 'save':
            case 'check':
            case 'check-circle':
                // Pulse effect
                gsap.to(icon, {
                    duration: 0.6,
                    scale: 1.25,
                    ease: "elastic.out(1, 0.3)",
                    repeat: 1,
                    yoyo: true
                });
                break;
                
            case 'home':
                // Gentle bounce
                gsap.to(icon, {
                    duration: 0.4,
                    y: -4,
                    scale: 1.15,
                    ease: "power2.out",
                    repeat: 1,
                    yoyo: true
                });
                break;
                
            case 'settings':
            case 'sliders':
                // Rotate
                gsap.to(icon, {
                    duration: 0.6,
                    rotation: 180,
                    scale: 1.1,
                    ease: "power2.out"
                });
                break;
                
            case 'plus':
            case 'plus-circle':
                // Cross expand
                gsap.timeline()
                    .to(icon, {
                        duration: 0.15,
                        scale: 1.2,
                        rotation: 90,
                        ease: "power2.out"
                    })
                    .to(icon, {
                        duration: 0.15,
                        scale: 1.1,
                        rotation: 0,
                        ease: "power2.out"
                    });
                break;
                
            case 'eye':
            case 'eye-off':
                // Blink effect
                gsap.timeline()
                    .to(icon, {
                        duration: 0.1,
                        scaleY: 0.1,
                        scale: 1.1,
                        ease: "power2.out"
                    })
                    .to(icon, {
                        duration: 0.1,
                        scaleY: 1,
                        ease: "power2.out"
                    });
                break;
                
            case 'heart':
                // Heartbeat
                gsap.to(icon, {
                    duration: 0.6,
                    scale: 1.25,
                    ease: "elastic.out(1, 0.5)",
                    repeat: 3,
                    yoyo: true
                });
                break;
                
            case 'phone':
            case 'phone-call':
                // Ring effect
                gsap.to(icon, {
                    duration: 0.5,
                    rotation: "10_cw",
                    scale: 1.1,
                    ease: "elastic.out(1, 0.5)",
                    repeat: 3,
                    yoyo: true
                });
                break;
                
            case 'calendar':
                // Flip effect
                gsap.timeline()
                    .to(icon, {
                        duration: 0.2,
                        rotationY: 90,
                        scale: 1.1,
                        ease: "power2.out"
                    })
                    .to(icon, {
                        duration: 0.2,
                        rotationY: 0,
                        ease: "power2.out"
                    });
                break;
                
            // Arrow icons
            case 'arrow-right':
                gsap.to(icon, { duration: 0.3, x: 3, scale: 1.1, ease: "power2.out" });
                break;
            case 'arrow-left':
                gsap.to(icon, { duration: 0.3, x: -3, scale: 1.1, ease: "power2.out" });
                break;
            case 'arrow-up':
                gsap.to(icon, { duration: 0.3, y: -3, scale: 1.1, ease: "power2.out" });
                break;
            case 'arrow-down':
                gsap.to(icon, { duration: 0.3, y: 3, scale: 1.1, ease: "power2.out" });
                break;
                
            case 'log-in':
            case 'log-out':
                // Slide effect
                gsap.to(icon, {
                    duration: 0.3,
                    x: 3,
                    scale: 1.1,
                    ease: "power2.out"
                });
                break;
                
            default:
                // Default hover animation
                gsap.to(icon, {
                    duration: 0.3,
                    scale: 1.1,
                    ease: "back.out(1.7)"
                });
        }
        
        // Add glow effect
        gsap.to(icon, {
            duration: 0.3,
            filter: "drop-shadow(0 0 5px rgba(64, 70, 88, 0.4))",
            ease: "power2.out"
        });
        
    } else {
        // Reset to normal state
        gsap.to(icon, {
            duration: 0.3,
            x: 0,
            y: 0,
            scale: 1,
            rotation: 0,
            rotationY: 0,
            scaleY: 1,
            filter: "drop-shadow(0 0 0px rgba(64, 70, 88, 0))",
            ease: "power2.out"
        });
    }
}

// Magnetic effect for navigation
function initializeMagneticEffect() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const icon = link.querySelector('i[data-feather]');
        if (!icon) return;
        
        link.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            gsap.to(icon, {
                duration: 0.3,
                x: x * 0.1,
                y: y * 0.1,
                ease: "power2.out"
            });
        });
        
        link.addEventListener('mouseleave', function() {
            gsap.to(icon, {
                duration: 0.5,
                x: 0,
                y: 0,
                ease: "elastic.out(1, 0.5)"
            });
        });
    });
}

// Breathing effect for primary buttons
function initializeBreathingEffect() {
    const primaryButtons = document.querySelectorAll('.btn-primary');
    
    primaryButtons.forEach(button => {
        const icon = button.querySelector('i[data-feather]');
        if (!icon) return;
        
        button.addEventListener('mouseenter', function() {
            gsap.to(icon, {
                duration: 2,
                scale: 1.15,
                ease: "sine.inOut",
                repeat: -1,
                yoyo: true
            });
        });
        
        button.addEventListener('mouseleave', function() {
            gsap.killTweensOf(icon);
            gsap.to(icon, {
                duration: 0.3,
                scale: 1,
                ease: "power2.out"
            });
        });
    });
}

// Staggered animations for cards with multiple buttons
function initializeStaggeredAnimations() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        const buttons = card.querySelectorAll('.btn');
        
        card.addEventListener('mouseenter', function() {
            buttons.forEach((button, index) => {
                const icon = button.querySelector('i[data-feather]');
                if (icon) {
                    gsap.to(icon, {
                        duration: 0.3,
                        scale: 1.05,
                        delay: index * 0.1,
                        ease: "power2.out"
                    });
                }
            });
        });
        
        card.addEventListener('mouseleave', function() {
            buttons.forEach((button, index) => {
                const icon = button.querySelector('i[data-feather]');
                if (icon) {
                    gsap.to(icon, {
                        duration: 0.3,
                        scale: 1,
                        delay: index * 0.05,
                        ease: "power2.out"
                    });
                }
            });
        });
    });
}

// Export functions for use in other scripts
window.gsapAnimations = {
    animatePageTransition,
    showNotification,
    animateProgressBar,
    animateIconHover,
    initializeIconAnimations,
    initializeMagneticEffect,
    initializeBreathingEffect,
    initializeStaggeredAnimations
};