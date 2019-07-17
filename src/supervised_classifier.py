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

import os
import numpy
from pandas import DataFrame
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from Address import Address
#Text cleaning
def supervised_classifier(input_SOURCES):
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
                        past_header, lines = False, []
                        f = open(file_path,errors='ignore')
                        for line in f:
                            if past_header:
                                lines.append(line)
                            elif line == NEWLINE:
                                past_header = True
                        f.close()
                        content = NEWLINE.join(lines)
                        yield file_path, content
                        
    #Training
        #Assigning classes to training set (label training dataset)
                        
    def build_data_frame(path, classification):
        rows = []
        index = []
        for file_name, text in read_files(path):
            rows.append({'text': text, 'class': classification})
            index.append(file_name)

        data_frame = DataFrame(rows, index=index)
        return data_frame
    
    Path_extracted=Address(1).split("\n")
    Path_extracted1=Path_extracted[0]
    SOURCES=input_SOURCES

    data = DataFrame({'text': [], 'class': []})
    for path, classification in SOURCES:
        data = data.append(build_data_frame(path, classification),sort=True)
    data = data.reindex(numpy.random.permutation(data.index))

        #Naive Bayes classifier

    count_vectorizer = CountVectorizer(stop_words=None)#Segmenting text file into words, counting occurrence number of each word and assigning this number as an ID to words for training set
    counts = count_vectorizer.fit_transform(data['text'].values)
    classifier = MultinomialNB()#Calculating coefficients for training set based on #Using Multinomial Naive Bayes
    targets = data['class'].values
    classifier.fit(counts, targets)

    #Testing

    def build_data_test_frame(path):
        rows = []
        index = []
        for file_name, text in read_files(path):
            rows.append({'text': text})
            index.append(file_name)

        data_frame_test = DataFrame(rows, index=index)
        return data_frame_test
    SOURCEStest = [#Testset directory
        #(os.path.join(os.path.join(Path_extracted1,'Text_test'), 'Temperature_Sensor'))
        (os.path.join(Path_extracted1,'Test_cropped_text'))
    ]
    data_test = DataFrame({'text': []})
    for path in SOURCEStest:
        data_test = data_test.append(build_data_test_frame(path))
    examples = data_test['text'].values
    example_counts = count_vectorizer.transform(examples)#Segmenting text file into words, counting occurrence number of each word and assigning this number as an ID to words for testing set
    predictions = classifier.predict(example_counts)#Applying calculated Naive Bayes coefficients and decision based on MAP
    return predictions
