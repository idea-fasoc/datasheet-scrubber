from supervised_classifier_ngram import supervised_classifier_ngram
import os
"""This function is to classify perfect paragraphs from pages"""
"""
Input:
testing_folder: pages we want to extract, each folder containing all paragraphs in the page (absolute path)
training_folder: all paragraphs labelled in three folders (absolute path)
"""
"""
Output:
An array with [paragraph_name, pred] tuples; paragraph_name without ".txt".
"""


def paragraph_classification(training_folder, testing_folder):
    # training_folder = os.path.join(training_folder, subject)
    # SOURCES for training
    perfect_label = 'perfect'
    good_label = 'good'
    bad_label = 'bad'
    perfect_path = [os.path.join(training_folder, perfect_label), perfect_label]
    good_path = [os.path.join(training_folder, good_label), good_label]
    bad_path = [os.path.join(training_folder, bad_label), bad_label]
    SOURCES = [perfect_path, good_path, bad_path]
    # start testing
    paragraph_classification_result = []
    for page in os.listdir(testing_folder):
        page = os.path.join(testing_folder, page)
        classifier_result = supervised_classifier_ngram(SOURCES, page)
        # paragraph_classification_result = paragraph_classification_result + classifier_result
        paragraph_classification_result.append(classifier_result)
    return paragraph_classification_result
