# Fashion MNIST Classification with Convolutional Neural Networks

This project implements a Convolutional Neural Network (CNN) for classifying fashion images using the Fashion MNIST dataset.

## Description

The Fashion MNIST dataset consists of 60,000 training images and 10,000 testing images, each of size 28x28 pixels. Each image belongs to one of 10 classes: T-shirt/top, Trouser, Pullover, Dress, Coat, Sandal, Shirt, Sneaker, Bag, Ankle boot.

The CNN model implemented in this project achieves an accuracy of 90% on the test set.

## Requirements

- Python 3
- TensorFlow 2.x
- NumPy
- Matplotlib

## Usage

1. Clone this repository:

```bash
git clone https://github.com/sanekSOkOlOv/DiplomCNN.git
cd DiplomCNN
```

## Flask Application
This project can be integrated into a Flask web application to serve as part of a clothing store website. Users can upload their own images, and the model will classify them to navigate to the appropriate section of the website (e.g., T-shirts, Dresses, Shoes).

## Files

- FashionMNIST_CNN.py: Jupyter Notebook containing the code for training, evaluation, and prediction.
- FashionMNIST_CNN.h5: Trained model saved in HDF5 format.
- app.py: Main program with Flask server
- templates: The templates folder is for HTML templates only.
- static: Static files (such as CSS, JavaScript, images) are usually stored in the static folder
-- products.json
