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

import decision_maximum_occurance
def decision_extractor(strings_ADC_Bit_general,strings_ADC_Bit_specific):
    non_equal_cells_general=False
    non_equal_cells_specific=False
    general_len=len(strings_ADC_Bit_general)
    specific_len=len(strings_ADC_Bit_specific)
    if general_len==0:
       # print("Nothing find at all")
        return [], 0
    elif general_len!=1:
        [non_equal_cells_general,k_general,occurance]=decision_maximum_occurance.decision_maximum_occurance(strings_ADC_Bit_general)
        if non_equal_cells_general:
            if k_general==1:
                max_general_occurance=max(set(strings_ADC_Bit_general), key=strings_ADC_Bit_general.count)
                #print ("More than one general is founded and they are not equal but they have one maximized occurance")
            else:
                max_general_occurance=strings_ADC_Bit_general[0]
                #print ("More than one general is founded and they are not equal and they have more than one maximized occurance")
        else:
            max_general_occurance=strings_ADC_Bit_general[0]
            #print ("More than one general is founded and they are equal")
            strings_ADC_Bit=strings_ADC_Bit_general[0]
            return strings_ADC_Bit, occurance
    else:
        #print("There is only one general")
        strings_ADC_Bit=strings_ADC_Bit_general[0]
        return strings_ADC_Bit,1
    if specific_len==0:
        #print ("Specific isn't founded")
        strings_ADC_Bit=max_general_occurance
        return strings_ADC_Bit,occurance
    elif specific_len==1:
        #print("only one specific is founded")
        #if strings_ADC_Bit_specific[0]!=max_general_occurance:
            #print("one specific and it is not equal to max of general")
        strings_ADC_Bit=strings_ADC_Bit_specific[0]
        return strings_ADC_Bit,occurance+1
    else:
        [non_equal_cells_specific,k_specific,occurance_specific]=decision_maximum_occurance.decision_maximum_occurance(strings_ADC_Bit_specific)
        if non_equal_cells_specific:
            if k_specific==1:
                max_specific_occurance=max(set(strings_ADC_Bit_specific), key=strings_ADC_Bit_specific.count)
                #print ("More than one specific is founded and they are not equal but they have one maximized occurance")
            else:
                max_specific_occurance=strings_ADC_Bit_specific[0]
                #print ("More than one specific is founded and they are not equal and they have more than one maximized occurance")
        else:
            max_specific_occurance=strings_ADC_Bit_specific[0]
            #print ("More than one specific is founded and they are equal")
        if max_general_occurance!=max_specific_occurance:
            strings_ADC_Bit=max_specific_occurance
            #print ("More than one specific is founded and max of specific isn't equal to max of general")
        else:
            #print ("More than one specific is founded but max of specific is equal to max of general")
            strings_ADC_Bit=max_specific_occurance
        return strings_ADC_Bit, occurance+occurance_specific
