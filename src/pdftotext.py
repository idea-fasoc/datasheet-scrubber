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
#pdfDir = r"C:\Users\whatsthenext\Desktop\research test\pdf"
# txtDir = r"C:\Users\whatsthenext\Desktop\research test\txt"
#print(convertMultiple(pdfDir))
