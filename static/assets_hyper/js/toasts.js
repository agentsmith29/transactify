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

    error(title, message, submessage, reload) {
        this._display('error', title, message, submessage);
        if (reload) {
            this.#storeForReload(title, message, submessage, 'error');
          }
    }

    success(title, message, submessage, reload) {
        this._display('success', title, message, submessage);
        if (reload) {
            this.#storeForReload(title, message, submessage, 'success');
          }
    }

    info(title, message, submessage, reload) {
        this._display('info', title, message, submessage);
        if (reload) {
            this.#storeForReload(title, message, submessage, 'info');
          }
    }

    warning(title, message, submessage, reload) {
        this._display('warning', title, message, submessage);
        if (reload) {
            this.#storeForReload(title, message, submessage, 'warning');
          }
    }

      // Function to save toast data and reload
  #storeForReload(title, message, submessage, type) {
    // Save toast data to localStorage
    localStorage.setItem('toastData', JSON.stringify({
        title: title,
        message: message,
        submessage: submessage,
        type: type
    }));
    // Reload the page
    location.reload();
  }
  
}

// Function to check and display toast after reload
function displayToastAfterReload() {
    // Get toast data from localStorage
    const toastData = JSON.parse(localStorage.getItem('toastData'));

    if (toastData) {
        // Display the toast
        window.storeManager.toastManager._display(toastData.type, toastData.title, toastData.message, toastData.submessage);

        // Clear the stored toast data
        localStorage.removeItem('toastData');
    }


}