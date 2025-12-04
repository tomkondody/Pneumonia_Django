import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image

model = load_model('ml/model.h5')

IMG_SIZE = 150   # change to your model's size

def predict_xray(image_path):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)

    preds = model.predict(img)[0]

    if preds[0] > 0.5:
        return "Pneumonia", float(preds[0])
    else:
        return "Normal", float(1 - preds[0])
