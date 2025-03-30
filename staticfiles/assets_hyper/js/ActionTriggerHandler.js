export default class ActionTriggerHandler {
    /**
     * Constructor for ActionTriggerHandler
     * @param {string} csrfToken - CSRF token for security
     * @param {object} toastManager - Reference to the toastManager instance
     */
    constructor(csrfToken, toastManager) {
        this.csrfToken = csrfToken;
        this.toastManager = toastManager;
    }

    /**
     * Generic method to send an AJAX request with only a command in the headers.
     * @param {string} cmd - Command type (e.g., 'start_process', 'shutdown')
     * @param {string} url - Endpoint URL for the request.
     */
    sendAction(cmd, url, data = {}) {
        console.log(`🚀 Sending action '${cmd}' to: ${url}`);

        return fetch(url, {
            method: "POST",
            mode: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFTOKEN": this.csrfToken,
                "X-Requested-With": "XMLHttpRequest",
                "cmd": cmd // Only sending command in headers
            },
            body: JSON.stringify(data), // Empty body
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Request failed: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                console.log("✅ Success:", data);
                this.toastManager.info(
                    "Success",
                    `Action '${cmd}' triggered successfully.`,
                    "",
                    true
                );
                return data;
            })
            .catch((error) => {
                console.error("❌ Error:", error);
                this.toastManager.error(
                    "Error",
                    `Failed to trigger action '${cmd}': ${error.message}`,
                    "error",
                    false
                );
            })
            .finally(() => {
                console.log("🔄 Request completed.");
            });
    }

    /**
     * Attaches an event listener to a button to trigger an action on click.
     * @param {string} cmd - Command type (e.g., 'shutdown', 'restart')
     * @param {string} buttonId - ID of the button element
     * @param {string} url - Endpoint URL for the request.
     */
    attachButton(cmd, buttonId, url) {
        const button = document.getElementById(buttonId);

        if (!button) {
            console.error(`🚨 Button with ID '${buttonId}' not found.`);
            return;
        }

        // ✅ Listen for button click
        button.addEventListener("click", (event) => {
            event.preventDefault();
            console.log(`📌 Button '${buttonId}' clicked, triggering action '${cmd}'...`);
            this.sendAction(cmd, url);
        });
    }
}
