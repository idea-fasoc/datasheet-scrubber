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

import my_text_extractor
import table_extracter
from Address import Address
import pdftotext
import os
import pin_extractor
def dissect (value): # cleans up the entries
    for i in value:
        if((~i.isdigit()) & (i != '.') & (i != "-")):   
            value = value.replace(i, "")
    try:
        return float(value)
    except:
        return value

def normalize(value, type): #expand
    if("Voltage" in type): #around V
        while(abs(value) > 25):
            value = value / 1000
    elif("Quiescent Current in Shutdown" == type): #around uA
        while(abs(value) > .00001):
            value = value / 1000
    elif("Current" in type): #around A
        while(abs(value) > 20):
            value = value / 1000
    elif("Frequency" in type): #over 10mhz
        while(abs(value) < 10000000):
            value = value * 1000
    elif("RMS" == type):
        while(abs(value) > .0001): #less than 100u
            value = value / 1000
    elif("Output Noise Spectral" == type):
        while(abs(value) > .000002): #less than 2u
            value = value / 1000
    return value
    

def extraction(type,path, CNN_TABLE):
    text_path = os.path.join(os.path.join(Address(1).split('\n')[0],  "Test_text"), path.split('\\')[-1].split('.')[0] + ".txt")
    text_data = my_text_extractor.my_text_extractor(type, text_path)
    text_pin = pin_extractor.pin_extraction(text_path)


    max_value, min_value, typ_value, named_list, keys, pin_names = table_extracter.table_extract(type,path,CNN_TABLE)

    final_dict_max = {}
    final_dict_min = {}
    final_dict_typ = {}
    final_dict_unit = {}
    adc_unit = {'Resolution': 'Bit', 'INL': 'Lsb', 'DNL': 'Lsb', 'Sampling Frequency': 'Hz', 'Sensing Voltage': 'V'}
    pll_unit = {'Output Frequency': 'Hz', 'Step Size': 'Hz', 'Tuning Range': 'Hz', 'In-band Phase Noise': 'dBc/Hz', 'Integrated Jitter': 's', 'Bandwidth': 'Hz', 'Reference Frequency': 'Hz'}
    ldo_unit = {'Dropout Voltage': 'V', 'Quiescent Current in Shutdown': 'A', 'line_reg_iset': 'A/V', 'line_reg_vos': 'V/V', 'load_reg_iset':'A', 'load_reg_vos': 'V', 'PSRR': 'dB', 'RMS':'RMS Voltage', 'Output Current':'A','Output Noise Spectral':'V/sqrt(Hz)','Initial Accuracy': '%' }
    temperature_unit = {'Temperature Range': 'Centigrade', 'Resolution': 'Centigrade', 'Reference Clock Frequency': 'Hz'}
    cdc_unit = {'Input Capacitance Range': 'F','Resolution':'bit','Reference Voltage': 'V'}
    memory_unit = {'Column':'bit', 'Row':'bit','Capacity': '','Clock Frequency':'Hz','Foundry':''}
    dcdc_unit = {'Input Voltage':'V','Output Voltage':'V','Load Current':'A'}
    bdrt_unit = {'Input Voltage':'V','Output Voltage':'V', '3-STATE Output Leakage':'A'}
    counters_unit = {'Input Voltage':'V','Input Current':'I','Output Voltage':'V','Supply Voltage':'V','Count Up':'','recovery time':'s'}
    dac_unit = {'Digital Input High Voltage':'V','Resolution':'Bit','Capacitance':'C','Digital Input Low Voltage':'V','SR':'V/s','DAC-to-DAC Crosstalk':'s'}
    delay_line_unit = {'Input Voltage Low':'V','Maximum Frequency':'Hz','Input-to-Tap Delay Tolerance':'s','Input Step':'s'}
    digital_potentiometers_unit = {'Input Voltage Low':'V','Resistor Noise Voltage':'V'}
    dsp_unit = {'Circuit current':'A','Output voltage':'V'}
    io_unit = {'Input Voltage Low':'V','Supply Voltage':'V','Standby Current':'A','SCL clock frequency':'Hz'}
    opamp_unit = {'Input Voltage Low':'V','Input Bias Current':'A','Supply Voltage Range':'V'}
    
    if type == 'ADC':
        final_dict_unit = adc_unit
    elif type == 'PLL':
        final_dict_unit = pll_unit
    elif type == 'LDO':
        final_dict_unit = ldo_unit
    elif type == 'Temperature_Sensor':
        final_dict_unit = temperature_unit
    elif type == 'CDC':
        final_dict_unit = cdc_unit
    elif type == 'SRAM':
        final_dict_unit = memory_unit
    elif type == 'DCDC':
        final_dict_unit = dcdc_unit
    elif type == 'BDRT':
        final_dict_unit = bdrt_unit
    elif type == 'counters':
        final_dict_unit = counters_unit
    elif type == 'DAC':
        final_dict_unit = dac_unit
    elif type == 'Delay_Line':
        final_dict_unit = delay_line_unit
    elif type == 'Digital_Potentiometers':
        final_dict_unit = digital_potentiometers_unit
    elif type == 'DSP':
        final_dict_unit = dsp_unit
    elif type == 'IO':
        final_dict_unit = io_unit
    elif type == 'Opamp':
        final_dict_unit = opamp_unit
        
    #print(max_value)
    #print(min_value)
    #print(typ_value)
    #print("")
    for block in named_list:
        temp = block[0]
        #print("")
        for x in keys:
            try:
                disTemp = float(dissect(max_value[(temp, x)]))
                if(disTemp != ""):                
                    if(temp not in final_dict_max or final_dict_max[temp] < disTemp):
                        final_dict_max[temp] = normalize(disTemp, temp)
            except:
                pass
        for x in keys:
            try:
                disTemp = float(dissect(min_value[(temp, x)]))
                if(disTemp != ""):
                    if(temp not in final_dict_min or final_dict_min[temp] > disTemp):
                        final_dict_min[temp] = normalize(disTemp, temp)
            except:
                pass
        for x in keys:
            try:
                disTemp = float(dissect(typ_value[(temp, x)]))
                if(disTemp != ""):
                    if(temp not in final_dict_typ):
                        final_dict_typ[temp] = normalize(disTemp, temp)
            except:
                pass
    #print(final_dict_max)
    #print(final_dict_min)
    #print(final_dict_typ)
    for block in named_list:
        for temp in block:
            for keys in text_data:
                if keys == temp:
                    if len(text_data[keys]['value'])==2:
                        final_dict_min[block[0]] = text_data[keys]['value'][0]
                        final_dict_max[block[0]] = text_data[keys]['value'][1]
                    else:
                        try:
                            final_dict_max[block[0]] = text_data[keys]['value'][0]
                        except:
                            final_dict_max[block[0]] = text_data[keys]['value']

    giant_array = []
    for block in named_list:
        temp_array = []
        temp = block[0]
        if(temp in final_dict_max or temp in final_dict_min or temp in final_dict_typ):
            temp_array.append(temp)
        if(temp in final_dict_max and final_dict_max[temp] != ""):
            temp_array.append("max")
            temp_array.append([str(final_dict_max[temp]),  final_dict_unit[temp]])
        if(temp in final_dict_min and final_dict_min[temp] != ""):
            temp_array.append("min")
            temp_array.append([str(final_dict_min[temp]),  final_dict_unit[temp]])
        if(temp in final_dict_typ and final_dict_typ[temp] != ""):
            temp_array.append("typ")
            temp_array.append([str(final_dict_typ[temp]),  final_dict_unit[temp]])
        if(temp_array):
            giant_array.append(temp_array)
    temp_array = []
    if(pin_names):
        for pin in pin_names:
            temp_array.append(pin)
    else:
         for pin in text_pin:
             temp_array.append(pin)

    return giant_array, temp_array
