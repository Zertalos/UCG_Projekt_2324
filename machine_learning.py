import numpy as np
import pandas as pd

import tensorflow as tf

from src.ConfigManager.config_store import ConfigStoreManager

config_store = ConfigStoreManager()[ConfigStoreManager.MAIN_CONFIG_NAME]

BASE_OUTPUT_FOLDER = config_store["output_folder"]

checkpoint_path = './checkpoints/ui_poc'


def prepare():
    print(f"TensorFlow version = {tf.__version__}\n")
    BASE_OUTPUT_FOLDER = config_store["output_folder"]

    df = pd.read_csv(f"{BASE_OUTPUT_FOLDER}/single_data.csv")
    grouped = df.groupby('Fahrtnummer', sort=False)

    min_lat = df['lat'].min()
    min_lon = df['lon'].min()
    max_lat = df['lat'].max()
    max_lon = df['lon'].max()

    inputs = []
    outputs = []

    drives = []  # yes, its a stupid intermediary copy
    for _, drive_entry in grouped:
        drive = []
        for i in range(len(drive_entry)):
            dp = drive_entry.iloc[i]
            through_traffic = 0
            if (dp['Typ'] == 'durch'):
                through_traffic = 1
            drive.append(
                [(float(dp['lat']) - min_lat) / (max_lat - min_lat), (float(dp['lon']) - min_lon) / (max_lon - min_lon),
                 float(dp['heading']), float(dp['speed']), float(through_traffic)])
        drives.append(drive)

    # Set a fixed random seed value, for reproducibility, this will allow us to get
    # the same random numbers each time the notebook is run
    SEED = 191285461
    np.random.seed(SEED)
    tf.random.set_seed(SEED)

    inputs = []
    outputs = []

    window = 5
    for drive in drives:
        tensor = []
        # for i in range(0, len(drive) - window + 1, window):  # segmenting window
        for i in range(0, len(drive) - window + 1, 1):  # sliding window
            inputs.append(drive[i:i + window][:-1])
            outputs.append(drive[0][-1])

    inputs = np.array(inputs).astype('float32')
    outputs = np.array(outputs).astype('float32').reshape((-1, 1))

    print("Data set parsing and preparation complete.")
    return inputs, outputs


def train(inputs, outputs):
    # https://stackoverflow.com/a/37710486/2020087
    num_inputs = len(inputs)
    randomize = np.arange(num_inputs)
    np.random.shuffle(randomize)

    inputs = inputs[randomize]
    outputs = outputs[randomize]

    TRAIN_SPLIT = int(0.6 * num_inputs)
    TEST_SPLIT = int(0.2 * num_inputs + TRAIN_SPLIT)

    inputs_train, inputs_test, inputs_validate = np.split(inputs, [TRAIN_SPLIT, TEST_SPLIT])
    outputs_train, outputs_test, outputs_validate = np.split(outputs, [TRAIN_SPLIT, TEST_SPLIT])

    print("Data set randomization and splitting complete.")
    # callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=5)
    # build the model and train it
    model = create_model()
    history = model.fit(inputs_train, outputs_train, epochs=10, batch_size=32,
                        validation_data=(inputs_validate, outputs_validate))  # , callbacks=[callback])
    model.save_weights(checkpoint_path)
    model.summary()
    return model, inputs_test, outputs_test
    print("Data set training complete.")


def create_model():
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(100, activation='relu'))
    model.add(tf.keras.layers.Dense(50, activation='relu'))
    model.add(tf.keras.layers.Dense(40, activation='relu'))
    model.add(tf.keras.layers.Dense(30, activation='relu'))
    model.add(tf.keras.layers.Dense(30, activation='relu'))
    model.add(tf.keras.layers.Dense(30, activation='relu'))
    model.add(tf.keras.layers.Dense(30, activation='relu'))
    model.add(tf.keras.layers.Dense(30, activation='relu'))
    model.add(tf.keras.layers.Dense(30, activation='relu'))
    model.add(tf.keras.layers.Dense(30, activation='relu'))
    model.add(tf.keras.layers.Dense(30, activation='relu'))
    model.add(tf.keras.layers.Dense(30, activation='relu'))
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
    model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
    #    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3), loss="sparse_categorical_crossentropy", metrics=['accuracy','mse'])
    return model


def run(model, inputs_test, outputs_test):
    # use the model to predict the test inputs
    model.evaluate(inputs_test, outputs_test, batch_size=1)


inputs = []
outputs = []

if __name__ == '__main__':
    inputs, outputs = prepare()
    model, inputs_test, outputs_test = train(inputs, outputs)
    # model = create_model()
    # model.load_weights(checkpoint_path)
    run(model, inputs_test, outputs_test)
    while True:
        i = int(input())
        print("Input: ", inputs[i:i + 1])
        print("Prediction:", model.predict(inputs[i:i + 1]))
        print("Actual:", outputs[i])


