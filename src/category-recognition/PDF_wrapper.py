import numpy
from numpy import zeros, ones
from numpy import asarray

from keras.preprocessing.text import Tokenizer
from keras.models import Sequential
from keras import backend as K
from keras.models import load_model

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

import math
import os
import pickle
import re
import sys

def custom_sig(x):
    return (K.sigmoid(x) + math.pow(.1, 6))

def convert(fname, word_amount):
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, 'utf-8', laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)
    with open(fname, 'rb') as infile:
        for page_num, page in enumerate(PDFPage.get_pages(infile)):
            interpreter.process_page(page)
            text = output.getvalue()
            if(len(text.split()) >= 256):
                break
    converter.close()  
    output.close
    return text 



model_location = r"D:\TEXT_IDENTIFY_MODEL_long.h5" #Change to the location of the model 
tokenizer_location = r"D:\tokenizer_long.pickle" #Change to the location of the tokenizer


#pdf_location = r"D:/Full_Dataset/ADC/PDFs/ad7819.pdf" #Change to the current pdf

#Get the pdf location from the main script
pdf_location = str(sys.argv)
#print("------pdf_location-------",pdf_location)
#pdf_location = input("Enter a PDF's location and name: ")


word_amount = 256
model = load_model(model_location, custom_objects={'custom_sig':custom_sig})

with open(tokenizer_location, 'rb') as handle:
    t = pickle.load(handle)

data = convert(pdf_location, word_amount)
data = data.lower()
cleaned_data = ""
skip_eol = False
for char in data:
    if(char == "-"):
        skip_eol = True
    elif(skip_eol and char != " " and char != r"\n"):
        cleaned_data += " "
        skip_eol = False

    if(not skip_eol):
        cleaned_data += char
 
data = cleaned_data.replace(r"\n", " ")
regex = re.compile('[^a-z" "]')
data = regex.sub(" ", data)

encoded_data = t.texts_to_sequences([data])
#print(encoded_data)
data_final = []
for data in encoded_data:
    #print(data)
    temp_array1D = []
    for iter in range(word_amount):
        if(iter < len(data)):
            temp_array1D.append(data[iter])
        else:
            temp_array1D.append(0)
    data_final.append(temp_array1D)
data_final = numpy.array(data_final)

final_identification = model.predict(data_final)

#print(final_identification)

Types = ['ADC', 'AFE', 'Amplifiers - Audio', 'Amplifiers - Video Amps and Modules', 'Clock Buffers, Drivers', 'Clocks', 
        'CODECs', 'Controllers', 'CPLDs', 'DAC', 'Delay Lines', 'Drivers, Receivers, Transceivers', 'DSP', 'FPGAs', 'Instrumentation, OP Amps, Buffer Amps', 
        'Interface Signal Buffers, Repeaters, Splitters', 'IO Expanders', 'Linear - Comparators', 'Linear - Video Processing', 'Logic - Buffers, Drivers, Receivers, Transceivers',
        'Logic - Counters, Dividers', 'Logic - FIFOs Memory', 'Logic - Flip Flops', 'Logic - Gates', 'Logic - Latches', 'Logic - Shift Registers',
        'Logic - Signal Switches, Multiplexers, Decoders', 'Logic - Translators, Level Shifters', 'Logic - Universal Bus Functions', 'Memory', 'Microcontrollers',
        'Microprocessors', 'PMIC - AC DC Converters, Offline Switchers', 'PMIC - Current Regulation Management', 'PMIC - Display Drivers', 'PMIC - Energy Metering',
        'PMIC - Full, Half-Bridge Drivers', 'PMIC - Gate Drivers', 'PMIC - Hot Swap Controllers', 'PMIC - Motor Drivers, Controllers', 'PMIC - PFC (Power Factor Correction)',
        'PMIC - Power Distribution', 'PMIC - Power Supply Controllers, Monitors', 'PMIC - Supervisors', 'PMIC - Voltage Reference', 'PMIC - Voltage Regulators', 'Potentiometer',
        'SoC', 'Switches', 'Timers', 'UARTs']

print(Types[numpy.argmax(final_identification[0])])
