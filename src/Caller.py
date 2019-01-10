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

def Caller(new_specs,old_output):
    auxiliary_value=[0]
    if 3<new_specs[3]<7:
        old_output[new_specs[3]-4]=new_specs[new_specs[3]]
    elif new_specs[3]==7:
        del new_specs[7][2:5]
        old_output[3].append(new_specs[7])
    elif new_specs[3]==72:
        auxiliary_value[0]=new_specs[7][2:5]
        old_output[3][-1].append(auxiliary_value[0])
    elif new_specs[3]==75:
        pass
    elif new_specs[3]==8:
        old_output[4].append(new_specs[8])
    new_output=old_output
    #print(new_output)
    return(new_output)
