!(function () {
    "use strict";

    // CSRF Token Handling
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const CSRF_TOKEN = getCookie("csrftoken");

    // CustomersView class
    function CustomersView(config) {
        // Initialize components with configuration
        this.toastManager = window.storeManager.toastManager;
        this.modalManager = window.storeManager.modalManager;
        this.webSocketHandler = window.storeManager.webSocketHandler;

        this.csrftoken = config.csrftoken;
        this.cardNumber = null; // To hold the card number from WebSocket

        // Bind WebSocket handlers
        this.initWebSocketHandlers();

        // Bind form submission handler
        this.initFormActions();

        // Bind modal open event
        this.initModalActions();
    }

    CustomersView.prototype.initWebSocketHandlers = function () {
        const webSocket = this.webSocketHandler;

        webSocket.onopen = () => {
            console.log("WebSocket connection established");
        };

        webSocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.card_number) {
                    console.log("Card Number Received:", data.card_number);
                    this.cardNumber = data.card_number;

                    // Check if the card number already exists
                    const existingCustomer = document.querySelector(`[data-card-number="${data.card_number}"]`);
                    if (existingCustomer) {
                        const redirectUrl = existingCustomer.getAttribute("data-url");
                        if (redirectUrl) {
                            window.location.href = redirectUrl;
                            return;
                        }
                    }

                    // Open the modal and populate the card number field
                    const modal = new bootstrap.Modal(document.getElementById("addCustomerModal"));
                    document.getElementById("card_number").value = data.card_number;
                    document.getElementById("card_number_container").style.display = "block";
                    modal.show();
                }

                if (data.message) {
                    console.log("Message:", data.message);
                    this.toastManager.info("Card detected", data.message, "", true);
                }
            } catch (error) {
                console.error("Error parsing WebSocket message:", error);
            }
        };

        webSocket.onclose = () => {
            console.log("WebSocket connection closed");
            this.toastManager.warning("WebSocket connection closed", "WebSocket was reset.", "", false);
        };

        webSocket.onerror = (error) => {
            console.error("WebSocket error:", error);
            this.toastManager.error("WebSocket error", "WebSocket encountered an error.", "", false);
        };
    };

    CustomersView.prototype.initFormActions = function () {
        const addCustomerForm = document.getElementById("addCustomerForm");
        if (addCustomerForm) {
            addCustomerForm.addEventListener("submit", (event) => {
                event.preventDefault(); // Prevent default submission

                const overlay = document.getElementById("nfcOverlay");
                overlay.style.display = "block"; // Show NFC overlay

                const cardNumberField = document.getElementById("card_number");
                const cardNumber = cardNumberField && cardNumberField.value ? cardNumberField.value : null;

                fetch("{% url 'customers' %}", {
                    method: "POST",
                    mode: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFTOKEN": CSRF_TOKEN,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body: JSON.stringify({
                        first_name: document.getElementById("first_name").value,
                        last_name: document.getElementById("last_name").value,
                        email: document.getElementById("email").value,
                        balance: document.getElementById("balance").value,
                        card_number: cardNumber, // Only append if opened with WebSocket trigger
                    }),
                })
                    .then((response) => {
                        if (response.ok) {
                            console.log("Customer added successfully");
                            location.reload();
                        } else {
                            console.error("Error adding customer:", response.status);
                            alert("Failed to add customer. Try again.");
                        }
                    })
                    .catch((error) => {
                        console.error("Fetch error:", error);
                    })
                    .finally(() => {
                        overlay.style.display = "none"; // Hide NFC overlay
                    });
            });
        }
    };

    CustomersView.prototype.initModalActions = function () {
        const addSellersButton = document.querySelector(".btn-danger.mb-2");
        if (addSellersButton) {
            addSellersButton.addEventListener("click", () => {
                this.cardNumber = null; // Reset card number if modal is opened manually
                const cardNumberContainer = document.getElementById("card_number_container");
                if (cardNumberContainer) {
                    cardNumberContainer.style.display = "none";
                }
                const modal = new bootstrap.Modal(document.getElementById("addCustomerModal"));
                modal.show();
            });
        }
    };

    // CustomersViewChart class for dynamic sparkline charts
    class CustomersViewChart {
        constructor(element, data) {
            this.element = element;
            this.data = data.balance;
            this.timestamp = data.timestamp;
            this.initChart();
        }

        initChart() {
            const daysToDisplay = 7; // Configurable number of days
            const now = new Date().getTime(); // Current timestamp in milliseconds
            const cutoff = now - daysToDisplay * 24 * 60 * 60 * 1000; // Timestamp for the cutoff date

            // Filter the data to include only the last `daysToDisplay` days
            const filteredData = this.data.filter((point, index) => {
                const timestamp = this.timestamp[index];
                return timestamp >= cutoff;
            });

            const filteredTimestamps = this.timestamp.filter(
                (timestamp) => timestamp >= cutoff
            );

            // If no data exists, add two points with value 0 at the beginning and end
            if (filteredData.length === 0) {
                // get the last datapoint
                const last_data = this.data[this.data.length - 1];
                filteredData.push(last_data, last_data);
                filteredTimestamps.push(cutoff, now);
            } else if (filteredData.length === 1) {
                // Add a zero point at the beginning and end if there is data
                const last_data = this.data[this.data.length - 1];
                filteredData.push(last_data);
                filteredTimestamps.push(now);
            }

            const options = {
                series: [
                    {
                        name: "Balance",
                        data: filteredData,
                    },
                ],
                chart: {
                    type: "area",
                    width: 80,
                    height: 35,
                    sparkline: {
                        enabled: true,
                    },
                },
                stroke: {
                    width: 2,
                    curve: "smooth",
                },
                xaxis: {
                    type: "datetime",
                    categories: filteredTimestamps,
                },
                colors: ["#4caf50"],
                tooltip: {
                    enabled: true,
                },
                // mouse hover
                fill: {
                    type: "gradient",
                    gradient: {
                        shadeIntensity: 1,
                        opacityFrom: 0.7,
                        opacityTo: 0.9,
                        stops: [0, 100],
                    },
                },
            };

            const chart = new ApexCharts(this.element, options);
            chart.render();
        }
    }

    // Initialize sparkline charts for all customers
    function initSparklineCharts() {
        const sparkCharts = document.querySelectorAll(".spark-chart");
        console.log("Sparkline charts found:", sparkCharts.length);

        sparkCharts.forEach((chart) => {
            const dataset = chart.getAttribute("data-dataset");
            if (dataset) {
                try {
                    // Decode the escaped JSON string
                    const decodedDataset = dataset.replace(/\\u0022/g, '"'); // Decode escaped double quotes
                    const data = JSON.parse(decodedDataset); // Parse the JSON data
                    new CustomersViewChart(chart, data);
                } catch (error) {
                    console.error("Error parsing dataset for sparkline chart:", error, dataset);
                }
            } else {
                console.warn("No dataset found for spark-chart element:", chart);
            }
        });
    }

    // Export CustomersView and initSparklineCharts
    window.CustomersView = CustomersView;
    window.initSparklineCharts = initSparklineCharts;
})(window.jQuery);
