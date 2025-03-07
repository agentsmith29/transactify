class Basket {
    constructor(containerId, summaryTable) {
        this.items = [];
        this.total = 0;
        this.containerId = containerId;
        this.summaryTable = summaryTable;
    }

    addItem(id, name, price, quantity = 1) {
        id = Number(id); // Ensure ID is a number
        let existingItem = this.items.find(item => item.id === id);
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.items.push({ id, name, price, quantity });
        }
        this.updateTotal();
        this.renderBasket();
        console.log("Added to cart: " + name)
    }

    removeItem(id) {
        id = Number(id);
        this.items = this.items.filter(item => item.id !== id);
        this.updateTotal();
        this.renderBasket();
    }

    updateQuantity(id, quantity) {
        id = Number(id);
        let item = this.items.find(item => item.id === id);
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
                    <tr id="basket-item-${item.id}">
                        <td>${item.name}</td>
                        <td>€${item.price.toFixed(2)}</td>
                        <td>
                            <button class="btn btn-sm btn-light" onclick="basket.updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                            <span id="quantity-${item.id}">${item.quantity}</span>
                            <button class="btn btn-sm btn-light" onclick="basket.updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                        </td>
                        <td>€<span id="total-${item.id}">${(item.price * item.quantity).toFixed(2)}</span></td>
                        <td><button class="btn btn-sm btn-danger" onclick="basket.removeItem(${item.id})">Remove</button></td>
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
                    <tr id="basket-item-${item.id}">
                    <td>
                        <img src="${item.image}" alt="product-img" class="rounded me-2" height="48">
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

