class ManageProducts {
    constructor(pageName, page_url) {
        this.page_url = page_url
        this.pageName = pageName;
        this.socket = new WebSocket(`ws://${window.location.host}/tcon/page/${pageName}/`);
        this.initSocket();
    }

    initSocket() {
        this.socket.onopen = () => {
            console.log("WebSocket connection established for page:", this.pageName);
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

                    const toastMessage = document.getElementById('toastMessage');
                    toastMessage.textContent = `New scanned barcode: ${data.barcode}`;
                    const toast = new bootstrap.Toast(document.getElementById('barcodeToast'));
                    toast.show();
                }
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

    submitProductForm() {
        const form = document.getElementById('addProductForm');
        const formData = new FormData(form);

        // print form data
        fetch(this.page_url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                'cmd': 'add'
            },
            body: JSON.stringify({
                product_ean: formData.get('product_ean'),
                product_name: formData.get('product_name'),
                resell_price: formData.get('resell_price')
            })
        }
    )
        .then(console.log("Form data sent to " + this.page_url))
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                //location.reload();
                window.toastManager.successAndReload('Product added successfully', data.message, "");
            } else {
                //window.toastManager.error(title, message, submessage)
                window.toastManager.error("Product add failed", data.message, "Please try again.");
            }
        })
        .catch(error => {
            console.error('Error adding product:', error);
            // Toast message with error
            window.toastManager.error("Failed to add product", error, "Please try again.");
        });
    }

    deleteProduct(ean) {
        fetch(this.page_url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'cmd': 'delete'
            },
            body: JSON.stringify({ product_ean: ean })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                //location.reload();
                window.toastManager.successAndReload(`Product ${ean} deleted successfully`, data.message, "");
                
            } else {
                window.toastManager.error("Failed to deleted product", data.message, "Please try again.");
            }
        })
        .catch(error => {
            console.error('Error deleting product:', error);
            window.toastManager.error("Failed to deleted product", error, "Please try again.");
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
                resell_price: formData.get('resell_price')
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                //location.reload();
                window.toastManager.successAndReload(`Product updated successfully`, data.message, ""); 
            } else {
                window.toastManager.error("Failed to deleted product", data.message, "Please try again.");
            }
        })
        .catch(error => {
            console.error('Error updating product:', error);
            window.toastManager.error("Failed to update product", error, "Please try again.");
        });
    }


}
