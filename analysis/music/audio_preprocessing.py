"""
Audio preprocessing pipeline. Code inspired by:
    https://www.youtube.com/watch?v=O04v3cgHNeM&t=687s
1) load a file
2) pad the signal (if necessary
3) extract log spectrogram
4) normalize the spectrogram
5) save the normalized spectrogram

PreprocessingPipeline
"""
import os
import warnings

from tqdm import tqdm

import librosa
import librosa.display

import numpy as np

warnings.filterwarnings("ignore")

DATA_DIR = "/home/giuseppe/Documents/Master/progetto/analysis/music/music_data"
OUTPUT_DIR = "preprocessed_data/"


def loader(filepath: str,
           s_r: int = 22050,
           length_in_s: int = 30,
           mono: bool = True) -> np.array:
    """
    This function load a file

    Parameters
    ----------
    filepath : str
        path of the file to load
    s_r :
    length_in_s :
    mono : bool
        Default True. True if you want to load the file in mono

    Returns
    -------
    np.array
    """
    loaded_mp3, _ = librosa.load(filepath,
                                 sr=s_r,
                                 duration=length_in_s,
                                 mono=mono)
    return loaded_mp3


def minmax_normalizer(array_to_normalize: np.array,
                      min_val: int = 0,
                      max_val: int = 1) -> np.array:
    """
    minmax_normalizer normalizes the spectrogram
    """
    x_std = (array_to_normalize - array_to_normalize.min()) \
            / (array_to_normalize.max() - array_to_normalize.min())
    x_scaled = x_std * (max_val - min_val) + min_val
    return x_scaled


def padder(array: np.array, num_missing_items: int,
           mode: str = "constant", how: str = "left") -> np.array:
    """Padder is responsible to apply padding to an array"""
    if how == "left":
        padded_array = np.pad(array,
                              (num_missing_items, 0),
                              mode=mode)
        return padded_array

    if how == "right":
        padded_array = np.pad(array,
                              (0, num_missing_items),
                              mode=mode)
        return padded_array

    raise ValueError("Only 'left' or 'right' are accepted as arguments")


def mel_log_spectrogram_extractor(signal_array: np.array,
                                  s_r: int = 22050) -> np.array:
    """
    log_spectrogram_extractor extract log spectrograms in Db from a time
    series signal
    """
    mel_ps = librosa.feature.melspectrogram(y=signal_array, sr=s_r)
    ps_db = librosa.power_to_db(mel_ps, ref=np.max)
    return ps_db


def log_spectrogram_extractor(signal_array: np.array,
                              frame_size: int = 512,
                              hop_length: int = 256) -> np.array:
    """
    log_spectrogram_extractor extract log spectrograms in Db from a time
    series signal
    """
    stft = librosa.stft(signal_array,
                        n_fft=frame_size,
                        hop_length=hop_length)[:-1]
    # (1+framesize/2, num_frames)
    # 1024 -> 513 -> 512
    spectrogram = np.abs(stft)
    log_spectrogram = librosa.amplitude_to_db(spectrogram)
    return log_spectrogram


def mfcc_extractor(signal_array: np.array,
                   frame_size: int = 512,
                   hop_length: int = 256,
                   s_r: int = 22050,
                   n_mfcc: int = 20):
    MFCCs = librosa.feature.mfcc(signal, s_r,
                                 n_fft=frame_size, hop_length=hop_length)
    return MFCCs


if __name__ == '__main__':
    FRAME_SIZE = 512
    HOP_LENGTH = 256
    SAMPLE_RATE = 22050
    DURATION = 10
    # loop over all the mp3 in the folder
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for file in tqdm(os.listdir(DATA_DIR)):
        file_path = os.path.join(DATA_DIR, file)
        output_name = os.path.join(OUTPUT_DIR, file[:-4] + ".npy")
        if os.path.exists(output_name):
            continue
        # load the mp3 with librosa

        try:
            signal = loader(file_path, s_r=SAMPLE_RATE, length_in_s=DURATION)
        except EOFError as e:
            print(e)
            print(f"could not process {file_path}")
            continue

        N_EXPECT_SAMPLES = int(SAMPLE_RATE * DURATION)
        # if the song is shorter than 30 seconds pad the end
        if len(signal) < N_EXPECT_SAMPLES:
            n_missing_samples = N_EXPECT_SAMPLES - len(signal)
            signal = padder(signal, n_missing_samples, how="right")

        signal = mel_log_spectrogram_extractor(signal, s_r=SAMPLE_RATE)
        # normalize the array
        signal = minmax_normalizer(signal)
        # save to file using numpy
        with open(output_name, "wb") as saver_handler:
            np.save(saver_handler, signal)
