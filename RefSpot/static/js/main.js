// Refspot - Professional Networking Platform JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializePageTransitions();
    initializeNavigation();
    initializeForms();
    initializeMessages();
    initializeSearch();
    initializeTooltips();
});

// Navigation enhancements
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const currentPath = window.location.pathname;
    
    // Highlight active navigation item
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
    }
}

// Form enhancements
function initializeForms() {
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
        
        // Initial resize
        textarea.style.height = textarea.scrollHeight + 'px';
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
    
    // Character count for limited fields
    const limitedFields = document.querySelectorAll('[data-max-length]');
    limitedFields.forEach(field => {
        const maxLength = parseInt(field.dataset.maxLength);
        const counter = document.createElement('div');
        counter.className = 'character-counter text-muted';
        counter.style.fontSize = '0.875rem';
        counter.style.marginTop = '0.25rem';
        
        field.parentNode.appendChild(counter);
        
        function updateCounter() {
            const remaining = maxLength - field.value.length;
            counter.textContent = `${remaining} characters remaining`;
            
            if (remaining < 0) {
                counter.classList.add('text-error');
                counter.classList.remove('text-muted');
            } else {
                counter.classList.remove('text-error');
                counter.classList.add('text-muted');
            }
        }
        
        field.addEventListener('input', updateCounter);
        updateCounter();
    });
}

// Form validation
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    });
    
    // Password confirmation
    const passwordField = form.querySelector('input[name="password"]');
    const confirmField = form.querySelector('input[name="password2"]');
    
    if (passwordField && confirmField && passwordField.value !== confirmField.value) {
        showFieldError(confirmField, 'Passwords do not match');
        isValid = false;
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error text-error';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';
    errorDiv.textContent = message;
    
    field.classList.add('is-invalid');
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Message system enhancements
function initializeMessages() {
    // Auto-scroll to bottom of conversation
    const conversationContainer = document.querySelector('.conversation-messages');
    if (conversationContainer) {
        conversationContainer.scrollTop = conversationContainer.scrollHeight;
    }
    
    // Mark messages as read when viewing conversation
    const messageItems = document.querySelectorAll('.message-item.message-unread');
    if (messageItems.length > 0) {
        // Simulate marking as read (would normally be an API call)
        setTimeout(() => {
            messageItems.forEach(item => {
                item.classList.remove('message-unread');
            });
        }, 1000);
    }
    
    // Real-time message updates (simplified)
    if (window.location.pathname.includes('/messages/')) {
        // In a real application, this would use WebSockets or polling
        setInterval(checkForNewMessages, 30000); // Check every 30 seconds
    }
}

function checkForNewMessages() {
    // Placeholder for real-time message checking
    // In a real implementation, this would make an API call
    console.log('Checking for new messages...');
}

// Search enhancements
function initializeSearch() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('input[name="query"]');
    
    if (searchInput) {
        // Search suggestions (simplified)
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    showSearchSuggestions(query);
                }, 300);
            } else {
                hideSearchSuggestions();
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target)) {
                hideSearchSuggestions();
            }
        });
    }
}

function showSearchSuggestions(query) {
    // In a real implementation, this would make an API call for suggestions
    const suggestions = [
        'Software Engineer',
        'Product Manager',
        'Data Scientist',
        'UX Designer',
        'Marketing Manager'
    ].filter(item => item.toLowerCase().includes(query.toLowerCase()));
    
    const existingSuggestions = document.querySelector('.search-suggestions');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
    
    if (suggestions.length > 0) {
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'search-suggestions';
        suggestionsDiv.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid rgb(var(--border));
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-md);
            z-index: 1000;
        `;
        
        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'search-suggestion-item';
            item.style.cssText = `
                padding: var(--spacing-sm) var(--spacing-md);
                cursor: pointer;
                transition: background-color 0.2s ease;
            `;
            item.textContent = suggestion;
            
            item.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgb(var(--surface))';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
            
            item.addEventListener('click', function() {
                document.querySelector('input[name="query"]').value = suggestion;
                hideSearchSuggestions();
            });
            
            suggestionsDiv.appendChild(item);
        });
        
        const searchContainer = document.querySelector('input[name="query"]').parentNode;
        searchContainer.style.position = 'relative';
        searchContainer.appendChild(suggestionsDiv);
    }
}

function hideSearchSuggestions() {
    const suggestions = document.querySelector('.search-suggestions');
    if (suggestions) {
        suggestions.remove();
    }
}

// Page Transition Animations
function initializePageTransitions() {
    // Add page transition class to main content
    const mainContent = document.querySelector('main') || document.querySelector('.container');
    if (mainContent) {
        mainContent.classList.add('page-transition');
        
        // Trigger fade in animation
        setTimeout(() => {
            mainContent.classList.add('loaded');
        }, 50);
    }
    
    // Add staggered animations to lists
    const animateLists = document.querySelectorAll('.row .col-md-4, .list-group, .card-body .row');
    animateLists.forEach(list => {
        if (list.children.length > 1) {
            list.classList.add('animate-list');
        }
    });
    
    // Smooth page transitions for navigation links
    const navLinks = document.querySelectorAll('.nav-link:not(.dropdown-toggle)');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('/') && !href.includes('#')) {
                e.preventDefault();
                transitionToPage(href);
            }
        });
    });
    
    // Smooth transitions for buttons that navigate
    const navButtons = document.querySelectorAll('a.btn');
    navButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('/') && !href.includes('#') && !this.hasAttribute('target')) {
                e.preventDefault();
                transitionToPage(href);
            }
        });
    });
}

function transitionToPage(url) {
    // Show loading animation
    showPageLoader();
    
    // Fade out current content
    const mainContent = document.querySelector('main') || document.querySelector('.container');
    if (mainContent) {
        mainContent.classList.add('page-fade-out');
    }
    
    // Navigate after short delay
    setTimeout(() => {
        window.location.href = url;
    }, 200);
}

function showPageLoader() {
    let loader = document.querySelector('.page-loader');
    if (!loader) {
        loader = document.createElement('div');
        loader.className = 'page-loader';
        loader.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(loader);
    }
    loader.classList.add('active');
}

function hidePageLoader() {
    const loader = document.querySelector('.page-loader');
    if (loader) {
        loader.classList.remove('active');
    }
}

// Enhanced hover effects for cards
function initializeCardAnimations() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Call card animations after page load
setTimeout(initializeCardAnimations, 100);

// Tooltip initialization
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showTooltip(this, this.dataset.tooltip);
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

function showTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.style.cssText = `
        position: absolute;
        background: rgb(var(--secondary));
        color: white;
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--radius-sm);
        font-size: var(--font-size-sm);
        white-space: nowrap;
        z-index: 1000;
        pointer-events: none;
    `;
    tooltip.textContent = text;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
    tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else if (diffDays < 30) {
        const weeks = Math.floor(diffDays / 7);
        return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
    } else {
        return date.toLocaleDateString();
    }
}

// Connection management
function sendConnectionRequest(username) {
    // In a real implementation, this would make an API call
    console.log(`Sending connection request to ${username}`);
    
    const button = document.querySelector(`[data-connect="${username}"]`);
    if (button) {
        button.textContent = 'Request Sent';
        button.disabled = true;
        button.classList.remove('btn-primary');
        button.classList.add('btn-secondary');
    }
}

// Skill management
function addSkill() {
    const skillInput = document.querySelector('input[name="skill_name"]');
    const proficiencySelect = document.querySelector('select[name="proficiency"]');
    
    if (skillInput && proficiencySelect && skillInput.value.trim()) {
        // In a real implementation, this would submit to the server
        console.log(`Adding skill: ${skillInput.value} (${proficiencySelect.value})`);
        
        // Clear form
        skillInput.value = '';
        proficiencySelect.selectedIndex = 0;
    }
}

// Export functions for global access
window.NetworkingPlatform = {
    sendConnectionRequest,
    addSkill,
    formatDate,
    debounce
};
