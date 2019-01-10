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

from collections import defaultdict
import numpy as np
def old_decision_maximum_occurance(array_occurance):
    array_occurance_len=len(array_occurance)
    non_equal_cells=False
    k=0
    result_5=[]
    for i in range(0,array_occurance_len-1):
        if array_occurance[i]!=array_occurance[i+1]:
            non_equal_cells=True
            break
    if non_equal_cells:
        d = defaultdict(int)
        for i in array_occurance:
            d[i] += 1
        result = max(d.items(), key=lambda x: x[1])
        '''Change iteritems to items'''
        result_1=result[1]
        result_2=[[x,array_occurance.count(x)] for x in set(array_occurance)]
        result_3=np.array(result_2)
        result_4=result_3[:,1]
        for element in result_4:
            result_5.append(int(element))
        for element in result_5:
            if result_1==element:
                k+=1
    return(non_equal_cells,k)

'''Faster and simplier version'''
'''Replace the decision_maximum_occurance with the following one '''
from collections import Counter
def decision_maximum_occurance(array_occurance):
    if len(array_occurance) != len(set(array_occurance)):
        k=0
        count=Counter(array_occurance)
        for member in count:
            if count[member]==count.most_common(1)[0][1]:
                k+=1
                return False,k,count[member]
            else:
                return True,k,count[member]
    else:
        return False,0,1
