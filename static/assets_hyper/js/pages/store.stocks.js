class ManageStock {
    constructor(pageName, page_url) {
        this.page_url = page_url
        this.initSocket();
    }

    initSocket() {
        window.storeManager.webSocketHandler.onmessage = (event) => {
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
    }

    initEventListeners() {
        // Attach change event to the EAN dropdown
        document.getElementById('ean').addEventListener('change', this.updateResellPrice.bind(this));
        // Attach event to quantity and purchase price fields to recalculate profit dynamically
        document.getElementById('quantity').addEventListener('input', this.updateResellPrice.bind(this));
        // purchase_price: <input type="number" class="form-control" id="purchase_price" name="purchase_price" step="0.01" required=""></input>
        // value change event
        document.getElementById('purchase_price').addEventListener('input', this.updateResellPrice.bind(this));
        
    }

    async submitStockForm() {
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

    restockProduct(ean) {
        const eanDropdown = document.getElementById('ean');
        eanDropdown.value = ean;
        this.updateResellPrice();

        // Scroll to the add stock form for user to input details
        document.getElementById('addStockForm').scrollIntoView({ behavior: 'smooth' });
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
        console.log("Updating resell price...");
        const eanDropdown = document.getElementById('ean');
        const selectedEan = eanDropdown.value; // Get the selected EAN
    
        // Find the product in the products array using the selected EAN
        const product = window.products.find(prod => prod.ean === selectedEan);
    
        if (product) {
            const resellPrice = product.resell_price;
    
            // Update resell price, cost, and profit fields
            document.getElementById('resell_price').textContent = `€ ${parseFloat(resellPrice).toFixed(2)}`;
            document.getElementById('product-card-title').textContent = product.name;
            const stockBadge = document.getElementById('product-card-badge')
            if (product.quantity > 2) {
                stockBadge.textContent = 'In Stock';
                stockBadge.className = 'badge bg-success-lighten';
            } else if (product.quantity > 0) {
                stockBadge.textContent = 'Low Stock';
                stockBadge.className = 'badge bg-warning-lighten';
            } else {
                stockBadge.textContent = 'Out of Stock';
                stockBadge.className = 'badge bg-danger-lighten';
            }
            //  purchase_price: <input type="number" class="form-control" id="purchase_price" name="purchase_price" step="0.01" required=""></input>
            cost =  parseFloat(document.getElementById('purchase_price').value);
            // check if cost is not empty, otherwise assign 0
            if (isNaN(cost)) {
                cost = 0
            }
            profit = resellPrice - cost
            document.getElementById('cost').textContent = `€ ${parseFloat(cost).toFixed(2)}`;
            document.getElementById('profit').textContent = `€ ${parseFloat(profit).toFixed(2)}`;
        } else {
            console.error("Product not found for the selected EAN");
        }
    }
    



}

