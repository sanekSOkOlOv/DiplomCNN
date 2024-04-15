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

document.addEventListener("DOMContentLoaded", function() {
    const cartItems = document.querySelectorAll('.cart-item');

    cartItems.forEach(item => {
        const cancelButton = item.querySelector('.cancel-overlay img');

        cancelButton.addEventListener('click', function() {
            const itemName = item.querySelector('h3').textContent;
            
            fetch('/remove_from_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: itemName }) // Передача имени товара в формате JSON
            })
            .then(response => response.json()) // Преобразование ответа в JSON
            .then(data => {
                console.log(data.message);
                updateTotalPrice(data.priceall); // Обновление общей стоимости
                showNotification(data.message); // Показ уведомления
                item.remove(); // Удаление элемента из DOM
            })
            .catch(error => {
                console.error('Ошибка при удалении товара из корзины:', error);
            });
        });
    });
});

function showNotification(message) {
    // Находим элемент уведомления
    var notification = document.getElementById('notification');
    // Устанавливаем текст уведомления
    notification.innerHTML = message;
    // Показываем уведомление
    notification.style.display = 'block';
    // Через 3 секунды скрываем уведомление
    setTimeout(function() {
        notification.style.display = 'none';
    }, 3000);
}

function updateTotalPrice(price) {
    const totalPriceElement = document.querySelector('.checkout-summary p');
    if (totalPriceElement) {
        totalPriceElement.textContent = `$${price}`;
    }
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