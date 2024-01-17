// Add event listener to execute code when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // Retrieve elements from template
    const total = document.getElementById("total");
    const billAmount = document.getElementById("id_sale-total_amount");
    billAmount.readOnly = true;
    const subTotalAmount = document.getElementById("id_total_amount");
    subTotalAmount.readOnly = true;
    // item inputs
    const product = document.querySelector("#id_product");
    const unitPrice = document.querySelector("#id_price");
    const discountPrice = document.querySelector("#id_discount_price");
    const quantity = document.querySelector("#id_quantity");
    const designation = document.querySelector("#dsg");
    const allInputs = document.querySelectorAll(".form-field");
    // dataset
    const products = JSON.parse(
        document.getElementById("products_data").textContent
    );

    // Create a dataset based on the "designation" values
    const designationBasedProducts = products.reduce((result, product) => {
        result[product.designation] = {
            id: product.id,
            unit_price: product.unit_price,
            marine_stores__quantity: product.marine_stores__quantity,
        };
        return result;
    }, {});

    // Extract the products' designation from the dataset
    const productDesignations = products.map((product) => product.designation);

    billAmount.value = Number(total.innerHTML) || 0;

    // Retrieve customers dataset from a JSON element and parse it
    const customers = JSON.parse(
        document.getElementById("customers_data").textContent
    );

    const customerName = document.getElementById("id_customer-name");
    const customerContact = document.getElementById("id_customer-contact");
    // Create two datasets based on the "name" and "contact" values
    const nameBasedCustomers = customers.reduce((result, customer) => {
        result[customer.name] = {
            contact: customer.contact,
        };
        return result;
    }, {});
    const contactBasedCustomers = customers.reduce((result, customer) => {
        result[customer.contact] = {
            name: customer.name,
        };
        return result;
    }, {});

    // Extract the desired values from the dataset
    const customerNames = customers.map((customer) => customer.name);
    const customerContacts = customers.map((customer) => customer.contact);

    // Initialize autocomplete functionality for the input elements
    autocomplete(designation, designationBasedProducts, productDesignations);
    autocomplete(customerName, nameBasedCustomers, customerNames);
    autocomplete(customerContact, contactBasedCustomers, customerContacts);
    allInputs.forEach((element) => {
        element.onclick = () => {
            calculateAmount(quantity.value, discountPrice.value);
        };
        element.onkeyup = () => {
            calculateAmount(quantity.value, discountPrice.value);
        };
        element.onchange = () => {
            calculateAmount(quantity.value, discountPrice.value);
        };
    });

    // function to automaticaly set subtotal amount of an item
    function calculateAmount(quantity, discountPrice) {
        subTotalAmount.value = `${Number(quantity) * discountPrice}`;
    }

    // Function to handle autocomplete functionality
    function autocomplete(inp, dataset, arr) {
        let currentFocus;

        inp.addEventListener("input", function(e) {
            const val = this.value;
            closeAllLists();

            if (!val) {
                return false;
            }

            currentFocus = -1;
            const container = document.createElement("DIV");
            container.setAttribute("id", this.id + "autocomplete-list");
            container.setAttribute("class", "autocomplete-items");
            this.parentNode.appendChild(container);

            // Generate autocomplete suggestions based on the input value
            for (let i = 0; i < arr.length; i++) {
                const item = String(arr[i]);

                if (item.toUpperCase().includes(val.toUpperCase())) {
                    const idx = item.toUpperCase().indexOf(val.toUpperCase());
                    const suggestion = document.createElement("DIV");
                    suggestion.innerHTML = item.substring(0, idx);
                    suggestion.innerHTML +=
                        "<strong>" + item.substr(idx, val.length) + "</strong>";
                    suggestion.innerHTML += item.substr(idx + val.length);
                    suggestion.innerHTML += '<input type="hidden" value="' + item + '">';
                    suggestion.addEventListener("click", function(e) {
                        // Set the selected suggestion as the input value
                        inp.value = this.getElementsByTagName("input")[0].value;

                        // Update other fields based on the selected suggestion
                        data = dataset[inp.value];

                        datasetUpdate(data);

                        closeAllLists();
                    });

                    container.appendChild(suggestion);
                }
            }
        });

        function datasetUpdate(data) {
            if (inp.id === "id_customer-name") {
                customerContact.value = data.contact;
            } else if (inp.id === "id_customer-contact") {
                customerName.value = data.name;
            } else if (inp.id === "dsg") {
                product.value = data.id;
                unitPrice.value = data.unit_price;
                discountPrice.value = data.unit_price;

                const existingQuantityElement = document.getElementById(data.id);
                const existingQuantity = existingQuantityElement ?
                    Number(existingQuantityElement.innerHTML.replace(",", "")) :
                    0;
                quantity.value =
                    data.marine_stores__quantity - existingQuantity ||
                    data.marine_stores__quantity;
                quantity.min = 1;

                calculateAmount(quantity.value, discountPrice.value);
            }
        }

        inp.addEventListener("keydown", function(e) {
            const suggestions = document.getElementById(
                this.id + "autocomplete-list"
            );

            if (suggestions) {
                const items = suggestions.getElementsByTagName("div");

                // Handle arrow key navigation and Enter key selection
                if (e.keyCode === 40) {
                    // Arrow DOWN
                    currentFocus++;
                    addActive(items);
                } else if (e.keyCode === 38) {
                    // Arrow UP
                    currentFocus--;
                    addActive(items);
                } else if (e.keyCode === 13) {
                    // Enter
                    e.preventDefault();
                    if (currentFocus > -1) {
                        items[currentFocus].click();
                    }
                }
            }
        });

        function addActive(items) {
            if (!items) {
                return false;
            }

            // Add 'autocomplete-active' class to the currently selected item
            removeActive(items);

            if (currentFocus >= items.length) {
                currentFocus = 0;
            }

            if (currentFocus < 0) {
                currentFocus = items.length - 1;
            }

            items[currentFocus].classList.add("autocomplete-active");
        }

        function removeActive(items) {
            // Remove 'autocomplete-active' class from all items
            for (let i = 0; i < items.length; i++) {
                items[i].classList.remove("autocomplete-active");
            }
        }

        function closeAllLists(except) {
            // Close all autocomplete lists except the current one
            const lists = document.getElementsByClassName("autocomplete-items");

            for (let i = 0; i < lists.length; i++) {
                if (except != lists[i] && except != inp) {
                    lists[i].parentNode.removeChild(lists[i]);
                }
            }
        }

        document.addEventListener("click", function(e) {
            // Close all autocomplete lists when clicking outside of them
            closeAllLists(e.target);
        });
    }
});