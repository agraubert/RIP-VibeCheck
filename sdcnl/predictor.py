# Predictor

import pandas as pd
import numpy as np
import pickle

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from keras.callbacks import ModelCheckpoint

from keras.models import Sequential

from tensorflow.keras.layers import Dense, Activation, Embedding, Flatten, MaxPooling1D, Dropout, Conv1D, Input, LSTM, SpatialDropout1D, Bidirectional

# Import data
with open('bert_3d.pkl', 'rb') as r:
    train_features = pickle.load(r)

# Prediction parameters
batch_size = 32
cnn_path = "/SDCNL/run/cnn"

# Reload the model
model = tf.keras.models.load_model('model')
mc = ModelCheckpoint(cnn_path + ".h5", monitor='val_accuracy', mode='max', verbose=1, save_best_only=True)

predictions = model.predict(x=train_features, batch_size=batch_size, callbacks=mc)

# df = pd.DataFrame({"predictions" : [predictions]})
df = pd.DataFrame(predictions)
df.to_csv('./run/predictions.csv')