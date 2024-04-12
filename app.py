import json
import pyodbc
from flask import Flask, jsonify, render_template, request
import os
import shutil
from tensorflow.keras.preprocessing import image
import numpy as np
from tensorflow.keras.models import load_model
import requests

app = Flask(__name__)

# ------------------------------Раздел БД----------------------------------
#(localdb)\MSSQLLocalDB


def connect_to_mssql():
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=ProductsDB;Trusted_Connection=yes;')
    return conn

connection = connect_to_mssql()

# Проверка успешности подключения
if connection:
    print("Подключение к базе данных MSSQL успешно установлено.")
    # Дальнейшие действия с подключением, если необходимо
else:
    print("Не удалось установить подключение к базе данных MSSQL.")

# ------------------------------Раздел API nova post----------------------------------

API_KEY = '9223d5054eb6dd03031032e0c7570646'

url = 'https://api.novaposhta.ua/v2.0/json'
api_key = '9223d5054eb6dd03031032e0c7570646'


# ------------------------------Раздел модели------------------------------------------
# Загрузка модели
model = load_model('FashionMNIST_CNN.h5')

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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


# ------------------------------Раздел сайта------------------------------
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
    cursor.execute('SELECT name, image, price FROM Products')
    products = cursor.fetchall()
    cursor.close()
    
    # Передача данных в шаблон
    return render_template('index.html', products=products)

# Обработка загрузки файла
@app.route('/upload', methods=['POST'])
def upload_file():
    clear_uploads_folder()

    if 'file' not in request.files:
        return render_template('index.html', message='No file part')
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', message='No selected file')
    if file and allowed_file(file.filename):
        # Сохраняем загруженное изображение
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        # Классифицируем изображение
        class_name = classify_image(file_path)
        return render_template('index.html', message='Classification result: {}'.format(class_name))
    else:
        return render_template('index.html', message='Invalid file extension')

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


@app.route('/cart')
def cart():
    total_price = calculate_total_price(cart_items)
    return render_template('cart.html', cart=cart_items, priceall=total_price)

@app.route('/add_to_basket', methods=['POST'])
def add_to_basket():
    product = request.json
    cart_items.append(product)
    return 'Товар успешно добавлен в корзину'

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.json  # Получение данных из POST-запроса
    item_name = data.get('name')  # Получение имени товара из запроса

    # Найдите товар в корзине и удалите его
    for item in cart_items:
        if item['name'] == item_name:
            cart_items.remove(item)
            total_price = calculate_total_price(cart_items)  # Пересчитайте общую стоимость
            return jsonify({'message': 'Товар успешно удален из корзины', 'priceall': total_price})

    return jsonify({'message': 'Товар не найден в корзине'})
# ------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)