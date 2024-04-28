from config import connectionString, ALLOWED_EXTENSIONS, API_KEY
import json
import pyodbc
from flask import Flask, jsonify, render_template, request
import os
import shutil
from tensorflow.keras.preprocessing import image
import numpy as np
from tensorflow.keras.models import load_model
import requests

from novaposhta.client import NovaPoshtaApi

app = Flask(__name__)

# ------------------------------Раздел БД----------------------------------
#(localdb)\MSSQLLocalDB

def connect_to_mssql():
    conn = pyodbc.connect(connectionString)
    return conn

connection = connect_to_mssql()

# Проверка успешности подключения
if connection:
    print("Подключение к базе данных MSSQL успешно установлено.")
    # Дальнейшие действия с подключением, если необходимо
else:
    print("Не удалось установить подключение к базе данных MSSQL.")

# ------------------------------Раздел API nova post----------------------------------
client = NovaPoshtaApi(API_KEY, timeout=30)

def search_settlements(city_name):
    settlements = client.address.search_settlements(city_name=city_name, limit=5)
    return settlements['data'][0]['Addresses']

def search_warehouses(city_name):
    warehouses = client.address.get_warehouses(city_name=city_name, limit=50)
    return warehouses

# ------------------------------Раздел модели------------------------------------------
predictedClassname = None
# Загрузка модели
model = load_model('FashionMNIST_CNN.h5')

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])


# Проверка разрешенных расширений файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Функция для классификации изображения
def classify_image(image_path):
    img = image.load_img(image_path, target_size=(28, 28), color_mode='grayscale')
    img_array = image.img_to_array(img)
    img_array /= 255.0  # Нормализация значений пикселей
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)
    class_id = np.argmax(prediction)
    classes = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
    return classes[class_id]


# ------------------------------Раздел главной страницы------------------------------
# Функция для очистки содержимого папки uploads
def clear_uploads_folder():
    folder = 'uploads'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

# Главная страница
@app.route('/')
def index():
    cursor = connection.cursor()
    cursor.execute('SELECT name, image, class, price FROM Products')
    products = cursor.fetchall()
    cursor.close()

    
    # Передача данных в шаблон
    return render_template('index.html', products=products)

@app.route('/upload', methods=['POST'])
def upload_file():
    global predictedClassname
    clear_uploads_folder()

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        # Сохраняем загруженное изображение
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        # Классифицируем изображение
        class_name = classify_image(file_path)
        predictedClassname = class_name
        print(class_name)
        # Возвращаем предсказанный класс в виде JSON
        return jsonify({'predicted_class': class_name})
    else:
        return jsonify({'error': 'Invalid file extension'})

@app.route('/classified_products')
def show_classified_products():

    cursor = connection.cursor()
    # Выберите только те продукты, у которых class соответствует предсказанному классу
    cursor.execute('SELECT name, image, class, price FROM Products WHERE class = ?', (predictedClassname,))
    filtered_products = cursor.fetchall()
    cursor.close()
    print("TRY>>>")
    print(predictedClassname)
    return render_template('classified_products.html', products=filtered_products)

# ------------------------------Раздел корзины------------------------------
cart_items = []

def calculate_total_price(cart_items):
    total_price = 0
    for item in cart_items:
        # Проверяем, что значение цены является числом
        if isinstance(item['price'], (int, float)):
            total_price += item['price']
        else:
            # Если значение цены не является числом, пытаемся преобразовать его в float
            try:
                total_price += float(item['price'])
            except ValueError:
                print(f"Ошибка: Невозможно преобразовать значение цены '{item['price']}' в число.")
    return round(total_price, 2)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        city_name = request.form['city']
        settlements = search_settlements(city_name)
        warehouses = search_warehouses(city_name)
        return render_template('descriptions.html',  warehouses = warehouses)
    total_price = calculate_total_price(cart_items)
    return render_template('cart.html', cart=cart_items, priceall=total_price)

@app.route('/add_to_basket', methods=['POST'])
def add_to_basket():
    product = request.json
    cart_items.append(product)
    return 'Товар успешно добавлен в корзину'

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.json  
    item_name = data.get('name')  

    
    for item in cart_items:
        if item['name'] == item_name:
            cart_items.remove(item)
            total_price = calculate_total_price(cart_items)  # Пересчитайте общую стоимость
            return jsonify({'message': 'Товар успешно удален из корзины', 'priceall': total_price})

    return jsonify({'message': 'Товар не найден в корзине'})
# ------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)