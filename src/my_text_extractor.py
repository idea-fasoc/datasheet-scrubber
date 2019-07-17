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

import element_extracter
import unit_convert
import os
import pdftotext
def my_text_extractor(subject, path):
    result={}
    General={
        'Input Supply Voltage Range': {
            'rex': r'(?i)(?:input voltages?)[^0-9|\.|\/]*([0-9]+\.?[0-9]*\s?v?\s?to\s?[0-9]+\.?[0-9]*\s?v)|([0-9]+\.?[0-9]*\s?v\s?to\s?[0-9]+\.?[0-9]*\s?v)[^0-9|\.|\/]*(?:input voltages?)|([0-9]+\.?[0-9]*\s?v)[^0-9|\.|\/]*(?:operating|input voltages?)|(?:operating|input voltages?)[^0-9|\.|\/]*([0-9]+\.?[0-9]*\s?v)',
            'word_main': ['description', 'descriptions'],
            'word_spare': ['features', 'feature']
            },
        'Temperature': {'rex': r'(?i)(?:temperature)[^0-9]{0,15}(\W?\-?\+?[0-9]+\s?\W?c?(?:[^0-9\-]){0,6}\-?\+?[0-9]+\s?\Wc)|(\W?\-?\+?[0-9]+\Wc(?:[a-z\s]){0,6}\W?\-?\+?[0-9]+\Wc)\s?(?:temperature)',
                        'word_main':['features', 'key features'],
                        'word_spare': ['description']}

    }
    ADC={
        'Resolution':{'rex':r"(?i)([0-9]+)-?bit[s]?(?:(?:\s|\-|,)[\s]?[0-9a-z\-.]*[ ]?){0,10}(?:analog[\s]?\-[\s]?to[\s]?\-[\s]?digital|ADC|A/D)|([0-9]+)[\s\-]?bit[s]?\s?(?:of|\s)\s?(?:resolution|converter)",
                       'word_main': ["product description", "general  description", "general description", "introduction"],
                       'word_spare': ["description"]},
        'INL':{'rex': r'((?:\+|\-|(?:\xc2\xb1))?[0-9]*\.[0-9]+|(?:\+|\-|(?:\xc2\xb1))?[0-9]+)[ ]*LSB[ ]*INL|INL[ ]*[:=]?[ ]*((?:\+|\-|(?:\xc2\xb1))?[0-9]*\.[0-9]+|(?:\+|\-|(?:\xc2\xb1))?[0-9]+)[ ]*LSB',
                 'word_main': ["product description", "product  description", "general  description", "general description", "introduction"],
                 'word_spare': ["features"]},
        'DNL':{'rex': r'(?i)\W?([0-9]+\.?[0-9]*)\s?(?:LSB)\s?(?:max?\s?DNL)|(?:DNL:\s|Differential Nonlinearity Error:\s)\n?\W?([0-9]+\.[0-9]*)\s?(?:LSB)',
                'word_main': ["product description"],
                'word_spare': ["description"]},
        'SNR':{'rex':r'(?i)SNR(?:\w|\W){0,32}\:?\s?\W*([0-9]+\.?[0-9]*\sdB[FS]*)|SNR\W of ([0-9]+\.?[0-9]*dB[FS]*)|([0-9]+\.?[0-9]*\sdB[FS]*)\s?(?:[a-z]|\W){0,20}\sSNR|([0-9]+\.?[0-9]*\WdBA)\sSignal-to-Noise Ratio',
                'word_main':["product description"],
                'word_spare':["description"]},
        'THD':{ 'rex':r'(?i)THD:\s?([^.][0-9]+\s?dB)|([^.][0-9]+\s?dB)\s?(?:THD|total harmonic distortion)',
                'word_main':["product description"],
                'word_spare':["description"]},
        'Conversion Rate':{ 'rex':r'(?i)([0-9]+\sMSPS)\s(?:conversion\srate)|(?:conversion rate of )([0-9]+\sMSPS)',
                            'word_main':["product description"],
                            'word_spare':["description"]},
        'Sampling Frequency':{'rex': r'(?i)(?:signal|sampling|sample)\s?(?:frequency|rate)(?:[^0-9]){0,10}([0-9]+\s?k?M?Hz)|(?:signal|sampling|sample)\s?(?:frequency|rate){0,1}(?:[^0-9]){0,15}([0-9]+\s?MSPS)|([0-9]+\.?[0-9]*\W?M?k?Hz)\s?(?:signal|sampling|sample)\s?(?:frequency|rate){0,1}|([0-9]+\.?[0-9]*\s?k?M?SPS)\s?[^0-9]*(?:signal|sampling|sample)\s?(?:frequency|rate){0,1}',
                              'word_main': ['specificcations'],
                              'word_spare': ['features'] }
    }
    PLL={
        'Output Frequency': {'rex':r'(?i)(?:outputs?|clocks?)\s?(?:frequenc(?:y|ies)|clocks?)\s?(?:[a-z]+)?\s?(?:from)\s?([0-9]+\.?[0-9]*\s?k?M?G?\s?Hz\s?(?:(?:up\s)?to)\s?[0-9]+\.?[0-9]*\s?k?M?G?\s?Hz)|(?i)(?:output\s(?:frequency)\s?up\sto)\s?([0-9]+\.?[0-9]*\s?k?M?G?\s?Hz)',
                            'word_main':["description","product description","general description"],
                            'word_spare':["features and benefits","features","general features","key features"]},
        'Step Size': {'rex': r'(?i)(?:step size\s?[is]*\s?)([0-9]+\s?ps)',
                     'word_main': ["description","product description","general description"],
                     'word_spare': ["features and benefits","features","general features","key features"]},
        'Frequency Stability':{ 'rex':r'(?i)([0-9]+\sppm\W?\w?\s?)(?:frequency stability)',
                               'word_main':["features and benefits","features","general features","key features"],
                               'word_spare':["description","product description","general description"]},
        'Bandwidth':{'rex':r'(?i)(?:bandwidth from )([0-9]+\sHz to [0-9]+\sHz)',
                     'word_main': ["features and benefits","features","general features","key features"],
                     'word_spare': ["description", "product description","general description"]},
        'Reference Frequency': {'rex': r'(?i)([0-9]+\.?[0-9]*\s?k?M?G?\s?Hz)(?: reference frequency)',
                                'word_main': ["DIRECT CONVERSION MODULATOR"],
                               'word_spare': ["features and benefits","features","general features","key features"]},
        'Reference Spur':{'rex': r'(?i)(?:reference spur)(?:[a-z]|[^-]){0,20}(\-?[0-9]+ dBc?)',
                          'word_main': ["LOCAL OSCILLATOR FOR THE GSM BASE STATION TRANSMITTER"],
                          'word_spare': ["features and benefits","features","general features","key features"]},
        }
    Temperature_Sensor={
        'Temperature Range':{'rex':r'(?i)(?:temperature range)(?:[a-z\s\:]){0,6}(\W?\-?\+?[0-9]+\s?\W?c?(?:[^0-9\-]){0,6}\-?\+?[0-9]+\s?\Wc)|(\W?\-?\+?[0-9]+\Wc(?:[a-z\s]){0,6}\W?\-?\+?[0-9]+\Wc)\s?(?:temperature range)',
                             'word_main': ["features","data","description"],
                             'word_spare': ["Dew Point"]},
        'Resolution':{'rex':r'(?i)([0-9]+\.?[0-9]*\Wc\s?)(?:resolutions?)|(?:resolutions?)(?:[a-z\s\:\-\(\)0-9]){0,30}([0-9]+\.?[0-9]*\s?\WC\s?)',
                      'word_main': ['features'],
                      'word_spare': ['general','temperautre sensor']},
        'Nonlinearity':{'rex':r'(?i)(?:Nonlinearity)(?:[a-z]|\s){0,10}(\W[0-9]+\.?[0-9]*\W\w)',
                        'word_main':['features','feature'],
                        'word_spare':['description']}
        }
    SRAM={
        'Row': {'rex': r'(?i)([0-9]+\,?[0-9]*\,?[0-9]*k?m?)\W?\s?(?:words?)|(?i)([0-9]+\,?[0-9]*\,?[0-9]*k?m?)(?:\s?x\s?[0-9]+\s?(?:bits?|Static\s?Random\s?Access\s?Memory|sram|cmos static ram|advanced high-speed cmos static ram))',
                'word_main': ['description'],
                'word_spare': ['overview']},
        'Column':{'rex': r'(?i)\s([0-9][0-9]?k?m?)(?:\-?\s?(?:bits?|Static\s?Random\s?Access\s?Memory|sram))|(?i)(?:[0-9]+k?m?)(?:\s?x\s?)([0-9]+)(?:bits?|Static\s?Random\s?Access\s?Memory|sram|cmos static ram)',
                   'word_main': ['description'],
                   'word_spare': ['overview']},
        'Access Time': {'rex': r'(?i)([0-9]+\s?n?s)(?:[a-z]|\s){0,11}(?:access time)|(?i)(?:access times?\:?\s?)(?:[a-z]|\s){0,10}((?:\s?[0-9]+\s?n?s?\,? ?\&?(?:and)*){1,4})|(?i)(?:access time)(?:\s?\.?){0,20}([0-9]+\/[0-9]+ns)',
                        'word_main': ['features'],
                        'word_spare': ['description']},
        'Cycle Time': {'rex': r'(?i)(?:cycle\s*times\s*)(?:[^0-9]){0,17}([0-9]+\s?n?s)',
                        'word_main': ['features'],
                        'word_spare': ['feature']
                       },
        'Capacity': {'rex': r'(?i)(?:a\s?)[^0-9]{0,10}([0-9]+\,?[0-9]*\,?[0-9]*(?:\W)k?m?)\W?(?:bits?)',
                     'word_main': ['overview'],
                     'word_spare':['general description']}
    }
    CDC={
        'Resolution': {'rex': r'(?i)([0-9]+)(?:\-?bits?)(?:[a-z]|\s){0,30}(?:resolution)|(?:resolution)(?:[a-z]|\s){0,10}([0-9]+)(?:bits?)|(?:resolution)\:\s*([0-9]+)(?:\s?bits?)',
                       'word_main': ['description'],
                       'word_spare': ['features']
                       },
        'Input Capacitance Range': {'rex': r'(?:input|sensor capacitance|range)[^0-9]*(\W?[0-9]+\s?p?F?)',
                              'word_main': ['features'],
                              'word_spare': ['description']}
    }
    LDO={
        'Dropout Voltage': {'rex':r'(?i)(?:dropout voltages?)\s?(?:[a-z]|\s|\:){0,32}(?:\([0-9]+\.?[0-9]*v\)\:?\s?){0,1}([0-9]+\.?[0-9]*\s?m?V)|(?:dropout\svoltage)\.*(?:[a-z]|\.|\s){0,6}([0-9]+\.?[0-9]*\s?m?V)',
                            'word_main': ['features'],
                            'word_spare': ['description']
                            },
        'Quiescent Current in Shutdown': {'rex': r'(?i)([0-9]+\s?u?m?µ?A)(?:[a-z]|\s){0,10}(?:quiescent current)|(?:quiescent current\s?\(?)(?:[a-z]|\s|\.){0,30}([0-9]+\s?u?m?µ?A)|(?: shutdown current)(?:[a-z]|\s|\.){0,30}([0-9]+\s?u?m?µ?A)',
                              'word_main': ['features'],
                              'word_spare': ['description', 'general description']
                              },
        'PSRR': {'rex': r'(?i)(?:PSRR\s?\:?)(?:[a-z]|\s|\(|>){0,20}([0-9]+\s?dB)',
                 'word_main': ['features'],
                 'word_spare': ['description']
                 },
        'RMS': {'rex': r'(?i)([0-9]+\.?[0-9]*\s?µ?V)(?:\s?RMS)',
                'word_main': ['features'],
                'word_spare': ['description']
                },
        'Output Current': {'rex': r'(?i)(?:output current)(?:[a-z]|\s){0,10}([0-9]+\.?[0-9]*\s?m?A)|([0-9]+\.?[0-9]*\s?m?A)(?:[a-z]|\s){0,20}(?:output current)',
                           'word_main': ['features'],
                           'word_spare': ['description']
                           },
        'Initial Accuracy': {'rex': r'(?i)(\W?[0-9]+\.?[0-9]*\%)(?:\s?accuracy)|(?:accuracy\s?)(?:[a-z]|\s|\:){0,20}(\W?[0-9]+\.?[0-9]*\%)|(?:accuracy\s?)\.*\s?(\W?[0-9]+\.?[0-9]*\%)',
                             'word_main': ['features'],
                             'word_spare': ['description']},
        'Input Voltage': {
            'rex': r'(?i)(?:input voltages?)[^0-9|\.|\/]*([0-9]+\.?[0-9]*\s?v?\s?to\s?[0-9]+\.?[0-9]*\s?v)|([0-9]+\.?[0-9]*\s?v\s?to\s?[0-9]+\.?[0-9]*\s?v)[^0-9|\.|\/]*(?:input voltages?)|([0-9]+\.?[0-9]*\s?v)[^0-9|\.|\/]*(?:input voltages?)|(?:input voltages?)[^0-9|\.|\/]*([0-9]+\.?[0-9]*\s?v)',
            'word_main': ['description', 'descriptions'],
            'word_spare': ['features', 'feature']
            },
    }
    DCDC={
        'Input Voltage': {'rex':r'(?i)(?:input voltages?)[^0-9|\.|\/]*([0-9]+\.?[0-9]*\s?v?\s?to\s?[0-9]+\.?[0-9]*\s?v)|([0-9]+\.?[0-9]*\s?v\s?to\s?[0-9]+\.?[0-9]*\s?v)[^0-9|\.|\/]*(?:input voltages?)|([0-9]+\.?[0-9]*\s?v)[^0-9|\.|\/]*(?:operating|input voltages?)|(?:operating|input voltages?)[^0-9|\.|\/]*([0-9]+\.?[0-9]*\s?v)',
                          'word_main':['description','descriptions'],
                          'word_spare': ['features','feature']
        },
        'Output Voltage': {'rex': r'(?i)(?:output voltages?)[^0-9|\.|\/]*([0-9]+\.?[0-9]*\s?v\s?to\s?[0-9]+\.?[0-9]*\s?v)|([0-9]+\.?[0-9]*\s?v\s?to\s?[0-9]+\.?[0-9]*\s?v)[^0-9|\.|\/]*(?:output voltages?)|([0-9]+\.?[0-9]*\s?v)[^0-9|\.|\/]*(?:output voltages?)|(?:output voltages?)[^0-9|\.|\/]*([0-9]+\.?[0-9]*\s?v\,?\s?){1,6}',
                           'word_main':['description','descriptions'],
                           'word_spare': ['features','feature']
        },
        'Load Current': {'rex': r'(?i)([0-9]+\.?[0-9]*\s?a)[^0-9|\.|\/]*(?:load|output current)',
                         'word_main': ['description', 'descriptions'],
                         'word_spare': ['features', 'feature']
        }
    }
    if subject == "ADC":
        for keys in ADC:
            result[keys] = element_extracter.element_extracter(path,ADC[keys]['word_main'],ADC[keys]['word_spare'],"ADC",keys,ADC[keys]['rex'])
    if subject == "PLL":
        for keys in PLL:
            result[keys]= element_extracter.element_extracter(path,PLL[keys]['word_main'],PLL[keys]['word_spare'],"PLL",keys,PLL[keys]['rex'])
    if subject == "Temperature_Sensor":
        for keys in Temperature_Sensor:
            result[keys] = element_extracter.element_extracter(path,Temperature_Sensor[keys]['word_main'],Temperature_Sensor[keys]['word_spare'],"Temperautre Sensor",keys,Temperature_Sensor[keys]['rex'])
    if subject == 'SRAM':
        for keys in SRAM:
            result[keys] = element_extracter.element_extracter(path,SRAM[keys]['word_main'],SRAM[keys]['word_spare'],'SRAM',keys,SRAM[keys]['rex'])
    if subject == 'CDC':
        for keys in CDC:
            result[keys] = element_extracter.element_extracter(path, CDC[keys]['word_main'],CDC[keys]['word_spare'], 'CDC', keys,CDC[keys]['rex'])
    if subject == 'LDO':
        for keys in LDO:
            result[keys] = element_extracter.element_extracter(path, LDO[keys]['word_main'], LDO[keys]['word_spare'], 'LDO', keys, LDO[keys]['rex'])
    if subject == 'DCDC':
        for keys in DCDC:
            result[keys] = element_extracter.element_extracter(path, DCDC[keys]['word_main'], DCDC[keys]['word_spare'], 'DCDC', keys, DCDC[keys]['rex'])
    if subject == 'General':
        for keys in General:
            result[keys] = element_extracter.element_extracter(path, General[keys]['word_main'], General[keys]['word_spare'], 'General', keys, General[keys]['rex'])
    new_result = {}
    for keys in result:
        if result[keys][0] != []:
            new_result[keys] = {'value': unit_convert.unit_convert(result[keys][0]), 'Occurrence': result[keys][1]}
    return new_result
