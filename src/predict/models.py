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
import os

os.chdir('/home/crow/Iota/seehorse')

# Get the pretrained Encoder
IMAGE_SHAPE = (224, 224, 3)
mobilenet = tf.keras.applications.MobileNetV3Small(
    input_shape=IMAGE_SHAPE,
    include_top=False,
    include_preprocessing=True)
mobilenet.trainable = False

# Load saved tokenizer
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization

def load_text_vectorization_layer(load_path='resources/saved/tokenizer'):
    loaded_model = tf.keras.models.load_model(load_path, custom_objects={'TextVectorization': TextVectorization})
    text_vectorization_layer = loaded_model.layers[0]
    return text_vectorization_layer


tokenizer = load_text_vectorization_layer()
print(tokenizer)