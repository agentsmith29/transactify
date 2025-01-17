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
        this.toastManager = window.storeManager.toastManager;
        this.modalManager = window.storeManager.modalManager;
        this.webSocketHandler = window.storeManager.webSocketHandler;

        this.csrftoken = config.csrftoken;
        this.page_url = config.page_url;
        this.cardNumber = null;

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

                    // Update modal with the card number
                    document.getElementById("card_number").value = data.card_number;
                    document.getElementById("card_number_container").style.display = "block";

                    // Close NFC overlay
                    const overlay = document.getElementById("nfcOverlay");
                    overlay.style.display = "none";

                    this.toastManager.success("Card detected", `Card number ${data.card_number} has been detected.`, "", false);
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
        window.submitAddCustomerForm = () => {
            const addCustomerForm = document.getElementById("addCustomerForm");
            if (addCustomerForm) {
                const overlay = document.getElementById("nfcOverlay");
                overlay.style.display = "block";

                const cardNumberField = document.getElementById("card_number");
                const cardNumber = cardNumberField && cardNumberField.value ? cardNumberField.value : null;

                fetch(this.page_url, {
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
                        card_number: cardNumber,
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
                        overlay.style.display = "none";
                    });
            }
        };
    };

    CustomersView.prototype.initModalActions = function () {
        const addSellersButton = document.querySelector("a.btn-danger.mb-2[data-bs-toggle='modal'][data-bs-target='#addCustomerModal']");
        if (addSellersButton) {
            addSellersButton.addEventListener("click", () => {
                const modalElement = document.getElementById("addCustomerModal");
                const modal = bootstrap.Modal.getOrCreateInstance(modalElement);

                const overlay = document.getElementById("nfcOverlay");
                overlay.style.display = "block"; // Show NFC overlay

                // Wait for WebSocket card_number
                const interval = setInterval(() => {
                    if (this.cardNumber) {
                        clearInterval(interval);
                        modal.show();
                        overlay.style.display = "none"; // Hide overlay
                    }
                }, 1000);

                // Reset fields in the modal
                document.getElementById("card_number").value = "";
                document.getElementById("card_number_container").style.display = "none";
            });
        }
    };

    // Export CustomersView
    window.CustomersView = CustomersView;
})(window.jQuery);
