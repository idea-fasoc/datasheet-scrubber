from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Conv2D
from keras.models import model_from_json
import keras
import pdf2image #poppler needs to be added and added to the path variable
from PIL import Image
import os
import cv2
import numpy
import copy
from sklearn.model_selection import train_test_split
from keras import backend as K

from Address import Address

def image_spliter(pdfs, verticle_size):
    data = []
    for pdf_num, pdf in enumerate(pdfs):
        for iter in range(len(pdf)):
            img = pdf[iter]

            #debug_loc = r"C:\Users\Zach\Downloads\Identifier\Main\Pdf" + str(pdf_num) + r"\page" + str(iter)
            debug_loc = os.path.join(Address(1), r"CNN_table\Identifier\Main\Pdf") + str(pdf_num) + r"\page" + str(iter)
            #if not os.path.exists(r"C:\Users\Zach\Downloads\Identifier\Main\Pdf" + str(pdf_num)):
                #os.mkdir(r"C:\Users\Zach\Downloads\Identifier\Main\Pdf" + str(pdf_num))
            if not os.path.exists(os.path.join(Address(1), r"CNN_table\Identifier\Main\Pdf") + str(pdf_num)):
                os.mkdir(os.path.join(Address(1), r"CNN_table\Identifier\Main\Pdf") + str(pdf_num))

            if not os.path.exists(debug_loc):
                os.mkdir(debug_loc)

            y_iter = 0
            while(y_iter + verticle_size <= img.size[1]):
                slice = img.crop((0, y_iter, img.size[0], y_iter + verticle_size))
                slice = slice.resize((850, verticle_size), Image.NEAREST) #THIS WILL NOT WORK IF RES IS CHANGED
                slice.save(debug_loc + "\\" + str(y_iter) +".png", 'png')

                slice = cv2.imread(debug_loc + "\\" + str(y_iter) +".png", 0)
                cv2.imwrite(debug_loc + "\\" + str(y_iter) +".png", slice) #debug

            
                data.append(slice)
                y_iter += verticle_size / 2

    data = numpy.array(data, dtype="float") / 255.0
    return(data)
        

def table_split(pdf, model):
   
    Test_pages = pdf2image.convert_from_path(pdf, 100)
    array = []
    for page in Test_pages:
        data = numpy.expand_dims(image_spliter([[page]], 100), axis = 3)
        results = model.predict(data)
        results = results.flatten()
        array.append(results)
    return array
