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

def text_cleaner(path,word):
    with open(path,'r', encoding='utf-8') as f_specific: #add encoding ='utf-8'
        lines = f_specific.read().split("\n")
    number_of_exact_words=[]
    i=0
    while -1<i<len(lines):
        lines[i]=lines[i].lower()
        for m in range(0,len(word)):
            if word[m] in lines[i]:
                number_of_exact_words.append(i)
                if len(lines[i-1])>1:
                   number_of_exact_words.pop()
                elif len(lines[i])>len(word[m])+1:
                    number_of_exact_words.pop()
                    if lines[i][0] in ['1','2','3','4','5','6','7','8','9','10']:
                        if lines[i][1] in ['.','-',' ']:
                            if len(lines[i])<len(word[m])+5:
                                number_of_exact_words.append(i)
        i+=1
    return(number_of_exact_words,lines)
