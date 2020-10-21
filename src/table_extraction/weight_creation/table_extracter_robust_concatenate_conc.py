from keras.layers import Dense, Conv2D, Permute, MaxPooling2D, AveragePooling2D, LSTM, Reshape, Flatten, Dropout
from keras.layers import multiply, add, average, maximum, Concatenate, Lambda
import keras
import tensorflow as tf

from sklearn.model_selection import train_test_split
import numpy as np
import os
import cv2

def crop(dimension, start, end):
    # Crops (or slices) a Tensor on a given dimension from start to end
    # example : to crop tensor x[:, :, 5:10]
    # call slice(2, 5, 10) as you want to crop on the second dimension
    def func(x):
        if dimension == 0:
            return x[start: end]
        if dimension == 1:
            return x[:, start: end]
        if dimension == 2:
            return x[:, :, start: end]
        if dimension == 3:
            return x[:, :, :, start: end]
        if dimension == 4:
            return x[:, :, :, :, start: end]
    return Lambda(func)

petal = 1 #1,2 or 4
root = r"C:\Users\Zach\Downloads\Table_extract_robust"





data_final = np.load(os.path.join(root, "DATA_concatenate_cols.npy"), allow_pickle=True)
LABELS = np.load(os.path.join(root, "LABELS_concatenate_cols.npy"), allow_pickle=True)

print(data_final.shape)

x_train, x_valid, y_train, y_valid = train_test_split(data_final, LABELS, test_size = 0.2, shuffle = True)

keras_input = keras.layers.Input(shape=(100,200, 1))



center_data_original = crop(2, 90, 110)(keras_input)
center_data_original = Conv2D(32, (5,5), activation="relu")(center_data_original)
center_data_original = MaxPooling2D((2,2))(center_data_original)
for i in range(3):
    temp0 = Conv2D(32, (3,3), activation="relu", padding='same')(center_data_original)
    temp1 = Conv2D(32, (3,3), activation="relu", padding='same')(temp0)
    temp2 = Conv2D(32, (3,3), activation="relu", padding='same')(temp1)
    center_data_original = keras.layers.concatenate([center_data_original,temp2])
    center_data_original = Conv2D(32, (3,3), activation="relu")(center_data_original)
    center_data_original = MaxPooling2D((2,1))(center_data_original)
    center_data_original = Dropout(.2)(center_data_original)
center_data_original = Flatten()(center_data_original)

ver_data = AveragePooling2D((100,1))(keras_input)
ver_data = MaxPooling2D((1,4))(ver_data)
ver_data = Conv2D(6, (1, 3), activation='relu')(ver_data)
ver_data = Conv2D(6, (1, 3), activation='relu')(ver_data)
ver_data = Conv2D(6, (1, 3), activation='relu')(ver_data)
ver_data = Dropout(.5)(ver_data)
ver_data = Flatten()(ver_data)

full_data = MaxPooling2D((2,2))(keras_input)
full_data = Conv2D(32, (5, 5), activation='relu')(full_data)
full_data = MaxPooling2D((2,2))(full_data)
full_data = Conv2D(64, (3, 3), activation='relu')(full_data)
full_data = MaxPooling2D((2,2))(full_data)
full_data = Conv2D(64, (3, 3), activation='relu')(full_data)
full_data = MaxPooling2D((2,2))(full_data)
full_data = Conv2D(64, (3, 3), activation='relu')(full_data)
full_data = MaxPooling2D((2,2))(full_data)
full_data = Dropout(.5)(full_data)
full_data = Flatten()(full_data)

data = Concatenate()([ver_data, full_data])
data = Dense(512, activation='relu')(data)
data = Dropout(.2)(data)
data = Dense(512, activation='relu')(data)
out = Dense(1, activation='sigmoid')(data)


conc = keras.models.Model(inputs=keras_input, outputs= out)
conc.compile(loss="binary_crossentropy", optimizer="adam", metrics = ["accuracy"])
conc.fit(x_train, y_train[:,0], validation_data = (x_valid, y_valid[:,0]), epochs = 30, batch_size = 32)
    
conc.save(r"C:\Users\Zach\Downloads\Table_extract_robust\conc_col.h5")

pred = conc.predict(data_final)
if(1):
    for i in range(len(pred)):
        #if((pred[i][0] > .5) != LABELS[i][0]):
        if(LABELS[i][0]):
            print(pred[i][0], " ", LABELS[i][0])
            #print(LABELS[i][1], " ", LABELS[i][2])
            print("")
            temp_img = cv2.cvtColor(data_final[i],cv2.COLOR_GRAY2RGB)
            cv2.line(temp_img, (100, 0), (100, 100), (255,0,0), 1)
            cv2.line(temp_img, (90, 0), (90, 100), (0,255,0), 1)
            cv2.line(temp_img, (110, 0), (110, 100), (0,255,0), 1)
            cv2.imshow('image', temp_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
else:
    for i in range(len(pred)):
        if(((pred[i][0] > .5) != LABELS[i][0]) or ((pred[i][1] > .5) != LABELS[i][1]) or ((pred[i][2] > .5) != LABELS[i][2])):
            print(pred[i][0], " ", LABELS[i][0])
            print(pred[i][1], " ", LABELS[i][1])
            print(pred[i][2], " ", LABELS[i][2])
            print("")
            cv2.imshow('image',data_final[i])
            cv2.waitKey(0)
            cv2.destroyAllWindows()


