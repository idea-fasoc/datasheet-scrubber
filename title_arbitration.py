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

from supervised_classifier_ngram import supervised_classifier_ngram
from supervised_classifier import supervised_classifier
from Address import Address
import os
def title_arbitration(normal_classifier_title_result,key_words_title_result,key_words_occurrence_array,key_words_title_result_second,max_zero_flag,max_second_zero_flag):
    ADC = 'ADC'
    AFE = 'AFE'
    BDRT = 'BDRT'
    CDC= 'CDC'
    COUNTER = 'COUNTER'
    DAC = 'DAC'
    DCDC= 'DCDC'
    DELAY_LINE = 'DELAY_LINE'
    DSP = 'DSP'
    IO = 'IO'
    LDO='LDO'
    OPAMP = 'OPAMP'
    OSCILLATOR = 'OSCILLATOR'
    POTENTIOMETER = 'POTENTIOMETER'
    PLL = 'PLL'
    SENSOR = 'SENSOR'
    SRAM='SRAM'
    Temperature_Sensor='Temperature_Sensor'

    title=[None]*len(key_words_title_result)
    Path_extracted=Address(1).split("\n")
    Path_extracted1=Path_extracted[0]
    ADC_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'ADC'),        ADC]
    AFE_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'ADE'),        AFE]
    BDRT_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'BDRT'),        BDRT]
    CDC_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'CDC'),        CDC]
    COUNTER_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'COUNTER'),        COUNTER]
    DAC_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'DAC'),        DAC]
    DCDC_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'DCDC'),        DCDC]
    DELAY_LINE_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'DELAY_LINE'),        DELAY_LINE]
    DSP_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'DSP'),        DSP]
    IO_path = [os.path.join(os.path.join(Path_extracted1, 'cropped_text'), 'IO'),       IO]
    LDO_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'LDO'),        LDO]
    OPAMP_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'OPAMP'),        OPAMP]
    OSCILLATOR_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'OSCILLATOR'),        OSCILLATOR]
    POTENTIOMETER_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'POTENTIOMETER'),        POTENTIOMETER]
    PLL_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'PLL'),        PLL]
    SENSOR_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'SENSOR'),        SENSOR]
    SRAM_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'SRAM'),        SRAM]
    Temperature_Sensor_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'Temperature_Sensor'),    Temperature_Sensor]

    SOURCES = [ADC_path,ADE_path,BDRT_path,COUNTER_path,DAC_path,DELAY_LINE_path,DSP_path,IO_path,OPAMP_path,OSCILLATOR_path,POTENTIOMETER_path,PLL_path,DCDC_path,CDC_path,Temperature_Sensor_path,SRAM_path,SENSOR_path,LDO_path]
    def loockup_title_table(title_input):
        if title_input=='CDC':
            ind_ex=0
        elif title_input=='ADC':
            ind_ex=1
        elif title_input=='DCDC':
            ind_ex=2
        elif title_input=='LDO':
            ind_ex=3
        elif title_input=='PLL':
            ind_ex=4
        elif title_input=='SRAM':
            ind_ex=5
        elif title_input=='Temperature_Sensor':
            ind_ex=6
        elif title_input=='AFE':
            ind_ex=7
        elif title_input=='BDRT':
            ind_ex=8
        elif title_input=='COUNTER':
            ind_ex=9
        elif title_input=='DAC':
            ind_ex=10
        elif title_input=='DELAY_LINE':
            ind_ex=11
        elif title_input=='DSP':
            ind_ex=12
        elif title_input=='IO':
            ind_ex=13
        elif title_input=='OPAMP':
            ind_ex=14
        elif title_input=='OSCILLATOR':
            ind_ex=15
        elif title_input=='POTENTIOMETER':
            ind_ex=16
        elif title_input=='SENSOR':
            ind_ex=17
        return ind_ex
    def title_classifier_caller(input_array):
        Accumulated_path=[]
        if 'CDC' not in input_array:
            Accumulated_path.append(CDC_path)
        if 'ADC' not in input_array:
            Accumulated_path.append(ADC_path)
        if 'DCDC' not in input_array:
            Accumulated_path.append(DCDC_path)
        if 'LDO' not in input_array:
            Accumulated_path.append(LDO_path)
        if 'PLL' not in input_array:
            Accumulated_path.append(PLL_path)
        if 'SRAM' not in input_array:
            Accumulated_path.append(SRAM_path)
        if 'Temperature_Sensor' not in input_array:
            Accumulated_path.append(Temperature_Sensor_path)
        if 'AFE' not in input_array:
            Accumulated_path.append(AFE_path)
        if 'BDRT' not in input_array:
            Accumulated_path.append(BDRT_path)
        if 'COUNTER' not in input_array:
            Accumulated_path.append(COUNTER_path)
        if 'DAC' not in input_array:
            Accumulated_path.append(DAC_path)
        if 'DELAY_LINE' not in input_array:
            Accumulated_path.append(DELAY_LINE_path)
        if 'DSP' not in input_array:
            Accumulated_path.append(DSP_path)
        if 'IO' not in input_array:
            Accumulated_path.append(IO_path)
        if 'OPAMP' not in input_array:
            Accumulated_path.append(OPAMP_path)
        if 'OSCILLATOR' not in input_array:
            Accumulated_path.append(OSCILLATOR_path)
        if 'POTENTIOMETER' not in input_array:
            Accumulated_path.append(POTENTIOMETER_path)
        if 'SENSOR' not in input_array:
            Accumulated_path.append(SENSOR_path)
        return Accumulated_path
    for i in range(0,len(key_words_title_result)):
        whole_title_classifier_guessed=[]
        if max_zero_flag[i]:
            title[i]=normal_classifier_title_result[i]
        else:
            if normal_classifier_title_result[i] in key_words_title_result[i]:
                title[i]=key_words_title_result[i][key_words_title_result[i].index(normal_classifier_title_result[i])]
            elif 'LDO' in key_words_title_result[i]:
                title[i]='LDO'
            else:
                if len(key_words_title_result[i])>1:
                    while normal_classifier_title_result[i] not in key_words_title_result[i]:
                        whole_title_classifier_guessed.append(normal_classifier_title_result[i])
                        SOURCE_input=title_classifier_caller(whole_title_classifier_guessed)
                        normal_classifier_title_result=supervised_classifier(SOURCE_input)    
                    title[i]=key_words_title_result[i][key_words_title_result[i].index(normal_classifier_title_result[i])]
                else:    
                    if not max_second_zero_flag[i]:
                        break_tag=False
                        while not break_tag:
                            if normal_classifier_title_result[i] in key_words_title_result[i]:
                                title[i]=key_words_title_result[i][key_words_title_result[i].index(normal_classifier_title_result[i])]
                                break_tag=True
                            if normal_classifier_title_result[i] in key_words_title_result_second[i]:
                                title[i]=key_words_title_result_second[i][key_words_title_result_second[i].index(normal_classifier_title_result[i])]
                                break_tag=True
                            whole_title_classifier_guessed.append(normal_classifier_title_result[i])
                            SOURCE_input=title_classifier_caller(whole_title_classifier_guessed)
                            normal_classifier_title_result=supervised_classifier(SOURCE_input)
                    else:
                        title[i]=key_words_title_result[i][0]
    return title
