from pdf_to_text import pdf_to_text
from supervised_classifier_ngram import supervised_classifier_ngram
from Address import Address
import pdf_cropper_for_extraction
import os
import shutil
def page_classification(subject):
    Path_extracted=Address(1).split("\n")
    Path_extracted1=Path_extracted[0]
    #label pages as perfect, good and bad, training set in three folders
    perfect_label = 'perfect'
    good_label = 'good'
    bad_label = 'bad'
    #pages_path = os.path.join(os.path.join(Path_extracted1, 'All_pages_text'), subject)
    pages_path = os.path.join(os.path.join(Path_extracted1, 'small_training_set_text'), subject)
    perfect_path = [os.path.join(pages_path,'perfect'), perfect_label]
    good_path = [os.path.join(pages_path,'good'), good_label]
    bad_path = [os.path.join(pages_path,'bad'), bad_label]
    SOURCES = [perfect_path, good_path, bad_path]
    #clean up files in test folders
    pageDir = os.path.join(Path_extracted1, 'Test_pages')
    textDir = os.path.join(Path_extracted1, 'Test_pages_text')
    for folder in os.listdir(pageDir):
        shutil.rmtree(os.path.join(pageDir, folder))
    for folder in os.listdir(textDir):
        shutil.rmtree(os.path.join(textDir, folder))
    #crop test pdf into test pages
    pdfDir = os.path.join(Path_extracted1, 'Test_pdf')
    pageDir = os.path.join(Path_extracted1, 'Test_pages')
    pdf_cropper_for_extraction.pdf_cropper_multiple(pdfDir, pageDir)
    pageDir = os.path.join(Path_extracted1, 'Test_pages')
    #convert test pages to text
    for pdf_folder in os.listdir(pageDir):
        page_pdf = os.path.join('Test_pages', pdf_folder)
        page_text = os.path.join('Test_pages_text', pdf_folder)
        pdf_to_text(page_pdf,page_text)
        page_classifier_result = supervised_classifier_ngram(SOURCES, page_text)
        print(page_classifier_result)
