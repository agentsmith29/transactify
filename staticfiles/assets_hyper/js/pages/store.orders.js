class ManageOrders {
    constructor(page_url) {
        this.page_url = page_url
        this.initSocket();
        this.initDataTables();
        this.initPurchaseModal();
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
        const dataTable = $("#orders-datatable").DataTable({
            language: {
                paginate: { previous: "<i class='mdi mdi-chevron-left'>", next: "<i class='mdi mdi-chevron-right'>" },
                info: "Showing products _START_ to _END_ of _TOTAL_",
                lengthMenu: 'Display <select class="form-select form-select-sm ms-1 me-1"><option value="10">10</option><option value="20">20</option><option value="-1">All</option></select> products',
            },
            columnDefs: [{ targets: -1, className: "dt-body-right" }],
            pageLength: 10,
            order: [[1, "asc"]],
            dom: 'lrtip', // Disable default search bar
            drawCallback: function () {
                $(".dataTables_paginate > .pagination").addClass("pagination-rounded"),
                    $("#orders-datatable_length label").addClass("form-label");
            },
        });
    
        // Custom Search Bar Integration
        const searchInput = document.getElementById("search-input");
        if (searchInput) {
            searchInput.addEventListener("input", function () {
                dataTable.search(this.value).draw();
            });
        }
    
        // Move lengthMenu next to the custom search bar
        const lengthMenu = document.getElementById("orders-datatable_length");
        const searchBarContainer = document.querySelector(".row.gy-2");
        if (searchBarContainer && lengthMenu) {
            lengthMenu.classList.add("ms-3"); // Add margin to separate from search bar
            searchBarContainer.appendChild(lengthMenu);
        }
    }

    initPurchaseModal() {
        const purchaseForm = document.getElementById("purchaseForm");
        if (purchaseForm) {
            purchaseForm.addEventListener("submit", (event) => {
                event.preventDefault();
                const formData = new FormData(purchaseForm);
                
                fetch(this.page_url, {
                    method: "POST",
                    body: formData,
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.storeManager.toastManager.success("Purchase Added", "The new purchase has been recorded successfully.", "", false);
                        $("#addPurchaseModal").modal("hide");
                        location.reload();
                    } else {
                        window.storeManager.toastManager.error("Error", "Failed to add purchase.", "", false);
                    }
                })
                .catch(error => console.error("Error adding purchase:", error));
            });
        }
    }
    
    
}

