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
# model_path = './ANN_2Hidden.h5'
model_path_usage = './cnn_usage.h5'
model_path_article_type = './cnn_articleType.h5'

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
    img = image.resize((80, 60))
    img_arr = np.array(img) / 255.0
    input_img = np.expand_dims(img_arr, axis=0)
    return input_img

UPLOAD_FOLDER = 'uploads2'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/uploads2/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads2', filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['file']
        if file:
            img = Image.open(file)
            input_img = preprocess_image(img)

            # Load the models and make predictions
            loaded_model_usage = tf.keras.models.load_model(model_path_usage)
            loaded_model_article_type = tf.keras.models.load_model(model_path_article_type)

            prediction_usage = loaded_model_usage.predict(input_img)
            predicted_label_usage = np.argmax(prediction_usage)

            prediction_article_type = loaded_model_article_type.predict(input_img)
            predicted_label_article_type = np.argmax(prediction_article_type)

            # Convert predicted_label_usage and predicted_label_article_type to human-readable labels
            label_map_usage = {0: 'Informal', 1: 'Formal'}
            # label_map_article_type = {0: 'Shirt', 1: 'Tshirt', 2: 'Bottom wear'}
            label_map_article_type = {0: 'Shirt', 2: 'Tshirt', 1: 'Bottom wear'}
            predicted_label_usage = label_map_usage.get(predicted_label_usage)
            predicted_label_article_type = label_map_article_type.get(predicted_label_article_type)

            # Return the predicted labels as a JSON response
            return jsonify({'predicted_label_usage': predicted_label_usage, 'predicted_label_article_type': predicted_label_article_type})
        else:
            return jsonify({'error': 'No file uploaded.'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to predict.'}), 500

@app.route('/store_image', methods=['POST'])
def store_image():
    file = request.files['file']
    if file:
        img = Image.open(file)
        input_img = preprocess_image(img)

        # Load the models and make predictions
        loaded_model_usage = tf.keras.models.load_model(model_path_usage)
        loaded_model_article_type = tf.keras.models.load_model(model_path_article_type)
        
        prediction_usage = loaded_model_usage.predict(input_img)
        predicted_label_usage = np.argmax(prediction_usage)
        
        prediction_article_type = loaded_model_article_type.predict(input_img)
        predicted_label_article_type = np.argmax(prediction_article_type)
        
        # Convert predicted_label_usage and predicted_label_article_type to human-readable labels
        label_map_usage = {0: 'Informal', 1: 'Formal'}
        # label_map_article_type = {0: 'Shirt', 1: 'Tshirt', 2: 'Bottom wear'}
        label_map_article_type = {0: 'Shirt', 2: 'Tshirt', 1: 'Bottom wear'}
        predicted_label_usage = label_map_usage.get(predicted_label_usage)
        predicted_label_article_type = label_map_article_type.get(predicted_label_article_type)

        # Generate a unique filename for the image
        image_filename = f"{time.time()}.jpg"
        image_path = os.path.join("uploads2", image_filename)

        # Save the image to the "uploads" folder
        img.save(image_path)

        # Insert the image path and labels into the database
        insert_query = "INSERT INTO predicted_imgs2 (img, usages, articleType) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (image_filename, predicted_label_usage, predicted_label_article_type))
        connection.commit()
        
        return jsonify({'message': 'Image and labels stored successfully!'})
    else:
        return jsonify({'error': 'No file uploaded.'}), 400

@app.route('/dashboard')
def dashboard():
    try:
        # Retrieve image_path, usage, and article_type from the 'images' table
        select_query = "SELECT img, usages, articleType FROM predicted_imgs2"
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

            # Load the models and make predictions
            loaded_model_usage = tf.keras.models.load_model(model_path_usage)
            loaded_model_article_type = tf.keras.models.load_model(model_path_article_type)
            
            prediction_usage = loaded_model_usage.predict(preprocess_image(img))
            predicted_label_usage = np.argmax(prediction_usage)
            
            prediction_article_type = loaded_model_article_type.predict(preprocess_image(img))
            predicted_label_article_type = np.argmax(prediction_article_type)

            # Convert predicted_label_usage and predicted_label_article_type to human-readable labels
            label_map_usage = {0: 'Informal', 1: 'Formal'}
            # label_map_article_type = {0: 'Shirt', 1: 'Tshirt', 2: 'Bottom wear'}
            label_map_article_type = {0: 'Shirt', 2: 'Tshirt', 1: 'Bottom wear'}
            predicted_label_usage = label_map_usage.get(predicted_label_usage)
            predicted_label_article_type = label_map_article_type.get(predicted_label_article_type)

            # Generate a unique filename for the image
            image_filename = f"{time.time()}.jpg"

            # Insert the image and labels into the database
            insert_query = "INSERT INTO predicted_imgs2 (img, usages, articleType) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (image_filename, predicted_label_usage, predicted_label_article_type))
            connection.commit()

            return jsonify({'message': 'Image captured from camera and stored successfully!'})
        else:
            return jsonify({'error': 'No image data received.'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to capture and store image.'}), 500

@app.route('/search_result')
def search_result():
    try:
        search_query = request.args.get('search', '')
        
        if search_query:
            # Split the search query into individual terms
            search_terms = search_query.lower().split()

            # Initialize an empty list to store the search conditions
            conditions = []

            # Loop through the search terms and generate search conditions based on labels
            for term in search_terms:
                formal_labels = ['formal', 'meeting', 'marriage']
                informal_labels = ['informal', 'party']
                if term in formal_labels:
                    conditions.append("LOWER(usages) = 'formal'")
                elif term in informal_labels:
                    conditions.append("LOWER(usages) = 'informal'")
                elif term == 'shirt':
                    conditions.append("LOWER(articleType) = 'shirt'")
                elif term == 'tshirt':
                    conditions.append("LOWER(articleType) = 'tshirt'")
                elif term == 'bottom' and 'wear' in search_terms:
                    conditions.append("LOWER(articleType) = 'bottom wear'")
                elif term == 'bottom':
                    conditions.append("LOWER(articleType) = 'bottom wear'")
                elif term == 'wear':
                    pass
                else:
                    conditions.append(f"LOWER(usages) = '{term}' OR LOWER(articleType) = '{term}'")
                    
            # Join the search conditions with 'AND' to create the final SQL condition
            sql_condition = ' AND '.join(conditions)

            # Construct the SQL query to search for images based on the generated condition
            select_query = f"""
                SELECT img, usages, articleType
                FROM predicted_imgs2
                WHERE {sql_condition}
            """

            # Execute the SQL query
            cursor.execute(select_query)
            records = cursor.fetchall()

            return render_template('search_result.html', images=records, search_query=search_query)
        else:
            return render_template('search_result.html', images=[], search_query='')
    
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to fetch search results.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
