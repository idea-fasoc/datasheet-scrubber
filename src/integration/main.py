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
import gdown

url_model1 = 'https://umich.box.com/s/bchj5h09tjtes6gyhbmosz6w7a15ehfv'
output = 'TEXT_IDENTIFY_MODEL_long.h5'
gdown.download(url_model1, output, quiet=False) 
print("EXT_IDENTIFY_MODEL_long.h5 was succesfully downloaded")


url_model2 ="https://umich.box.com/s/tbby5r2xrck10hnd0z9hzmnx60l3e8c1"
output = 'tokenizer_long.pickle'
gdown.download(url_model2, output, quiet=False)

print("okenizer_long.pickle was succesfully downloaded")



#pdf_location = str(sys.argv[1])


def announce():
    print("Imported!")

#get module for python file, this is for the wrapper
def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

#call the module
wrapper = module_from_file("category_recognizer", "/Users/zinebbenameur/clean/datasheet-scrubber/src/category-recognition/category_recognizer.py")

#Get number of pages from wrapper module
pdf = wrapper.get_number_pages()
number_pages= pdf.getNumPages()

first_page = 1
last_page = number_pages

arguments_weights= "--weight_dir /Users/zinebbenameur/Desktop/datasheet-scrubber/src/Table_extract_robust "
arguments_pdf = "--pdf_dir /Users/zinebbenameur/Desktop/datasheet-scrubber/tests/table_extraction/test.pdf "
arguments_dir = "--work_dir ./ "
argument_pages = "--first_table_page "+ str(first_page)+" --last_table_page "+str(last_page)

#build arguments for table extraction
argumets= arguments_weights + arguments_pdf + arguments_dir + argument_pages
#call table extraction
call("python3 /Users/zinebbenameur/Desktop/datasheet-scrubber/src/table_extraction/table_extraction.py"+" "+argumets, shell=True)
