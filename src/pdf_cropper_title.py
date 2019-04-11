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
import PyPDF2
from PyPDF2 import PdfFileReader, PdfFileWriter
from Address import Address
from shutil import copyfile
import re
def pdf_cropper_title(sourth_path,destin_path):
    Path_extracted=Address(1).split("\n")
    Path_extracted1=Path_extracted[0]
    #source_pdf_Dir=os.path.join(Path_extracted1,os.path.join('All_pdf','ADC'))
    #destin_pdf_Dir=os.path.join(Path_extracted1,os.path.join('All_text','ADC'))
    source_pdf_Dir=os.path.join(Path_extracted1,sourth_path)
    destin_pdf_Dir=os.path.join(Path_extracted1,destin_path)
    basic_search_words = r'(?:product description|Product description|Product Description|PRODUCT DESCRIPTION|general description|General description|General Description|GENERAL DESCRIPTION)'
    non_crop_words=r'(?:TABLE OF CONTENTS|Table Of Contents|Table of Contents|Table of contents|table of contents)'
    for pdf in os.listdir(source_pdf_Dir):
        #print("ALL PDF"+pdf)
        single_source_name = os.path.join(source_pdf_Dir , pdf)
        single_destin_name = os.path.join(destin_pdf_Dir , pdf)
        pdf1 = PdfFileReader(open(single_source_name,'rb'),strict=False)
        if pdf1.isEncrypted:
            try:
                pdf1.decrypt('')
            except:
                command = ("cp "+ single_source_name +
                " temp.pdf; qpdf --password='' --decrypt temp.pdf " + single_source_name
                + "; rm temp.pdf")
                os.system(command)
                pdf1 = PdfFileReader(open(single_source_name,'rb'),strict=False)
        page_number=pdf1.getNumPages()
        pdf_writer = PdfFileWriter()
        find_page_tag=False
        for i in range(0, page_number):
            PageObj = pdf1.getPage(i)
            Text = PageObj.extractText() 
            if re.search(basic_search_words, Text):
               # print("document_name"+pdf)
                #print("salam"+str(i))
                find_page_tag=True
                target_page=i
                break
        if find_page_tag:
            pdf_writer.addPage(pdf1.getPage(target_page))
            with open(single_destin_name, 'wb') as out:
                pdf_writer.write(out)
        else:
            if page_number>=2:
                for page in range(0, 2):
                    PageObj = pdf1.getPage(page)
                    Text = PageObj.extractText() 
                    if not re.search(non_crop_words, Text):
                        pdf_writer.addPage(pdf1.getPage(page))
                    else:
                        pass
                with open(single_destin_name, 'wb') as out:
                    pdf_writer.write(out)
            else:
                copyfile(single_source_name, single_destin_name)
