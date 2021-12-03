# Classifiers

# This notebook contains the implementation of our three deep neural classifiers with correct hyperparameters.

import pandas as pd
import numpy as np
import pickle

import tensorflow
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import ModelCheckpoint

from tensorflow.keras.models import Sequential

from tensorflow.keras.layers import Dense, Activation, Embedding, Flatten, MaxPooling1D, Dropout, Conv1D, Input, LSTM, SpatialDropout1D, Bidirectional

# train_features = pd.read_csv('train_features.csv', delimiter=',') # load the features after creating them
# test_feautres = pd.read_csv('test_features.csv', delimiter=',') # load the features after creating them

# train_features = pd.read_csv('./run/bert-training-features.csv', delimiter=',', header=None) # load the features after creating them
import pickle
import argparse




# training hyperparameters

epochs = 80
batch_size = 32

# Convolutional Neural Network

# cnn = Sequential()

# cnn_path = "./run/model_cnn"

# filters = 3
# kernal = 2

# cnn.add(Input(shape=(512,768)))
# cnn.add(Conv1D(filters= filters, kernel_size = kernal, activation='relu'))
# cnn.add(Dropout(0.25))
# cnn.add(Flatten())
# cnn.add(Dense(64, activation='relu', kernel_initializer='he_uniform'))
# cnn.add(Dense(1, activation='sigmoid'))

# cnn.compile(optimizer='adam',
#               loss='binary_crossentropy',
#               metrics=['accuracy'])

# mc = ModelCheckpoint(cnn_path + ".h5", monitor='val_accuracy', mode='max', verbose=1, save_best_only=True)

# Added by Sean to train model once layers are created
# Training feature / label sets are given a dummy dimension to fit model 3-dimensional requirement

# train_features = train_features.values[..., None]

# train_features = train_features.astype('float32')
# train_labels = train_labels.astype('float32')




if __name__ == '__main__':
    parser = argparse.ArgumentParser('SDCNL-classifier')
    parser.add_argument('input', help="Original input csv containing is_suicide labels to train")
    parser.add_argument('embeddings', help="Clustered embeddings pickle to train model")
    parser.add_argument('-m', '--model', help='Output model name', default='model.h5')
    parser.add_argument('-l', '--label-column', help="Column in label table. Defaults to 'is_suicide'", default='is_suicide')

    args = parser.parse_args()

    # with open(args.embeddings, 'rb') as r:
    #     train_features = pickle.load(r)

    train_features = pd.read_csv(args.embeddings, index_col=0)

    train_labels = pd.read_csv(args.input)[args.label_column]

    dense = Sequential()

    dense_path = "./run/model_dense"

    dense = Sequential()
    dense.add(Input(shape=(512,)))
    dense.add(Dense(128, activation='relu', kernel_initializer='he_uniform'))
    dense.add(Dense(64, activation='relu', kernel_initializer='he_uniform'))
    dense.add(Dense(1, activation='sigmoid'))

    dense.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    mc = ModelCheckpoint(dense_path + ".h5", monitor='val_accuracy', mode='max', verbose=1, save_best_only=True)

    dense.fit(x=train_features, y=train_labels, epochs=epochs, batch_size=batch_size, callbacks=[mc])

    dense.summary()

    dense.save(args.model)


# predictions = cnn.predict(x=train_features, batch_size=batch_size, callbacks=mc)

# print(predictions)




# # Fully Dense Network


# # Bi-LSTM
# bilstm = Sequential()

# bilstm_path = "bilstm"

# pool_size = 2

# bilstm.add(Input(shape=(512,768)))
# bilstm.add(Bidirectional(LSTM(20, return_sequences=True, dropout=0.25, recurrent_dropout=0.2)))
# bilstm.add(MaxPooling1D(pool_size = pool_size))
# bilstm.add(Flatten())
# bilstm.add(Dense(10, activation='relu', kernel_initializer='he_uniform'))
# bilstm.add(Dense(1, activation='sigmoid'))


# bilstm.compile(optimizer='adam',
#               loss='binary_crossentropy',
#               metrics=['accuracy'])

# mc = ModelCheckpoint(bilstm_path + ".h5", monitor='val_accuracy', mode='max', verbose=1, save_best_only=True)

# bilstm.summary()
