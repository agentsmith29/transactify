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
            if (data.success && data.code == 103 ) {
                //location.reload();
                window.toastManager.success('Product added successfully', data.message, "", true);
            } 
            else if (data.success && data.code == 104) {
                window.toastManager.info('Product updated successfully', data.message, "", true);
            }
            else {
                //window.toastManager.error(title, message, submessage)
                window.toastManager.error("Product add failed", data.message, "Please try again.", false);
            }
        })
        .catch(error => {
            console.error('Error adding product:', error);
            // Toast message with error
            window.toastManager.error("Failed to add product", error, "Please try again.", false);
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
                window.toastManager.success(`Product ${ean} deleted successfully`, data.message, "", true);
                
            } else {
                window.toastManager.error("Failed to deleted product", data.message, "Please try again.", false);
            }
        })
        .catch(error => {
            console.error('Error deleting product:', error);
            window.toastManager.error("Failed to deleted product", error, "Please try again.", false);
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
                window.toastManager.success(`Product updated successfully`, data.message, "", true); 
            } else {
                window.toastManager.error("Failed to deleted product", data.message, "Please try again.", false);
            }
        })
        .catch(error => {
            console.error('Error updating product:', error);
            window.toastManager.error("Failed to update product", error, "Please try again.", false);
        });
    }


    openEditModal(ean, name, resellPrice) {
        document.getElementById('modal_ean').value = ean;
        document.getElementById('modal_name').value = name;
        document.getElementById('modal_resellprice').value = resellPrice;
        //$('#editProductModal').modal('show');
        const editProductModal = document.getElementById('editProductModal');
        // show modal
        editProductModal.modal = "show";
        

    }
    
    closeEditModal() {
        const editProductModal = document.getElementById('editProductModal');
        editProductModal.hidden = true;
    }

}
