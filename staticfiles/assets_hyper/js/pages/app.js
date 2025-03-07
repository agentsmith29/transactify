const App = {
    toastManager: null,
    modalManager: null,
    webSocketHandler: null,
    requestHandler: null,
    csrfToken: null,
    resolverName: null,
    socketAddress: null,
    urls: {},

    /**
     * Initializes the application.
     * @param {object} config - Configuration object.
     */
    init(config) {
        this.csrfToken = config.csrfToken;
        this.resolverName = config.resolverName;
        this.socketAddress = config.socketAddress;
        this.urls = config.urls || {};

        // Initialize managers
        this.toastManager = new ToastManager(config.toastImgBase);
        this.modalManager = new ModalDialogManager(config.modalId);
        this.webSocketHandler = new WebSocketHandler(this.socketAddress, this.resolverName, this.toastManager);
        this.requestHandler = new RequestHandler(this.csrfToken, this.toastManager);
        this.actionTrigger = new ActionTriggerHandler(this.csrfToken, this.toastManager);
        // Bind button actions
        this.initActions();
        
        console.log("🚀 App Initialized Successfully!");
    },

    /**
     * Sends a system request (shutdown/reboot).
     * @param {string} url - The API endpoint.
     */
    async sendSysRqCommand(url) {
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": this.csrfToken,
                },
            });

            if (response.ok) {
                const data = await response.json();
                this.toastManager.success("Success", data.message, "success");
            } else {
                this.toastManager.error("Error", "Unable to perform the requested action.", "error");
            }
        } catch (error) {
            console.error("Error:", error);
            this.toastManager.error("Error", "An unexpected error occurred.", "error");
        }
    },

    
    /**
     * Initializes button click events.
     */
    initActions() {
        const shutdownBtn = document.getElementById("shutdownBtn");
        const rebootBtn = document.getElementById("rebootBtn");

        if (shutdownBtn) {
            shutdownBtn.addEventListener("click", () => {
                this.modalManager.display(
                    "Confirm Shutdown",
                    "Are you sure you want to shutdown the system?",
                    "Shutdown",
                    () => {
                        this.sendSysRqCommand(this.urls.shutdownUrl);
                        console.log("Shutdown command sent!");
                    }
                );
            });
        }

        if (rebootBtn) {
            rebootBtn.addEventListener("click", () => {
                this.modalManager.display(
                    "Confirm Reboot",
                    "Are you sure you want to reboot the system?",
                    "Reboot",
                    () => {
                        this.sendSysRqCommand(this.urls.rebootUrl);
                        console.log("Reboot command sent!");
                    }
                );
            });
        }

        this.displayToastAfterReload();
        
    },

                                // Function to check and display toast after reload
    displayToastAfterReload() {
        // Get toast data from localStorage
        const toastData = JSON.parse(localStorage.getItem('toastData'));

        if (toastData) {
            // Display the toast
            this.toastManager._display(toastData.type, toastData.title, toastData.message, toastData.submessage);

            // Clear the stored toast data
            localStorage.removeItem('toastData');
        }
    }
                
                               
};

// Expose globally
window.App = App;
