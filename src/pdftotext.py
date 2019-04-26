from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import os

def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, 'utf-8', laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    with open(fname, 'rb') as infile:
        for page in PDFPage.get_pages(infile, pagenums):
            interpreter.process_page(page)
    converter.close()
    text = output.getvalue()
    output.close
    return text 
#converts all pdfs in directory pdfDir, saves all resulting txt files to txtdir
def convertMultiple(pdfDir):
    # if pdfDir == "": pdfDir = os.getcwd() + "\\" #if no pdfDir passed in
    # for pdf in os.listdir(pdfDir): #iterate through pdfs in pdf directory
    #     fileExtension = pdf.split(".")[-1]
    #     if fileExtension == "pdf":
    #         pdfFilename = os.path.join(pdfDir, pdf)
    #         text = convert(pdfFilename) #get string of text content of pdf
    #         textFilename = os.path.join(txtDir, pdf.split('.')[0] + ".txt")
    #         textFile = open(textFilename, "w", encoding='utf-8') #make text file
    #         textFile.write(text) #write text to text file

    text = convert(pdfDir)  # get string of text content of pdf
    textFilename = os.path.join(pdfDir, pdfDir.split('.')[0] + ".txt")
    textFile = open(textFilename, "w", encoding='utf-8') #make text file
    textFile.write(text) #write text to text file
    return textFilename
# pdfDir = r'C:\Users\whatsthenext\Desktop\research test\pdf\STM32F303xD.pdf'
# # txtDir = r"C:\Users\whatsthenext\Desktop\research test\txt"
# print(convertMultiple(pdfDir))
def PDFtoTEXT(source, destination):
    text = convert(source)  # get string of text content of pdf
    textFilename = os.path.join(destination, source.split('\\')[-1].split('.')[0] + ".txt")
    textFile = open(textFilename, "w", encoding='utf-8') #make text file
    textFile.write(text) #write text to text file
    return textFilename
