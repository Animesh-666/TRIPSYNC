/**
 * TripSync — Chart.js Visualizations Module
 * Renders Category Distribution, Payment Status, and Top Destinations charts.
 */

document.addEventListener('DOMContentLoaded', () => {
    if (typeof Chart === 'undefined') return;

    // Chart.js Global Font & Styling Defaults
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
    Chart.defaults.color = '#64748B';

    // 1. Travel Category Distribution (Doughnut Chart)
    const categoryCanvas = document.getElementById('categoryDistributionChart');
    if (categoryCanvas && window.CHART_CATEGORY_DATA) {
        const catData = window.CHART_CATEGORY_DATA;
        const labels = Object.keys(catData).map(k => k.charAt(0).toUpperCase() + k.slice(1));
        const dataValues = Object.values(catData);

        new Chart(categoryCanvas, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: dataValues,
                    backgroundColor: [
                        '#0284C7', // Flight (Blue)
                        '#9333EA', // Train (Purple)
                        '#EA580C', // Bus (Orange)
                        '#0D9488', // Hotel (Teal)
                    ],
                    borderWidth: 2,
                    borderColor: '#FFFFFF',
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 16,
                            usePointStyle: true,
                            pointStyle: 'circle',
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ` ${context.label}: ${context.raw} active booking(s)`;
                            }
                        }
                    }
                },
                cutout: '68%',
            }
        });
    }

    // 2. Payment Status Overview (Doughnut/Pie Chart)
    const paymentCanvas = document.getElementById('paymentStatusChart');
    if (paymentCanvas && window.CHART_PAYMENT_DATA) {
        const payData = window.CHART_PAYMENT_DATA;
        const labels = Object.keys(payData);
        const dataValues = Object.values(payData);

        new Chart(paymentCanvas, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: dataValues,
                    backgroundColor: [
                        '#16A34A', // Paid (Green)
                        '#D97706', // Partially Paid (Amber)
                        '#DC2626', // Unpaid (Red)
                    ],
                    borderWidth: 2,
                    borderColor: '#FFFFFF',
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 16,
                            usePointStyle: true,
                            pointStyle: 'circle',
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ` ${context.label}: ${context.raw} booking(s)`;
                            }
                        }
                    }
                },
                cutout: '68%',
            }
        });
    }

    // Last six months of active booking creation (server-derived data)
    const monthlyCanvas = document.getElementById('monthlyBookingsChart');
    if (monthlyCanvas && window.CHART_MONTHLY_LABELS && window.CHART_MONTHLY_COUNTS) {
        new Chart(monthlyCanvas, {
            type: 'line',
            data: {
                labels: window.CHART_MONTHLY_LABELS,
                datasets: [{
                    label: 'Active Bookings Created',
                    data: window.CHART_MONTHLY_COUNTS,
                    borderColor: '#0D9488',
                    backgroundColor: 'rgba(13, 148, 136, 0.10)',
                    fill: true,
                    tension: 0.25,
                    pointRadius: 4,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
                plugins: { legend: { display: false } },
            },
        });
    }

    // 3. Top Destinations Bar Chart
    const destCanvas = document.getElementById('topDestinationsChart');
    if (destCanvas && window.CHART_DESTINATION_DATA) {
        const destItems = window.CHART_DESTINATION_DATA; // Array of [city, count]
        const labels = destItems.map(item => item[0]);
        const dataValues = destItems.map(item => item[1]);

        new Chart(destCanvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Active Bookings',
                    data: dataValues,
                    backgroundColor: '#0D9488',
                    borderRadius: 6,
                    maxBarThickness: 32,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y', // Horizontal bars
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        },
                        grid: {
                            color: '#F1F5F9'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
});
