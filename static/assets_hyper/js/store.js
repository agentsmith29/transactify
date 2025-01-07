class ToastManager {
    constructor(imgSrcBase) {
        this.imgSrcBase = imgSrcBase;
    }

    #displayToast(title, message, submessage, iconFileName, iconClass) {
        const toastLiveExample = document.getElementById("infoToast");
        const toastTitle = document.getElementById('toastTitle');
        const toastMessage = document.getElementById('toastMessage');
        const toastSubMessage = document.getElementById('toastSubMessage');
        const toastImage = document.getElementById('toastIcon');

        toastTitle.textContent = title;
        toastMessage.textContent = message;
        toastSubMessage.textContent = submessage;

        toastImage.src = `${this.imgSrcBase}${iconFileName}`;
        toastImage.className = `${iconClass} rounded me-2`;

        const toast = new bootstrap.Toast(toastLiveExample);
        toast.show();
    }

    _display(type, title, message, submessage) {
        const toastTypeMap = {
            error: { icon: 'x-circle-fill.svg', class: 'toastImageError' },
            success: { icon: 'check-circle-fill.svg', class: 'toastImageSuccess' },
            info: { icon: 'info-circle-fill.svg', class: 'toastImageInfo' },
            warning: { icon: 'exclamation-circle-fill.svg', class: 'toastImageWarning' },
        };

        const { icon, class: iconClass } = toastTypeMap[type] || {};
        if (!icon || !iconClass) {
            console.error(`Invalid toast type: ${type}`);
            return;
        }

        this.#displayToast(title, message, submessage, icon, iconClass);
    }

    error(title, message, submessage) {
        this._display('error', title, message, submessage);
    }

    success(title, message, submessage) {
        this._display('success', title, message, submessage);
    }

    info(title, message, submessage) {
        this._display('info', title, message, submessage);
    }

    warning(title, message, submessage) {
        this._display('warning', title, message, submessage);
    }
}

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

