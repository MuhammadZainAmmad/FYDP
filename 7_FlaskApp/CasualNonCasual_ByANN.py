# Implementing ANN
import os
import numpy as np
import tensorflow as tf
import keras

from PIL import Image

from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.callbacks import TensorBoard

from time import strftime # gives hours and minutes of current time.

from sklearn.metrics import precision_score, recall_score

# import matplotlib.pyplot as plt
print(tf.__version__, keras.__version__)
### Loading the data
df_images = np.load('../3_PreprocessingMaleDS/df_images.npy')

print(type(df_images))
df_images.shape
df_usageEncoded = np.load('../3_PreprocessingMaleDS/df_usageEncoded.npy')

print(type(df_usageEncoded))
df_usageEncoded.shape
### Scaling and flattening the data
#Scaling the data between 0 and 1 (Normalization)
x_scaled = df_images / 255.0
#Let us see the data again after scaling.
x_scaled
#note that this is a 4D tensor.
#Flattening the train tensor; placing all pixel for one image in one dimension
TOTAL_INPUTS = 80*60*3
x_scaled_flat = x_scaled.reshape(x_scaled.shape[0], TOTAL_INPUTS)
#Let us see how this flat array looks like
x_scaled_flat
#Now it is a 2D tensor.
x_scaled_flat.shape
#Note that 14400 = 80 x 60 x 3
### Creating train, test and validation Dataset
TEST_SIZE = 1000

##Creating test set
x_test = x_scaled_flat[:TEST_SIZE]
y_test = df_usageEncoded[:TEST_SIZE]
x_test.shape
VAL_SIZE = 500

##Creating test set
x_val = x_scaled_flat[:VAL_SIZE]
y_val = df_usageEncoded[:VAL_SIZE]
x_val.shape
##Creating the remaining train set
x_train = x_scaled_flat[TEST_SIZE + VAL_SIZE:]
y_train = df_usageEncoded[TEST_SIZE + VAL_SIZE:]
x_train.shape
# So now we have two scaled and flattened datasets:
# - The train set haing 15366 samples
# - The test set having 5000 samples
# - The validation set having 1000 samples
## Define the Neural Network using Keras
### Model 1
model_1 = Sequential([
    Dense(units=128, input_dim=TOTAL_INPUTS, activation='relu', name='m1_hidden1'),
    Dense(units=64, activation='relu', name='m1_hidden2'),
    Dense(16, activation='relu', name='m1_hidden3'),
    Dense(2, activation='softmax', name='m1_output')
])
#if we donot give names to the layers, then the names keep on changing on every run

model_1.compile(optimizer='adam', 
                loss='sparse_categorical_crossentropy', 
                metrics=['accuracy'])
type(model_1)
model_1.summary()
# - Total neurons in layer m1_hidden1 = (TOTAL_INPUTS+1)*128 = ((80*60*3)+1)*128 = 1843328
# - Total neurons in layer m1_hidden2 = (128+1)*64  
# - Total neurons in layer m1_hidden3 = (64+1)*16
# - Total neurons in layer m1_output = (16+1)*10
## Tensorboard (visualising learning)
#Setting main folder and subfolders for tendboard
LOG_DIR = 'tensorboard_cifar_logs/'

def get_tensorboard(model_name):
    sub_folder_name = f'{model_name}_at_{strftime("%H_%M")}'
    dir_paths = os.path.join(LOG_DIR, sub_folder_name)
    os.makedirs(dir_paths)
    return TensorBoard(log_dir=dir_paths)
### Loading tensor board in notebook
# Load the TensorBoard notebook extension
# %load_ext tensorboard
# %tensorboard --logdir=tensorboard_cifar_logs
## Fitting the Model
samples_per_batch = 1000
nr_epochs = 150
# %%time
model_1.fit(x_train, y_train, batch_size=samples_per_batch, epochs=nr_epochs,
            callbacks=[get_tensorboard('Model_1')], verbose=0, validation_data=(x_val, y_val))
# Saving the model
model_1.save('ANN_2Hidden.h5')
## Making Predictions on Individual Images
# - In the following code model_1 is used for prediction.
# - You may use model_2 or model_3 too by making necessary alterations in the model name.
image_nr=25
x_val[image_nr].shape
##Adding a dimension as per requirement of predict method
test = np.expand_dims(x_val[image_nr], axis=0)
test.shape
model_1.predict(test)
#Picking the highest probability class
predicted_value=np.argmax(model_1.predict(test), axis=1)
actual_value=y_val[image_nr]

print(f'Actual value: {actual_value} vs. predicted: {predicted_value[0]}')
## Evaluation
#Recalling the metrics that we set during compilation of the model.
model_1.metrics_names
# Let us print the loss funcstion value and overall accuracy of our model on test data.
test_loss, test_accuracy = model_1.evaluate(x_test, y_test)
print(f'Test loss is {test_loss:0.3} and test accuracy is {test_accuracy:0.1%}')
y_pred =np.argmax(model_1.predict(x_test), axis=1)
precision = precision_score(y_test, y_pred)
precision
recall = recall_score(y_test, y_pred)
recall
### Predicting real-world data
im = Image.open('./formalShirt2.jpg')
im = im.resize((80, 60))

im_arr = np.array(im)
scaled_imArr = im_arr/255
flat_imArr = scaled_imArr.reshape(-1)

im = np.expand_dims(flat_imArr, axis=0)

model = tf.keras.models.load_model('./ANN_2Hidden.h5')

pred1 = model.predict(im)

print(type(pred1))
print(pred1)
print(np.max(pred1))
np.argmax(pred1)
im2 = Image.open('./casualShirt.jpg')
im2 = im2.resize((80, 60))

im2_arr = np.array(im2)
scaled_im2Arr = im2_arr/255
flat_im2Arr = scaled_im2Arr.reshape(-1)

im2 = np.expand_dims(flat_im2Arr, axis=0)

model = tf.keras.models.load_model('./ANN_2Hidden.h5')

pred2 = model.predict(im2)

print(type(pred2))
print(pred2)
print(np.max(pred2))
np.argmax(pred2)