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

import PyPDF2
import re
import os.path
def pdf_cropper(source_path,destination_path,pdf_filename,number_page):
    page_seperated=[]
    PDFfilename = source_path #filename of your PDF/directory where your PDF is stored
    pfr = PyPDF2.PdfFileReader(open(PDFfilename, "rb")) #PdfFileReader object
    if pfr.isEncrypted: #needed for some encrypted files lke AD7183
        pfr.decrypt('')
    #page_number= pfr.getNumPages()

    for i in range(0,number_page):
        page_seperated.append(str(i))
        new_folder_path=os.path.join(destination_path, page_seperated[i])
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        NewPDFfilename=os.path.join(new_folder_path,pdf_filename)#filename of your PDF/directory where you want your new PDF to be
        pg = pfr.getPage(i) #extract pg 1
        writer = PyPDF2.PdfFileWriter() #create PdfFileWriter object
	#add pages
        writer.addPage(pg)
        with open(NewPDFfilename, "wb") as outputStream: #create new PDF
            writer.write(outputStream) #write pages to new PDF


def pdf_cropper_all(source_path,destination_path,pdf_filename,number_page):
    ## generate  number_page pdf in one file
    PDFfilename = source_path #filename of your PDF/directory where your PDF is stored
    pfr = PyPDF2.PdfFileReader(open(PDFfilename, "rb")) #PdfFileReader object
    if pfr.isEncrypted: #needed for some encrypted files lke AD7183
        pfr.decrypt('')
    NewPDFfilename = os.path.join(destination_path, pdf_filename)  # filename of your PDF/directory where you want your new PDF to be
    writer = PyPDF2.PdfFileWriter()  # create PdfFileWriter object
    for i in range(0, number_page):
        pg = pfr.getPage(i)  # extract pg 1
        # add pages
        writer.addPage(pg)
    with open(NewPDFfilename, "ab+") as outputStream:  # create new PDF
        writer.write(outputStream)  # write pages to new PDF