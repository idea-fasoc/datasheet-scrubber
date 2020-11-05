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

from pdf_to_text import pdf_to_text
from supervised_classifier_ngram import supervised_classifier_ngram
from judgement import supervised_classifier
#from Address import Address
import pdf_cropper_for_extraction
from os.path import isdir
from os.path import join as p_join
from os import mkdir, listdir, remove
from shutil import rmtree

#This function is to classify perfect pages from datasheets"""
# Input:
# testing_folder: datasheets we want to extract (absolute path)
# training_folder: all pages labelled in three folders (absolute path)
# Output:
# An array with [paragraph_name, pred] tuples; paragraph_name without ".txt".


def page_classification(training_folder, testing_folder):
    # path_extracted = Address(1).split("\n")
    # base_dir = path_extracted[0]
    code_dir = os.path.dirname(__file__)
    main_dir = os.path.relpath(os.path.join(code_dir,"../.."))
    base_dir = main_dir
    pages_pdf_dir = p_join(base_dir, 'tmp_pdf')  # create a temporary directory to split pages
    pages_txt_dir = p_join(base_dir, 'tmp_txt')  # create a temporary directory to convert into texts
    if isdir(pages_pdf_dir):
        rmtree(pages_pdf_dir)
    if isdir(pages_txt_dir):
        rmtree(pages_txt_dir)
    # labels and training directory
    perfect_label = 'perfect'
    bad_label = 'bad'
    perfect_path = [p_join(training_folder, perfect_label), perfect_label]
    bad_path = [p_join(training_folder, bad_label), bad_label]
    SOURCES = [perfect_path, bad_path]
    # crop test pdf into test pages
    pdf_cropper_for_extraction.pdf_cropper_multiple(testing_folder, pages_pdf_dir)
    # convert test pages to text
    page_classification_result = []
    for pdf_folder in listdir(pages_pdf_dir):
        page_pdf = p_join(pages_pdf_dir, pdf_folder)
        page_text = p_join(pages_txt_dir, pdf_folder)
        pdf_to_text(page_pdf, page_text)
        classifier_result = supervised_classifier(SOURCES, page_text)
        page_classification_result = page_classification_result + classifier_result
    rmtree(pages_pdf_dir)
    rmtree(pages_txt_dir)
    return page_classification_result

def paragraph_classification(training_folder, testing_folder):
    # training_folder = p_join(training_folder, subject)
    # SOURCES for training
    perfect_label = 'perfect'
    good_label = 'good'
    bad_label = 'bad'
    perfect_path = [p_join(training_folder, perfect_label), perfect_label]
    good_path = [p_join(training_folder, good_label), good_label]
    bad_path = [p_join(training_folder, bad_label), bad_label]
    SOURCES = [perfect_path, good_path, bad_path]
    # start testing
    paragraph_classification_result = []
    for page in listdir(testing_folder):
        page = p_join(testing_folder, page)
        classifier_result = supervised_classifier_ngram(SOURCES, page)
        # paragraph_classification_result = paragraph_classification_result + classifier_result
        paragraph_classification_result.append(classifier_result)
    return paragraph_classification_result

def subparagraph_classification(training_folder, testing_folder):
    # label subparagraphs as perfect and bad, training set in two folders
    perfect_label = 'perfect'
    bad_label = 'bad'
    # the following line is for cross validation:
    # paragraph_subparagraph_folders = os.path.join(os.path.join(Path_extracted1, 'All_subparagraph_folders'), subject)
    perfect_path = [p_join(training_folder, perfect_label), perfect_label]
    bad_path = [p_join(training_folder, bad_label), bad_label]
    SOURCES = [perfect_path, bad_path]
    subparagraph_classification_result = []
    for paragraph in listdir(testing_folder):
        paragraph = p_join(testing_folder, paragraph)
        classifier_result = supervised_classifier_ngram(SOURCES, paragraph)
        subparagraph_classification_result = subparagraph_classification_result + classifier_result
    return subparagraph_classification_result

def sentence_classification(training_folder, testing_folder):
    feedback = 0  # 0 when nothing needs to change; 1 when bad is wrongly classified
    prob_subparagraph = "None"  # problem subparagraph: bad subparagraph wrongly classified as perfect
    prob_col = 2
    # label sentences as perfect and bad, training set in two folders
    perfect_label = 'perfect'
    bad_label = 'bad'
    perfect_path = [p_join(training_folder, 'perfect'), perfect_label]
    bad_path = [p_join(training_folder, 'bad'), bad_label]
    SOURCES = [perfect_path, bad_path]
    # define the directory with subparagraphs
    sentence_classification_result = []
    for subparagraph in listdir(testing_folder):
        subparagraph = p_join(testing_folder, subparagraph)
        classifier_result = supervised_classifier_ngram(SOURCES, subparagraph)
        sentence_classification_result = sentence_classification_result + classifier_result
    return sentence_classification_result
