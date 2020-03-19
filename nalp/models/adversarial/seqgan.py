import tensorflow as tf
import numpy as np
from tensorflow.keras import layers

import nalp.utils.logging as l
from nalp.models.base import AdversarialModel, Model
from nalp.models.recurrent.lstm import LSTM

logger = l.get_logger(__name__)


class Generator(LSTM):
    """
    """

    def __init__(self, vocab_size, embedding_size, hidden_size):
        """
        """
        
        # Overrides its parent class with any custom arguments if needed
        super(Generator, self).__init__(vocab_size=vocab_size, embedding_size=embedding_size, hidden_size=hidden_size)

    def generate_batch(self, batch_size=1, length=1, temperature=1.0):
        """
        """

        # Encoding the start string into tokens
        start_batch = tf.zeros([batch_size, 1])

        # Creating an empty list to hold the sampled_tokens
        sampled_batch = tf.zeros([batch_size, 1], dtype='int64')

        # Resetting the network states
        self.reset_states()

        # For every possible generation
        for i in range(length):
            # Predicts the current token
            preds = self(start_batch)

            # Removes the first dimension of the tensor
            preds = tf.squeeze(preds, 1)

            # Regularize the prediction with the temperature
            preds /= temperature

            # Samples a predicted token
            start_batch = tf.random.categorical(preds, num_samples=1)

            #
            sampled_batch = tf.concat([sampled_batch, start_batch], axis=1)

        sampled_batch = sampled_batch[:, 1:]

        return sampled_batch

class SeqGAN(AdversarialModel):
    """A SeqGAN class is the one in charge of Sequence Generative Adversarial Networks implementation.

    References:
        

    """

    def __init__(self, encoder, vocab_size=1, embedding_size=1, hidden_size=1):
        """Initialization method.

        Args:
            

        """

        logger.info('Overriding class: AdversarialModel -> SeqGAN.')

        self.encoder = encoder

        # Creating the discriminator network
        # D = Discriminator(n_samplings, alpha, dropout_rate)

        # Creating the generator network
        G = Generator(vocab_size, embedding_size, hidden_size)

        # Overrides its parent class with any custom arguments if needed
        super(SeqGAN, self).__init__(None, G, name='seqgan')

    @tf.function
    def G_pre_step(self, x, y):
        """Performs a single batch optimization step.

        Args:
            x (tf.Tensor): A tensor containing the inputs.

        """

        # Using tensorflow's gradient
        with tf.GradientTape() as tape:
            # Calculate the predictions based on inputs
            preds = self.G(x)

            # Calculate the loss
            loss = self.loss(y, preds)

        # Calculate the gradient based on loss for each training variable
        gradients = tape.gradient(loss, self.G.trainable_variables)

        # Apply gradients using an optimizer
        self.G_optimizer.apply_gradients(
            zip(gradients, self.G.trainable_variables))

    @tf.function
    def D_pre_step(self, x, y):
        """
        """

        pass



    def pre_fit(self, batches, epochs=100):
        """
        """

        logger.info('Pre-fitting generator ...')

        # Iterate through all epochs
        for e in range(epochs):
            logger.info(f'Epoch {e+1}/{epochs}')

            # Iterate through all possible training batches
            for x_batch, y_batch in batches:
                # Performs the optimization step
                self.G_pre_step(x_batch, y_batch)

        logger.info('Pre-fitting discriminator ...')

        # Iterate through all epochs
        for e in range(epochs):
            logger.info(f'Epoch {e+1}/{epochs}')

            # Iterate through all possible training batches
            for x_batch, _ in batches:
                #
                batch_size, max_length = x_batch.shape[0], x_batch.shape[1]

                #
                x_fake_batch = self.G.generate_batch(batch_size, max_length, 0.5)

                #
                x_batch = tf.concat([x_batch, x_fake_batch], axis=0)

                #
                y_batch = tf.concat([tf.zeros(batch_size,), tf.ones(batch_size,)], axis=0)

                #
                for _ in range(3):
                    #

                    indices = np.random.choice(x_batch.shape[0], batch_size, replace=False)

                    #
                    self.D_pre_step(tf.gather(x_batch, indices), tf.gather(y_batch, indices))