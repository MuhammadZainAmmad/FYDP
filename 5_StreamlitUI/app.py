import streamlit as st
import tensorflow as tf
import numpy as np

# Load the saved Keras model
model = tf.keras.models.load_model('../4_CausualFormalPredUsingANN/ANN_2Hidden.h5')

# Create the user interface
st.title('Clothing Formality Predictor')
uploaded_file = st.file_uploader('Upload an image of clothing')

if uploaded_file is not None:
    # Make a prediction
    img = tf.keras.preprocessing.image.load_img(uploaded_file, target_size=(80, 60, 3))
    img = tf.keras.preprocessing.image.img_to_array(img)
    img = tf.keras.applications.resnet50.preprocess_input(img)

    #Scaling the data between 0 and 1 (Normalization)
    img_scaled = img / 255.0

    #Flattening the train tensor; placing all pixel for one image in one dimension
    TOTAL_INPUTS = 80*60*3
    img_scaled_flat = img_scaled.reshape(TOTAL_INPUTS)

    pred = model.predict(tf.expand_dims(img_scaled_flat, axis=0))[0]

    st.write(pred)

    #Picking the highest probability class
    predicted_value=np.argmax(pred)

    st.write(predicted_value)

    # if pred == 1:
    #     st.write('This clothing is formal.')
    # elif pred == 0:
    #     st.write('This clothing is informal.')
    # else:
    #     st.write('Wrong prediction')