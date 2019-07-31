#MIT License

#Copyright (c) 2018 The University of Michigan

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import word_finder_table
import pdf_cropper
import pdf_csv_converter
import PyPDF2
import csv
from Address import Address
import os
import re

from CNN_Table_Extracter import main_func

def cleaner (value): # cleans up the entries
    for i in value:
        if((i.isdigit()) | (i == '.') | (i == ",")):   
            value = value.replace(i, "")
    return value

def table_extract(type_of_device, source_pdf_path, CNN_TABLE):
    #ta = Address(1).split("\n")
    Path_extracted1 = os.path.split(source_pdf_path)[0]

    if("ADC" in type_of_device):
        named_list=[
                    ["INL", "integral non-linearity", "integral nonlinearity","inl","integral linearity error","integral linearity"], 
                    ["DNL", "differential non-linearity", "differential nonlinearity","dnl","differential linearity error","differential linearity"],
                    ["Resolution", "resolution"],
                    ["Sampling Frequency", "sampling frequency"],
                    ["Sensing Voltage", "sensing voltage", "sense_vol"]]
        exception_list=["vinl","iinl", "tinl"]
    elif(type_of_device == "PLL"):
        named_list=[
                    ["Output Frequency", "output frequency"],
                    ["Step Size", "step size"],
                    ["Tuning Range", "tuning range"],
                    ["In-band Phase Noise", "in band phase noise", "in-band phase noise"],
                    ["Integrated Jitter", "jitter"],
                    ["Bandwidth", "bandwidth"],
                    ["Reference Frequency", "reference frequency"]]
        exception_list=["by"]
    elif(type_of_device == "LDO"):
        named_list=[
                    ["Dropout Voltage", "dropout voltage"],
                    ["Quiescent Current in Shutdown", "quiescent current in shutdown", "shutdown current"],
                    ["Line Regulation Iset", "line regulation iset"],
                    ["Line Regulation VOS", "line regulation vos"],
                    ["Load Regulation Iset", "load regulation iset"],
                    ["Load Regulation VOS", "load regulation vos"],
                    ["PSRR", "psrr"],
                    ["Output RMS Noise", "RMS"],
                    ["Output Current", "output current"],
                    ["Output Noise Spectral", "output noise spectral"],
                    ["Initial Accuracy", "initial accuracy"]]
        exception_list=[]
    elif(type_of_device == "Temperature_Sensor"):
        named_list=[
                    ["Temperature Range", "temperature range", "operating temperature"],
                    ["Resolution", "resolution"],
                    ["Reference Clock Frequency", "reference clk freq", "reference clk frequency", "reference clock freq", "reference clock frequency"]]
        exception_list=["storage temperature range"]
    elif(type_of_device == "CDC"):
        named_list=[
                    ["Input Capacitance Range", "input range", "input capacitance range"],
                    ["Resolution", "resolution"],
                    ["Reference Voltage", "reference voltage"]]
        exception_list=[]
    elif(type_of_device == "SRAM"):
        named_list=[
                    ["Address Size", "address size"],
                    ["Word Size", "word size"],
                    ["Capacity", "capacity"],
                    ["Clock Frequency", "clk_freq", "clock frequency"],
                    ["Foundry", "foundry"]]
        exception_list=[]
    elif(type_of_device == "DCDC"):
        named_list=[
                    ["Switching Frequency"],
                    ["Feedback Voltage"],
                    ["Maximum Output Current","IOUT"],
                    ["Load Current", "load current", "circuit current"]]
        exception_list=[]
    elif(type_of_device == "BDRT"):
        named_list=[
            ["Input Voltage", "input voltage"],
            ["Output Voltage", "output voltage"],
            ["3-STATE Output Leakage", "3-STATE Output Leakage Current"]]
        exception_list=[]
    elif (type_of_device == "counters"):
        named_list = [
            ["Input Voltage", "input voltage"],
            ["Input Current", "input current"],
            ["Output Voltage", "output voltage"],
            ["Supply Voltage", "supply voltage"],
            ["Count Up","Count Down"],
            ["recovery time"]]
        exception_list=[]
    elif (type_of_device == "DAC"):
        named_list = [
            ["Digital Input High Voltage", "input voltage", "Input Voltage"],
            ["Resolution", "resolution"],
            ["Capacitance"],
            ["Digital Input Low Voltage", "input low voltage"],
            ["SR", "Slew Rate", "slew rate"],
            ["DAC-to-DAC Crosstalk"]]
        exception_list=[]
    elif (type_of_device == "Delay_Line"):
        named_list = [
            ["Input Voltage Low", "Digital Input Low Voltage", "input low voltage", "Input Voltage", "input voltage"],
            ["Maximum Frequency"],
            ["Input-to-Tap Delay Tolerance"],
            ["Input Step","Step Delay"]]
        exception_list=[]
    elif (type_of_device == "Digital_Potentiometers"):
        named_list = [
            ["Input Voltage Low", "Digital Input Low Voltage", "input low voltage", "Input Voltage", "input voltage"],
            ["Resistor Noise Voltage", "Resistor Noise Voltage Density", "End-to-End Resistor Tolerance", "End-to-End Resistor Tempco"],
            ]
        exception_list=[]
    elif (type_of_device == "DSP"):
        named_list = [
            ["Circuit current","IQ"],
            ["Output voltage","VREG"]
            ]
        exception_list=[]
    elif (type_of_device == "IO"):
        named_list = [
            ["Input Voltage Low","Digital Input Low Voltage", "input low voltage"],
            ["Supply Voltage", "supply voltage"],
            ["Standby Current","standby current"],
            ["SCL clock frequency", "Serial Clock Frequency"]
            ]
        exception_list=[]
    elif (type_of_device == "Opamp"):
        named_list = [
            ["Input Voltage"],
            ["Input Bias Current","BIAS CURRENT, initial"],
            ["Supply Voltage Range", "Supply voltage (1)"]
            ]
        exception_list=[]
    destination_pdf_path=os.path.join(Path_extracted1,'Modified_pdf')
    source_csv_path=destination_pdf_path
    destination_csv_path=os.path.join(Path_extracted1,'CSV')

    last_directory_word_spliting_pdf=source_pdf_path.split(chr(92)) #Replaced back slash with forward slash; now an array of all parts

    last_pdf_directory_word = last_directory_word_spliting_pdf[-1] #Last element

    last_directory_word_spliting_csv=last_pdf_directory_word.split(".")
    last_csv_directory_word=last_directory_word_spliting_csv[0]+"."+"csv"

    pfr = PyPDF2.PdfFileReader(open(source_pdf_path, "rb"))


    number_page=pfr.getNumPages()#Counting number of pdf pages
    pdf_cropper.pdf_cropper(source_pdf_path, destination_pdf_path, last_pdf_directory_word, number_page)
    if(CNN_TABLE):
        main_func(source_csv_path,destination_csv_path, last_pdf_directory_word, last_csv_directory_word, number_page)
    else:
        #Convert each pdf page to CSV file and save each CSV page separately    
        pdf_csv_converter.pdf_csv_converter(source_csv_path,destination_csv_path, last_pdf_directory_word, last_csv_directory_word, number_page)

    pins={}
    max_value={}
    min_value={}
    typ_value={}
    max_={}
    min_={}
    typ_={}
    keys=[]

    for block in named_list:
        temp = block[0]
        for element in block[1:]:##need to generalize not only for lsb
            #print (element)
            max_,min_,typ_=word_finder_table.word_finder_table(source_pdf_path,element,exception_list)
            for key, value in max_.items():
                max_value[(temp,key)]=value
                if(key not in keys):
                    keys.append(key)
            for key, value in min_.items():
                min_value[(temp,key)]=value
                if(key not in keys):
                    keys.append(key)
            for key, value in typ_.items():
                typ_value[(temp,key)]=value
                if(key not in keys):
                    keys.append(key)

    pfr = PyPDF2.PdfFileReader(open(source_pdf_path, "rb"))
    number_page=pfr.getNumPages()

    pin_names = []
    for page in range(0,number_page):#logic for pins
        irregular = False
        column_holder = -1
        row_holder = 0
        destination_csv_extraction_path=os.path.join(destination_csv_path,str(page),last_csv_directory_word) 
        size=os.path.getsize(destination_csv_extraction_path)
        if size!=0:
            with open(destination_csv_extraction_path, 'r') as csvfile:
                csv_file = list(csv.reader(csvfile))
                for row_counter, row in enumerate(csv_file):
                    if(column_holder == -1):
                        for column_counter, word in enumerate (row):
                                word=word.lower()
                                if(word == "pin name" or word == "pin names"):
                                    column_holder = column_counter
                                    row_holder = row_counter
                                elif("pin" in word):
                                    A = True
                                    B = True
                                    C = True
                                    try:
                                        csv_file[row_counter + 1][column_counter]
                                    except:
                                        A = False
                                    try:
                                        csv_file[row_counter + 2][column_counter]
                                    except:
                                        B = False
                                    try:
                                        csv_file[row_counter][column_counter + 1]
                                    except:
                                        C = False
                                    if(A and "name" in csv_file[row_counter + 1][column_counter].lower()):
                                        column_holder = column_counter
                                        row_holder = row_counter + 1
                                    elif(B and "name" in csv_file[row_counter + 2][column_counter].lower()):
                                        column_holder = column_counter
                                        row_holder = row_counter + 2
                                    elif(C and "name" in csv_file[row_counter][column_counter+1].lower()):
                                        column_holder = column_counter+1
                                        row_holder = row_counter
                    elif(row[column_holder] != ""):
                        if((row[column_holder].split(" ")[0] not in pin_names) and (row_holder < row_counter)):
                            try: #remove pure numbers
                                float(row[column_holder].split(" ")[0])
                            except:
                                pin_names.append(row[column_holder].split(" ")[0])
                    else:
                        if(row_counter-row_holder < 8):
                            irregular = True
                        elif(not irregular):
                            break
    return max_value, min_value, typ_value, named_list, keys, pin_names
