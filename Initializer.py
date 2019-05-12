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
import shutil
from init_dropbox import init_dropbox

current_path = input("Please enter the directory path where All_pdf.zip file is now e.g. Users\morte\Downloads\All_pdf.zip") 
main_path = input("Please enter the directory path where you want to save training\testing zip file set e.g. Users\morte\Box Sync\Education_tools\Test_init2")
code_directory = input("Please enter the directory path where the datasheet scrubber codes after cloning are e.g. Users\morte\Box Sync\Education_tools\project_python_code\Datasheet-Scrubber")
open(os.path.join(code_directory,"Address.txt"), 'w').close()
with open(os.path.join(code_directory,"Address.txt"), 'w') as f:
    f.write(main_path)
shutil.move(current_path, main_path)
init_dropbox(main_path)
