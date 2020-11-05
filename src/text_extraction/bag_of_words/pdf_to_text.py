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
import sys, getopt
#from Address import Address
def pdf_to_text(sourth_path,destin_path):
    code_dir = os.path.dirname(__file__)
    main_dir   = os.path.relpath(os.path.join(code_dir,"../.."))
    
    def convert(fname, pages=None):
        if not pages:
            pagenums = set()
        else:
            pagenums = set(pages)

        output = StringIO()
        manager = PDFResourceManager()
        converter = TextConverter(manager, output, laparams=LAParams())
        '''add utf-8'''
        interpreter = PDFPageInterpreter(manager, converter)

        infile = open(fname, 'rb')      # For Python 2 it was infile=file(fname, 'rb')
        for page in PDFPage.get_pages(infile, pagenums):
            interpreter.process_page(page)
        infile.close()
        converter.close()
        text = output.getvalue()
        output.close
        return text
    #converts all pdfs in directory pdfDir, saves all resulting txt files to txtdir
    def convertMultiple(pdfDir, txtDir):
        if pdfDir == "": pdfDir = os.getcwd() + "\\" #if no pdfDir passed in
        if not os.path.exists(txtDir):
            os.makedirs(txtDir)
        for pdf in os.listdir(pdfDir): #iterate through pdfs in pdf directory
           # print(pdf)
            fileExtension = pdf.split(".")[-1]
            if fileExtension == "pdf":
                pdfFilename = os.path.join(pdfDir , pdf)
                pdfname = pdf.split(".pdf")[0]
                textname = pdfname + ".txt"
                textFilename=os.path.join(txtDir , textname)
               # exists=os.path.isfile(textFilename)
                #if not exists:
                text = convert(pdfFilename) #get string of text content of pdf
                textFile = open(textFilename, "w",encoding='utf-8') #make text file
                '''add utf-8'''
                textFile.write(text) #write text to text file

    #Path_extracted=Address(1).split("\n")
    #Path_extracted1=Path_extracted[0]
    Path_extracted1 = main_dir
    pdfDir=os.path.join(Path_extracted1,sourth_path)
    txtDir=os.path.join(Path_extracted1,destin_path)
    convertMultiple(pdfDir, txtDir)
