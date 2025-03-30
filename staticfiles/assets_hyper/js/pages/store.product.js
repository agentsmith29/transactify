class ManageProduct {
    constructor(page_url, config) {
        this.page_url = page_url;
        this.config = config;


        App.ready.then(() => {
            console.log("🚀 Initializing Product Manager...");
            // modalId, titleId, bodyId, submitButtonId, closeButtonId
            this.editModalManager = new App.classes.ModalDialogManager(
                'editProductModal',
                '#editProductModalHeader', '#editProductModalBody', 
                '#editProductFormSubmit', '#editProductFormClose'
            );

            this.imageUploadModalManager = new App.classes.ModalDialogManager(
                'imageUploadModal',
                '#imageUploadModalHeader', '#imageUploadModalBody', 
                '#imageUploadModalSubmit', '#imageUploadModalClose'
            );
            this.requestHandler = App.requestHandler;
            this.actionTrigger = App.actionTrigger;

            this.csrftoken = document.cookie.match(/csrftoken=([^;]+)/)[1];
           
    
            // Bind event listeners
            this.initActions();
        });
    }

    initActions(){  
        // bind modal_image_upload_btn
        // this.actionTrigger.attachButton("update_image", "modal_image_upload_btn", this.page_url);

        this.requestHandler.attachFormAndButton(
            "update_product", // Command type
            "editProductModalForm", // Form ID
            "editProductFormSubmit", // Submit button ID
            this.page_url
        );

        this.init_upload_image_modal();


  
    }

    init_upload_image_modal() {
        const sourceSelect = document.getElementById('image_source');
        const urlGroup = document.getElementById('url_input_group');
        const fileGroup = document.getElementById('file_input_group');
        const preview = document.getElementById('image_preview');
        const urlInput = document.getElementById('modal_image_url');
        const fileInput = document.getElementById('modal_image_file');
    
        // Set up event listeners once
        if (!this._upload_modal_events_initialized) {
            sourceSelect.addEventListener('change', () => {
                const source = sourceSelect.value;
                urlGroup.classList.toggle('d-none', source !== 'url');
                fileGroup.classList.toggle('d-none', source !== 'upload' && source !== 'file');
    
                if (source === 'openfoodfacts') {
                    preview.src = '#';
                    preview.style.display = 'none';
                }
            });
    
            urlInput.addEventListener('input', () => {
                const url = urlInput.value.trim();
                if (url) {
                    preview.src = url;
                    preview.style.display = 'block';
                }
            });
    
            fileInput.addEventListener('change', () => {
                const file = fileInput.files[0];
                if (file) {
                    const objectUrl = URL.createObjectURL(file);
                    preview.src = objectUrl;
                    preview.style.display = 'block';
                }
            });
    
            this._upload_modal_events_initialized = true;
        }
    
        // Reset modal fields when shown
        const modalElement = document.getElementById('imageUploadModal');
        modalElement.addEventListener('show.bs.modal', () => {
            urlInput.value = '';
            fileInput.value = '';
            preview.src = '#';
            preview.style.display = 'none';
            urlGroup.classList.add('d-none');
            fileGroup.classList.add('d-none');
    
            // 👇 Force trigger content visibility based on prefilled dropdown value
            const source = sourceSelect.value;
            sourceSelect.dispatchEvent(new Event('change'));
        });
    
        // Bind form submission
        this.requestHandler.attachFormAndButton(
            "update_from_url",
            "url_upload_form",
            "modal_image_upload_btn",
            this.page_url
        );
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

