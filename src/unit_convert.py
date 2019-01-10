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
def unit_convert(data_in):
    target_number = re.compile(r'\W?[0-9]+\.?\,?[0-9]*\,?[0-9]*')
    target_unit = re.compile(r'(?i)\w?Hz|\w?V|\w?A|\w?s|k|m|m?ksps|\w?f')
    raw_number = re.findall(target_number, data_in)
    raw_unit = re.findall(target_unit, data_in)
    number = []
    unit = []
    for word in raw_number:
        inter_number = ''
        for letter in word:
            if letter.isdigit() or letter == '.' or letter == '-' or letter== '−':
                inter_number += letter
        number.append(inter_number)
    if len(raw_unit)>len(number):
        inter_unit = ''
        for element in raw_unit:
            inter_unit += element
        unit.append(inter_unit)
    else:
        unit=raw_unit
    if unit == []:
        return number
    for element in range(0,len(unit)):
        '''convert Hz'''
        unit[element]=unit[element].lower()
        if unit[element][len(unit[element])-2:len(unit[element])]=='hz':
            if unit[element][0]=='h':
                continue
            if unit[element][0] == 'm':
                number[element] = str(float(number[element]) * 10**6)
            if unit[element][0] == 'g':
                number[element] = str(float(number[element]) * 10**9)
            if unit[element][0] == 'k':
                number[element] = str(float(number[element]) * 10**3)
                '''convert V'''
        if unit[element][len(unit[element])-1:len(unit[element])]=='v':
            if unit[element][0]=='v':
                continue
            if unit[element][0] == 'u':
                number[element] = str(float(number[element]) / 10**6)
            if unit[element][0] == 'm':
                number[element] = str(float(number[element]) / 10**3)
                '''convert s'''
        if unit[element][len(unit[element]) - 1:len(unit[element])] == 's':
            if unit[element][0] == 's':
                continue
            if unit[element][0] == 'p':
                number[element] = str(float(number[element]) / 10**12)
            if unit[element][0] == 'n':
                number[element] = str(float(number[element]) / 10**9)
        '''convert A'''
        if unit[element][len(unit[element]) - 1:len(unit[element])] == 'a':
            if unit[element][0] == 'a':
                continue
            if unit[element][0] == 'u':
                number[element] = str(float(number[element]) / 10**6)
            if unit[element][0] == 'm':
                number[element] = str(float(number[element]) / 10**3)
        '''convert bit'''
        if unit[element][len(unit[element]) - 1:len(unit[element])] == 'k':
            number[element] = str(float(number[element])* 1024)
        if unit[element][len(unit[element]) - 1:len(unit[element])] == 'm':
            number[element] = str(float(number[element])* 1024 ** 2)
        '''convert sps'''
        if unit[element] == 'msps':
            number[element] = str(float(number[element])*10**6)
        if unit[element] == 'ksps':
            number[element] = str(float(number[element])*10**3)
        '''convert f'''
        if unit[element][len(unit[element]) - 1:len(unit[element])] == 'f':
            if unit[element][0] == 'f':
                continue
            if unit[element][0] == 'p':
                number[element] = str(float(number[element]) / 10**12)
            if unit[element][0] == 'n':
                number[element] = str(float(number[element]) / 10**9)
    return number
