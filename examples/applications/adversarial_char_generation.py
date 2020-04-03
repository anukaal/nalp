import tensorflow as tf

from nalp.corpus.text import TextCorpus
from nalp.encoders.integer import IntegerEncoder
from nalp.models.relgan import RelGAN

# When generating artificial text, make sure
# to use the same data, classes and parameters
# as the pre-trained network

# Creating a character TextCorpus from file
corpus = TextCorpus(from_file='data/text/chapter1_harry.txt', type='char')

# Creating an IntegerEncoder
encoder = IntegerEncoder()

# Learns the encoding based on the TextCorpus dictionary and reverse dictionary
encoder.learn(corpus.vocab_index, corpus.index_vocab)

# Creating the SeqGAN
seqgan = RelGAN(encoder=encoder, vocab_size=corpus.vocab_size, max_length=10,
                embedding_size=256, n_slots=5, n_heads=5, head_size=25, n_blocks=1, n_layers=3,
                n_filters=[64, 128, 256], filters_size=[3, 5, 5], dropout_rate=0.25, tau=5)

# Loading pre-trained SeqGAN weights
seqgan.load_weights('trained/relgan').expect_partial()

# Now, for the inference step, we build with a batch size equals to 1
seqgan.G.build((1, 10))

# Defining an start string to generate the text
start_string = 'Mr.'

# Generating artificial text
text = seqgan.G.generate_text(start=start_string, length=1000, temperature=1)

# Outputting the text
print(start_string + ''.join(text))
