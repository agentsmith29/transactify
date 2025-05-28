class ManageCustomer {
    constructor(page_url, config, requestHandler, actionTrigger) {
        this.page_url = page_url;
        this.config = config;


        App.ready.then(() => {
            console.log("🚀 Initializing Customer Manager...");
            this.requestHandler = App.requestHandler;
            this.actionTrigger = App.actionTrigger;

            this.csrftoken = document.cookie.match(/csrftoken=([^;]+)/)[1];
            this.customerCardNumber = this.config.customerCardNumber;
            this.customerDetailUrl = this.config.customerDetailUrl;

            this.editCustomerModalManager = new App.classes.ModalDialogManager(
                'editCustomerModal',
                '#editCustomerModalHeader', '#editCustomerModal', 
                '#editCustomerModalSubmit', '#editCustomerModalClose'
            );
    
            // Initialize the WebSocket connection
            //this.webSocketHandler = window.storeManager.webSocketHandler;
    
            // Bind event listeners
            this.initActions();
            this.initSimpleMDE();
        });
    }

    initActions() {
        
        const self = this;
        const updateForm = document.getElementById('updateBalanceForm');

        if (updateForm) {
            updateForm.addEventListener('submit', function (event) {
                event.preventDefault(); // Prevent form submission

                const depositAmount = document.getElementById('depositAmount').value;

                // Make a POST request
                fetch(self.customerDetailUrl, {
                    method: 'POST',
                    mode: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFTOKEN': self.csrftoken,
                        'X-Requested-With': 'XMLHttpRequest', // Identify as AJAX request
                        'cmd': 'deposit'
                    },
                    body: JSON.stringify({
                        deposit_amount: depositAmount,
                    }),
                })
                    .then((response) => {
                        if (response.ok) {
                            console.log('Request successful');
                            window.storeManager.toastManager.info(
                                'Submitted balance',
                                'Balance has been added.',
                                '',
                                true
                            );
                            return response.json();
                        } else {
                            console.error('Request failed:', response.status);
                            window.storeManager.toastManager.error(
                                'Error',
                                'An error occurred while updating balance.',
                                'error',
                                false
                            );
                            throw new Error('Error occurred. Please try again.');
                        }
                    })
                    .then((data) => {
                        console.log('Response data:', data);
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                        window.storeManager.toastManager.error(
                            'Error',
                            'An error occurred while updating balance.',
                            'error',
                            false
                        );
                    })
                    .finally(() => {
                        console.log('Request completed');
                    });
            });
        }

        $("#sendMessageButton").click(function () {
            self.sendCustomerEmail();
        });

        this.requestHandler.attachFormAndButton(
            "update",                // Command
            "editCustomerForm",      // Form ID
            "editCustomerModalSubmit", // Submit button ID
            this.page_url    // URL
        );
        
        this.requestHandler.attachFormAndButton(
            "update_config",                // Command
            "editCustomerConfigForm",      // Form ID
            "editCustomerConfigFormSubmit", // Submit button ID
            this.page_url    // URL
        );

        this.requestHandler.attachFormAndButton(
            "deposit", // Command type
            "updateBalanceForm", // Form ID
            "updateBalanceButton", // Submit button ID
            this.page_url
        );


        // Connect the buttons
        this.actionTrigger.attachButton("test_send_mail_email_on_deposit", "send_mail_email_on_deposit", this.page_url);
        this.actionTrigger.attachButton("test_send_mail_email_on_purchase", "send_mail_email_on_purchase", this.page_url);
  

    };

    handleCardNumber(cardNumber) {
        this.cardNumber = cardNumber;
        const existingCustomer = document.querySelector(`[data-card-number="${cardNumber}"]`);
        if (existingCustomer) {
            const redirectUrl = existingCustomer.getAttribute("data-url");
            if (redirectUrl) {
                window.location.href = redirectUrl;
                return;
            }
        }
        const cardNumberInput = document.getElementById("modal_card_number");
        cardNumberInput.style.color = "red";
        cardNumberInput.style.fontWeight = "bold";
        cardNumberInput.value = "New Card Number";
        const modalElementHeader = document.getElementById("editCustomerModalHeader");
        modalElementHeader.innerText = "New Customer Card";

        const modalElement = document.getElementById("editCustomerModal");
        const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
        document.getElementById("modal_card_number").value = cardNumber;
        //document.getElementById("card_number_container").style.display = "block";
        modal.show();
    }

    initWebSocketHandlers() {
        this.webSocketHandler.onopen = () => console.log("WebSocket connection established");

        this.webSocketHandler.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.card_number) {
                    this.handleCardNumber(data.card_number);
                }
                if (data.message) {
                    this.toastManager.info("Card detected", data.message, "", false);
                }
            } catch (error) {
                console.error("Error parsing WebSocket message:", error);
            }
        };

        this.webSocketHandler.onclose = () => {
            console.log("WebSocket connection closed");
            this.toastManager.warning("WebSocket connection closed", "WebSocket was reset.", "", false);
        };

        this.webSocketHandler.onerror = (error) => {
            console.error("WebSocket error:", error);
            this.toastManager.error("WebSocket error", "WebSocket encountered an error.", "", false);
        };
    }

    initSimpleMDE() {
        this.simplemde = new SimpleMDE({ 
            element: document.getElementById("simplemde1"), 
            spellChecker: false, 
            placeholder: "Write something..", 
            tabSize: 2, 
            status: false, 
            autosave: { enabled: false }
        });
    }

    parseBool(value) {
        return  value === "True" || value === "true" || value === "on" || value === 1 || value === "1";
    }

    openEditModal(card_number, first_name, last_name, email, auto_deposit) {
        document.getElementById("modal_card_number").value = card_number;
        document.getElementById("modal_first_name").value = first_name;
        document.getElementById("modal_last_name").value = last_name;
        document.getElementById("modal_email").value = email;
        // Set auto_deposit checkbox based on customer.config.auto_deposit
        document.getElementById("modal_auto_deposit").checked = this.parseBool(auto_deposit);

        // Open the modal
        const modal = new bootstrap.Modal('#editCustomerModal');
        modal.show();
    }

    
    submitEditForm() {
        // cmd, content, elementId, url
        const form = document.getElementById("editCustomerForm");
        //const formData = new FormData(form);
        // this.requestHandler.sendRequest(
        //     "update",
        //     form,
        //     this.page_url 
        // );
        
        // const form = document.getElementById("editCustomerForm");
        // const formData = new FormData(form);
      

        // fetch(this.page_url, {
        //     method: "POST",
        //     headers: {
        //         "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
        //         'cmd': 'update' // Pass additional command header
        //     },
        //     body: JSON.stringify({
        //         first_name: formData.get('first_name'),
        //         last_name: formData.get('last_name'),
        //         email: formData.get('email'),
        //         config: {
        //             auto_deposit: this.parseBool(formData.get('auto_deposit'))
        //         }
        //     })
        // })
        // .then(response => response.json())
        // .then(data => {
        //     if (data.success) {
        //         window.storeManager.toastManager.info(
        //             "Success",
        //             "Customer updated successfully.",
        //             "",
        //             true
        //         );
        //         location.reload();
        //     } else {
        //         window.storeManager.toastManager.error(
        //             "Error",
        //             "Error updating customer: " + data.error,
        //             "error",
        //             false
        //         );
        //     }
        // })
        // .catch(error => console.error("Error:", error));
    }

    
    sendCustomerEmail() {
        const subject = document.getElementById('mailsubject').value;
        const markdownMessage = this.simplemde.value();
        const htmlMessage = this.simplemde.options.previewRender(markdownMessage); // Convert Markdown to HTML
        
        
        if (!subject || !htmlMessage) {
            window.storeManager.toastManager.error("Error", "Subject and message cannot be empty.", "error", false);
            return;
        }
        
        fetch(this.customerDetailUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrftoken,
                'cmd': 'send_email'
            },
            body: JSON.stringify({
                subject: subject,
                html_message: htmlMessage
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.storeManager.toastManager.info("Success", "Email sent successfully.", "", true);
            } else {
                window.storeManager.toastManager.error("Error", "Error sending email: " + data.error, "error", false);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            window.storeManager.toastManager.error("Error", "An error occurred while sending the email.", "error", false);
        });
    }

    deleteDepositEntry(deposit_id) {
        this.requestHandler.sendRequest(
            "delete_deposit",
            {'deposit_id': deposit_id},
            this.page_url
        );

    }
}

// CustomerViewChart class
class CustomerViewChart {
    constructor({ balanceData, depositData, purchasesData, categories, chartElementId, colors }) {
        this.balanceData = balanceData || [];
        this.depositData = depositData || [];
        this.purchasesData = purchasesData || [];
        this.categories = categories || [];
        this.chartElementId = chartElementId || 'chart';
        this.colors = colors || ['#4caf50', '#f44336', '#2196f3'];
        this.initChart();
    }

    initChart() {
        const options = {
            chart: {
                height: 256,
                type: 'area',
                zoom: {
                    autoScaleYaxis: true,
                    enabled: true,
                },
            },
            series: [
                {
                    name: 'Balance',
                    data: this.balanceData,
                    type: 'area',
                },
                {
                    name: 'Deposits',
                    data: this.depositData,
                    type: 'column',
                },
                {
                    name: 'Purchases',
                    data: this.purchasesData,
                    type: 'column',
                },
            ],
            dataLabels: {
                enabled: false,
            },
            tooltip: {
                x: {
                    format: 'dd MMM yyyy',
                },
            },
            xaxis: {
                type: 'datetime',
                categories: this.categories,
                tickAmount: 6,
            },
            fill: {
                type: 'gradient',
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.7,
                    opacityTo: 0.9,
                    stops: [0, 100],
                },
            },
            colors: this.colors,
        };
    
        const chart = new ApexCharts(
            document.querySelector(`#${this.chartElementId}`),
            options
        );
        chart.render();
    
        // Helper function to reset active class for buttons
        const resetCssClasses = (activeEl) => {
            const els = document.querySelectorAll('.time-filter button');
            els.forEach((el) => {
                el.classList.remove('active');
            });
            activeEl.target.classList.add('active');
        };
    }
}

