import json
from flask import Flask, render_template, request
import os
import shutil
from tensorflow.keras.preprocessing import image
import numpy as np
from tensorflow.keras.models import load_model

app = Flask(__name__)
# ------------------------------Раздел модели------------------------------
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
        return render_template('index.html')

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


# ------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)