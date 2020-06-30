from pdf_to_text import pdf_to_text
from supervised_classifier_ngram import supervised_classifier_ngram
from judgement import supervised_classifier
from Address import Address
import pdf_cropper_for_extraction
from os.path import isdir
from os.path import join as p_join
from os import mkdir, listdir, remove
from shutil import rmtree

"""This function is to classify perfect pages from datasheets"""
"""
Input:
testing_folder: datasheets we want to extract (absolute path)
training_folder: all pages labelled in three folders (absolute path)
"""
"""
Output:
An array with [paragraph_name, pred] tuples; paragraph_name without ".txt".
"""


def page_classification(training_folder, testing_folder):
    path_extracted = Address(1).split("\n")
    base_dir = path_extracted[0]
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
