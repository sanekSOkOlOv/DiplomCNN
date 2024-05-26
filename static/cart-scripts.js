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

