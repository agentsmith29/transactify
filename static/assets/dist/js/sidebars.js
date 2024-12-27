/* global bootstrap: false */
(() => {
  'use strict'
  const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.forEach(tooltipTriggerEl => {
    new bootstrap.Tooltip(tooltipTriggerEl)
  })
})()


class ToastManager {
  constructor(imgSrcBase) {
      this.imgSrcBase = imgSrcBase; // Base path for images
      //this.displaySuccessAfterReload()
  }

  // Private method to display a toast
  #displayToast(title, message, submessage, iconFileName, iconClass) {
      const toastLiveExample = document.getElementById("infoToast");
      const toastTitle = document.getElementById('toastTitle');
      const toastMessage = document.getElementById('toastMessage');
      const toastSubMessage = document.getElementById('toastSubMessage');
      const toastImage = document.getElementById('toastIcon');

      // Set content
      toastTitle.textContent = title;
      toastMessage.textContent = message;
      toastSubMessage.textContent = submessage;

      // Set icon
      toastImage.src = `${this.imgSrcBase}${iconFileName}`;
      toastImage.className = `${iconClass} rounded me-2`;

      // Show toast
      const toast = new bootstrap.Toast(toastLiveExample);
      toast.show();
  }

  _display(type, title, message, submessage){
    if (type == 'error') {
      this.error(title, message, submessage);
    }
    else if (type == 'success') {
      this.success(title, message, submessage);
    }
    else if (type == 'info') {
      this.info(title, message, submessage);
    }
    else if (type == 'warning') {
      this.warning(title, message, submessage);
    }
  }

  // Public method for error toast
  error(title, message, submessage, reload) {
      this.#displayToast(title, message, submessage, 'x-circle-fill.svg', 'toastImageError');
      if (reload) {
        this.#storeForReload(title, message, submessage, 'error');
      }
  }

  // Public method for success toast
  success(title, message, submessage, reload) {
      this.#displayToast(title, message, submessage, 'check-circle-fill.svg', 'toastImageSuccess');
      if (reload) {
        this.#storeForReload(title, message, submessage, 'success');
      }
  }

  // Public method for info toast
  info(title, message, submessage, reload) {
      this.#displayToast(title, message, submessage, 'info-circle-fill.svg', 'toastImageInfo');
      if (reload) {
        this.#storeForReload(title, message, submessage, 'info');
      }
  }

  // Public method for warning toast
  warning(title, message, submessage, reload) {
      this.#displayToast(title, message, submessage, 'exclamation-circle-fill.svg', 'toastImageWarning');
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
        toastManager._display(toastData.type, toastData.title, toastData.message, toastData.submessage);

        // Clear the stored toast data
        localStorage.removeItem('toastData');
    }


}



