from supervised_classifier_ngram import supervised_classifier_ngram
from Address import Address
import pdf_cropper_for_extraction
import numpy as np
import os
import shutil


def subparagraph_classification(training_folder, testing_folder):
    # label subparagraphs as perfect and bad, training set in two folders
    perfect_label = 'perfect'
    bad_label = 'bad'
    # the following line is for cross validation:
    # paragraph_subparagraph_folders = os.path.join(os.path.join(Path_extracted1, 'All_subparagraph_folders'), subject)
    perfect_path = [os.path.join(training_folder, perfect_label), perfect_label]
    bad_path = [os.path.join(training_folder, bad_label), bad_label]
    SOURCES = [perfect_path, bad_path]
    subparagraph_classification_result = []
    for paragraph in os.listdir(testing_folder):
        paragraph = os.path.join(testing_folder, paragraph)
        classifier_result = supervised_classifier_ngram(SOURCES, paragraph)
        subparagraph_classification_result = subparagraph_classification_result + classifier_result
    return subparagraph_classification_result
