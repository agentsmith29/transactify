!(function ($) {
    "use strict";

    // StoreManager class
    function StoreManager(config) {
        // Initialize components with configuration
        this.toastManager = new ToastManager(config.toastImgBase);
        this.modalManager = new ModalDialogManager(config.modalId);
        this.socketAddress = config.socketAddress;
        this.csrfToken = config.csrfToken;
        this.resolverName = config.resolverName;
        this.urls = config.urls;
        this.shutdownUrl = this.urls.shutdownUrl;
        this.rebootUrl = this.urls.rebootUrl;

        // Initialize the WebSocket connection
        this.webSocketHandler = new WebSocketHandler(this.socketAddress, this.resolverName);

        // Bind event listeners
        this.initActions();
    }

    // Send SysRq Command
    StoreManager.prototype.sendSysRqCommand = async function (url) {
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": this.csrfToken, // CSRF token
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
    };

    // Initialize button actions
    StoreManager.prototype.initActions = function () {
        const self = this;

        // Shutdown Button
        document.getElementById("shutdownBtn").addEventListener("click", () => {
            self.modalManager.display(
                "Confirm shutdown",
                "Are you sure you want to shutdown the system? After shutdown, the system will be powered off.",
                "Shutdown",
                () => {
                    
                    self.sendSysRqCommand(self.shutdownUrl);
                    console.log("Shutdown command sent!");
                }
            );
        });

        // Reboot Button
        document.getElementById("rebootBtn").addEventListener("click", () => {
            self.modalManager.display(
                "Confirm reboot",
                "Are you sure you want to reboot the system?",
                "Reboot",
                () => {
                    self.sendSysRqCommand(self.rebootUrl);
                    console.log("Reboot command sent!");
                }
            );
        });
    };

    // Export StoreManager
    window.StoreManager = StoreManager;
})(window.jQuery);
