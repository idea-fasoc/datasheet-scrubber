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

import re
from Address import Address
import os
def key_words_title_counter(source_dir):
    title_result=[]
    title_result_second=[]
    occurrence_array_result=[]
    max_zero_flag=[]
    max_second_zero_flag=[]
    Path_extracted=Address(1).split("\n")
    Path_extracted1=Path_extracted[0]
    #txtDir=os.path.join(Path_extracted1,os.path.join('All_text','ADC'))
    txtDir=os.path.join(Path_extracted1,source_dir)
    for text in os.listdir(txtDir):
        #print (text)
        maximum_occurence_index=[]
        maximum_occurence_index_second=[]
        f=open(os.path.join(txtDir,text),errors='ignore')
        CDC_words=re.findall(r'(?i)(?:(?:capacitive|capacitance)[\s]?\-[\s]?to[\s]?\-[\s]?digital|[^a-z][^d]CDC[s]?[^a-z]|Sensor\s+Interface|(?:capacitive|capacitance)\s+sensor|(?:capacitive|Capacitance)\s*\-\s*Digital\s*\-\s*|(?:capacitive|capacitance)\s*[\-]?\s*sensor|(?:capacitance|capacitive)\s+[a-z]*\s+sensor|digital\s+(?:capacitance|capacitive))[s]?',f.read())
        f.close()
        f=open(os.path.join(txtDir,text),errors='ignore')
        ADC_words=re.findall(r'(?i)(?:analog[\s]?\-[\s]?to[\s]?\-[\s]?digital|[^a-z]A/D[s]?[^a-z]|[^a-z]ADC[s]?[^a-z])[s]?',f.read())
        f.close()
        f=open(os.path.join(txtDir,text),errors='ignore')
        DCDC_words=re.findall(r'(?i)(?:[^a-z](?:Buck|Boost|Buck[\s]?-[\s]?Boost)(?:\s+Converter|\s+Regulator|\s*)[s]?[^a-z]|[^a-z]DC[\s]?[\-]?(?:/|to|\s*)[\s]?[\-]?DC[s]?[^a-z]|Step-(?:Up|Down)(?:\s+Regulator|\s+Converter|\s*))[s]?',f.read())
        f.close()
        f=open(os.path.join(txtDir,text),errors='ignore')
        LDO_words=re.findall(r'(?i)[^a-z](?:LDO\s+|Dropout)[s]?[^a-z]',f.read())
        f.close()
        f=open(os.path.join(txtDir,text),errors='ignore')
        PLL_words=re.findall(r'(?i)(?:[^a-z][d]?PLL[s]?[^a-z]|[^a-z]crystal[s]?[^a-z]|phased\s+locked\s+loop|[^a-z]jitter[s]?[^a-z]|clock\s+generator|[^a-z]VCO[s]?[^a-z]|[^a-z]DLL[s]?[^a-z])[s]?',f.read())
        f.close()
        f=open(os.path.join(txtDir,text),errors='ignore')
        SRAM_words=re.findall(r'(?i)[^a-z](?:SRAM|RAM|memory|memories|(?:read|write)\s+cycle)[s]?[^a-z]',f.read())
        f.close()
        f=open(os.path.join(txtDir,text),errors='ignore')
        Temperature_Sensor_words=re.findall(r'(?i)(?:(?:thermal|temperature)\s+sensor|(?:thermal|Temperature)\s+Detect(?:ion|or)|Humidity\s+(?:and|&)\s+(?:thermal|Temperature)|(?:thermal|Temperature)\s+(?:and|&)\s+Humidity|(?:thermal|temperature)\s+alarm|[^a-z]thermometer[s]?[^a-z]|[^a-z]RTD[s]?[^a-z]|Resistance\s+(?:thermal|Temperature)\s+Detector|(?:thermal|Temperature)\s+conversion|Temperature\s+result|thermistor)[s]?',f.read())
        
        occurrence_array=[len(CDC_words),len(ADC_words),len(DCDC_words),len(LDO_words),len(PLL_words),len(SRAM_words),len(Temperature_Sensor_words)]
        occurrence_array_copy=[len(CDC_words),len(ADC_words),len(DCDC_words),len(LDO_words),len(PLL_words),len(SRAM_words),len(Temperature_Sensor_words)]
        def title_name(maximum_occurrence):
            title_local=[]
            for i in range(0,len(maximum_occurrence)):
                if maximum_occurrence[i]==0:
                    title='CDC'
                elif maximum_occurrence[i]==1:
                    title='ADC'
                elif maximum_occurrence[i]==2:
                    title='DCDC'
                elif maximum_occurrence[i]==3:
                    title='LDO'
                elif maximum_occurrence[i]==4:
                    title='PLL'
                elif maximum_occurrence[i]==5:
                    title='SRAM'
                elif maximum_occurrence[i]==6:
                    title='Temperature_Sensor'
                title_local.append(title)
            return title_local
        
        for i in range(0,len(occurrence_array)):
            if occurrence_array[i]==max(occurrence_array):
                maximum_occurence_index.append(i)
        if max(occurrence_array)==0:
            max_zero_flag.append(True)
        else:
            max_zero_flag.append(False)
        title=title_name(maximum_occurence_index)
        for i in range (0,len(maximum_occurence_index)):
            occurrence_array_copy[maximum_occurence_index[i]]=0
        for i in range(0,len(occurrence_array_copy)):
            if occurrence_array_copy[i]==max(occurrence_array_copy):
                maximum_occurence_index_second.append(i)
        if max(occurrence_array_copy)==0:
            max_second_zero_flag.append(True)
        else:
            max_second_zero_flag.append(False)
        title_second=title_name(maximum_occurence_index_second)
        title_result_second.append(title_second)
        title_result.append(title)
        occurrence_array_result.append(occurrence_array)
    return title_result,occurrence_array_result,title_result_second,max_zero_flag,max_second_zero_flag
