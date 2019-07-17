#MIT License
#
# Copyright (c) 2018 The University of Michigan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import decision_extractor
import text_cleaner
import clean_string_single
import clean_string_multiple
import unit_convert
import re
def element_extracter(path,word_main,word_spare,subject,element,rex):
    total_specific_result = []
    [number_of_exact_words, lines] = text_cleaner.text_cleaner(path, word_main)
    with open(path, 'r', encoding='utf-8') as file:
        target = re.compile(rex)
        general_result = re.findall(target, file.read())
        #print("general:")
        #print(general_result)
        general_result=clean_string_single.clean_string_single(general_result)
        if len(number_of_exact_words)==0:
            [number_of_exact_words, lines] = text_cleaner.text_cleaner(path, word_spare)
            if len(number_of_exact_words)==0:
                #print("We don't have specific")
                strings_element,number_of_occurance = decision_extractor.decision_extractor(general_result,[])
                #print("{text}{number}".format(text=subject+"'s "+element+" is ", number=strings_element))
                #print("specific:")
                #print([])
                return strings_element,number_of_occurance
        if len(number_of_exact_words) > 0:
            for j in range(0, len(number_of_exact_words)):
                new_lines = lines[number_of_exact_words[j] + 1:number_of_exact_words[j] + 36]
                data = '\n'.join(line.rstrip() for line in new_lines)
                specific_result = re.findall(target, data)
                specific_result=clean_string_single.clean_string_single(specific_result)
                total_specific_result.append(specific_result)
            specific_result=clean_string_multiple.clean_string_multiple(total_specific_result)
            #print("specific:")
            #print(specific_result)
            strings_element,number_of_occurance = decision_extractor.decision_extractor(general_result, specific_result)
            #print("{text}{number}".format(text=subject+"'s "+element+" is ", number=strings_element))
            return strings_element,number_of_occurance
