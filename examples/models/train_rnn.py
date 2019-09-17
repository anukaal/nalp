import tensorflow as tf

import nalp.utils.preprocess as p
from nalp.corpus.text import TextCorpus
from nalp.datasets.next import NextDataset
from nalp.encoders.integer import IntegerEncoder
from nalp.models.rnn import RNN

# Creating a character TextCorpus from file
corpus = TextCorpus(from_file='data/text/chapter1_harry.txt', type='char')

# Creating an IntegerEncoder
encoder = IntegerEncoder()

# Learns the encoding based on the TextCorpus dictionary and reverse dictionary
encoder.learn(corpus.vocab_index, corpus.index_vocab)

# Applies the encoding on new data
encoded_tokens = encoder.encode(corpus.tokens)

# Creating next target Dataset
dataset = NextDataset(encoded_tokens, max_length=10, batch_size=64)

# Creating the RNN
rnn = RNN(vocab_size=corpus.vocab_size, embedding_size=256, hidden_size=512)

def accuracy(labels, logits):
    return tf.keras.metrics.sparse_categorical_accuracy(labels, logits)

def loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

# Compiling the RNN
rnn.compile(optimize=tf.optimizers.Adam(learning_rate=0.001),
            loss=loss, metrics=[accuracy])

# Fitting the RNN
rnn.fit(dataset.batches, epochs=100)

# Evaluating the RNN
# rnn.evaluate(dataset.batches)

# Saving RNN weights
# rnn.save_weights('models/rnn', save_format='tf')

# Loading RNN weights
# rnn.load_weights('models/rnn')