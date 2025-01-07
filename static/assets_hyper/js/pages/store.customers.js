!(function () {
    "use strict";

    // CSRF Token Handling
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const CSRF_TOKEN = getCookie("csrftoken");

    // Form Submission Handler
    const addCustomerForm = document.getElementById("addCustomerForm");
    if (addCustomerForm) {
        addCustomerForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Prevent form submission

            const overlay = document.getElementById("nfcOverlay");
            overlay.style.display = "block"; // Show NFC overlay

            const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
            console.log("CSRF Token:", csrftoken);

            fetch("{% url 'customers' %}", {
                method: "POST",
                mode: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFTOKEN": CSRF_TOKEN,
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({
                    first_name: document.getElementById("first_name").value,
                    last_name: document.getElementById("last_name").value,
                    email: document.getElementById("email").value,
                    balance: document.getElementById("balance").value
                })
            })
                .then(response => {
                    if (response.ok) {
                        console.log("Request successful");
                        location.reload();
                        return response.json();
                    } else {
                        console.error("Request failed:", response.status);
                        alert("Error occurred. Please try again.");
                    }
                })
                .then(data => {
                    console.log("Response data:", data);
                })
                .catch(error => {
                    console.error("Error:", error);
                })
                .finally(() => {
                    overlay.style.display = "none"; // Hide NFC overlay
                });
        });
    }


    socket.onopen = function () {
        console.log(`WebSocket connection established for page: ${webpage}`);
    };

    socket.onmessage = function (event) {
        console.log("Message received from server:", event.data);

        try {
            const data = JSON.parse(event.data);
            if (data.message) {
                console.log("Message:", data.message);
                console.log("card_id:", data.card_id);

                const toastMessage = document.getElementById("toastMessage");
                toastMessage.textContent = data.message;
                const toast = new bootstrap.Toast(document.getElementById("barcodeToast"));
                toast.show();
            }

            if (data.barcode) {
                console.log("Barcode:", data.card_id);

                const eanField = document.getElementById("ean");
                if (eanField) {
                    eanField.value = data.barcode;
                } else {
                    console.error("EAN field not found in the DOM");
                }
            }
        } catch (error) {
            console.error("Error parsing WebSocket message:", error);
        }
    };

    socket.onclose = function () {
        console.log("WebSocket connection closed");
        toastManager.warning("WebSocket connection closed", "WebSocket connection was closed or resetted.", "", false);
    };

    socket.onerror = function (error) {
        console.error("WebSocket error:", error);
        console.error("WebSocket error:", error.message);

    };
})();
