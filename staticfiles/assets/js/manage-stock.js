class ManageStock {
    constructor(pageName, page_url) {
        this.page_url = page_url
        this.pageName = pageName;
        this.socket = new WebSocket(`ws://${window.location.host}/tcon/page/${pageName}/`);
        this.initSocket();
    }

    initSocket() {
        this.socket.onopen = () => {
            console.log("WebSocket connection established for page:", this.pageName);
            //window.toastManager.info("WebSocket connection established", `Connected to websocket ws://${window.location.host}/tcon/page/${this.pageName}/`, "");
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("Message received from server:", data);

                if (data.barcode) {
                    const eanField = document.getElementById('ean');
                    if (eanField) {
                        eanField.value = data.barcode;
                    } else {
                        console.error("EAN field not found.");
                    }
                    window.toastManager.info("Barcode recieved", `New scanned barcode: ${data.barcode}`, "", false);
                }
            } catch (error) {
                console.error("Error processing WebSocket message:", error);
            }
        };

        this.socket.onclose = () => {
            console.log("WebSocket connection closed");
            window.toastManager.warning("WebSocket connection closed", "WebSocket connection was closed or resetted.", "", false);
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    }

    submitStockForm() {
        const form = document.getElementById('addStockForm');

        // Validate required fields
        const requiredFields = ['ean', 'quantity', 'purchase_price'];
        for (const field of requiredFields) {
            const inputElement = form.querySelector(`[name="${field}"]`);
            if (!inputElement || !inputElement.value) {
                window.toastManager.error("Missing required field", `Please fill in the ${field.replace('_', ' ')}`, "Required fields cannot be empty.", false);
                return;
            }
        }

        const formData = new FormData(form);
        const resell_price = parseFloat(formData.get('resell_price'));
        const purchase_price =  parseFloat(formData.get('purchase_price'));
        console.log("Resell price: "+ resell_price + " Purchase price: " + purchase_price);

        if (resell_price < purchase_price) {
            modalManager.display(
                "Entered resell price is smaller than purchase price",
                "Resell price is smaller than purchase price. Are you sure you want to continue?",
                "Continue",
                () => {
                    this.proceedWithStockForm(formData);
                }
            );
            return;
        }
        this.proceedWithStockForm(formData);
    }

    proceedWithStockForm(formData) {
        fetch(this.page_url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                'cmd': 'add_stock'
            },
            body: JSON.stringify({
                product_ean: formData.get('ean'),
                quantity: formData.get('quantity'),
                purchase_price: formData.get('purchase_price'),
            })
        })
            .then(response => {
                console.log("submitStockForm: Form data sent to " + this.page_url);
                return response.json();
            })
            .then(data => {
                if (data.success && data.code === 116) {
                    window.toastManager.success('Stock added successfully', data.message, "", true);
                } else {
                    window.toastManager.error("Stock update failed", data.message, "Please try again.", false);
                }
            })
            .catch(error => {
                console.error("Failed to update stock", error);
                window.toastManager.error("Failed to update stock", error, "Please try again.", false);
            });
    }


    updateResellPrice() {
        const dropdown = document.getElementById('ean');
        const selectedOption = dropdown.options[dropdown.selectedIndex];
        const resellPrice = selectedOption.getAttribute('data_price');
        
        const resellPriceInput = document.getElementById('resell_price');
        resellPriceInput.value = resellPrice || ''; // Set the price or clear if undefined
    }


}

