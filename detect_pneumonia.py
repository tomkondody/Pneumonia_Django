# main.py
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping # <<< KEY CHANGE: Import EarlyStopping
import matplotlib.pyplot as plt
import os

# --- 1. Define Paths and Parameters ---
base_dir = 'chest_xray'
train_dir = os.path.join(base_dir, 'train')
test_dir = os.path.join(base_dir, 'test')

# Image and training parameters
IMG_HEIGHT = 150
IMG_WIDTH = 150
BATCH_SIZE = 32
# We can set a high number of epochs because EarlyStopping will halt training
# when the model is at its best.
EPOCHS = 50

# --- 2. Prepare the Data ---

train_image_generator = ImageDataGenerator(
    rescale=1./255,
    rotation_range=45,
    width_shift_range=.15,
    height_shift_range=.15,
    horizontal_flip=True,
    zoom_range=0.5,
    validation_split=0.2
)

test_image_generator = ImageDataGenerator(rescale=1./255)

# --- Create Data Generators ---

train_data_gen = train_image_generator.flow_from_directory(
    batch_size=BATCH_SIZE,
    directory=train_dir,
    shuffle=True,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    class_mode='binary',
    subset='training'
)

val_data_gen = train_image_generator.flow_from_directory(
    batch_size=BATCH_SIZE,
    directory=train_dir,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    class_mode='binary',
    subset='validation'
)

test_data_gen = test_image_generator.flow_from_directory(
    batch_size=BATCH_SIZE,
    directory=test_dir,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    class_mode='binary'
)

# --- 3. Build the CNN Model ---

model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dropout(0.5),
    Dense(512, activation='relu'),
    Dense(1, activation='sigmoid')
])

# --- 4. Compile the Model ---

model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

model.summary()

# --- 5. Train the Model with Early Stopping ---

# <<< KEY CHANGE: Create an EarlyStopping callback.
# It will monitor the validation loss.
# 'patience=5' means it will wait 5 epochs for improvement before stopping.
# 'restore_best_weights=True' ensures the model is returned to its best state.
early_stopper = EarlyStopping(
    monitor='val_loss',
    patience=5,
    verbose=1,
    restore_best_weights=True
)

history = model.fit(
    train_data_gen,
    steps_per_epoch=train_data_gen.samples // BATCH_SIZE,
    epochs=EPOCHS,
    validation_data=val_data_gen,
    validation_steps=val_data_gen.samples // BATCH_SIZE,
    callbacks=[early_stopper] # Pass the callback to the fit method
)

# --- 6. Evaluate the Model ---

print("\n--- Evaluating on Test Data ---")
test_loss, test_accuracy = model.evaluate(test_data_gen, steps=test_data_gen.samples // BATCH_SIZE)
print(f"Test Accuracy: {test_accuracy * 100:.2f}%")

# --- 7. Visualize Training Results ---

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

# Get the number of epochs that actually ran
epochs_ran = len(acc)
epochs_range = range(epochs_ran)

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

# --- 8. Save the Model ---
model.save('pneumonia_detection_model_final.h5')
print("\nModel.h5")
