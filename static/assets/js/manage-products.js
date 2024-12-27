class ManageProducts {
    constructor(pageName) {
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

        fetch('/manage_products/', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
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
                showToast('Product added successfully.', true);
                location.reload();
            } else {
                //showErrorToast(title, message, submessage)
                showErrorToast("Product add failed", data.message, "Please try again.");
            }
        })
        .catch(error => {
            console.error('Error adding product:', error);
            // Toast message with error
            showErrorToast("Failed to add product", error, "Please try again.");
        });
    }

    deleteProduct(ean) {
        fetch('/manage_products/', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ delete_ean: ean })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(`Product with EAN ${ean} deleted successfully.`, true);
                location.reload();
            } else {
                showErrorToast("Failed to deleted product", data.message, "Please try again.");
            }
        })
        .catch(error => {
            console.error('Error deleting product:', error);
            showErrorToast("Failed to deleted product", error, "Please try again.");
        });
    }

    submitEditForm() {
        const form = document.getElementById('editProductForm');
        const formData = new FormData(form);

        fetch('/manage_products/', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
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
                this.showToast('Product updated successfully.', true);
                location.reload();
            } else {
                showErrorToast("Failed to deleted product", data.message, "Please try again.");
            }
        })
        .catch(error => {
            console.error('Error updating product:', error);
            showErrorToast("Failed to update product", error, "Please try again.");
        });
    }


}
