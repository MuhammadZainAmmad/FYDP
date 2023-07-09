import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image

# Load the saved Keras model
model = tf.keras.models.load_model('../4_CausualFormalPredUsingANN/ANN_2Hidden.h5')

# Create the user interface
st.title('Clothing Formality Predictor')
uploaded_file = st.file_uploader('Upload an image of clothing')

if uploaded_file is not None:
    im = Image.open(uploaded_file)

    # Image preprocessing
    im = im.resize((80, 60))
    im_arr = np.array(im)
    scaled_imArr = im_arr/255
    flat_imArr = scaled_imArr.reshape(-1)
    im = np.expand_dims(flat_imArr, axis=0)

    pred = model.predict(im)

    st.write('The predicted model array is ' + str(pred))

    # Picking the highest probability class
    pred_value=np.argmax(pred)
    st.write('The predicted class is ' + str(pred_value))

    if pred_value == 1:
        st.write('This clothing is formal.')
    elif pred_value == 0:
        st.write('This clothing is informal.')
    else:
        st.write('Wrong prediction')