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

def clean_string_single(string_ADC_Bit):
    updated_string_ADC_Bit=[]
    broken=True
    for element in string_ADC_Bit:
        for j in range(0, len(element)):
            if element[j] != '':
                updated_string_ADC_Bit.append(element[j])
            else:
                broken=False
    # for element in updated_string_ADC_Bit:
    #     if len(element)!=1:
    #         broken=False
    if broken:
        updated_string_ADC_Bit=string_ADC_Bit
    return updated_string_ADC_Bit
    #it will make 0.5 Hz to 900 Mhz  to 0 . 5 H Z....

'''clean_string_single has bug when deal with tlv320adc3100.txt 
input['','','92'] output[]'''
#input ['4 Hz to 2 Hz'] will output []
