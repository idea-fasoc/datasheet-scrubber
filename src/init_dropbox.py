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
import pdf_cropper
import pdf_csv_converter
import pdftotext
import PyPDF2
import zipfile

def init_dropbox(main_path):
    print("Extracting All_pdf.zip...")
    source_path = os.path.join(main_path,"All_pdf")
    if not os.path.exists(source_path):
        os.mkdir(source_path)
    else:
        print("ERROR: All_pdf path already exists")
        return -1
    zip_file = zipfile.ZipFile(os.path.join(main_path,"All_pdf.zip"),'r')
    zip_file.extractall(source_path)
    print("Extracting All_pdf.zip Complete")
    destination_csv_path = os.path.join(main_path, "CSV")
    destination_pdf_path = os.path.join(main_path, "Modified_pdf")
    destination_text_path = os.path.join(main_path, "All_text")
    destination_cropped_pdf_path = os.path.join(main_path, "cropped_pdf")
    destination_cropped_text_path = os.path.join(main_path, "cropped_text")
    New_pdf_path = os.path.join(main_path, "New_pdf")
    Test_pdf = os.path.join(main_path, "Test_pdf")
    Test_text = os.path.join(main_path, "Test_text")
    Test_cropped_pdf = os.path.join(main_path, "Test_cropped_pdf")
    Test_cropped_text = os.path.join(main_path, "Test_cropped_text")


    ##creating the cooresponding folder
    print("Creating folder...")
    if not os.path.exists(destination_csv_path):
        os.mkdir(destination_csv_path)
    else:
        print("ERROR: CSV path already exists")
        return -1
    if not os.path.exists(destination_pdf_path):
        os.mkdir(destination_pdf_path)
    else:
        print("ERROR: Modified pdf path already exists")
        return -1
    if not os.path.exists(destination_text_path):
        os.mkdir(destination_text_path)
    else:
        print("ERROR: All_text path already exists")
        return -1
    if not os.path.exists(destination_cropped_pdf_path):
        os.mkdir(destination_cropped_pdf_path)
    else:
        print("ERROR: cropped_pdf path already exists")
        return -1
    if not os.path.exists(destination_cropped_text_path):
        os.mkdir(destination_cropped_text_path)
    else:
        print("ERROR: cropped_text path already exists")
        return -1
    if not os.path.exists(New_pdf_path):
        os.mkdir(New_pdf_path)
    else:
        print("ERROR: New_pdf path already exists")
        return -1
    if not os.path.exists(Test_cropped_pdf):
        os.mkdir(Test_cropped_pdf)
    else:
        print("ERROR: Test_cropped_pdf path already exists")
        return -1
    if not os.path.exists(Test_cropped_text):
        os.mkdir(Test_cropped_text)
    else:
        print("ERROR: Test_cropped_text path already exists")
        return -1
    if not os.path.exists(Test_pdf):
        os.mkdir(Test_pdf)
    else:
        print("ERROR: Test_pdf path already exists")
        return -1
    if not os.path.exists(Test_text):
        os.mkdir(Test_text)
    else:
        print("ERROR: Test_text path already exists")
        return -1
    print("Creating folder Complete")

    print("Initializing files...")
    for fpath, dirname, fname in os.walk(source_path):
        for files in fname:
            print(files)
            print("--------------------------------------------------------")
            try:
                ## creating the empty folder
                category_folder = fpath.split("\\")[-1]
                if not os.path.exists(os.path.join(New_pdf_path, category_folder)):
                    os.mkdir(os.path.join(New_pdf_path, category_folder))
                 ## creating the source path
                source_pdf_path = os.path.join(fpath, files)
                source_csv_path = destination_pdf_path
                print("Generating text...")
                if not os.path.exists(os.path.join(destination_text_path, category_folder)):
                    os.mkdir(os.path.join(destination_text_path, category_folder))
                final_destination_text_path = os.path.join(destination_text_path, category_folder)
                pdftotext.PDFtoTEXT(source_pdf_path, final_destination_text_path)
                print("Generating text Complete")
                ## creating cropped pdf
                print("Generating cropped pdf...")
                if not os.path.exists(os.path.join(destination_cropped_pdf_path, category_folder)):
                    os.mkdir(os.path.join(destination_cropped_pdf_path, category_folder))
                final_destination_cropped_pdf_path = os.path.join(destination_cropped_pdf_path, category_folder)
                pdf_cropper.pdf_cropper_all(source_pdf_path, final_destination_cropped_pdf_path, files, 2)
                print("Generating cropped pdf Complete")
                ## creating cropped text
                print("Generating cropped text...")
                if not os.path.exists(os.path.join(destination_cropped_text_path, category_folder)):
                    os.mkdir(os.path.join(destination_cropped_text_path, category_folder))
                cropped_text_source = os.path.join(destination_cropped_pdf_path, category_folder, files)
                final_destination_cropped_text_path = os.path.join(destination_cropped_text_path, category_folder)
                pdftotext.PDFtoTEXT(cropped_text_source, final_destination_cropped_text_path)
                print("Generating cropped text Complete")
                print(files, "Complete")
            except:
                continue

    print("Initializing Complete")

    # the input is the source directory of all pdf, it will create modified pdf and csv in the same directory as the source directory
    # eg.  init_dropbox(r"D:\All_pdf")
    #init_dropbox(r"D:\All_pdf")
