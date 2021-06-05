from tensorflow import keras as K

MODEL_PATH = "/home/giuseppe/Documents/Master/progetto/analysis/music/saved_model/autoencoder_music.h5"

encoder = K.models.load_model(filepath=MODEL_PATH)