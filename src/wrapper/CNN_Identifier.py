from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Conv2D
from keras.models import model_from_json
from sklearn.model_selection import train_test_split
import keras
import numpy
from keras import backend as K

import pickle

import gensim

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import os

from Address import Address
from pdf_to_text import pdf_to_text



def clean(raw_data, word_depth):   
    #raw_data = raw_data.replace("\n", " ")
    raw_data = raw_data.lower()
    raw_data = raw_data.strip()

    #########################################################
    long_string = ""
    start = 0
    space_count = 0
    last_char = ""
    for char_num, character in enumerate(raw_data): #remove tables/diagrams ##TODO IMPROVE
        if(character == "\n" and last_char == "\n"):
            if(space_count >= 5):
               long_string += raw_data[start:char_num]
            start = char_num + 1
            space_count = 0
        elif(character == " "):
            space_count += 1
        last_char = character
    ###########################################################

    tokens = word_tokenize(long_string) #Replace with long string to use digram remover
    if(len(tokens) > word_depth):
        tokens = tokens[:word_depth]

    ###################################################################
    last_item = ""
    for item_num, item in enumerate(tokens): #fix hyphenated words
        if(len(last_item) > 1 and last_item[-1] == "-"):
            item = last_item[:-1] + item
            del tokens[item_num - 1]
        last_item = item
    #################################################################





    ################remove non words#############
    final_list = []
    for token in tokens:
        a_str = ""
        len_d_str = 0
        o_str = ""
        for char in token:
            if(char.isalpha()):
                a_str += char
            elif(char.isdigit()):
                len_d_str += 1
            else:
                o_str += char
    
        if(len(a_str) > len_d_str):
            final_list.append(a_str)
        elif(len_d_str >= 1):
            final_list.append("NUMBER")
        else:
            final_list.append(o_str)
    #################################################


    return final_list

def convert(fname):
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, 'utf-8', laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    with open(fname, 'rb') as infile:
        for page_num, page in enumerate(PDFPage.get_pages(infile)):
            if(page_num < 10): #first x page(s)
                interpreter.process_page(page)
                text = output.getvalue()
    converter.close()  
    output.close
    return text 

def array_creater(clean_pdfs, freq, word_depth):
    x_list = []
    for tup in freq:
        x_list.append(str(tup[0]))

    massive_array = []
    for pdf in clean_pdfs:
        single_array2D = []      
        for word in x_list:
            single_array1D = [0 for x in range(word_depth)]
            for item_count in range(0,word_depth):
                if(item_count >= len(pdf)):
                    break
                if(pdf[item_count] == word):
                    single_array1D[item_count] = 1
            single_array2D.append(single_array1D)   
        massive_array.append(single_array2D)

    massive_array = numpy.array(massive_array, dtype="float")
    return massive_array


def CNN_Identifier():
    unique_words = 1000
    word_depth = 500

    pdf_to_text('Test_pdf','Test_text')

    with open(os.path.join(Address(1), r"model_architecture.json"), 'r') as f:
        model = model_from_json(f.read())
    model.load_weights(os.path.join(Address(1), r"model_weights.h5"))
    with open(os.path.join(Address(1), r"word_list.txt"), "rb") as file:
        freq = pickle.load(file)   


    ##########################################################DEBUG
    final_output = []
    type_list = ['ADC', 'CDC', 'Opamp', 'LDO', 'PLL', 'SRAM', 'Temperature_Sensor', 'DCDC', 'BDRT', 'counters', 'Digital_Potentiometers', 'DSP', 'IO']

    for file in os.listdir(os.path.join(Address(1), r"Test_pdf")): #Ideally this will be using Test_text, but I was having issues
        raw_test_data = convert(os.path.join(Address(1), r"Test_pdf", file))
        clean_test_data = [clean(raw_test_data, word_depth)]
        test_data = numpy.expand_dims(array_creater(clean_test_data, freq, word_depth), axis = 3)
        results = model.predict(test_data)
        final_output.append(type_list[numpy.argmax(results)])
    return final_output
    ########################################################