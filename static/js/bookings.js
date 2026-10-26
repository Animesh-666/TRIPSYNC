/**
 * TripSync — Booking Management Interface Helpers
 * Filter synchronization, resets, and table navigation.
 */

document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('bookings-filter-form');
    const resetBtn = document.getElementById('reset-filters-btn');

    if (resetBtn) {
        resetBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = '/bookings';
        });
    }

    // Auto-submit filter form on dropdown selection change for smooth interaction
    if (filterForm) {
        const autoSubmitSelects = filterForm.querySelectorAll('select[data-auto-submit]');
        autoSubmitSelects.forEach(sel => {
            sel.addEventListener('change', () => {
                filterForm.submit();
            });
        });
    }
});
