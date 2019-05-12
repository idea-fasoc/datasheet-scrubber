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
def find_pin(target_pin,old_place,new_place,lines,final_result,depth,width):
    in_line_place = -1
    if new_place+width < old_place+50 and depth<3:
        for element in lines[new_place:new_place + width]:
            in_line_place = in_line_place +1
            if element != '\n':
                word = element.split(' ')
                for element in word:
                    if element != '' and element != '\n':
                        result = re.findall(target_pin, element)
                        if len(result) == 1:
                            for element in result:
                                if len(element) > 1 and len(
                                        element) < 6 and element != 'PIN' and element != 'NAME' and element != 'TYPE' and element != 'UNIT':
                                    final_result.append(result)
                                    if width>5:
                                        width = width - 2
                                    find_pin(target_pin,old_place,new_place+in_line_place+1,lines,final_result,depth+1,width)
                                else:
                                    continue
def pin_extraction(path):
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        place = -1
        final_result = []
        target = re.compile(r'(?i)pin\s?\/?(?:functions?|descriptions?)')
        target_pin = re.compile(r'[A-Z]{1,4}[0-9]{0,2}')
        for line in lines:
            place = place+1
            new_place = place
            if len(re.findall(target,line)) != 0:
                find_pin(target_pin,place,new_place,lines,final_result,0,15)
    output_result = []
    for element in final_result:
        if element not in output_result:
            output_result.append(element)
    return output_result
