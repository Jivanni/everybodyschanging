import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from typing import List, Tuple

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
sns.set_theme()

from sklearn.model_selection import train_test_split
from sklearn.manifold import TSNE

from tqdm import tqdm

import tensorflow as tf
from tensorflow import keras as K
from tensorflow.keras import layers
from tensorflow.keras import optimizers
from tensorflow.keras import callbacks

from wavenet import Conv1dDilatedAutoencoder

HOME =  "./"
OUTPUTS = os.path.join(HOME, "outputs/")
DATA_DIR = os.path.join(HOME, "preprocessed_data")

dilation_rates = [2, 4, 8, 16]
conv_layers = [64, 32]

def load_spectrograms():

    file_names = os.listdir(DATA_DIR)
    path_list = [
                 os.path.join(DATA_DIR, filepath)
                 for filepath in file_names
                 ]

    data_list = []

    for npy_file in tqdm(path_list):
        data = np.load(npy_file).transpose()
        if data.shape[0] != 431:
            continue
        data_list.append(data)

    return np.stack(data_list)

if __name__ == "__main__":
    data_list = load_spectrograms()
    x_train, x_test = train_test_split(data_list, test_size=0.7)


    print(f"shape: {data_list[0].shape}")
    print(f"\ntrain size:\t{len(x_train)}\n"
          f"test size:\t{len(x_test)}\n"
          f"total:\t\t{len(data_list)}")

    steps, channels = data_list[0].shape
    BS = 64

    callback_list = [
        callbacks.EarlyStopping(
            monitor="val_loss",
            patience=5
        )
    ]

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
        dec_conv = layers.Conv1DTranspose(filters=channels,
                                 kernel_size=2,
                                 padding="same",
                                 activation="relu",
                                 dilation_rate=dilation_rate,
                                 name=f"{dilation_rate}dilated_deconv")(dec_conv)

    dec_conv = layers.ZeroPadding1D(padding=1)(dec_conv)
    dec_conv = layers.Conv1D(filters=channels,
                                 kernel_size=2,
                                 padding="same",
                                 activation="relu")(dec_conv)

    autoencoder = K.Model(inputs=input_layer, outputs=dec_conv)
    autoencoder.compile(loss="mse", optimizer=optimizers.Adam(3e-4), metrics=["mae", "msle"])

    history = autoencoder.fit(
            x=x_train, 
            y=x_train, 
            epochs=150, 
            batch_size=BS, 
            validation_split=0.2, 
            callbacks=callback_list
    )

    fig, ax = plt.subplots(ncols=1, nrows=3, sharex=True, dpi=300, figsize=plt.figaspect(0.5))
    ax[0].plot(history.epoch, history.history["loss"], label="train")
    ax[0].plot(history.epoch, history.history["val_loss"], label="validation")
    ax[0].set(ylabel="mse")
    ax[0].legend()

    ax[1].plot(history.epoch, history.history["mae"], label="train")
    ax[1].plot(history.epoch, history.history["val_mae"], label="validation")
    ax[1].set(ylabel="mae")

    ax[2].plot(history.epoch, history.history["msle"])
    ax[2].plot(history.epoch, history.history["val_msle"])
    ax[2].xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax[2].set(ylabel="msle")
    plt.savefig(os.path.join(OUTPUTS, "training.png"))

    reconstructed = autoencoder.predict(x_test)

    n = 10
    c = 0
    fig, ax = plt.subplots(3, n, dpi=300,
                           figsize=plt.figaspect(0.2))
    for j, (x, p) in enumerate(zip(x_test, reconstructed)):
        c += 1
        ax[0][j].imshow(x,
                        aspect="auto",
                        vmin=0, vmax=1)
        ax[0][j].axis("off")

        ax[1][j].imshow(p,
                        aspect="auto",
                        vmin=0, vmax=1)
        ax[1][j].axis("off")

        ax[2][j].imshow(x-p,
                        aspect="auto",
                        vmin=0, vmax=1)
        ax[2][j].axis("off")

        if c == n:
            break
    ax[0][0].set_ylabel("Original")
    ax[1][0].set_ylabel("Reconstructed")
    ax[2][0].set_ylabel("Difference")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS, "comparison.png"))

    autoencoder.save(os.path.join(OUTPUTS, "autoencoder.h5"))

    encoder = K.Model(inputs=input_layer, outputs=enc_conv, name="encoder")
    encoder.compile()
    encoder.save(os.path.join(OUTPUTS, "encoder.h5"))



    
    # extract hidden representations
    file_names = os.listdir(DATA_DIR)
    path_list = [
                 os.path.join(DATA_DIR, filepath)
                 for filepath in file_names
                 ]

    data_list = []

    for npy_file in tqdm(path_list):
        data = np.load(npy_file).transpose()
        if data.shape[0] != 431:
            continue
        data_list.append(data)

    everything = np.stack(data_list)

    data = encoder.predict(everything)

    data_df = pd.DataFrame(data, columns=[f"H{n}" for n in range(data.shape[1])])
    data_df["song_id"] = pd.Series([filename[:-4] for filename in file_names])

    data_df.to_csv(os.path.join(OUTPUTS, "hiddens.csv", index=False))
