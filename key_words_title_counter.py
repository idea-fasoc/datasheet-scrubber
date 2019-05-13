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
    #Path_extracted1 = r"D:\All_pdf\test"
    txtDir=os.path.join(Path_extracted1,source_dir)
    #txtDir=os.path.join(Path_extracted1,source_dir)
    #txtDir = r'C:\Users\whatsthenext\Desktop\research\text_source'
    for text in os.listdir(txtDir):
        #print (text)
        maximum_occurence_index=[]
        maximum_occurence_index_second=[]
        f=open(os.path.join(txtDir,text),errors='ignore')
        temp = re.findall(r'CDC',f.read())
        CDC_words = []
        if len(temp) > 5:
            for _ in range(0,100):
                CDC_words += 'P'
        elif len(temp) > 10:
            for _ in range(0,200):
                CDC_words += 'P'
        else:
            CDC_words=re.findall(r'(?i)(?:(?:capacitive|capacitance)[\s]?\-[\s]?to[\s]?\-[\s]?digital|[^a-z][^d]CDC[s]?[^a-z]|Sensor\s+Interface|(?:capacitive|capacitance)\s+sensor|(?:capacitive|Capacitance)\s*\-\s*Digital\s*\-\s*|(?:capacitive|capacitance)\s*[\-]?\s*sensor|(?:capacitance|capacitive)\s+[a-z]*\s+sensor|digital\s+(?:capacitance|capacitive))[s]?|CDC|[0-9]+\W?bits',f.read())
        f.close()
        f=open(os.path.join(txtDir,text),errors='ignore')
        ADC_words=re.findall(r'ADC|INL|DNL|(?i)(?:analog[\s]?\-[\s]?to[\s]?\-[\s]?digital|[^a-z]ADC[s]?[^a-z])[s]?|A/D|Differential Nonlinearity|Integral Nonlinearity|conversion time|[0-9]+\W?bits',f.read())
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
        temp = re.findall(r'SRAM|RAM', f.read()[:500])
        SRAM_words = []
        if len(temp) != 0:
            for _ in range(0,100):
                SRAM_words += 'P'
        else:
            SRAM_words = re.findall(r'[^a-z](?: SRAM | RAM |memory|memories|(?:read|write)\s+cycle)[s]?[^a-z]|static|[0-9]+\w\s?x\s?[0-9]+\s?bits?',f.read())
        f.close()
        f=open(os.path.join(txtDir,text),errors='ignore')
        Temperature_Sensor_words = re.findall(r'(?i)(?:(?:thermal|temperature)\s+sensor|(?:thermal|Temperature)\s+Detect(?:ion|or)|Humidity\s+(?:and|&)\s+(?:thermal|Temperature)|(?:thermal|Temperature)\s+(?:and|&)\s+Humidity|(?:thermal|temperature)\s+alarm|[^a-z]thermometer[s]?[^a-z]|[^a-z]RTD[s]?[^a-z]|Resistance\s+(?:thermal|Temperature)\s+Detector|(?:thermal|Temperature)\s+conversion|Temperature\s+result|thermistor)[s]?',f.read())
        f = open(os.path.join(txtDir, text), errors='ignore')
        temp = re.findall(r'(?i)buffer/line driver|SINGLE BUFFER|State Buffer|Non-Inverting Buffer|3-state|non-inverting|BIDIRECTIONAL TRANSCEIVER|Schmitt\-?trigger buffer|Triple Buffer|Single Input Buffer|Buffer with open-drain output',f.read()[:500])
        BDRT_words = []
        if len(temp) !=0:
            for _ in range(0,200):
                BDRT_words += 'P'
        else:
            BDRT_words = re.findall(r'(?i)(?:triple|input|quads?|3-state|octal|non-inverting)\s?buffers?|buffer/line driver|BIDIRECTIONAL TRANSCEIVER|Schmitt trigger buffer', f.read())
        f.close()
        f = open(os.path.join(txtDir, text), errors='ignore')
        temp = re.findall(r'(?i)counters?', f.read()[:300])
        COUNTER_words = []
        if len(temp) != 0:
            for _ in range(0,200):
                COUNTER_words += 'P'
        else:
            COUNTER_words = re.findall(r'(?i)[0-9]+\W?(?:bits?|stage)\s?binary\s?[a-z]*\s?counter|counter', f.read())
        f.close()
        f = open(os.path.join(txtDir, text), errors='ignore')
        DAC_words = re.findall(r'DAC|(?i)digital\W?to\W?analog\W?converter|process\s?control', f.read())
        f.close()
        f = open(os.path.join(txtDir, text), errors='ignore')
        DELAY_LINE_words = re.findall(r'(?i)delay\s?(?:range|block|lines?|chip|matching|\s?[A-Z]*\s?[0-9]+[a-z]?s)', f.read())
        f.close()
        f = open(os.path.join(txtDir, text), errors='ignore')
        temp = re.findall(r'DSP|(?i)Digital\sSignal\sProcessor', f.read()[:1000])
        DSP_words = []
        if len(temp) != 0:
            for _ in range(0,200):
                DSP_words += 'P'
        else:
            DSP_words = re.findall(r'\sDSP\s|(?i)Digital Signal Processor', f.read())
            if len(DSP_words) > 10:
                for _ in range(0, 200):
                    DSP_words += 'P'
        f.close()
        f = open(os.path.join(txtDir, text), errors='ignore')
        temp = re.findall(r'(?i)I/O expanders?|I/O Port Expander|Input/Output \(GPIO\) expansion|I/O port with ', f.read()[:1000])
        IO_words = []
        if len(temp) != 0:
            for _ in range(0,200):
                IO_words += 'P'
        else:
            IO_words = re.findall(r'(?i)I/O expanders?|I2C|SPI|GPIO', f.read())
        f.close()
        f = open(os.path.join(txtDir, text), errors='ignore')
        OPAMP_words = re.findall(r'(?i)operation(?:al) amplifiers?|op\Wamps?|rail\s?to\s?rail', f.read())
        f.close()
        f = open(os.path.join(txtDir, text), errors='ignore')
        POTENTIOMETER_words = re.findall(r'(?i)Potentiometers?|wiper|readback|position|Digitally\WControlled', f.read())
        f.close()

        occurrence_array=[len(CDC_words),len(ADC_words),len(DCDC_words),len(LDO_words),len(PLL_words),len(SRAM_words),len(Temperature_Sensor_words), len(BDRT_words), len(COUNTER_words), len(DAC_words), len(DELAY_LINE_words),len(DSP_words), len(IO_words), len(OPAMP_words), len(POTENTIOMETER_words)]
        occurrence_array_copy=[len(CDC_words),len(ADC_words),len(DCDC_words),len(LDO_words),len(PLL_words),len(SRAM_words),len(Temperature_Sensor_words), len(BDRT_words), len(COUNTER_words), len(DAC_words), len(DELAY_LINE_words), len(DSP_words), len(IO_words), len(OPAMP_words), len(POTENTIOMETER_words)]
        #print (occurrence_array)
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
                elif maximum_occurrence[i]==7:
                    title='BDRT'
                elif maximum_occurrence[i]==8:
                    title='counters'
                elif maximum_occurrence[i]==9:
                    title='DAC'
                elif maximum_occurrence[i]==10:
                    title='Delay_Line'
                elif maximum_occurrence[i]==11:
                    title='DSP'
                elif maximum_occurrence[i]==12:
                    title='IO'
                elif maximum_occurrence[i]==13:
                    title='Opamp'
                elif maximum_occurrence[i]==14:
                    title='Digital_Potentiometers'
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
        #print (title)
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
