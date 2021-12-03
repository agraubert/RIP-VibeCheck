# Transformers Notebook

# This notebook contains the implementation of our BERT and Google Universal Sentence Encoder (GUSE) transformers.

import numpy as np
import pandas as pd
import pickle

import torch
import transformers as ppb
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import tensorflow_hub as hub

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import MultinomialNB
import argparse
import os
import pickle
import subprocess


# Google Universal Sentence Encoder (GUSE) Transformer

# install the following
# run 'pip install tensorflow==1.15'
# run 'pip install "tensorflow_hub>=0.6.0"'
# run 'pip3 install tensorflow_text==1.15'

def getEmbedModule():
    if not os.path.isdir('/content/module_useT'):
        os.makedirs('/content/module_useT')
    if not len(os.listdir('/content/module_useT')):
        subprocess.check_call(
            'curl -L "https://tfhub.dev/google/universal-sentence-encoder-large/3?tf-hub-format=compressed" | tar -zxvC /content/module_useT',
            shell='/bin/bash'
        )
    return hub.Module('/content/module_useT')



# define the GUSE transformer
def encodeData(messages):
  # Reduce logging output.
  embed = getEmbedModule()
  tf.logging.set_verbosity(tf.logging.ERROR)
  with tf.Session() as session:
      session.run([tf.global_variables_initializer(), tf.tables_initializer()])
      message_embeddings = session.run(embed(messages))

  final_embeddings = pd.DataFrame(data=message_embeddings)

  return final_embeddings


## These are the two GUSE sets for Aaron
# transform the text features to word embeddings using GUSE
training_regular = pd.read_csv('./data/training-set.csv')['selftext']
new_training_regular = encodeData(training_regular)
new_training_regular.to_csv('guse-training-features.csv')

training_regular = pd.read_csv('./data/testing-set.csv')['selftext']
new_training_regular = encodeData(training_regular)
new_training_regular.to_csv('./run/guse-testing-features.csv')


# BERT Transformer
# install the following
# run'pip install transformers'

# importing bert-base, tokenizers, and models from libraries
model_class, tokenizer_class, pretrained_weights = (ppb.BertModel, ppb.BertTokenizer, 'bert-base-uncased')
tokenizer = tokenizer_class.from_pretrained(pretrained_weights)
model = model_class.from_pretrained(pretrained_weights)

# defining the BERT transformer
# Look at the below comments to determine whether you want to output the 2-dimensional or 3-dimensional BERT features.
def getFeatures(batch_1):

  tokenized = batch_1.apply((lambda x: tokenizer.encode(x, add_special_tokens=True, truncation=True, max_length=512)))

  max_len = 0
  for i in tokenized.values:
      if len(i) > max_len:
          max_len = len(i)

  padded = np.array([i + [0]*(max_len-len(i)) for i in tokenized.values])


  attention_mask = np.where(padded != 0, 1, 0)
  attention_mask.shape


  input_ids = torch.tensor(padded)
  attention_mask = torch.tensor(attention_mask)

  with torch.no_grad():
      last_hidden_states = model(input_ids, attention_mask=attention_mask)

  # features = last_hidden_states[0][:,0,:].numpy() # use this line if you want the 2D BERT features
  features = last_hidden_states[0].numpy() # use this line if you want the 3D BERT features

  return features

if __name__ == '__main__':
    parser = argparse.ArgumentParser('SDCNL-embeddings')
    parser.add_argument('input', help="Input csv file containing 'selftext' column")
    parser.add_argument('output', help="output pickle file")

    # print("Bert shape: ", bert_features.shape)
    # np.savetxt("bert-3d-training-features.csv", bert_features, delimiter=',')

    args = parser.parse_args()

    with open(args.output, 'wb') as w:
        pickle.dump(encodeData(pd.read_csv(args.input)['selftext']), w)
