#!/usr/bin/env python3

# MIT License

# Copyright (c) 2018 The University of Michigan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import math
import numpy
import pickle
import argparse

from keras.preprocessing.text import Tokenizer
from keras import backend as K
from keras.models import load_model

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

from PyPDF2 import PdfFileReader

pyth_dir = os.path.dirname(__file__)
models_path = os.path.join(pyth_dir,'Models')

parser = argparse.ArgumentParser(description='Category Recognition Tool')
parser.add_argument('--pdf_dir', required = True, help = 'pdf directory')
args = parser.parse_args()

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
	output.close()
	return text 

print("------LOOK FOR PATHS TO MODEL FILES-------")
model_location = os.path.join(models_path,'TEXT_IDENTIFY_MODEL_long.h5')
tokenizer_location = os.path.join(models_path,'tokenizer_long.pickle') 

print(str(model_location),str(tokenizer_location))
pdf_location = (args.pdf_dir)

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
data_final = []
for data in encoded_data:
    temp_array1D = []
    for iter in range(word_amount):
        if(iter < len(data)):
            temp_array1D.append(data[iter])
        else:
            temp_array1D.append(0)
    data_final.append(temp_array1D)
data_final = numpy.array(data_final)

final_identification = model.predict(data_final)

Types = ['ADC', 'AFE', 'Amplifiers - Audio', 'Amplifiers - Video Amps and Modules', 'Clock Buffers, Drivers', 'Clocks', 
        'CODECs', 'Controllers', 'CPLDs', 'DAC', 'Delay Lines', 'Drivers, Receivers, Transceivers', 'DSP', 'FPGAs', 'Instrumentation, OP Amps, Buffer Amps', 
        'Interface Signal Buffers, Repeaters, Splitters', 'IO Expanders', 'Linear - Comparators', 'Linear - Video Processing', 'Logic - Buffers, Drivers, Receivers, Transceivers',
        'Logic - Counters, Dividers', 'Logic - FIFOs Memory', 'Logic - Flip Flops', 'Logic - Gates', 'Logic - Latches', 'Logic - Shift Registers',
        'Logic - Signal Switches, Multiplexers, Decoders', 'Logic - Translators, Level Shifters', 'Logic - Universal Bus Functions', 'Memory', 'Microcontrollers',
        'Microprocessors', 'PMIC - AC DC Converters, Offline Switchers', 'PMIC - Current Regulation Management', 'PMIC - Display Drivers', 'PMIC - Energy Metering',
        'PMIC - Full, Half-Bridge Drivers', 'PMIC - Gate Drivers', 'PMIC - Hot Swap Controllers', 'PMIC - Motor Drivers, Controllers', 'PMIC - PFC (Power Factor Correction)',
        'PMIC - Power Distribution', 'PMIC - Power Supply Controllers, Monitors', 'PMIC - Supervisors', 'PMIC - Voltage Reference', 'PMIC - Voltage Regulators', 'Potentiometer',
        'SoC', 'Switches', 'Timers', 'UARTs']

print('The category is: ', Types[numpy.argmax(final_identification[0])])

def get_number_pages():
    return PdfFileReader(open(pdf_location,'rb'))