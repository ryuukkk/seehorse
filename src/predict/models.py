import tensorflow as tf
from tensorflow import keras
import pathlib
import collections
import matplotlib.pyplot as plt
import concurrent.futures
import requests
import hashlib
import itertools
import tqdm
import re
import string
import einops
import numpy as np

def standardize(s):
  s = tf.strings.lower(s)
  s = tf.strings.regex_replace(s, f'[{re.escape(string.punctuation)}]', '')
  s = tf.strings.join(['[START]', s, '[END]'], separator=' ')
  return s

# Use the top 6000 words for a vocabulary.
vocabulary_size = 6000
tokenizer = tf.keras.layers.TextVectorization(
    max_tokens=vocabulary_size,
    standardize=standardize,
    ragged=True)
# Learn the vocabulary from the caption data.

tokenizer.adapt(flickr_train.map(lambda fp,txt: txt).unbatch().batch(1024))