export default class RequestHandler {
    /**
     * Constructor for RequestHandler
     * @param {string} csrfToken - CSRF token for security
     * @param {object} toastManager - Reference to the toastManager instance
     */
    constructor(csrfToken, toastManager) {
        this.csrfToken = csrfToken;
        this.toastManager = toastManager;
    }

    /**
     * Collects form data and converts it to a JSON object.
     * @param {HTMLFormElement} form - The form element to process.
     * @returns {object} JSON object containing form data.
     */
    static collectFormData(form) {
        const formData = new FormData(form);
        const jsonData = {};
    
        // Process all entries in FormData
        formData.forEach((value, key) => {
            if (typeof value === "string") {
                const lower = value.toLowerCase();
                if (lower === "true" || lower === "on") {
                    value = true;
                } else if (lower === "false" || lower === "off") {
                    value = false;
                } else if (!isNaN(value) && value.trim() !== "") {
                    value = value.includes(".") ? parseFloat(value) : parseInt(value, 10);
                }
            }
    
            if (jsonData[key]) {
                if (!Array.isArray(jsonData[key])) {
                    jsonData[key] = [jsonData[key]];
                }
                jsonData[key].push(value);
            } else {
                jsonData[key] = value;
            }
        });
    
        // Handle unchecked checkboxes (they don't appear in FormData)
        form.querySelectorAll('input[type=checkbox]').forEach((checkbox) => {
            if (!formData.has(checkbox.name)) {
                jsonData[checkbox.name] = false;
            }
        });
    
        // Handle unselected radio buttons (only selected ones appear in FormData)
        const radioGroups = new Set();
        form.querySelectorAll('input[type=radio]').forEach((radio) => {
            radioGroups.add(radio.name);
        });
    
        radioGroups.forEach((name) => {
            if (!formData.has(name)) {
                jsonData[name] = null; // Explicitly mark as null if no option was selected
            }
        });
    
        return jsonData;
    }
    

    /**
     * Disables all form inputs until the form is successfully initialized.
     * @param {HTMLFormElement} form - The form element to disable.
     */
    static disableFormInputs(form) {
        form.querySelectorAll("input, button, select, textarea").forEach((element) => {
            element.disabled = true;
        });
    }

    /**
     * Enables all form inputs after successful binding.
     * @param {HTMLFormElement} form - The form element to enable.
     */
    static enableFormInputs(form) {
        form.querySelectorAll("input, button, select, textarea").forEach((element) => {
            element.disabled = false;
        });
    }

    /**
     * Generic method to send an AJAX request.
     * @param {string} cmd - Command type (e.g., 'update')
     * @param {object} jsonData - JSON data collected from form
     * @param {string} url - Endpoint URL for the request.
     */
    sendRequest(cmd, jsonData, url) {
        if (!url.endsWith('/')) {
            url += '/';
        }
        console.log(`🚀 Sending to page: ${url} with content`, jsonData);
        return fetch(url, {
            method: "POST",
            mode: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFTOKEN": this.csrfToken,
                "X-Requested-With": "XMLHttpRequest",
                "cmd": cmd
            },
            body: JSON.stringify(jsonData),
        })
            .then((response) => {
                if (!response.ok) {
                    return response.json().then((errorData) => {
                        throw new Error(`Request failed (${response.status}). Response from server: ${errorData.error}`);
                    });
                }
                return response.json();
            })
            .then((data) => {
                console.log("✅ Success:", data);
                this.toastManager.info(
                    "Success",
                    `Operation '${cmd}' completed successfully.`,
                    "",
                    true
                );
                return data;
            })
            .catch((error) => {
                console.error("❌:", error);
                this.toastManager.error(
                    "Error",
                    `Failed to complete '${cmd}': ${error.message}`,
                    "error",
                    false
                );
            })
            .finally(() => {
                console.log("🔄 Request completed.");
            });
    }

    /**
     * Attaches event listeners to a form and its submit button.
     * @param {string} cmd - Command type (e.g., 'update')
     * @param {string} formId - ID of the form element
     * @param {string} buttonId - ID of the submit button
     * @param {string} url - Endpoint URL for the request.
     */
    attachFormAndButton(cmd, formId, buttonId, url) {
        const form = document.getElementById(formId);
        const button = document.getElementById(buttonId);

        if (!form) {
            console.error(`❌ Error for ${formId} and input ${buttonId} during form binding: Form with ID '${formId}' not found.`);
            return;
        }

        // Disable form inputs initially
        RequestHandler.disableFormInputs(form);

        if (!button) {
            console.error(`❌ Error for ${formId} and input ${buttonId} during form binding: Button with ID '${buttonId}' not found.`);
            return;
        }

        try {
            // ✅ Listen for form submit (Enter key)
            form.addEventListener("submit", (event) => {
                event.preventDefault();
                console.log("📌 Form submitted via Enter key...");
                const jsonData = RequestHandler.collectFormData(form);
                this.sendRequest(cmd, jsonData, url);
            });

            // ✅ Listen for button click
            button.addEventListener("click", (event) => {
                event.preventDefault();
                console.log("📌 Submit button clicked...");
                const jsonData = RequestHandler.collectFormData(form);
                this.sendRequest(cmd, jsonData, url);
            });

            // Enable form inputs after binding
            RequestHandler.enableFormInputs(form);
            console.log(`✅ Form ${formId} and input ${buttonId} enabled after successful binding .`);
        } catch (error) {
            console.error(`❌ Error for ${formId} and input ${buttonId} during form binding: ${error}`);
            this.toastManager.error(
                "Error",
                "Failed to attach event listeners to the form.",
                "error",
                false
            );
        }
    }

    /**
     * Attaches event listeners to a dictionary and its submit button.
     * @param {string} cmd - Command type (e.g., 'update')
     * @param {object} dict - Dictionary containing data
     * @param {string} buttonId - ID of the submit button
     * @param {string} url - Endpoint URL for the request.
     */
    attachDictAndButton(cmd, dict, formId, buttonId, url) {
        const form = document.getElementById(formId);
        const button = document.getElementById(buttonId);

        if (!form) {
            console.error(`❌ Error for ${formId} and input ${buttonId} during form binding: Form with ID '${formId}' not found.`);
            return;
        }

        if (!button) {
            console.error(`❌ Error during dict binding: Button with ID '${buttonId}' not found.`);
            return;
        }

        try {
            // ✅ Listen for button click
            button.addEventListener("click", (event) => {
                event.preventDefault();
                const jsonData = RequestHandler.collectFormData(form);
                console.log(jsonData);
                // Combine dictionaries
                const combinedDict = { ...dict, ...jsonData };
                console.log("📌 Submit button clicked...");
                this.sendRequest(cmd, combinedDict, url);
            });

            console.log(`✅ Button ${buttonId} enabled after successful binding with dictionary.`);
        } catch (error) {
            console.error(`❌ Error during dict binding: ${error}`);
            this.toastManager.error(
                "Error",
                "Failed to attach event listeners to the dictionary.",
                "error",
                false
            );
        }
    }
}
