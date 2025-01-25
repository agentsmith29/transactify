class ChartManager {
    constructor({ revenueData, costsData, profitsData, categories, chartElementId, colors }) {
        this.revenueData = revenueData || [];
        this.costsData = costsData || [];
        this.profitsData = profitsData || [];
        this.categories = categories || [];
        this.chartElementId = chartElementId || 'chart';
        this.colors = colors || ['#4caf50', '#f44336', '#2196f3'];
        this.initChart();
    }

    initChart() {
        const options = {
            chart: {
                type: 'area',
                height: 256,
            },
            series: [
                {
                    name: 'Revenue',
                    data: this.revenueData,
                },
                {
                    name: 'Costs',
                    data: this.costsData,
                },
                {
                    name: 'Profits',
                    data: this.profitsData,
                },
            ],
            xaxis: {
                categories: this.categories,
            },
            colors: this.colors,
        };

        const chart = new ApexCharts(document.querySelector(`#${this.chartElementId}`), options);
        chart.render();
    }
}

