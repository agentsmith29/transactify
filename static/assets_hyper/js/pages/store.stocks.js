
"use strict";

class ManageStock {
    constructor(page_url) {
        this.page_url = page_url;
        this.initSocket();
        this.initEventListeners();
        this.initDataTables();
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
                    window.storeManager.toastManager.info("Barcode received", `New scanned barcode: ${data.barcode}`, "", false);
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
        // Attach events for logic expression and toggle input method
        document.getElementById('logic_expression').addEventListener('input', this.calculateFromExpression.bind(this));
        document.getElementById('logic_expression').addEventListener('input', this.updateResellPrice.bind(this));
        document.getElementById('use_direct_price').addEventListener('click', () => this.toggleInputMethod('direct'));
        document.getElementById('use_logic_expression').addEventListener('click', () => this.toggleInputMethod('expression'));
        
    
    }

    initDataTables() {
        // Initialize DataTable for products
        $("#products-datatable").DataTable({
            language: {
                paginate: { previous: "<i class='mdi mdi-chevron-left'>", next: "<i class='mdi mdi-chevron-right'>" },
                info: "Showing products _START_ to _END_ of _TOTAL_",
                lengthMenu: 'Display <select class="form-select form-select-sm ms-1 me-1"><option value="10">10</option><option value="20">20</option><option value="-1">All</option></select> products',
            },
            columnDefs: [{ targets: -1, className: "dt-body-right" }],
            pageLength: 10,
            order: [[1, "asc"]],
            drawCallback: function () {
                $(".dataTables_paginate > .pagination").addClass("pagination-rounded"),
                    $("#products-datatable_length label").addClass("form-label");
            },
        });

        // Initialize DataTable for restocks
        $("#restocks-datatable").DataTable({
            language: {
                paginate: { previous: "<i class='mdi mdi-chevron-left'>", next: "<i class='mdi mdi-chevron-right'>" },
                info: "Showing restocks _START_ to _END_ of _TOTAL_",
                lengthMenu: 'Display <select class="form-select form-select-sm ms-1 me-1"><option value="10">10</option><option value="20">20</option><option value="-1">All</option></select> restocks',
            },
            columnDefs: [{ targets: -1, className: "dt-body-right" }],
            pageLength: 10,
            order: [[1, "asc"]],
            drawCallback: function () {
                $(".dataTables_paginate > .pagination").addClass("pagination-rounded"),
                    $("#restocks-datatable_length label").addClass("form-label");
            },
        });
    }

    async submitStockForm() {
        const form = document.getElementById('addStockForm');

        // Validate required fields
        const requiredFields = ['ean', 'quantity', 'purchase_price'];
        for (const field of requiredFields) {
            const inputElement = form.querySelector(`[name="${field}"]`);
            if (!inputElement || !inputElement.value) {
                window.storeManager.toastManager.error("Missing required field", `Please fill in the ${field.replace('_', ' ')}`, "Required fields cannot be empty.", false);
                return;
            }
        }

        const formData = new FormData(form);
        const resell_price = parseFloat(formData.get('resell_price'));
        const purchase_price = parseFloat(formData.get('purchase_price'));
        console.log("Resell price: " + resell_price + " Purchase price: " + purchase_price);

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
                    window.storeManager.toastManager.success('Stock added successfully', data.message, "", true);
                } else {
                    window.storeManager.toastManager.error("Stock update failed", data.message, "Please try again.", false);
                }
            })
            .catch(error => {
                console.error("Failed to update stock", error);
                window.storeManager.toastManager.error("Failed to update stock", error, "Please try again.", false);
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
            const stockBadge = document.getElementById('product-card-badge');
            if (product.stock_quantity > 2) {
                stockBadge.textContent = 'In Stock';
                stockBadge.className = 'badge bg-success';
            } else if (product.stock_quantity > 0) {
                stockBadge.textContent = 'Low Stock';
                stockBadge.className = 'badge bg-warning';
            } else {
                stockBadge.textContent = 'Out of Stock';
                stockBadge.className = 'badge bg-danger';
            }

            const cost = parseFloat(document.getElementById('purchase_price').value) || 0;
            const profit = resellPrice - cost;
            document.getElementById('cost').textContent = `€ ${cost.toFixed(2)}`;
            document.getElementById('profit').textContent = `€ ${profit.toFixed(2)}`;
        } else {
            console.error("Product not found for the selected EAN");
        }
    }

    toggleInputMethod(method) {
        const logicExpressionField = document.getElementById('logic_expression');
        const purchasePriceField = document.getElementById('purchase_price');

        if (method === 'direct') {
            logicExpressionField.disabled = true;
            purchasePriceField.disabled = false;
        } else if (method === 'expression') {
            logicExpressionField.disabled = false;
            purchasePriceField.disabled = true;
        }
    }

    calculateFromExpression() {
        const logicExpressionField = document.getElementById('logic_expression');
        const quantityField = document.getElementById('quantity');
        const purchasePriceField = document.getElementById('purchase_price');

        try {
            const expressionResult = eval(logicExpressionField.value); // Evaluate the expression
            const quantity = parseFloat(quantityField.value) || 1; // Avoid division by zero
            purchasePriceField.value = (expressionResult).toFixed(2); // Calculate price per unit
        } catch (error) {
            console.error("Invalid logic expression", error);
        }
    }
}

// export
window.ManageStock = ManageStock; // Make it globally accessible

