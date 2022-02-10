import tensorflow as tf
import numpy as np
print(f'Tenforflow version: {tf.__version__}')
from argparse import ArgumentParser
import json

def getArgs():
    parser=ArgumentParser()
    parser.add_argument('--input', '-i', action='store', help='Input file')
    parser.add_argument('--output', '-o', action='store', help='Output file')
    args = parser.parse_args()
    return args

num_classes = 10
input_shape = (28, 28, 1)

def create_model(hyperparameters={}):
    activation=hyperparameters.get('activation', 'relu')
    optimizer=hyperparameters.get('optimizer', 'adam')
    n_dense_layers=hyperparameters.get('n_dense', 1)
    dropout=hyperparameters.get('dropout', 1)
    

    model = tf.keras.Sequential(
        [
            tf.keras.Input(shape=input_shape),
            tf.keras.layers.Conv2D(32, kernel_size=(3, 3), activation=activation),
            tf.keras.layers.MaxPool2D(pool_size=(2, 2)),
            tf.keras.layers.Conv2D(64, kernel_size=(3, 3), activation=activation),
            tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dropout(dropout)
        ]
    )

    while n_dense_layers > 0:
        model.add(
            tf.keras.layers.Dense(16 * n_dense_layers, activation=activation)
        )
        model.add(
            tf.keras.layers.Dropout(dropout)
        )        
        n_dense_layers -= 1
    
    model.add(tf.keras.layers.Dense(num_classes, activation="softmax"))

    model.summary()

    loss_fn = "categorical_crossentropy"

    model.compile(
        loss=loss_fn,
        optimizer=optimizer,
        metrics=['accuracy']
    )

    return model


def main():
    args = getArgs()
    input_file = args.input
    output_file = args.output

    with open(input_file, 'r') as f:
        hyperparameters=json.load(f)

    mnist = tf.keras.datasets.mnist
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0
    
    x_train = np.expand_dims(x_train, -1)
    x_test = np.expand_dims(x_test, -1)

    print("x_train shape:", x_train.shape)
    print(x_train.shape[0], "train samples")
    print(x_test.shape[0], "test samples")

    y_train = tf.keras.utils.to_categorical(y_train, num_classes)
    y_test = tf.keras.utils.to_categorical(y_test, num_classes)
    
    model = create_model(hyperparameters)

    batch_size=hyperparameters.get('batch_size', 128)
    epochs=hyperparameters.get('epochs', 5)

    model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=0.1)

    loss, acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"Test loss: {loss}")
    print(f"Test accuracy: {acc}")

    output = {
        'loss': loss,
        'accuracy': acc
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=4)

if __name__ == '__main__':
    main()