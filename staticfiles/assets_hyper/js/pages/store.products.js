class OFFParser {
    constructor() {
        this.apiBase = "https://world.openfoodfacts.org/api/v2/product/"
        this.apiTestURL = "https://world.openfoodfacts.org/api/v2/status.json";
        this.apiAvailable = false;

        // Check API availability when the class is initialized
        this.checkAPIAvailability();
    }

    async checkAPIAvailability() {
        try {
            const response = await fetch(this.apiTestURL, { method: "HEAD" });
            this.apiAvailable = response.ok;
            console.log(`Open Food Facts API available: ${this.apiAvailable}`);
        } catch (error) {
            console.warn("Open Food Facts API is unreachable:", error);
            window.storeManager.toastManager.error("Barcode recieved", `Open Food Facts API is unreachable: ${error}`, "", false);
            this.apiAvailable = false;
        }
    }

    async fetchProduct(barcode) {
        try {
            const response = await fetch(`${this.apiBase}${barcode}.json`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();

            if (data.status === 1 && data.product) {
                return data.product.product_name_de || 
                    data.product.product_name_en || 
                    data.product.product_name || 
                    "Unknown Product";
            } else {
                console.warn("Product not found in Open Food Facts.");
                return "Product Not Found";
            }
        } catch (error) {
            console.error("Error fetching product data:", error);
            return "Error fetching data";
        }
    }
}

class ManageProducts {
    constructor(page_url) {
        this.page_url = page_url;
        $(document).ready(() => {
            this.initSocket();
            this.initDataTables();
            this.offParser = new OFFParser();
            this.csrftoken = document.cookie.match(/csrftoken=([^;]+)/)[1];
        
        });
    }

    initSocket() {
        window.storeManager.webSocketHandler.onmessage = async (event) => {
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
                    window.storeManager.toastManager.info("Barcode recieved", `New scanned barcode: ${data.barcode}`, "", false);

                    // Fetch product name and populate input field
                    const productName = await this.offParser.fetchProduct(data.barcode);
                    const nameField = document.getElementById("name");
                    if (nameField) {
                        nameField.value = productName;
                    } else {
                        console.error("Product name field not found.");
                    }
                }
            } catch (error) {
                console.error("Error processing WebSocket message:", error);
            }
        };
    }

    initDataTables() {
        const tableSelector = "#product-list-datatable";
        if ($(tableSelector).length === 0) {
            console.error("Table with ID 'product-list-datatable' not found.");
            return;
        }
        // Initialize DataTable for products
        $(tableSelector).DataTable({
            language: {
                paginate: { previous: "<i class='mdi mdi-chevron-left'>", next: "<i class='mdi mdi-chevron-right'>" },
                info: "Showing products _START_ to _END_ of _TOTAL_",
                lengthMenu: 'Display <select class="form-select form-select-sm ms-1 me-1"><option value="10">10</option><option value="20">20</option><option value="-1">All</option></select> products',
                emptyTable: "No products available to display.", // Message for empty tables
            },
            columnDefs: [{ targets: -1, className: "dt-body-right" }],
            pageLength: 10,
            order: [[1, "asc"]],
            drawCallback: function () {
                $(".dataTables_paginate > .pagination").addClass("pagination-rounded"),
                    $("#product-list-datatable_length label").addClass("form-label");
            },
        });
    }

    submitProductForm() {
 
        const form = document.getElementById('addProductForm');
        const formData = new FormData(form);
       
        fetch(this.page_url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json', // Ensure this header is set correctly
                'X-CSRFToken': this.csrftoken, //formData.get('csrfmiddlewaretoken'), // Extract CSRF token
                'cmd': 'add' // Pass additional command header
            },
            body: JSON.stringify({
                product_ean: formData.get('product_ean'),
                product_name: formData.get('product_name'),
                resell_price: parseFloat(formData.get('resell_price')),
                discount: parseFloat(formData.get('discount') / 100)
            })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.code == 103) {
                    window.storeManager.toastManager.success('Product added successfully', data.message, "", true);
                } else if (data.success && data.code == 104) {
                    window.storeManager.toastManager.info('Product updated successfully', data.message, "", true);
                } else {
                    window.storeManager.toastManager.error("Product add failed", data.message, "Please try again.", false);
                }
            })
            .catch(error => {
                console.error('Error adding product:', error);
                window.storeManager.toastManager.error("Failed to add product", error.message, "Please try again.", false);
            });
    }


    deleteProduct(ean) {
        const form = document.getElementById('deleteProductForm');
        const formData = new FormData(form);

        fetch(this.page_url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json', // Ensure this header is correctly set
                'X-CSRFToken': this.csrftoken, // Pass CSRF token here
                'cmd': 'add' // Custom command header
            },
            body: JSON.stringify({ product_ean: formData.get('product_ean') })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                //location.reload();
                window.storeManager.toastManager.success(`Product ${ean} deleted successfully`, data.message, "", true);
                
            } else {
                window.storeManager.toastManager.error("Failed to deleted product", data.message, "Please try again.", false);
            }
        })
        .catch(error => {
            console.error('Error deleting product:', error);
            window.storeManager.toastManager.error("Failed to deleted product", error, "Please try again.", false);
        });
    }

    submitEditForm() {
        const form = document.getElementById('editProductForm');
        const formData = new FormData(form);

        fetch(this.page_url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': this.csrftoken,
                'cmd': 'edit'
            },
            body: JSON.stringify({
                product_ean: formData.get('product_ean'),
                product_name: formData.get('product_name'),
                resell_price: formData.get('resell_price'),
                discount: parseFloat(formData.get('discount')/100)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                //location.reload();
                window.storeManager.toastManager.success(`Product updated successfully`, data.message, "", true); 
            } else {
                window.storeManager.toastManager.error("Failed to deleted product", data.message, "Please try again.", false);
            }
        })
        .catch(error => {
            console.error('Error updating product:', error);
            window.storeManager.toastManager.error("Failed to update product", error, "Please try again.", false);
        });
    }

    openEditModal(ean, name, resellPrice, dicount) {
        console.log("Opening edit modal for product:", ean);
        document.getElementById('editProductModalLabel').value = `Edit Product ${ean}`;
        document.getElementById('modal_ean').value = ean;
        document.getElementById('modal_name').value = name;
        document.getElementById('modal_resellprice').value = resellPrice;
        document.getElementById('modal_discount').value = dicount * 100;
        // Use Bootstrap's modal API to show the modal
        const modal = new bootstrap.Modal('#editProductModal');
        modal.show();

    }
    
    closeModal() {
        // Use Bootstrap's modal API to hide the modal
        const modal = bootstrap.Modal.getInstance('#editProductModal');
        if (modal) {
            modal.hide();
        }
    }


}

