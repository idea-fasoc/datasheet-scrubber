from keras.layers import Dense, Conv2D, Permute, MaxPooling2D, AveragePooling2D, LSTM, Reshape, Flatten, Dropout
from keras.layers import multiply, add, average, maximum, concatenate
import keras

from sklearn.model_selection import train_test_split
import numpy as np
import os
import cv2


root = r"C:\Users\Zach\Downloads\Table_extract_robust"
dim = 800
section_input_width = 20

data_final = np.load(os.path.join(root, "DATA_rows.npy"), allow_pickle=True)
LABELS = np.load(os.path.join(root, "LABELS_rows.npy"), allow_pickle=True)


print(data_final.shape)
print(LABELS.shape)

x_train, x_valid, y_train, y_valid = train_test_split(data_final, LABELS, test_size = 0.2, shuffle = True)

y_train = np.transpose(y_train)
y_valid = np.transpose(y_valid)

print(y_train.shape)

losses = {
	"out_binary": "binary_crossentropy",
	"out_loc": "mse",
}

metrics = {
	"out_binary": "accuracy",
}

if(0):
    for h in range(len(data_final)):
        pixel_data = cv2.cvtColor(data_final[h],cv2.COLOR_GRAY2RGB)
        if(LABELS[h][0]  > .5):
            print(LABELS[h][1])
            reconvert = int((LABELS[h][1] + 1)*section_input_width/2)+10
            cv2.line(pixel_data, (-1, reconvert), (dim, reconvert), (255,0,0), 1)

        cv2.imshow("image", pixel_data)
        cv2.waitKey();


keras_input = keras.layers.Input(shape=(section_input_width*2,dim,1), name='keras_input')

data = Conv2D(16, (3, 3), activation='relu')(keras_input)
for i in range(5):
    data = Conv2D(8, (3, 3), activation='relu')(data)
    data = Dropout(.2)(data)

data0 = Conv2D(8, (3, 3), activation='relu')(data)
data0 = Conv2D(8, (3, 3), activation='relu')(data0)
data0 = Flatten()(data0)

data1 = Conv2D(8, (3, 3), activation='relu')(data)
data1 = Conv2D(8, (3, 3), activation='relu')(data1)
data1 = Flatten()(data1)

#data0 = Dense(256, activation='relu')(data0)
#data1 = Dense(256, activation='relu')(data1)
out_binary = Dense(1, activation='sigmoid', name = "out_binary")(data0)
out_loc = Dense(1, activation='tanh', name = "out_loc")(data1)
row_finder = keras.models.Model(inputs=keras_input, outputs=[out_binary, out_loc])
row_finder.compile(loss=losses, optimizer="adam", metrics = metrics)
row_finder.fit(x_train, [y_train[0], y_train[1]], validation_data = (x_valid, [y_valid[0], y_valid[1]]), epochs = 100, batch_size = 64)

pred_binary, pred_input = row_finder.predict(x_valid)


for h in range(len(pred_binary)):
    pixel_data = cv2.cvtColor(x_valid[h],cv2.COLOR_GRAY2RGB)
    if(pred_binary[h]  > .5):
        reconvert = int((pred_input[h] + 1)*section_input_width/2)+10
        cv2.line(pixel_data, (-1, reconvert), (dim, reconvert), (255,0,0), 1)
        print(pred_binary[h], " ", pred_input[h], "   ", y_valid[0][h], y_valid[1][h])
        cv2.imshow("image", pixel_data)
        cv2.waitKey();