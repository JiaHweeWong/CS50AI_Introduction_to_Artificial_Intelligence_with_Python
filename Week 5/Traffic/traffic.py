import cv2
import numpy as np
import os
import sys
import tensorflow as tf
import ntpath

from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Dropout

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    list_of_all_img_arr = []
    list_of_all_labels = []

    list_of_labels = os.listdir(data_dir)
    for label in list_of_labels: # for each label
        label_path = os.path.join(data_dir, label)
        img_filenames = os.listdir(label_path)
        for img_filename in img_filenames: # for each image
            img_path = os.path.join(label_path, img_filename)
            img_arr = cv2.imread(img_path) # read in the image as a numpy array
            img_arr = cv2.resize(img_arr, (IMG_WIDTH, IMG_HEIGHT)) # resize the image
            list_of_all_img_arr.append(img_arr) # Append the image numpy array to a list
            list_of_all_labels.append(label) # Append the labels to a list

    return (list_of_all_img_arr, list_of_all_labels) # return a tuple of image arrays and labels

def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    model = tf.keras.models.Sequential([
        Conv2D(32, (3, 3), activation = "relu", input_shape = (IMG_WIDTH, IMG_HEIGHT, 3)),
        MaxPooling2D(pool_size= (2, 2)),
        Conv2D(32, (3, 3), activation = "relu"),
        MaxPooling2D(pool_size = (2, 2)),
        # Conv2D(32, (3, 3), activation = "relu"),
        # MaxPooling2D(pool_size = (2, 2)),
        Flatten(),
        Dense(128, activation="relu"),
        Dropout(0.5),
        # Dense(64, activation="relu"),
        # Dropout(0.5),

        Dense(NUM_CATEGORIES, activation = 'softmax')
    ])

    model.compile(
        optimizer = "adam",
        loss = "categorical_crossentropy",
        metrics = ['accuracy']
    )

    return model


if __name__ == "__main__":
    main()
