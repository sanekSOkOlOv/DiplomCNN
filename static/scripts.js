// document.addEventListener("DOMContentLoaded", function() {
//     fetch('/static/products.json')
//         .then(response => response.json())
//         .then(data => {
//             const productContainer = document.getElementById('product-container');
//             data.forEach(product => {
//                 const productDiv = document.createElement('div');
//                 productDiv.classList.add('product');
//                 productDiv.innerHTML = `
//                     <img src="${product.image}" alt="${product.name}" onclick="addToBasket('${product.name}', '${product.image}', ${product.price})">
//                     <h4>${product.name}</h4>
//                     <p>Цена: $${product.price.toFixed(2)}</p>
//                 `;
//                 productContainer.appendChild(productDiv);
//             });
//         })
//         .catch(error => console.error('Ошибка загрузки данных о товарах:', error));
// });

function addToBasket(name, image, price) {
    const product = { name: name, image: image, price: price };
    fetch('/add_to_basket', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(product)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка при добавлении товара в корзину');
        }
        return response.text();
    })
    .then(message => {
        console.log(message);
    })
    .catch(error => {
        console.error('Ошибка при добавлении товара в корзину:', error);
    });
}

$(document).ready(function() {
    $('#city').on('input', function() {
        var formData = $('#search-form').serialize();
        $.ajax({
            type: 'POST',
            url: '/cart',
            data: formData,
            success: function(response) {
                $('#descriptions').html(response);
            }
        });
    });
});