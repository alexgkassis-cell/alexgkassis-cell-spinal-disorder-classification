"""Reference CNN topology used in final C08 study. TensorFlow is optional."""


def make_reference_cnn(input_shape=(128, 128, 1)):
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise RuntimeError("TensorFlow is required: pip install -e '.[inference]'") from exc
    layers = tf.keras.layers
    return tf.keras.Sequential([
        layers.Input(shape=input_shape),
        layers.Conv2D(32, 3, activation="relu", padding="same"),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation="relu", padding="same"),
        layers.MaxPooling2D(),
        layers.Conv2D(128, 3, activation="relu", padding="same"),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation="relu"),
        layers.Dense(3, activation="softmax"),
    ], name="reference_cnn")
