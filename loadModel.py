import numpy as np
import pandas as pd

import loadData

from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from debug import ipsh

from random import seed
RANDOM_SEED = 54321
seed(RANDOM_SEED) # set the random seed so that the random permutations can be reproduced again
np.random.seed(RANDOM_SEED)


def convertSklearnDtypeToPytorch(input_obj):
  return input_obj
  # isinstance(input_obj, (np.ndarray))
  # return np.around(input_obj, 4).astype('float32')


def loadModelForDataset(model_class, dataset_string):

  if not (model_class == 'lr' or model_class == 'mlp'):
    raise Exception(f'{model_class} not supported.')

  if not (dataset_string == 'random' or dataset_string == 'mortgage' or dataset_string == 'german'):
    raise Exception(f'{dataset_string} not supported.')

  dataset_obj = loadData.loadDataset(dataset_string, return_one_hot = False, load_from_cache = True, debug_flag = False)
  balanced_data_frame, input_cols, output_col = loadData.getBalancedDataFrame(dataset_obj)

  # get train / test splits
  all_data = balanced_data_frame.loc[:,input_cols]
  all_true_labels = balanced_data_frame.loc[:,output_col]
  X_train, X_test, y_train, y_test = train_test_split(
    all_data.to_numpy(),
    all_true_labels.to_numpy(),
    train_size=.7,
    random_state = RANDOM_SEED)

  if model_class == 'lr':
    model_pretrain = LogisticRegression(penalty='l1')
  elif model_class == 'mlp':
    model_pretrain = MLPClassifier(hidden_layer_sizes = (10, 10))

  model_trained = model_pretrain.fit(X_train, y_train)

  # need to do this to match pytorch's dtypes for proper comparison
  if model_class == 'lr':

    # the returned model_trained for 'mortgage' has 100% train & test accuracy.
    if dataset_string == 'mortgage':
      mortgage_cutoff = -225000
      w = np.array([[1], [5]]).T
      b = np.ones(1) * mortgage_cutoff
    elif dataset_string == 'german' or dataset_string == 'random':
      w = model_trained.coef_
      b = model_trained.intercept_

    model_trained.coef_ = convertSklearnDtypeToPytorch(w)
    model_trained.intercept_ = convertSklearnDtypeToPytorch(b)

  elif model_class == 'mlp':

    for i in range(len(model_trained.coefs_)):
      model_trained.coefs_[i] = convertSklearnDtypeToPytorch(model_trained.coefs_[i])
      model_trained.intercepts_[i] = convertSklearnDtypeToPytorch(model_trained.intercepts_[i])

  return model_trained






























