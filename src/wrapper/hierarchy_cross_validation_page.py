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
all_pdf_folder = 'All_datasheets/ADC'
#all_page_txt_folder = 'All_pages_text/ADC'
all_page_txt_folder = 'small_training_set_text/ADC'
training_set_txt_folder = 'training_set_pages_text'
testing_set_pdf_folder = 'testing_set_pdf'
testing_set_page_folder = 'testing_set_pages'
testing_set_text_folder = 'testing_set_pages_text'
pdfDir = os.path.join(Path_extracted1, all_pdf_folder)
pagetxtDir = os.path.join(Path_extracted1, all_page_txt_folder)
trainingDir = os.path.join(Path_extracted1, training_set_txt_folder)
testingDir = os.path.join(Path_extracted1, testing_set_pdf_folder)
testpageDir = os.path.join(Path_extracted1, testing_set_page_folder)
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
#array all_datasheets record all pdf names
all_datasheets = []
for pdf in os.listdir(pdfDir):
    pdf_name = pdf.split(".pdf")[0]
    all_datasheets.append(pdf_name)
#build a dictionary recording all the true labels
page_labels = {}
for labeled_class in os.listdir(pagetxtDir):
    class_path = os.path.join(pagetxtDir, labeled_class)
    for page_txt in os.listdir(class_path):
        page_name = page_txt.split(".txt")[0]
        page_labels.update({page_name: labeled_class})

all_pages_folder = os.path.join(Path_extracted1, 'all_pdf_folder')
training_pages_folder = os.path.join(Path_extracted1, 'training_set_pages')
n = 10
accuracy = 0
while 5*n+4 <= len(all_datasheets):
    true = 0
    training_set = []
    testing_set = []
    for i in range(len(all_datasheets)):
        if i<5*n or i>5*n+4:
            training_set.append(all_datasheets[i])
        else:
            testing_set.append(all_datasheets[i])
    #clean up files in test folders
    pageDir = os.path.join(Path_extracted1, 'Test_pages')
    textDir = os.path.join(Path_extracted1, 'Test_pages_text')
    for folder in os.listdir(trainingDir):
        shutil.rmtree(os.path.join(trainingDir, folder))
    os.makedirs(os.path.join(trainingDir, 'perfect'))
    os.makedirs(os.path.join(trainingDir, 'good'))
    os.makedirs(os.path.join(trainingDir, 'bad'))
    for file in os.listdir(testingDir):
        os.remove(os.path.join(testingDir, file))
    for folder in os.listdir(testpageDir):
        shutil.rmtree(os.path.join(testpageDir, folder))
    for folder in os.listdir(testtxtDir):
        shutil.rmtree(os.path.join(testtxtDir, folder))
    #build partial training set
    for pdf_name in training_set:
        pdf = pdf_name + ".pdf"
        read_pdf = os.path.join(pdfDir, pdf)
        pfr = PyPDF2.PdfFileReader(open(read_pdf, "rb"))
        page_number = pfr.getNumPages()
        #for i in range(page_number):
        for i in range(5):
            page_name = pdf_name + '_' + str(i)
            page_txt = page_name + ".txt"
            label = page_labels[page_name]
            copy_pagetxt = os.path.join(os.path.join(pagetxtDir, label), page_txt)
            shutil.copy(copy_pagetxt, os.path.join(trainingDir, label))
    #build partial testing set
    for pdf_name in testing_set:
        pdf = pdf_name + ".pdf"
        copy_pdf = os.path.join(all_pdf_folder, pdf)
        shutil.copy(copy_pdf, testingDir)
    #crop test pdf into test pages
    pdf_cropper_for_extraction.pdf_cropper_multiple(testingDir, testpageDir)
    #the following for loop is for small page set
    for folder in os.listdir(testpageDir):
        keep_page = [folder+"_0", folder+"_1", folder+"_2", folder+"_3", folder+"_4"]
        for page in os.listdir(os.path.join(testpageDir, folder)):
            if page.split(".pdf")[0] not in keep_page:
                os.remove(os.path.join( testpageDir, os.path.join(folder, page) ))
    #convert test pages to text and check number of truly classified pages
    for pdf_folder in os.listdir(testpageDir):
        page_pdf = os.path.join(testing_set_page_folder, pdf_folder)
        page_text = os.path.join(testing_set_text_folder, pdf_folder)
        pdf_to_text(page_pdf,page_text)
        page_classifier_result = supervised_classifier_ngram(SOURCES, page_text)
        for tuple in page_classifier_result:
            if tuple[1] != 'bad' and tuple[1] == page_labels[tuple[0]]:
                true += 1
                break
    print(true)
    exit(0)
    accuracy += true
    n += 1
accuracy /= 5*n
print("accuracy: " + str(accuracy))
