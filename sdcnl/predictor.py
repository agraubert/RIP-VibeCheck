# Predictor

import pandas as pd
import numpy as np
import pickle

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import ModelCheckpoint

from tensorflow.keras.models import Sequential

from tensorflow.keras.layers import Dense, Activation, Embedding, Flatten, MaxPooling1D, Dropout, Conv1D, Input, LSTM, SpatialDropout1D, Bidirectional
import argparse
# Import data
# with open('bert_3d.pkl', 'rb') as r:
#     train_features = pickle.load(r)
# train_features = pd.read_csv('./run/guse-testing-features.csv', index_col=0, header=None).iloc[1:]
# print(train_features.head())

# Prediction parameters
batch_size = 32
cnn_path = "/SDCNL/run/model_dense"

# Reload the model

if __name__ == '__main__':
    parser = argparse.ArgumentParser('SDCNL-predictor')
    parser.add_argument('input', help="Input embeddings pickle containing text to be classified")
    parser.add_argument('output', help="output predictions csv")
    parser.add_argument('-m', '--model', help="Model name", default='model.h5')

    args = parser.parse_args()

    features = pd.read_csv(args.input, index_col=0)


    model = tf.keras.models.load_model(args.model)
    mc = ModelCheckpoint(cnn_path + ".h5", monitor='val_accuracy', mode='max', verbose=1, save_best_only=True)

    predictions = model.predict(x=features, batch_size=batch_size, callbacks=[mc])

    # df = pd.DataFrame({"predictions" : [predictions]})
    pd.DataFrame(predictions).to_csv(args.output)
