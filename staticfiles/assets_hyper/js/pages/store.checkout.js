class Basket {
    constructor(containerId, summaryTable) {
        this.items = [];
        this.total = 0;
        this.containerId = containerId;
        this.summaryTable = summaryTable;
    }

    addItem(ean, name, price, quantity = 1) {
        ean = Number(ean); // Ensure ID is a number
        let existingItem = this.items.find(item => item.ean === ean);
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.items.push({ ean, name, price, quantity });
        }
        this.updateTotal();
        this.renderBasket();
        console.log(`Added ${name} (${quantity}) to  cart.`)
    }

    removeItem(ean) {
        ean = Number(ean);
        this.items = this.items.filter(item => item.ean !== ean);
        this.updateTotal();
        this.renderBasket();
    }

    updateQuantity(ean, quantity) {
        ean = Number(ean);
        let item = this.items.find(item => item.ean === ean);
        if (item) {
            item.quantity = Math.max(1, quantity); // Ensure quantity is at least 1
        }
        this.updateTotal();
        this.renderBasket();
    }

    updateTotal() {
        this.total = this.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
    }

    clearBasket() {
        this.items = [];
        this.total = 0;
        this.renderBasket();
    }

    getBasket() {
        return this.items;
    }

    getTotal() {
        return this.total.toFixed(2);
    }

    renderBasket() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        // **Clear previous HTML content before rendering new content**
        container.innerHTML = '';

        if (this.items.length === 0) {
            container.innerHTML = '<p>Your cart is empty.</p>';
            document.getElementById("basket-total").textContent = "0.00";
            return;
        }

        const table = document.createElement('table');
        table.classList.add('table', 'table-centered', 'w-100', 'dt-responsive', 'nowrap');

        table.innerHTML = `
            <thead class="table-light">
                <tr>
                    <th>Product</th>
                    <th>Price</th>
                    <th>Quantity</th>
                    <th>Total</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody id="` + this.containerId +`">
                ${this.items.map(item => `
                    <tr id="basket-item-${item.ean}">
                        <td>${item.name}</td>
                        <td>€${item.price.toFixed(2)}</td>
                        <td>
                            <button class="btn btn-sm btn-light" onclick="window.manageCustomerCheckout.basket.updateQuantity(${item.ean}, ${item.quantity - 1})">-</button>
                            <span id="quantity-${item.ean}">${item.quantity}</span>
                            <button class="btn btn-sm btn-light" onclick="window.manageCustomerCheckout.basket.updateQuantity(${item.ean}, ${item.quantity + 1})">+</button>
                        </td>
                        <td>€<span id="total-${item.ean}">${(item.price * item.quantity).toFixed(2)}</span></td>
                        <td><button class="btn btn-sm btn-danger" onclick="window.manageCustomerCheckout.basket.removeItem(${item.ean})">Remove</button></td>
                    </tr>
                `).join('')}
            </tbody>
        `;

        container.appendChild(table);

        // Update the total amount
        document.getElementById("basket-total").textContent = this.getTotal();
        this.renderSummaryTable()
    }

    renderSummaryTable() {
        const container = document.getElementById(this.summaryTable);
        if (!container) return;

        // **Clear previous HTML content before rendering new content**
        container.innerHTML = '';

        if (this.items.length === 0) {
            container.innerHTML = '<p>Your cart is empty.</p>';
            document.getElementById("basket-total").textContent = "0.00";
            return;
        }

        const table = document.createElement('table');
        table.classList.add('table', 'table-centered', 'w-100', 'dt-responsive', 'nowrap');

        table.innerHTML = `
            <tbody id="` + this.summaryTable +`">
                ${this.items.map(item => `
                    <tr id="basket-item-${item.ean}">
                    <td>
                        <img src="${item.image_url}" alt="${item.name}" class="rounded me-2" height="48">
                        <p class="m-0 d-inline-block align-middle">
                            <a href="#" class="text-body fw-semibold">${item.name}</a>
                            <br>
                            <small>${item.quantity} x €${item.price.toFixed(2)}</small>
                        </p>
                    </td>
                    </tr>
                `).join('')}
            </tbody>
        `;

        container.appendChild(table);

        document.getElementById("basket-summary-subtotal").textContent = this.getTotal();
        document.getElementById("basket-summary-total").textContent = this.getTotal();

    }
}


class ManageCustomerCheckout {
    constructor(page_url, requestHandler, actionTrigger) {
        this.page_url = page_url;
        App.ready.then(() => {
            this.requestHandler = App.requestHandler;
            this.actionTrigger = App.actionTrigger;
            this.basket = new Basket("basket-table", "basket-total-table");
    
            // Bind event listeners
            this.initActions();
        });
    }

    initActions() {
        
        const self = this;
        const updateForm = document.getElementById('updateBalanceForm');
        
        this.requestHandler.attachDictAndButton(
             "add_purchase", // Command type
             {'items': this.basket.getBasket()}, // JSON data
             "place_order", // Submit button ID
             this.page_url
         );
  

    };


    parseBool(value) {
        return  value === "True" || value === "true" || value === "on" || value === 1 || value === "1";
    }

}