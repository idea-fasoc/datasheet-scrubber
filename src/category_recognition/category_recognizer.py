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


from PyPDF2 import PdfFileReader

import os
import os.path


#cur_dir = os.getcwd() # Dir from where search starts can be replaced with any path

def find_file(file_name,cur_dir):
    while True:
        file_list = os.listdir(cur_dir)
        parent_dir = os.path.dirname(cur_dir)
        if file_name in file_list:
            print("File Exists in: ", cur_dir)
            break
        else:
            if cur_dir == parent_dir: #if dir is root dir
                print("File not found")
                break
            else:
                cur_dir = parent_dir
    return os.path.join(cur_dir, file_name)


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

print("------LOOK FOR PATHS TO MODEL FILES-------")
#get urls to models files using the main script
#model_location = str(find_file("TEXT_IDENTIFY_MODEL_long.h5","/Users/zinebbenameur/clean/datasheet-scrubber/src"))
#tokenizer_location = str(find_file("tokenizer_long.pickle","/Users/zinebbenameur/clean/datasheet-scrubber/src"))

model_location = "/Users/zinebbenameur/clean/datasheet-scrubber/src/Table_extract_robust/TEXT_IDENTIFY_MODEL_long.h5" #Change to the location of the model 
tokenizer_location = "/Users/zinebbenameur/clean/datasheet-scrubber/src/Table_extract_robust/tokenizer_long.pickle" #Change to the location of the tokenizer


print(str(model_location),str(tokenizer_location))

#pdf_location = r"D:/Full_Dataset/ADC/PDFs/ad7819.pdf" #Change to the current pdf

#pdf_location = str(sys.argv[1])
pdf_location = input("Enter a PDF's location and name: ")

#pdf_location = get_pdf()
#print("PDF LOCATION", pdf_location)


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

def get_number_pages():
    return PdfFileReader(open(pdf_location,'rb'))