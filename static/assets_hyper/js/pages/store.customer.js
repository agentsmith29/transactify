!(function ($) {
    "use strict";

    // CustomerView class
    function CustomerView(config) {
        // Initialize components with configuration
        this.toastManager = window.StoreManager.toastManager;
        this.modalManager = window.StoreManager.modalManager;

        this.csrftoken = config.csrftoken;
        this.customerCardNumber = config.customerCardNumber;
        this.customerDetailUrl = config.customerDetailUrl;

        // Initialize the WebSocket connection
        this.webSocketHandler = window.StoreManager.webSocketHandler;

        // Bind event listeners
        this.initActions();
    }

    CustomerView.prototype.initActions = function () {
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
                    },
                    body: JSON.stringify({
                        deposit_amount: depositAmount,
                    }),
                })
                    .then((response) => {
                        if (response.ok) {
                            console.log('Request successful');
                            window.toastManager.info(
                                'Submitted balance',
                                'Balance has been added.',
                                '',
                                true
                            );
                            return response.json();
                        } else {
                            console.error('Request failed:', response.status);
                            window.toastManager.error(
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
                        window.toastManager.error(
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
    };

    // Export CustomerView
    window.CustomerView = CustomerView;

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
        
            // Event listeners for time range buttons
            document.querySelector('#one_month').addEventListener('click', (e) => {
                resetCssClasses(e);
                const now = new Date().getTime();
                const oneMonthAgo = now - 30 * 24 * 60 * 60 * 1000;
                chart.zoomX(oneMonthAgo, now);
            });
        
            document.querySelector('#six_months').addEventListener('click', (e) => {
                resetCssClasses(e);
                const now = new Date().getTime();
                const sixMonthsAgo = now - 6 * 30 * 24 * 60 * 60 * 1000;
                chart.zoomX(sixMonthsAgo, now);
            });
        
            document.querySelector('#one_year').addEventListener('click', (e) => {
                resetCssClasses(e);
                const now = new Date().getTime();
                const oneYearAgo = now - 12 * 30 * 24 * 60 * 60 * 1000;
                chart.zoomX(oneYearAgo, now);
            });
        
            document.querySelector('#all').addEventListener('click', (e) => {
                resetCssClasses(e);
                chart.resetZoom();
            });
        
            // Add a slider for interactive zooming
            const slider = document.getElementById('zoom-slider');
            slider.addEventListener('input', (e) => {
                const value = e.target.value;
                const now = new Date().getTime();
                const range = (value / 100) * (now - this.categories[0]);
                chart.zoomX(now - range, now);
            });
        }
        
    }

    // Export CustomerViewChart
    window.CustomerView = CustomerView;
    window.CustomerViewChart = CustomerViewChart;
})(window.jQuery);