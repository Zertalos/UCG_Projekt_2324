import numpy as np
import pandas as pd

import tensorflow as tf

from src.ConfigManager.config_store import ConfigStoreManager

config_store = ConfigStoreManager()[ConfigStoreManager.MAIN_CONFIG_NAME]

BASE_OUTPUT_FOLDER = config_store["output_folder"]


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
    SEED = 1337
    np.random.seed(SEED)
    tf.random.set_seed(SEED)

    # the list of gestures that data is available for
    classification = [
        "through-traffic"
    ]

    SAMPLES_PER_CLASSIFICATION = 1  # TODO

    NUM_CLASSIFICATIONS = len(classification)

    # create a one-hot encoded matrix that is used in the output
    ONE_HOT_ENCODED_CLASSIFICATIONS = np.eye(NUM_CLASSIFICATIONS)

    # read each csv file and push an input and output
    # NOTE extendable for extra classifications (only 1 rn)
    inputs = []
    outputs = []
    for index, classification in enumerate(classification):
        print(f"Processing '{classification}'.")

        output = ONE_HOT_ENCODED_CLASSIFICATIONS[index]

        # TODO adjust for own data
        # calculate the number of gesture recordings in the file
        window = 5
        for drive in drives:
            tensor = []
            for i in range(0, len(drive) - window + 1, window):  # segmenting window
                # for i in range(0, len(drive)-window+1, 1): #sliding window
                inputs.append(drive[i:i + window][:-1])
                outputs.append(drive[0][-1])

    ##            print("----------------")
    ##            for i in tensor:
    ##                print(i)

    # convert the list to numpy array
    inputs = np.array(inputs)
    outputs = np.array(outputs)

    print("Data set parsing and preparation complete.")
    return inputs, outputs


def train(inputs, outputs):
    # Randomize the order of the inputs, so they can be evenly distributed for training, testing, and validation
    # https://stackoverflow.com/a/37710486/2020087
    num_inputs = len(inputs)
    randomize = np.arange(num_inputs)
    np.random.shuffle(randomize)

    # Swap the consecutive indexes (0, 1, 2, etc) with the randomized indexes
    inputs = inputs[randomize]
    outputs = outputs[randomize]

    # Split the recordings (group of samples) into three sets: training, testing and validation
    TRAIN_SPLIT = int(0.6 * num_inputs)
    TEST_SPLIT = int(0.2 * num_inputs + TRAIN_SPLIT)

    inputs_train, inputs_test, inputs_validate = np.split(inputs, [TRAIN_SPLIT, TEST_SPLIT])
    outputs_train, outputs_test, outputs_validate = np.split(outputs, [TRAIN_SPLIT, TEST_SPLIT])

    print("Data set randomization and splitting complete.")

    # build the model and train it
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(50, activation='relu'))  # relu is used for performance
    model.add(tf.keras.layers.Dense(15, activation='relu'))
    model.add(tf.keras.layers.Dense(1,
                                    activation='softmax'))  # softmax is used, because we only expect one gesture to occur per input
    model.compile(optimizer='rmsprop', loss='mse', metrics=['mae'])
    history = model.fit(inputs_train, outputs_train, epochs=600, batch_size=1,
                        validation_data=(inputs_validate, outputs_validate))
    model.save_weights('./checkpoints/ui_poc')
    print("Data set training complete.")


def run():
    # use the model to predict the test inputs
    predictions = model.predict(inputs_test)

    # print the predictions and the expected ouputs
    print("predictions =\n", np.round(predictions, decimals=3))
    print("actual =\n", outputs_test)


inputs = []
outputs = []

if __name__ == '__main__':
    inputs, outputs = prepare()
    train(inputs, outputs)
    run()

