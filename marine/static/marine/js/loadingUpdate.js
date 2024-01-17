// Add event listener to execute code when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // Retrieve elements from template
    const products = JSON.parse(
        document.getElementById("products_data").textContent
    );
    const product = document.querySelector("#id_product");
    const unitPrice = document.querySelector("#id_price");
    const quantity = document.querySelector("#id_quantity");
    const designation = document.querySelector("#dsg");

    // Extract the designation values from the dataset
    const productDesignations = products.map((product) => product.designation);

    // Create  dataset based on the  "designation" values
    const designationBasedProducts = products.reduce((result, product) => {
        result[product.designation] = {
            id: product.id,
            unit_price: product.unit_price,
            marine_warehouses__quantity: product.marine_warehouses__quantity,
        };
        return result;
    }, {});

    // Check if a product is already loaded in the input
    // and apply the maximum quantity to the quantity field
    productValue = designation.value;
    if (productValue.trim() !== "") {
        quantity.max =
            Number(
                designationBasedProducts[productValue].marine_warehouses__quantity
            ) + Number(quantity.value);
        quantity.min = 1;
    }

    // Initialize autocomplete functionality for the "dsg" element
    autocomplete(designation, designationBasedProducts, productDesignations);

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
                const item = arr[i];

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
                        product.value = data.id;
                        unitPrice.value = data.unit_price;

                        // Find the element representing the existing quantity
                        const existingQuantityElement = document.getElementById(data.id);

                        // Extract the existing quantity from the element, or use 0 as the default value
                        const existingQuantity = existingQuantityElement ?
                            Number(existingQuantityElement.innerHTML.replace(",", "")) :
                            0;

                        // Calculate the available quantity by subtracting the existing quantity from the maximum quantity
                        quantity.value = quantity.max =
                            data.marine_warehouses__quantity - existingQuantity ||
                            data.marine_warehouses__quantity;

                        // Set the minimum quantity to 1
                        quantity.min = 1;

                        closeAllLists();
                    });

                    container.appendChild(suggestion);
                }
            }
        });

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