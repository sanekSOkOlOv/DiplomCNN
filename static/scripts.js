document.addEventListener("DOMContentLoaded", function() {
    // Загружаем данные о товарах из JSON файла
    fetch('/static/products.json')
        .then(response => response.json())
        .then(data => {
            const productContainer = document.getElementById('product-container');
            data.forEach(product => {
                const productDiv = document.createElement('div');
                productDiv.classList.add('product');
                productDiv.innerHTML = `
                    <img src="${product.image   }" alt="${product.name}">
                    <h4>${product.name}</h4>
                    <p>Цена: $${product.price.toFixed(2)}</p>
                `;
                productContainer.appendChild(productDiv);
            });
        })
        .catch(error => console.error('Ошибка загрузки данных о товарах:', error));
});