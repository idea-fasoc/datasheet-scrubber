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

from PyPDF2 import PdfFileReader
from subprocess import call
import importlib.util



#pdf_location = str(sys.argv[1])
def get_pdf():
    return input("Enter a PDF's location and name: ")

def announce():
    print("Imported!")

#get module for python file, this is for the wrapper
def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

#call the module
wrapper = module_from_file("PDF_wrapper", "/Users/zinebbenameur/clean/datasheet-scrubber/src/category-recognition/PDF_wrapper.py")

#build arguments for table extraction
argumets="--weight_dir /Users/zinebbenameur/Desktop/datasheet-scrubber/src/Table_extract_robust --pdf_dir /Users/zinebbenameur/Desktop/datasheet-scrubber/tests/table_extraction/test.pdf --work_dir ./ --first_table_page 2 --last_table_page 4"
#call table extraction
call("python3 /Users/zinebbenameur/Desktop/datasheet-scrubber/src/table_extraction/table_extraction.py"+" "+argumets, shell=True)
