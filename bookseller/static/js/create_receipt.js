let totalPrice = 0; // Biến để tính tổng giá trị hóa đơn
let totalQuantity =0

document.getElementById("product-select").addEventListener('change', function() {
    const productSelect = document.getElementById("product-select");
    const warningDiv = document.getElementById("product-warning");

//    // Nếu giá trị là '-' (nghĩa là không có sản phẩm nào được chọn)
//    if (productSelect.options[productSelect.selectedIndex] == "-") {
//        warningDiv.style.display = 'block'; // Hiển thị cảnh báo
//    } else {
//        warningDiv.style.display = 'none'; // Ẩn cảnh báo nếu có sản phẩm được chọn
//    }
});



function addProductToReceipt() {
    const productSelect = document.getElementById("product-select");
    const quantityInput = document.getElementById("quantity");
    const selectedProductId = productSelect.value;
    const selectedProductName = productSelect.options[productSelect.selectedIndex].getAttribute("data-name");
    const selectedProductPrice = parseInt(productSelect.options[productSelect.selectedIndex].getAttribute("data-price"));
    const selectedProductCategory = productSelect.options[productSelect.selectedIndex].getAttribute("data-category");
    const quantity = parseInt(quantityInput.value);



//    if (productSelect.value === "") {
//        warningDiv.style.display = 'block'; // Hiển thị cảnh báo
//    } else {
//        warningDiv.style.display = 'none'; // Ẩn cảnh báo nếu có sản phẩm được chọn
//    }

    const totalProductPrice = selectedProductPrice * quantity;


    // Thêm dòng sản phẩm vào bảng
    const tableBody = document.getElementById("receipt-products-table").getElementsByTagName('tbody')[0];
    const newRow = tableBody.insertRow();
    newRow.setAttribute("data-product-id", selectedProductId);

    newRow.innerHTML = `
        <td>${selectedProductName}</td>
        <td>${selectedProductCategory}</td>
        <td>${quantity}</td>
        <td>${selectedProductPrice} VNĐ</td>
        <td class="text-center"><button class="btn btn-danger"
        onclick="removeProductFromReceipt(this, ${totalProductPrice}, ${quantity})">Xóa</button></td>
    `;

    // Cập nhật tổng giá trị hóa đơn
    totalPrice += totalProductPrice;
    totalQuantity += quantity
    document.getElementById("total-price").innerText = totalPrice;
    document.getElementById("total-quantity").innerText = totalQuantity;
}

function removeProductFromReceipt(button, productPrice, productQuantity) {
    const row = button.parentElement.parentElement;
    row.remove();
    totalPrice -= productPrice;
    totalQuantity -= productQuantity;
    document.getElementById("total-price").innerText = totalPrice;
    document.getElementById("total-quantity").innerText = totalQuantity;
}

// Xử lý lập hóa đơn
document.getElementById("receipt-form").onsubmit = function(event) {
    event.preventDefault();
    const customerName = document.getElementById("customer-name").value;
    const receiptDate = document.getElementById("receipt-date").value;

    const products = [];
    const rows = document.getElementById("receipt-products-table").getElementsByTagName('tbody')[0].rows;
    for (let row of rows) {
        const productId = row.getAttribute("data-product-id");
        const productName = row.cells[0].innerText;
        const quantity = row.cells[1].innerText;
        const price = row.cells[2].innerText.replace(" VNĐ", "");
        products.push({ productId, productName, quantity, price });
    }

    // Gửi thông tin hóa đơn lên server
    const receiptData = {
        customer_name: customerName,
        receipt_date: receiptDate,
        products: products,
        total_price: totalPrice
    };

    fetch('/create_receipt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(receiptData)
    })
    .then(response => response.json())
    .then(data => {
        alert('Hóa đơn đã được lập thành công!');
        // Xử lý sau khi lập hóa đơn (e.g., chuyển hướng hoặc làm mới trang)
    });
};


function updatePrice() {
        // Lấy các phần tử từ DOM

        const productSelect = document.getElementById('product-select'); // Sửa lại tên id cho đúng
        const quantity = document.getElementById('quantity'); // Lấy giá trị số lượng
        const priceInput = document.getElementById('price'); // Lấy trường giá


        // Kiểm tra nếu người dùng đã chọn sản phẩm
        if (productSelect.value !== "") {
            const selectedProductPrice = parseInt(productSelect.options[productSelect.selectedIndex].getAttribute("data-price"));
            const quantityValue = parseInt(quantity.value);

            // Tính giá tổng và cập nhật vào trường price
             const p = selectedProductPrice * quantityValue
             priceInput.value = p.toLocaleString('vi-VN');

        } else {
            priceInput.value = ""; // Nếu chưa chọn sản phẩm, xóa giá
        }
    }

window.onload = function() {
    updatePrice(); // Cập nhật giá khi trang tải
    document.getElementById('product-select').addEventListener('change', updatePrice);
    document.getElementById('quantity').addEventListener('input', updatePrice);
    document.getElementById('price').addEventListener('onblur', updatePrice);
};








