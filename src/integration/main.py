#!/usr/bin/env python3

# MIT License

# Copyright (c) 2018 The University of Michigan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
#importing the scripts to run by the scheduler


######SCRIPT UNDER CONSTRUCTION#######


import sys
from subprocess import call
""" sys.path.insert(1, '/Users/zinebbenameur/Desktop/datasheet-scrubber/src/Category-Recognition/PDF_wrapper.py')

import PDF_wrapper
from PDF_wrapper import pdf_location
 """

pdf_location = input("Enter a PDF's location and name: ")
from PyPDF2 import PdfFileReader
pdf = PdfFileReader(open(pdf_location,'rb'))
print("number of pages in the pdf", pdf.getNumPages())

#construct argument for table_extraction script
#should include first page and last page
#path to pdf again

argument = ''
#call scripts
call(["python3", "/Users/zinebbenameur/Desktop/datasheet-scrubber/src/Category-Recognition/PDF_wrapper.py"]);call("python3 /Users/zinebbenameur/Desktop/datasheet-scrubber/src/table_extraction/table_extraction.py --weight_dir /Users/zinebbenameur/Desktop/datasheet-scrubber/src/Table_extract_robust --pdf_dir /Users/zinebbenameur/Desktop/datasheet-scrubber/tests/table_extraction/test.pdf --work_dir ./ --first_table_page 2 --last_table_page 4", shell=True)
