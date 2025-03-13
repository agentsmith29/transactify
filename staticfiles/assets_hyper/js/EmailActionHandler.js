export default class EmailActionHandler {
    constructor(apiEndpoint) {
        this.apiEndpoint = apiEndpoint;
        this.initEventListeners();
    }

    /**
     * Initializes event listeners for all email action buttons.
     */
    initEventListeners() {
        document.querySelectorAll(".action-icon").forEach((icon) => {
            icon.addEventListener("click", (event) => {
                event.preventDefault(); // Prevent default link behavior

                let actionType = icon.id.replace("send_mail_", ""); // Extract action name

                // Directly trigger the email action
                this.postRequest(actionType);
            });
        });
    }

    /**
     * Sends a POST request to the backend to trigger an email action.
     * @param {string} actionType - The action identifier (e.g., "email_on_deposit").
     */
    async postRequest(actionType) {
        try {
            const response = await fetch(this.apiEndpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": this.getCSRFToken(), // Include CSRF token for security
                },
                body: JSON.stringify({ action: actionType }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || "Failed to trigger email action.");
            }

            this.showToast(`Action "${actionType}" triggered successfully!`);
        } catch (error) {
            console.error("Error:", error);
            this.showToast(`Error: ${error.message}`, true);
        }
    }

    /**
     * Retrieves the CSRF token from cookies (Django compatibility).
     * @returns {string} CSRF token
     */
    getCSRFToken() {
        let cookieValue = null;
        if (document.cookie) {
            document.cookie.split(";").forEach(cookie => {
                let [name, value] = cookie.trim().split("=");
                if (name === "csrftoken") {
                    cookieValue = value;
                }
            });
        }
        return cookieValue;
    }

    /**
     * Displays a toast notification.
     * @param {string} message - The message to display.
     * @param {boolean} isError - Whether the message is an error.
     */
    showToast(message, isError = false) {
        let toast = document.createElement("div");
        toast.className = `toast-message ${isError ? "error" : "success"}`;
        toast.innerText = message;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}
