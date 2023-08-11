import io
import time
import os
import numpy as np
import tensorflow as tf
from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image
import mysql.connector
import base64

app = Flask(__name__)
model_path = './ANN_2Hidden.h5'

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'capture_dress',
}

# Connect to the MySQL database
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

def preprocess_image(image):
    # Resize and preprocess the image before making predictions
    img = image.resize((80, 60))
    img_arr = np.array(img) / 255.0
    flat_img_arr = img_arr.reshape(-1)
    input_img = np.expand_dims(flat_img_arr, axis=0)
    return input_img

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

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

@app.route('/store_image', methods=['POST'])
def store_image():
    file = request.files['file']
    if file:
        img = Image.open(file)
        input_img = preprocess_image(img)

        # Load the model and make predictions
        loaded_model = tf.keras.models.load_model(model_path)
        prediction = loaded_model.predict(input_img)
        predicted_label = np.argmax(prediction)

        # Convert predicted_label to a human-readable label
        label_map = {0: 'Informal', 1: 'Formal'}
        predicted_label = label_map.get(predicted_label)

        # Generate a unique filename for the image
        image_filename = f"{time.time()}.jpg"
        image_path = os.path.join("uploads", image_filename)

        # Save the image to the "uploads" folder
        img.save(image_path)

        # Save the image path and label in the database
        insert_query = "INSERT INTO predicted_imgs (img, label) VALUES (%s, %s)"
        cursor.execute(insert_query, (image_filename, predicted_label))
        connection.commit()

        return jsonify({'message': 'Image and label stored successfully!'})
    else:
        return jsonify({'error': 'No file uploaded.'}), 400

@app.route('/dashboard')
def dashboard():
    try:
        # Retrieve image_path and label from the 'images' table
        select_query = "SELECT img, label FROM predicted_imgs"
        cursor.execute(select_query)
        records = cursor.fetchall()

        return render_template('dashboard.html', images=records)
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to fetch images.'}), 500


@app.route('/capture', methods=['POST'])
def capture():
    try:
        data = request.get_json()
        image_data = data.get('image_data')

        if image_data:
            # Convert the base64-encoded image data to bytes
            image_bytes = base64.b64decode(image_data.split(',')[1])

            # Convert bytes to a PIL Image
            img = Image.open(io.BytesIO(image_bytes))

            # Perform prediction and storage similar to /store_image route
            
            # Load the model and make predictions
            loaded_model = tf.keras.models.load_model(model_path)
            prediction = loaded_model.predict(preprocess_image(img))
            predicted_label = np.argmax(prediction)

            # Convert predicted_label to a human-readable label
            label_map = {0: 'Informal', 1: 'Formal'}
            predicted_label = label_map.get(predicted_label)

            return jsonify({'message': 'Image captured from camera and stored successfully!'})
        else:
            return jsonify({'error': 'No image data received.'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to capture and store image.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
