// Wait for the DOM to load before executing the script
document.addEventListener("DOMContentLoaded", function () {
    // Add interactivity based on the current page
    const page = document.body.getAttribute("data-page");
  
    if (page === "farmer_dashboard") {
      initFarmerDashboard();
    } else if (page === "consumer_dashboard") {
      initConsumerDashboard();
    }
  });
  
  // Farmer Dashboard Functions
  function initFarmerDashboard() {
    // Fetch consumer requests from the server
    fetchRequests();
  
    // Event listener for adding items
    const addItemForm = document.querySelector("#add-item-form");
    if (addItemForm) {
      addItemForm.addEventListener("submit", function (e) {
        e.preventDefault();
  
        const name = document.querySelector("#item-name").value;
        const price = document.querySelector("#item-price").value;
        const quantity = document.querySelector("#item-quantity").value;
  
        // Send the item data to the server
        fetch("/farmer_dashboard", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, price, quantity }),
        })
          .then((response) => {
            if (response.ok) {
              alert("Item added successfully!");
              addItemForm.reset();
            } else {
              alert("Error adding item. Please try again.");
            }
          })
          .catch((err) => console.error(err));
      });
    }
  }
  
  // Consumer Dashboard Functions
  function initConsumerDashboard() {
    // Fetch available items from the server
    fetchItems();
  
    // Event listener for sending requests
    const requestForms = document.querySelectorAll(".request-item-form");
    requestForms.forEach((form) => {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
  
        const farmerId = form.querySelector('input[name="farmer_id"]').value;
        const itemName = form.querySelector('input[name="item_name"]').value;
  
        // Send the request to the server
        fetch("/consumer_dashboard", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ farmer_id: farmerId, item_name: itemName }),
        })
          .then((response) => {
            if (response.ok) {
              alert("Request sent successfully!");
            } else {
              alert("Error sending request. Please try again.");
            }
          })
          .catch((err) => console.error(err));
      });
    });
  }
  
  // Utility Function: Fetch Items for Consumer Dashboard
  function fetchItems() {
    fetch("/get_items")
      .then((response) => response.json())
      .then((items) => {
        const itemsList = document.querySelector("#items-list");
        itemsList.innerHTML = "";
  
        items.forEach((item) => {
          const listItem = document.createElement("li");
          listItem.innerHTML = `
            ${item.name} - $${item.price} (Qty: ${item.quantity})
            <form class="request-item-form">
              <input type="hidden" name="farmer_id" value="${item.farmer_id}">
              <input type="hidden" name="item_name" value="${item.name}">
              <button type="submit">Request</button>
            </form>
          `;
          itemsList.appendChild(listItem);
        });
      })
      .catch((err) => console.error(err));
  }
  
  // Utility Function: Fetch Requests for Farmer Dashboard
  function fetchRequests() {
    fetch("/get_requests")
      .then((response) => response.json())
      .then((requests) => {
        const requestsList = document.querySelector("#requests-list");
        requestsList.innerHTML = "";
  
        requests.forEach((request) => {
          const listItem = document.createElement("li");
          listItem.textContent = `${request.consumer_name} requested ${request.item_name}`;
          requestsList.appendChild(listItem);
        });
      })
      .catch((err) => console.error(err));
  }
  