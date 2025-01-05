class LogViewHelper {
    constructor(pageName, page_url) {
        this.page_url = page_url;
        this.pageName = pageName;
        this.socket = new WebSocket(`ws://${window.location.host}/tcon/page/${pageName}/`);
        this.logLevelFilter = document.getElementById("logLevelFilter");
        this.searchLogs = document.getElementById("searchLogs");
        this.logsTableBody = document.getElementById("logsTableBody");
        this.logEntries = Array.from(this.logsTableBody.getElementsByClassName("log-entry"));
        this.clearLogsButton = document.getElementById("clearLogsButton");

        this.initSocket();
        this.initFilters();
        this.initClearLogs();
    }

    initSocket() {
        this.socket.onopen = () => {
            console.log("WebSocket connection established for page:", this.pageName);
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("Message received from server:", data);
                // Process WebSocket message if needed
            } catch (error) {
                console.error("Error processing WebSocket message:", error);
            }
        };

        this.socket.onclose = () => {
            console.log("WebSocket connection closed");
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    }

    initFilters() {
        const filterLogs = () => {
            const filterValue = this.logLevelFilter.value.toLowerCase();
            const searchQuery = this.searchLogs.value.toLowerCase();

            this.logEntries.forEach((entry) => {
                const logLevel = entry.getAttribute("data-loglevel").toLowerCase();
                const module = entry.getAttribute("data-module").toLowerCase();
                const message = entry.textContent.toLowerCase();

                const matchesFilter = !filterValue || logLevel === filterValue;
                const matchesSearch =
                    !searchQuery ||
                    module.includes(searchQuery) ||
                    message.includes(searchQuery);

                entry.style.display = matchesFilter && matchesSearch ? "" : "none";
            });
        };

        this.logLevelFilter.addEventListener("change", filterLogs);
        this.searchLogs.addEventListener("input", filterLogs);
    }

    initClearLogs() {
        this.clearLogsButton.addEventListener("click", () => {
            if (confirm("Are you sure you want to clear all logs? This action cannot be undone.")) {
                fetch(this.page_url, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                        "cmd": "clear_logs",
                    },
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.success) {
                            window.toastManager.success('Loges cleared successfully', data.message, "", true);
                        } else {
                            window.toastManager.error("Error clearing logs", data.message, "Please try again.", false);
                        }
                    })
                    .catch((error) => {
                        console.error("Error clearing logs:", error);
                        window.toastManager.error("Error clearing logs", data.message, "Please try again.", false);
                    });
            }
        });
    }
}

// Initialize LogViewHelper
document.addEventListener("DOMContentLoaded", () => {
    const logViewHelper = new LogViewHelper("logs_page", window.location.href);
});
