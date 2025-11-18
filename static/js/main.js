document.addEventListener("DOMContentLoaded", () => {
    console.log("Flux Expense Tracker loaded.");

    const canvas = document.getElementById("monthlyCategoryChart");
    if (!canvas) {
        // Not on the dashboard, nothing to do.
        return;
    }

    let apiUrl = canvas.dataset.url;
    if (!apiUrl) {
        console.error("Chart dataset URL is missing.");
        return;
    }

    const year = canvas.dataset.year;
    const month = canvas.dataset.month;

    const params = new URLSearchParams();
    if (year) params.set("year", year);
    if (month) params.set("month", month);

    if ([...params].length > 0) {
        apiUrl = `${apiUrl}?${params.toString()}`;
    }

    fetch(apiUrl)
        .then((response) => response.json())
        .then((data) => {
            if (!data.labels || data.labels.length === 0) {
                console.log("No data for monthly category breakdown.");
                return;
            }

            const ctx = canvas.getContext("2d");

            new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            data: data.values,
                            borderWidth: 0,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: "bottom",
                            labels: {
                                color: "#e5e7eb",
                                boxWidth: 12,
                            },
                        },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const label = context.label || "";
                                    const value = context.raw || 0;
                                    return `${label}: $${value.toFixed(2)}`;
                                },
                            },
                        },
                    },
                },
            });
        })
        .catch((err) => {
            console.error("Error loading chart data:", err);
        });
});