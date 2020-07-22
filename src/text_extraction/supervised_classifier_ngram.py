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

"""This function is to train a classifier and do the testing"""
"""
Input:
input_SOURCES: An array containing [path, label] arrays for all classes
test_directory: contains txt files waiting to be tested
"""

import os
import numpy
from pandas import DataFrame
from sklearn import model_selection, naive_bayes, svm
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB, ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import KFold  # Modified to be compatible with python3
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import BernoulliNB
from Address import Address
from statistics import stdev


# Text cleaning
def supervised_classifier_ngram(input_SOURCES, test_directory):
    NEWLINE = '\n'
    SKIP_FILES = {'cmds'}

    def read_files(path):
        for root, dir_names, file_names in os.walk(path):
            for path in dir_names:
                read_files(os.path.join(root, path))
            for file_name in file_names:
                if file_name not in SKIP_FILES:
                    file_path = os.path.join(root, file_name)
                    if os.path.isfile(file_path):
                        # past_header, lines = False, []
                        past_header, lines = True, []
                        f = open(file_path, errors='ignore')
                        for line in f:
                            if past_header:
                                lines.append(line)
                            elif line == NEWLINE:
                                past_header = True
                        f.close()
                        content = NEWLINE.join(lines)
                        yield file_path, content

    def build_data_test_frame(path):
        rows = []
        index = []
        for file_name, text in read_files(path):
            rows.append({'text': text})
            index.append(file_name)
            # print("[DEBUG] file_name: {}".format(file_name))
        data_frame_test = DataFrame(rows, index=index)
        return data_frame_test

    def build_data_frame(path, classification):
        rows = []
        index = []
        for file_name, text in read_files(path):
            # print("[DEBUG] text: {}".format(text))
            rows.append({'text': text, 'class': classification})
            index.append(file_name)
        data_frame = DataFrame(rows, index=index)
        return data_frame

    # Training
    # Assigning classes to training set (label training dataset)

    Path_extracted = Address(1).split("\n")
    Path_extracted1 = Path_extracted[0]
    SOURCES = input_SOURCES

    data = DataFrame({'text': [], 'class': []})
    for path, classification in SOURCES:
        new_data_frame = build_data_frame(path, classification)
        data = data.append(new_data_frame, sort=True)
    data = data.reindex(numpy.random.permutation(data.index))

    # Naive Bayes classifier

    count_vectorizer = CountVectorizer(stop_words=None)  # Segmenting text file into words, counting occurrence number of each word and assigning this number as an ID to words for training set
    # print("[DEBUG] data['text'].values: {}".format(data['text'].values))
    counts = count_vectorizer.fit_transform(data['text'].values)
    # print("[DEBUG] count: {}".format(counts))

    # comment the above two lines and apply TF-IDF with the following two line of codes
    # count_vectorizer = TfidfVectorizer(use_idf=True)
    # counts = count_vectorizer.fit_transform(data['text'].values)

    # below is for the MultinomialNB method:
    classifier = MultinomialNB()  # Calculating coefficients for training set based on Naive Bayes
    targets = data['class'].values
    classifier.fit(counts, targets)  # classifier.class_ = ['bad', 'good', 'perfect']


    # below is for the SVM method:
    # classifier = svm.SVC(C=1.0, kernel='linear', degree=3, gamma='auto', probability=True)
    # targets = data['class'].values
    # classifier.fit(counts, targets)

    # define perfect as the location of class 'perfect'
    perfect = 0
    for i in range(len(classifier.classes_)):
        if classifier.classes_[i] == 'perfect':
            perfect = i


    # find boundary possibility
    # SOURCEStrain = [path for path, classification in SOURCES]
    # data_train = DataFrame({'text': []})
    # for path in SOURCEStrain:
    #     data_train = data_train.append(build_data_test_frame(path))
    # training_samples = data_train['text'].values
    # sample_counts = count_vectorizer.transform(training_samples)
    # all_possibility = classifier.predict_proba(sample_counts)
    # boundary = numpy.mean(all_possibility)
    # print(boundary)

    # Testing

    SOURCEStest = [os.path.join(Path_extracted1, test_directory)]  # Testset directory of pages
    # SOURCEStest = [os.path.join(Path_extracted1,'Test_cropped_text')#Testset directory
    # (os.path.join(os.path.join(Path_extracted1,'Text_test'), 'Temperature_Sensor'))]
    # print("source dir here: {}".format(SOURCEStest))
    data_test = DataFrame({'text': []})
    for path in SOURCEStest:
        data_test = data_test.append(build_data_test_frame(path))
    examples = data_test['text'].values
    example_counts = count_vectorizer.transform(examples)
    # print("[DEBUG] example count at path: {},\n{}".format(Path_extracted, example_counts))
    # Applying calculated Naive Bayes coefficients and decision based on MAP
    predictions = classifier.predict(example_counts)

    # # check whether all the predictions are 'bad'
    # all_bad = 1
    # for prediction in predictions:
    #     if not prediction == 'bad':
    #         all_bad = 0
    #         break
    # if all_bad == 1:
    #     perfect_prob = [pred_prob[perfect] for pred_prob in classifier.predict_proba(example_counts)]
    #     perfect_page = perfect_prob.index(max(perfect_prob))
    #     predictions[perfect_page] = 'perfect'

    perfect_prob = [pred_prob[perfect] for pred_prob in classifier.predict_proba(example_counts)]
    # if max(perfect_prob) > boundary:
    perfect_page = perfect_prob.index(max(perfect_prob))
    predictions[perfect_page] = 'perfect'
    for i in range(len(predictions)):
        if not i == perfect_page:
            predictions[i] = 'bad'
    # else:
    #     for i in range(len(predictions)):
    #         predictions[i] = 'bad'

    # print result in tuples
    page_classification_result = []
    for path in SOURCEStest:
        for page, label in zip(os.listdir(path), predictions):
            page_name = page.split(".txt")[0]
            predicted_tuple = [page_name, label]
            page_classification_result.append(predicted_tuple)
    return page_classification_result
