import os
import numpy as np
import tensorflow as tf
from flask import Flask, render_template, request, jsonify
from PIL import Image
# import my_model  # Renamed model.py to my_model.py

app = Flask(__name__)
model_path = './ANN_2Hidden.h5'

def preprocess_image(image):
    # Resize and preprocess the image before making predictions
    img = image.resize((80, 60))
    img_arr = np.array(img) / 255.0
    flat_img_arr = img_arr.reshape(-1)
    input_img = np.expand_dims(flat_img_arr, axis=0)
    return input_img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['file']
    if file:
        img = Image.open(file)
        input_img = preprocess_image(img)

        # Load the model and make predictions
        loaded_model = tf.keras.models.load_model(model_path)
        prediction = loaded_model.predict(input_img)
        predicted_label = np.argmax(prediction)

        # Convert predicted_label to a Python int
        predicted_label = int(predicted_label)

        # Return the predicted label as a JSON response
        return jsonify({'predicted_label': predicted_label})
    else:
        return jsonify({'error': 'No file uploaded.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
