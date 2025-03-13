const scriptPath = {
    "js/ToastManager.js": "ToastManager",
    "js/ModalDialogManager.js": "ModalDialogManager",
    "js/WebSocketHandler.js": "WebSocketHandler",
    "js/RequestHandler.js": "RequestHandler",
    "js/ActionTriggerHandler.js": "ActionTriggerHandler",
};

const classReferences = {}; // Store references for later use

// Import all modules dynamically and store references
async function loadScripts() {
    const importPromises = Object.entries(scriptPath).map(async ([script, className]) => {
        try {
            const module = await import(`${window.static}${script}`);
            console.debug(`✅ Script loaded from ${window.static}${script}:`, module);

            // Ensure the module provides either a named or default export
            const ClassRef = module[className] || module.default;
            if (ClassRef) {
                classReferences[className] = ClassRef;
            } else {
                console.error(`❌ Module '${script}' did not export '${className}' or a default export.`);
            }
        } catch (error) {
            console.error(`❌ Error loading script: ${window.static}${script}`, error);
        }
    });

    // Wait for all imports to complete
    await Promise.all(importPromises);
    console.log("🚀 All modules loaded successfully!");

    return classReferences; // Return stored references after all imports finish
}

    
const App = {
    toastManager: null,
    modalManager: null,
    webSocketHandler: null,
    requestHandler: null,
    csrfToken: null,
    resolverName: null,
    socketAddress: null,
    urls: {},

    
    /** Initialize the `ready` promise when `init()` is called */
    ready: null,
    resolveReady: null,
    /**
     * Initializes the application.
     * @param {object} config - Configuration object.
     */
    async init(config) {
        console.log("🚀 Initializing App...");
        const classes = await loadScripts();

        // **Initialize `ready` only once**
        if (!this.ready) {
            this.ready = new Promise((resolve) => {
                this.resolveReady = resolve;
            });
        }

        this.csrfToken = config.csrfToken;
        this.resolverName = config.resolverName;
        this.socketAddress = config.socketAddress;
        this.urls = config.urls || {};

        // Initialize managers
        this.toastManager = new classes.ToastManager(config.toastImgBase);
        this.modalManager = new classes.ModalDialogManager(config.modalId);
        this.webSocketHandler = new classes.WebSocketHandler(this.socketAddress, this.resolverName, this.toastManager);
        this.requestHandler = new classes.RequestHandler(this.csrfToken, this.toastManager);
        this.actionTrigger = new classes.ActionTriggerHandler(this.csrfToken, this.toastManager);
        // Bind button actions
        this.initActions();
        
        console.log("🚀 App Initialized Successfully!");

        // ✅ Remove loading overlay after full initialization
        document.getElementById("loadingOverlay").style.display = "none";

        // **Resolve `ready` when initialization completes**
        this.resolveReady();
    },
    

    /** Initializes the global `ready` Promise */
    initializeReadyPromise() {
        this.ready = new Promise((resolve) => {
            this.resolveReady = resolve; // Store resolver function
        });
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


// **Initialize the ready promise before App.init() runs**
App.initializeReadyPromise();
