class ModalDialogManager {
    constructor(modalId) {
        this.modalElement = document.getElementById(modalId);
        this.modalTitle = this.modalElement.querySelector('#confirmationModalTitle');
        this.modalBody = this.modalElement.querySelector('#confirmationModalBody');
        this.modalAcceptButton = this.modalElement.querySelector('#confirmationModalAccept');
        this.callback = null;

        this.modalAcceptButton.addEventListener('click', () => {
            if (this.callback) {
                this.callback();
            }
            this.closeModal();
        });
    }

    display(title, body, acceptText, callback) {
        this.modalTitle.textContent = title;
        this.modalBody.textContent = body;
        this.modalAcceptButton.textContent = acceptText;
        this.callback = callback;

        const modalInstance = new bootstrap.Modal(this.modalElement);
        modalInstance.show();
    }

    closeModal() {
        const modalInstance = bootstrap.Modal.getInstance(this.modalElement);
        if (modalInstance) {
            modalInstance.hide();
        }
    }
}
