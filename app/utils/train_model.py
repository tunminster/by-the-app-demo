import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D, Input, LSTM, Dense 
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np

def train_model(training_data, labels):
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(training_data)
    sequences = tokenizer.texts_to_sequences(training_data)
    padded = pad_sequences(sequences, maxlen=100, padding='post', truncating='post')
    
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(tokenizer.num_words, 64),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(padded, np.array(labels), epochs=10)
    
    return model