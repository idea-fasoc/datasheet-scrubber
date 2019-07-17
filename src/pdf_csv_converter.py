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

from tabula import convert_into
import os.path
def pdf_csv_converter(source_path,destination_path,pdf_filename,csv_filename,number_page):
    page_seperated=[]
    for i in range(0,number_page): #CHANGE BACK  number_page
        page_seperated.append(str(i))
        new_pdf_folder_path=os.path.join(source_path, page_seperated[i])
        complete_pdf_path=os.path.join(new_pdf_folder_path,pdf_filename)
        new_csv_folder_path=os.path.join(destination_path, page_seperated[i])
        if not os.path.exists(new_csv_folder_path):
            os.makedirs(new_csv_folder_path)
        complete_csv_path=os.path.join(new_csv_folder_path,csv_filename)
        convert_into(complete_pdf_path,complete_csv_path,output_format="csv")



        

        
