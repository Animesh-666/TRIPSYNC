/**
 * TripSync — Global Application JavaScript
 * Handles Navigation, 3D Tilt Animations, Toasts, and Confirmations.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Navigation Toggle
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('.navbar-toggle-btn');
    const overlay = document.querySelector('.sidebar-overlay');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('show');
            if (overlay) overlay.classList.toggle('show');
        });
    }

    if (overlay && sidebar) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }

    // 2. 3D Tilt Effect on Dashboard & KPI Cards
    const tiltCards = document.querySelectorAll('.tilt-card');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!prefersReducedMotion) {
        tiltCards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                const rotateX = ((y - centerY) / centerY) * -6; // max 6deg
                const rotateY = ((x - centerX) / centerX) * 6;

                card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-4px)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
            });
        });
    }

    // 3. Auto-initialize Bootstrap Toasts
    const toastElements = document.querySelectorAll('.toast');
    toastElements.forEach(toastEl => {
        if (window.bootstrap && bootstrap.Toast) {
            const toast = new bootstrap.Toast(toastEl, { delay: 6000 });
            toast.show();
        }
    });

    // 4. Form Submit Protection against double-clicks
    const submitProtectedForms = document.querySelectorAll('form[data-protect-submit]');
    submitProtectedForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Processing...`;
                // Re-enable after 8 seconds in case of client validation abort
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 8000);
            }
        });
    });
});

/**
 * Global helper to confirm destructive actions.
 */
function confirmAction(message, formElement) {
    if (confirm(message)) {
        if (formElement) formElement.submit();
        return true;
    }
    return false;
}
