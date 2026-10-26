/**
 * TripSync — Dynamic Booking Form Calculations & Category Toggle
 * Updates live financial breakdowns and adapts fields based on travel category.
 */

document.addEventListener('DOMContentLoaded', () => {
    const bookingForm = document.getElementById('booking-form');
    if (!bookingForm) return;

    const categorySelect = document.getElementById('travel_type');
    const transportFields = document.getElementById('transport-fields');
    const hotelFields = document.getElementById('hotel-fields');

    const sourceInput = document.getElementById('source');
    const destinationInput = document.getElementById('destination');
    const travelDateInput = document.getElementById('travel_date');
    const checkOutDateInput = document.getElementById('check_out_date');
    const passengersInput = document.getElementById('passengers');
    const roomsInput = document.getElementById('rooms');
    const guestsInput = document.getElementById('guests');
    const hotelNameInput = document.getElementById('hotel_name');
    const unitFareInput = document.getElementById('unit_fare');
    const amountPaidInput = document.getElementById('amount_paid');

    const travelDateLabel = document.getElementById('travel-date-label');
    const unitFareLabel = document.getElementById('unit-fare-label');
    const destinationLabel = document.getElementById('destination-label');

    // Preview Elements
    const previewFormula = document.getElementById('preview-formula');
    const previewTotal = document.getElementById('preview-total');
    const previewPaid = document.getElementById('preview-paid');
    const previewBalance = document.getElementById('preview-balance');
    const previewStatusBadge = document.getElementById('preview-status-badge');
    const paymentWarning = document.getElementById('payment-warning');

    function formatINR(amount) {
        const num = Number(amount) || 0;
        const parts = num.toFixed(2).split('.');
        let integerPart = parts[0];
        const decimalPart = parts[1];

        if (integerPart.length > 3) {
            const lastThree = integerPart.substring(integerPart.length - 3);
            let remaining = integerPart.substring(0, integerPart.length - 3);
            const groups = [];
            while (remaining.length > 2) {
                groups.unshift(remaining.substring(remaining.length - 2));
                remaining = remaining.substring(0, remaining.length - 2);
            }
            if (remaining.length > 0) {
                groups.unshift(remaining);
            }
            integerPart = groups.join(',') + ',' + lastThree;
        }

        return `₹${integerPart}.${decimalPart}`;
    }

    function calculateNights(inStr, outStr) {
        if (!inStr || !outStr) return 1;
        const dIn = new Date(inStr);
        const dOut = new Date(outStr);
        const diffMs = dOut - dIn;
        const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
        return diffDays > 0 ? diffDays : 1;
    }

    function updateFormVisibility() {
        const category = categorySelect ? categorySelect.value : 'flight';

        if (category === 'hotel') {
            if (transportFields) transportFields.classList.add('d-none');
            if (hotelFields) hotelFields.classList.remove('d-none');

            if (travelDateLabel) travelDateLabel.textContent = 'Check-in Date';
            if (unitFareLabel) unitFareLabel.textContent = 'Rate per Room / Night (₹)';
            if (destinationLabel) destinationLabel.textContent = 'Hotel City / Location';

            if (sourceInput) sourceInput.removeAttribute('required');
            if (hotelNameInput) hotelNameInput.setAttribute('required', 'required');
            if (checkOutDateInput) checkOutDateInput.setAttribute('required', 'required');
        } else {
            if (transportFields) transportFields.classList.remove('d-none');
            if (hotelFields) hotelFields.classList.add('d-none');

            if (travelDateLabel) travelDateLabel.textContent = 'Travel Date';
            if (unitFareLabel) unitFareLabel.textContent = 'Fare per Passenger (₹)';
            if (destinationLabel) destinationLabel.textContent = 'Destination Location';

            if (sourceInput) sourceInput.setAttribute('required', 'required');
            if (hotelNameInput) hotelNameInput.removeAttribute('required');
            if (checkOutDateInput) checkOutDateInput.removeAttribute('required');
        }

        recalculateAmounts();
    }

    function recalculateAmounts() {
        const category = categorySelect ? categorySelect.value : 'flight';
        const unitFare = parseFloat(unitFareInput ? unitFareInput.value : 0) || 0;
        const amountPaid = parseFloat(amountPaidInput ? amountPaidInput.value : 0) || 0;

        let total = 0;
        let formulaText = '';

        if (category === 'hotel') {
            const rooms = parseInt(roomsInput ? roomsInput.value : 1, 10) || 1;
            const inDate = travelDateInput ? travelDateInput.value : '';
            const outDate = checkOutDateInput ? checkOutDateInput.value : '';
            const nights = calculateNights(inDate, outDate);

            total = rooms * nights * unitFare;
            formulaText = `${rooms} Room(s) × ${nights} Night(s) × ${formatINR(unitFare)}`;
        } else {
            const passengers = parseInt(passengersInput ? passengersInput.value : 1, 10) || 1;
            total = passengers * unitFare;
            formulaText = `${passengers} Passenger(s) × ${formatINR(unitFare)}`;
        }

        const balance = Math.max(0, total - amountPaid);

        // Update previews
        if (previewFormula) previewFormula.textContent = formulaText;
        if (previewTotal) previewTotal.textContent = formatINR(total);
        if (previewPaid) previewPaid.textContent = formatINR(amountPaid);
        if (previewBalance) previewBalance.textContent = formatINR(balance);

        // Validate Amount Paid <= Total
        if (paymentWarning) {
            if (amountPaid > total && total > 0) {
                paymentWarning.textContent = 'Amount paid cannot exceed total booking amount.';
                paymentWarning.classList.remove('d-none');
            } else {
                paymentWarning.classList.add('d-none');
            }
        }

        // Update Status Badge
        if (previewStatusBadge) {
            if (amountPaid <= 0 || total <= 0) {
                previewStatusBadge.className = 'badge-custom badge-pay-unpaid';
                previewStatusBadge.textContent = 'Unpaid';
            } else if (amountPaid >= total) {
                previewStatusBadge.className = 'badge-custom badge-pay-paid';
                previewStatusBadge.textContent = 'Paid';
            } else {
                previewStatusBadge.className = 'badge-custom badge-pay-partial';
                previewStatusBadge.textContent = 'Partially Paid';
            }
        }
    }

    // Attach Event Listeners
    if (categorySelect) categorySelect.addEventListener('change', updateFormVisibility);
    if (unitFareInput) unitFareInput.addEventListener('input', recalculateAmounts);
    if (amountPaidInput) amountPaidInput.addEventListener('input', recalculateAmounts);
    if (passengersInput) passengersInput.addEventListener('input', recalculateAmounts);
    if (roomsInput) roomsInput.addEventListener('input', recalculateAmounts);
    if (travelDateInput) travelDateInput.addEventListener('change', recalculateAmounts);
    if (checkOutDateInput) checkOutDateInput.addEventListener('change', recalculateAmounts);

    // Initial Execution
    updateFormVisibility();
});
