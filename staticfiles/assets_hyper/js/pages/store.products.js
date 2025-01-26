class ManageProducts {
    constructor(page_url) {
        this.page_url = page_url;
        $(document).ready(() => {
            this.initSocket();
            this.initDataTables();
        });
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
                    window.storeManager.toastManager.info("Barcode recieved", `New scanned barcode: ${data.barcode}`, "", false);
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
        const csrftoken = document.cookie.match(/csrftoken=([^;]+)/)[1];
    
        fetch(this.page_url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json', // Ensure this header is set correctly
                'X-CSRFToken': csrftoken, //formData.get('csrfmiddlewaretoken'), // Extract CSRF token
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
        fetch(this.page_url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json', // Ensure this header is correctly set
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'), // Pass CSRF token here
                'cmd': 'add' // Custom command header
            },
            body: JSON.stringify({ product_ean: ean })
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
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
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

