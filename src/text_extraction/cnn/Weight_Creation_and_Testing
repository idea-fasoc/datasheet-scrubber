from sklearn.model_selection import train_test_split
import numpy
from numpy import zeros, ones
from numpy import asarray

from keras.preprocessing.text import Tokenizer
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Permute, MaxPooling2D, AveragePooling2D, LSTM, Embedding, Reshape
from keras.layers import multiply, add, average, maximum, concatenate
import keras

from keras.layers import Input
import tensorflow as tf

from keras.layers import Activation
from keras import backend as K
from keras.utils.generic_utils import get_custom_objects


from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import os

import pickle
import math
import pandas as pd
from sklearn.model_selection import StratifiedKFold


def compress(arr):
    compressed_arr = []
    for onedim in arr:
        compressed_arr.append(numpy.argmax(onedim))
    return numpy.array(compressed_arr) 


def custom_sig(x): #stops many NaN errors
    return (K.sigmoid(x) + math.pow(.1, 6))

 
ReEmbed = False
word_amount = 256
root_folder = r"D:\Full_Dataset"


Types = [d for d in os.listdir(root_folder)]
print(Types)
print(len(Types))

if(ReEmbed):
    raw_data = []
    labels_final = []

    #folder_locs = [os.path.join(root_folder, Type_iter, "TXTs") for Type_iter in Types]
    folder_locs = [os.path.join(root_folder, Type_iter, "TXTs_long") for Type_iter in Types]
    for folder_num, folder in enumerate(folder_locs):
        temp_types = [0 for i in range(len(Types))]
        temp_types[folder_num] = 1
        for file in os.listdir(folder):
            print(os.path.join(folder, file))
            with open(os.path.join(folder, file), "r") as file:
            #with open(os.path.join(folder, file), "rb") as file:
                content = file.read()
                raw_data.append(content)
                #raw_data.append(pickle.load(file))
                labels_final.append(temp_types)
    t = Tokenizer()
    t.fit_on_texts(raw_data)
    cin = input()
    with open(r'D:\tokenizer_long.pickle', 'wb') as handle:
        pickle.dump(t, handle, protocol=pickle.HIGHEST_PROTOCOL)


    vocab_size = len(t.word_index) + 1

    embeddings_index = dict()
    with open(r'C:\Users\Zach\Downloads\glove.840B.300d.txt', encoding="utf8") as f:
        for line in f:
            try:
                values = line.split()
                word = values[0]
                coefs = asarray(values[1:], dtype='float32')
                embeddings_index[word] = coefs
            except:
                pass
    print('Loaded %s word vectors.' % len(embeddings_index))



    embedding_matrix = zeros((vocab_size, 300))
    for word, i in t.word_index.items():
        embedding_vector = embeddings_index.get(word)

        if(embedding_vector is not None):      
            embedding_matrix[i] = embedding_vector
    print(embedding_matrix.shape)
    

    encoded_data = t.texts_to_sequences(raw_data)
    data_final = []
    for data in encoded_data:
        temp_array1D = []
        for iter in range(word_amount): #Use the first x words
            if(iter < len(data)):
                temp_array1D.append(data[iter])
            else:
                temp_array1D.append(0) #this number should corrispond to all zeros in the embedding matrix
        data_final.append(temp_array1D)
    
    data_final = numpy.array(data_final)
    labels_final = numpy.array(labels_final)

    numpy.save(os.path.join(root_folder + "DATA"), data_final)
    numpy.save(os.path.join(root_folder + "LABELS"), labels_final)
    numpy.save(os.path.join(root_folder + "EMB"), embedding_matrix)
else:
    data_final = numpy.load(os.path.join(root_folder + "DATA.npy"), allow_pickle=True)
    labels_final = numpy.load(os.path.join(root_folder + "LABELS.npy"), allow_pickle=True)
    embedding_matrix = numpy.load(os.path.join(root_folder + "EMB.npy"), allow_pickle=True)
    vocab_size = embedding_matrix.shape[0]

###############DEBUG 
conf_matrix = zeros((len(Types), len(Types)))
real_vec = zeros((len(Types)))
###############DEBUG 

kfold = StratifiedKFold(n_splits=5, shuffle=True)

labels_final_compressed = compress(labels_final)
print("here ", labels_final_compressed)
for train, test in kfold.split(data_final, labels_final_compressed):
    keras_input = keras.layers.Input(shape=(word_amount,), name='keras_input')
    print(train)
    word_window = [4, 8, 8, 32, 256, 256, 256]
    word_types =  [2, 2, 4, 4,  1,   2,   4]
    results = []
    training_outs = []
    e = Embedding(vocab_size, 300, weights=[embedding_matrix], input_length=word_amount, trainable=False)(keras_input)
    e = Reshape((word_amount, 300, 1))(e)

    for i in range(len(word_window)):
        data = Conv2D(word_types[i]*512, kernel_size=(1, 300), activation='softsign')(e)
        data = Permute((1, 3, 2))(data)

        data = MaxPooling2D(pool_size=(word_window[i], 1), strides=(1,1))(data)
        data = AveragePooling2D(pool_size=(1, word_types[i]), strides=(1,word_types[i]))(data)


        data = MaxPooling2D(pool_size=(256-word_window[i]+1, 1))(data)
        data = keras.layers.Flatten()(data)
        data = keras.layers.Dropout(0.5)(data)
        data = Dense(128, activation= 'softsign')(data)
        results.append(data)
        training_outs.append(Dense(len(Types), activation= custom_sig)(data))

    word_window2 = [16, 32, 253, 253, 253]
    word_types2 =  [2,  2,  1,   2,   4]
    for i in range(len(word_window2)):
        data = Conv2D(word_types2[i]*512, kernel_size=(4, 300), activation='softsign')(e)
        data = Permute((1, 3, 2))(data)

        data = MaxPooling2D(pool_size=(word_window2[i], 1), strides=(1,1))(data)
        data = AveragePooling2D(pool_size=(1, word_types2[i]), strides=(1,word_types2[i]))(data)


        data = MaxPooling2D(pool_size=(256-3-word_window2[i]+1, 1))(data)
        data = keras.layers.Flatten()(data)
        data = keras.layers.Dropout(0.5)(data)
        data = Dense(128, activation= 'softsign')(data)
        results.append(data)
        training_outs.append(Dense(len(Types), activation= custom_sig)(data))


    a = keras.layers.Concatenate(axis = 1)(results) 
    a = keras.layers.Dropout(0.4)(a)
    out = Dense(len(Types), activation= custom_sig)(a)

    model = keras.models.Model(inputs=keras_input, outputs=out)

    model_train = keras.models.Model(inputs=keras_input, outputs=[out] + [training_outs[i] for i in range(len(word_window) + len(word_window2))])

    model.compile(loss=keras.losses.categorical_crossentropy, optimizer='adam',  metrics=['categorical_accuracy'])
    model_train.compile(loss=keras.losses.categorical_crossentropy, loss_weights = [1] + [(1/(len(word_window) + len(word_window2))) for i in range(len(word_window) + len(word_window2))], optimizer='adam',  metrics=['categorical_accuracy'])

    #model.fit(data_final[train], labels_final[train], validation_data = (data_final[test], labels_final[test]), epochs = 100)
    model_train.fit(data_final[train], [labels_final[train] for i in range(len(word_window)+len(word_window2)+1)], validation_data = (data_final[test], [labels_final[test] for i in range(len(word_window)+len(word_window2)+1)]), epochs = 30)

    ###############DEBUG 
    final_results = model.predict(data_final[test])
    for num, data in enumerate(final_results):
        conf_matrix[numpy.argmax(labels_final[test][num])][numpy.argmax(data)] += 1 #real\\pred
        real_vec[numpy.argmax(labels_final[test][num])] += 1

    if(1): #Run once
        break

 
if(1):
    for i in range(len(Types)):
        for j in range(len(Types)):
            conf_matrix[i][j] /= real_vec[i]

df = pd.DataFrame((conf_matrix), columns=Types, index = Types)
export_csv = df.to_csv (r'C:\Users\Zach\Downloads\conf_matrix.csv')


#model.save('D:\TEXT_IDENTIFY_MODEL_long.h5')   

cin = input()
