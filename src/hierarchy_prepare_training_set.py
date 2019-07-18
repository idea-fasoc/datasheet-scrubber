"""
This file is used for building the training set. As long as the folder All_pages_text is download,
there is no need to run code in this file.
"""
from Address import Address
from pdf_to_text import pdf_to_text
import pdf_cropper_for_extraction
import page_classification
import PyPDF2
import os
import shutil
Path_extracted=Address(1).split("\n")
Path_extracted1=Path_extracted[0]
#data sheet -> pages
"""
training_pdf_folder_name = 'training_set_ADC_4'
pdfDir = os.path.join(Path_extracted1, training_pdf_folder_name)
for pdf in os.listdir(pdfDir):
    pdfname = pdf.split(".pdf")[0]
    source_path = os.path.join(pdfDir,pdf)
    destination_path=os.path.join(pdfDir,pdfname)
    pfr = PyPDF2.PdfFileReader(open(source_path, "rb"))
    number_page=pfr.getNumPages()#Counting number of pdf pages
    pdf_cropper_for_extraction.pdf_cropper(source_path, destination_path, pdf, number_page)
"""
#label each page before proceeding
#page_pdf -> page_text

page_training_perfect_pdf = 'All_pages_pdf/ADC/perfect'
page_training_perfect_text = 'All_pages_text/ADC/perfect'
pdf_to_text(page_training_perfect_pdf, page_training_perfect_text)
page_training_good_pdf = 'All_pages_pdf/ADC/good'
page_training_good_text = 'All_pages_text/ADC/good'
pdf_to_text(page_training_good_pdf, page_training_good_text)
page_training_bad_pdf = 'All_pages_pdf/ADC/bad'
page_training_bad_text = 'All_pages_text/ADC/bad'
pdf_to_text(page_training_bad_pdf, page_training_bad_text)
