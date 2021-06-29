from typing import List, Tuple

import tensorflow as tf
from tensorflow import keras as k
from tensorflow.keras import layers, optimizers

dilation_rates = [2, 4, 8, 16]
conv_layers = [64, 32, 16, 8]

steps, channels = 431, 128

# Encoder
input_layer = layers.Input(shape=(steps, channels),
                           name="input_decoder")
# Feature extraction with dilated conv
enc_conv = layers.Conv1D(filters=channels,
                         kernel_size=2,
                         padding="causal",
                         activation="relu",
                         dilation_rate=dilation_rates[0],
                         name=f"{dilation_rates[0]}dilated_conv")(input_layer)
for dilation_rate in dilation_rates[1:]:
    enc_conv = layers.Conv1D(filters=channels,
                             kernel_size=2,
                             padding="causal",
                             activation="relu",
                             dilation_rate=dilation_rate,
                             name=f"{dilation_rate}dilated_conv")(enc_conv)
# Dimensionality reduction
for conv_layer in conv_layers:
    enc_conv = layers.Conv1D(filters=conv_layer,
                             kernel_size=5,
                             strides=2,
                             activation="relu",
                             name=f"{conv_layer}enc_conv")(enc_conv)

# Decoder
dec_conv = layers.Conv1DTranspose(filters=conv_layers[-1],
                                  kernel_size=5,
                                  strides=2,
                                  activation="relu",
                                  name=f"{conv_layers[-1]}deconv_layer")(enc_conv)
for deconv_layer in reversed(conv_layers[:-1]):
    dec_conv = layers.Conv1DTranspose(filters=deconv_layer,
                                      kernel_size=5,
                                      strides=2,
                                      activation="relu",
                                      name=f"{deconv_layer}deconv_layer")(dec_conv)

for dilation_rate in reversed(dilation_rates):
    dec_conv = layers.Conv1DTranspose(
        filters=channels,
        kernel_size=2,
        padding="same",
        activation="relu",
        dilation_rate=dilation_rate,
        name=f"{dilation_rate}dilated_deconv"
    )(dec_conv)

dec_conv = layers.ZeroPadding1D(padding=1)(dec_conv)
dec_conv = layers.Conv1D(filters=channels,
                         kernel_size=2,
                         padding="same",
                         activation="relu")(dec_conv)

autoencoder = K.Model(inputs=input_layer, outputs=dec_conv,
                      name="autoencoder")

autoencoder.compile(optmizer=optimizers.Adam(learning_rate=3e-4),
                    loss="msle",
                    metrics=["mse", "mae"])

autoencoder.save("autoencoder.h5")
