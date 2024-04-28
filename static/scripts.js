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


function updateMaxPrice(value) {
    document.getElementById('max-price-value').textContent = value;
}

function applyPriceFilter() {
    var maxPrice = parseFloat(document.getElementById('max-price').value);

    // Обойти все продукты
    var products = document.querySelectorAll('.product');
    products.forEach(function(product) {
        var priceElement = product.querySelector('.product-item p');
        var price = parseFloat(priceElement.textContent.replace('$', ''));

        // Проверить, попадает ли цена продукта в заданный максимальный диапазон
        if (price <= maxPrice) {
            // Если цена не превышает максимальную, показать продукт
            product.style.display = 'block';
        } else {
            // Если цена превышает максимальную, скрыть продукт
            product.style.display = 'none';
        }
    });
}

function applyClothingClassFilter() {
    var selectedClass = document.getElementById('clothing-class').value;

    // Обойти все продукты
    var products = document.querySelectorAll('.product');
    products.forEach(function(product) {
        var classElement = product.querySelector('.product-class');
        var productClass = classElement.textContent.trim();
        console.log('Applying clothing class filter with predicted class:', selectedClass);
        // Проверить, соответствует ли класс продукта выбранному классу
        if (selectedClass === '' || productClass === selectedClass) {
            // Если продукт соответствует выбранному классу или выбран "Все", показать продукт
            product.style.display = 'block';
        } else {
            // Если продукт не соответствует выбранному классу, скрыть продукт
            product.style.display = 'none';
        }
    });
}

function uploadImage() {
    var input = document.getElementById('file');
    var file = input.files[0];

    var formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Получить классификацию изображения из данных
        var predictedClass = data.predicted_class;
        window.location.href = '/classified_products';
    })
    .catch(error => console.error('Ошибка при загрузке изображения:', error));
}

