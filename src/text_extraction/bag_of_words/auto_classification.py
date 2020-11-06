#!/usr/bin/env python3

# MIT License

# Copyright (c) 2018 The University of Michigan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from single_layer_classification import page_classification, paragraph_classification, subparagraph_classification, sentence_classification
from os.path import isdir
import os
import shutil

def auto_classification(training_list, testing_list):
    [page_train, para_train, subpara_train, sentence_train] = training_list
    [page_test, para_test, subpara_test, sentence_test] = testing_list
    print("start page classification:")
    page_classification_result = page_classification(page_train, page_test)
    has_perfect = False
    for page, pred in page_classification_result:
        if pred == 'perfect':
            has_perfect = True
            copy_src = os.path.join("All_paragraph_folders/ADC", page)
            copy_dst = os.path.join(para_test, page)
            if isdir(copy_src):
                shutil.copytree(copy_src, copy_dst)
                print("Correctly classified page: {}".format(page))
            else:
                print("Wrongly classified page: {}".format(page))
    if not has_perfect:
        print('no perfect page in this testing group')
        exit(0)
    print("start paragraph classification:")
    paragraph_classification_result = paragraph_classification(para_train, para_test)
    for result_list in paragraph_classification_result:
        has_perfect = False
        for paragraph, pred in result_list:
            if pred == 'perfect':
                has_perfect = True
                copy_src = os.path.join("All_subparagraph_folders/ADC", paragraph)
                copy_dst = os.path.join(subpara_test, paragraph)
                shutil.copytree(copy_src, copy_dst)
        if not has_perfect:
            for paragraph, pred in result_list:
                if pred == 'good':
                    copy_src = os.path.join("All_subparagraph_folders/ADC", paragraph)
                    copy_dst = os.path.join(subpara_test, paragraph)
                    shutil.copytree(copy_src, copy_dst)
    print("start subparagraph classification:")
    subparagraph_classification_result = subparagraph_classification(subpara_train, subpara_test)
    for subparagraph, pred in subparagraph_classification_result:
        if pred == 'perfect':
            copy_src = os.path.join("All_sentence_folders/ADC", subparagraph)
            copy_dst = os.path.join(sentence_test, subparagraph)
            if isdir(copy_src):
                shutil.copytree(copy_src, copy_dst)
                print("Correctly classified subparagraph: {}".format(subparagraph))
            else:
                print("Wrongly classified subparagraph: {}".format(subparagraph))
    print("start sentence classification:")
    sentence_classification_result = sentence_classification(sentence_train, sentence_test)
    return sentence_classification_result
