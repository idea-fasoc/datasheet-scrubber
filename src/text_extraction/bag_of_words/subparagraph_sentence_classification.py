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

# This function is the original implementation of feedback loop. It is inconsistent with the current classification structure."""
#from Address import Address
from subparagraph_classification import subparagraph_classification
from sentence_classification_loop import sentence_classification
import os
import shutil


def subparagraph_sentence_classification(training_folder, testing_folder):
    # Path_extracted = Address(1).split("\n")
    # Path_extracted1 = Path_extracted[0]
    code_dir = os.path.dirname(__file__)
    main_dir = os.path.relpath(os.path.join(code_dir,"../.."))
    Path_extracted1 = main_dir
    # a list of paths
    all_paragraph_folder = 'All_subparagraph_folders/ADC'  # folders with paragraph name, containing subparagraphs
    all_subparagraph_folder = 'both_subparagraph_sentence_folders/ADC'  # folders with subparagraph name, containing sentences
    training_folder = 'training_set_subparagraphs_text'
    testing_sentence_folder = 'subparagraph_sentence_test_2'
    paragraphDir = os.path.join(Path_extracted1, all_paragraph_folder)
    subparagraphDir = os.path.join(Path_extracted1, all_subparagraph_folder)
    training_subparagraph = os.path.join(Path_extracted1, training_folder)
    testing_sentence = os.path.join(Path_extracted1, testing_sentence_folder)
    subparagraphtxtDir = os.path.join(Path_extracted1, 'All_subparagraph_text/ADC')
    subparagraph_set = os.path.join(Path_extracted1, 'subparagraphs/ADC')

    # record all the paragraph names with ".txt"
    paragraph_list = []
    for file in os.listdir(paragraphDir):
        file = file + ".txt"
        paragraph_list.append(file)
    # generate labeled set
    subparagraph_labels = {}
    for labeled_class in os.listdir(subparagraphtxtDir):
        class_path = os.path.join(subparagraphtxtDir, labeled_class)
        for subparagraph_txt in os.listdir(class_path):
            subparagraph_name = subparagraph_txt.split(".txt")[0]
            subparagraph_labels.update({subparagraph_name: labeled_class})

    # run the subparagraph classification code
    subparagraph_classifier_result = subparagraph_classification('ADC')
    # put pred perfect subparagraph folders into sentence testing set
    for subparagraph, pred in subparagraph_classifier_result:
        if pred == 'perfect':
            sentence_path = os.path.join(subparagraphDir, subparagraph)
            copy_src = sentence_path
            copy_dst = os.path.join(testing_sentence, subparagraph)
            shutil.copytree(copy_src, copy_dst)
    [sentence_classifier_result, feedback, prob_subparagraph] = sentence_classification('ADC')
    while feedback != 0:
        # put wrongly classified subparagraph into "bad" folder
        prob_file = prob_subparagraph + ".txt"
        copy_src = os.path.join(subparagraph_set, prob_file)
        copy_dst = os.path.join(training_subparagraph, 'bad')
        shutil.copy(copy_src, copy_dst)
        # clean up folders from which sentences are extracted
        for directory in os.listdir(testing_sentence):
            shutil.rmtree(os.path.join(testing_sentence, directory))
        # test subparagraphs again
        subparagraph_classifier_result = subparagraph_classification('ADC')
        # extract sentence again
        for subparagraph, pred in subparagraph_classifier_result:
            if pred == 'perfect':
                sentence_path = os.path.join(subparagraphDir, subparagraph)
                copy_src = sentence_path
                copy_dst = os.path.join(testing_sentence, subparagraph)
                shutil.copytree(copy_src, copy_dst)
        [sentence_classifier_result, feedback, prob_subparagraph] = sentence_classification('ADC')
    return sentence_classifier_result
