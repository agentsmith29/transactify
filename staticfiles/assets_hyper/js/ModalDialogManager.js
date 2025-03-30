export default class ModalDialogManager {
    constructor(modalId, titleId, bodyId, submitButtonId, closeButtonId) {
        this.modalElement = document.getElementById(modalId);
        this.modalTitle = this.modalElement.querySelector(titleId);
        this.modalBody = this.modalElement.querySelector(bodyId);
        this.modalAcceptButton = this.modalElement.querySelector(submitButtonId);
        this.modalCloseButton = this.modalElement.querySelector(closeButtonId);
        this.callback = null;

        this.modalAcceptButton.addEventListener('click', () => {
            if (this.callback) {
                this.callback();
            }
            this.closeModal();
        });

        this.modalCloseButton.addEventListener('click', () => {
            this.closeModal();
        });
    }
    
    display(content_dict, callback) {
        console.log("Displaying modal...");
    
        // Set all fields using the content_dict
        for (const [fieldId, value] of Object.entries(content_dict)) {
            const field = this.modalElement.querySelector(`#${fieldId}`);
            if (field) {
                if (field.tagName === 'INPUT' || field.tagName === 'TEXTAREA' || field.tagName === 'SELECT') {
                    field.value = value;
                } else {
                    field.textContent = value;
                }
            } else {
                console.warn(`Field with ID "${fieldId}" not found in modal.`);
            }
        }
    
        this.callback = callback;
    
        const modalInstance = new bootstrap.Modal(this.modalElement);
        modalInstance.show();
    
        console.log("Modal displayed!");
    }
    

    closeModal() {
        const modalInstance = bootstrap.Modal.getInstance(this.modalElement);
        if (modalInstance) {
            modalInstance.hide();
        }
        console.log("Modal closed!");
    }
}
