from pdf_to_text import pdf_to_text
from supervised_classifier_ngram import supervised_classifier_ngram
from Address import Address
import pdf_cropper_for_extraction
import os
import shutil
import PyPDF2

Path_extracted=Address(1).split("\n")
Path_extracted1=Path_extracted[0]
#a list of paths
all_paragraph_txt_folder = 'paragraphs/ADC'
paragraph_training_folder = 'All_paragraphs_text/ADC'
training_set_txt_folder = 'training_set_paragraphs_text'
testing_set_text_folder = 'testing_set_paragraphs_text'
paragraphDir = os.path.join(Path_extracted1, all_paragraph_txt_folder)
paragraphtxtDir = os.path.join(Path_extracted1, paragraph_training_folder)
trainingDir = os.path.join(Path_extracted1, training_set_txt_folder)
testtxtDir = os.path.join(Path_extracted1, testing_set_text_folder)
#SOURCES for training
perfect_label = 'perfect'
good_label = 'good'
bad_label = 'bad'
pages_path = os.path.join(os.path.join(Path_extracted1, training_set_txt_folder), 'ADC')
perfect_path = [os.path.join(trainingDir,'perfect'), perfect_label]
good_path = [os.path.join(trainingDir,'good'), good_label]
bad_path = [os.path.join(trainingDir,'bad'), bad_label]
SOURCES = [perfect_path, good_path, bad_path]
#array all_paragraphs record all paragraph names
all_paragraphs = []
for paragraph in os.listdir(paragraphDir):
    paragraph_name = paragraph.split(".txt")[0]
    all_paragraphs.append(paragraph_name)
#build a dictionary recording all the true labels
paragraph_labels = {}
for labeled_class in os.listdir(paragraphtxtDir):
    class_path = os.path.join(paragraphtxtDir, labeled_class)
    for paragraph_txt in os.listdir(class_path):
        paragraph_name = paragraph_txt.split(".txt")[0]
        paragraph_labels.update({paragraph_name: labeled_class})

n = 0
accuracy = 0
while 5*n+4 <= len(all_paragraphs):
    true = 0
    training_set = []
    testing_set = []
    for i in range(len(all_paragraphs)):
        if i<5*n or i>5*n+4:
            training_set.append(all_paragraphs[i])
        else:
            testing_set.append(all_paragraphs[i])
    #clean up files in test folders
    for folder in os.listdir(trainingDir):
        shutil.rmtree(os.path.join(trainingDir, folder))
    os.makedirs(os.path.join(trainingDir, 'perfect'))
    os.makedirs(os.path.join(trainingDir, 'good'))
    os.makedirs(os.path.join(trainingDir, 'bad'))
    for file in os.listdir(testtxtDir):
        os.remove(os.path.join(testtxtDir, file))
    #build partial training set
    for paragraph_name in training_set:
        paragraph = paragraph_name + ".txt"
        label = paragraph_labels[paragraph_name]
        copy_paragraph = os.path.join(paragraphDir, paragraph)
        shutil.copy(copy_paragraph, os.path.join(trainingDir, label))
    #build partial testing set
    for paragraph_name in testing_set:
        paragraph = paragraph_name + ".txt"
        copy_paragraph = os.path.join(paragraphDir, paragraph)
        shutil.copy(copy_paragraph, testtxtDir)
    #convert test pages to text and check number of truly classified pages
    page_classifier_result = supervised_classifier_ngram(SOURCES, testtxtDir)
    print(page_classifier_result)
    for [paragraph_name, prediction] in page_classifier_result:
        if prediction == paragraph_labels[paragraph_name]:
            true += 1
    accuracy += true/5
    n += 1
accuracy /= n
print("accuracy: " + str(accuracy))
