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
import gspread

from novaposhta.client import NovaPoshtaApi

app = Flask(__name__)

# ------------------------------Розділ БД----------------------------------
#(localdb)\MSSQLLocalDB

def connect_to_mssql():
    conn = pyodbc.connect(connectionString)
    return conn

connection = connect_to_mssql()

# Проверка успешности подключения
if connection:
    print("Подключение к базе данных MSSQL успешно установлено.")
else:
    print("Не удалось установить подключение к базе данных MSSQL.")

# ------------------------------Розділ API -----------------------------------
client = NovaPoshtaApi(API_KEY, timeout=30)

def search_settlements(city_name):
    settlements = client.address.search_settlements(city_name=city_name, limit=5)
    return settlements['data'][0]['Addresses']

def search_warehouses(city_name):
    warehouses = client.address.get_warehouses(city_name=city_name, limit=150)
    return warehouses

gc = gspread.service_account(filename='gspread-project-424508-94ae4e7c6185.json')

# Відкриваємо Google Sheets
wks = gc.open("orders").sheet1
# ------------------------------Розділ модели------------------------------------------
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


# ------------------------------Розділ главной страницы------------------------------
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

# Головна сторінка
@app.route('/')
def index():
    cursor = connection.cursor()
    cursor.execute('SELECT name, image, class, price FROM Products')
    products = cursor.fetchall()
    cursor.close()

    
    # Передача даних до шаблону
    return render_template('index.html', products=products)

@app.route('/new_products')
def new_products():
    cursor = connection.cursor()
    cursor.execute('SELECT TOP 10 name, image, class, price FROM Products ORDER BY id DESC')
    new_products = cursor.fetchall()
    cursor.close()

    # Передача даних до шаблону
    return render_template('new_products.html', products=new_products)

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
        # Зберігаємо завантажене зображення
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        # Класифікуємо зображення
        class_name = classify_image(file_path)
        predictedClassname = class_name
        print(class_name)
        # Повертаємо передбачений клас у вигляді JSON
        return jsonify({'predicted_class': class_name})
    else:
        return jsonify({'error': 'Invalid file extension'})

# @app.route('/classified_products')
# def show_classified_products():

#     cursor = connection.cursor()
#     # Выберите только те продукты, у которых class соответствует предсказанному классу
#     cursor.execute('SELECT name, image, class, price FROM Products WHERE class = ?', (predictedClassname,))
#     filtered_products = cursor.fetchall()
#     cursor.close()
#     print("TRY>>>")
#     print(predictedClassname)
#     return render_template('classified_products.html', products=filtered_products)
@app.route('/classified_products')
def show_classified_products():
    cursor = connection.cursor()
    
    if predictedClassname == "Shirt":
        cursor.execute('SELECT name, image, class, price FROM Products WHERE class IN (?, ?)', ("Shirt", "T-shirt/top"))
    else:
        cursor.execute('SELECT name, image, class, price FROM Products WHERE class = ?', (predictedClassname,))
    
    filtered_products = cursor.fetchall()
    cursor.close()
    print("TRY>>>")
    print(predictedClassname)
    return render_template('classified_products.html', products=filtered_products)


# ------------------------------Розділ корзини------------------------------
cart_items = []

def calculate_total_price(cart_items):
    total_price = 0
    for item in cart_items:
        if isinstance(item['price'], (int, float)):
            total_price += item['price']
        else:
            try:
                total_price += float(item['price'])
            except ValueError:
                print(f"Помилка: Неможливо змінити значення ціни '{item['price']}' на число.")
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

@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        city_name = request.form['city']
        user_name = request.form['user_name']
        surname = request.form['surname']
        phone = request.form['phone']
        payment_method = request.form['payment_method']
        cart_items = request.form['cartItems']
        description = request.form.get('description')  # Получаем значение почтового отделения

        cart_items = json.loads(cart_items)

        total_price = sum(float(item['price']) for item in cart_items)

        order_data = {
            'city': city_name,
            'user_name': user_name,
            'surname': surname,
            'phone': phone,
            'payment_method': payment_method,
            'description': description, 
            'cart_items': cart_items,
            'total_price': total_price,
            'completed': False
        }

        all_orders_file = 'all_orders.json'
        if os.path.exists(all_orders_file):
            with open(all_orders_file, 'r', encoding='utf-8') as f:
                all_orders = json.load(f)
        else:
            all_orders = []

        all_orders.append(order_data)
        with open(all_orders_file, 'w', encoding='utf-8') as f:
            json.dump(all_orders, f, ensure_ascii=False, indent=4)

        # Отправка данных в Google Sheets
        row = [city_name, user_name, surname, phone, payment_method, description, json.dumps(cart_items), total_price, False]
        wks.append_row(row)

        return jsonify({'message': 'Заказ успешно оформлен'}), 200
    except KeyError as e:
        return jsonify({'error': f'Missing form data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)