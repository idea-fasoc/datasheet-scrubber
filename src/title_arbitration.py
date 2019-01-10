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
    PLL = 'PLL'
    DCDC= 'DCDC'
    CDC= 'CDC'
    Temperature_Sensor='Temperature_Sensor'
    SRAM='SRAM'
    LDO='LDO'
    title=[None]*len(key_words_title_result)
    Path_extracted=Address(1).split("\n")
    Path_extracted1=Path_extracted[0]
    ADC_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'ADC'),        ADC]
    PLL_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'PLL'),        PLL]
    DCDC_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'DCDC'),        DCDC]
    CDC_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'CDC'),        CDC]
    Temperature_Sensor_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'Temperature_Sensor'),    Temperature_Sensor]
    SRAM_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'SRAM'),        SRAM]
    LDO_path=[os.path.join(os.path.join(Path_extracted1,'cropped_text'), 'LDO'),        LDO]
    SOURCES = [ADC_path,PLL_path,DCDC_path,CDC_path,Temperature_Sensor_path,SRAM_path,LDO_path]    
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
