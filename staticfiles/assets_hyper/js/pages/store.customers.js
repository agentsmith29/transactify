class CustomersManager {
    constructor(page_url, toastManager, modalManager, webSocketHandler, requestHandler) {

        App.ready.then(() => {
            this.toastManager = App.toastManager;
            this.modalManager =  App.tmodalManager;
            this.webSocketHandler =  App.twebSocketHandler;
            this.requestHandler =  App.trequestHandler;
            this.page_url = page_url;
        
        
            this.initWebSocketHandlers();
            this.initFormActions();
            this.initModalActions();
            
        });

    }

    initWebSocketHandlers() {
        this.webSocketHandler.onopen = () => console.log("WebSocket connection established");

        this.webSocketHandler.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.card_number) {
                    this.handleCardNumber(data.card_number);
                }
                if (data.message) {
                    this.toastManager.info("Card detected", data.message, "", false);
                }
            } catch (error) {
                console.error("Error parsing WebSocket message:", error);
            }
        };

        this.webSocketHandler.onclose = () => {
            console.log("WebSocket connection closed");
            this.toastManager.warning("WebSocket connection closed", "WebSocket was reset.", "", false);
        };

        this.webSocketHandler.onerror = (error) => {
            console.error("WebSocket error:", error);
            this.toastManager.error("WebSocket error", "WebSocket encountered an error.", "", false);
        };
    }

    handleCardNumber(cardNumber) {
        this.cardNumber = cardNumber;
        const existingCustomer = document.querySelector(`[data-card-number="${cardNumber}"]`);
        if (existingCustomer) {
            const redirectUrl = existingCustomer.getAttribute("data-url");
            if (redirectUrl) {
                window.location.href = redirectUrl;
                return;
            }
        }
        
        const modalElement = document.getElementById("addCustomerModal");
        const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
        document.getElementById("card_number").value = cardNumber;
        document.getElementById("card_number_container").style.display = "block";
        modal.show();
    }

    submitAddCustomerForm() {
        this.requestHandler.attachFormAndButton("add", "addCustomerForm", "submitCustomerButton", this.page_url);
    }

    deleteCustomer(username) {
        this.requestHandler.sendRequest("delete", { username }, this.page_url);
    }

    initModalActions() {
        const addSellersButton = document.querySelector("a.btn-danger.mb-2[data-bs-toggle='modal'][data-bs-target='#addCustomerModal']");
        if (addSellersButton) {
            addSellersButton.addEventListener("click", () => {
                const modalElement = document.getElementById("addCustomerModal");
                const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
                document.getElementById("card_number").value = "";
                document.getElementById("card_number_container").style.display = "none";
                modal.show();
            });
        }
    }
}
