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
from Address import Address
Path_extracted=Address(1).split("\n")
Path_extracted1=Path_extracted[0]
import shutil

shutil.rmtree(os.path.join(Path_extracted1,'Test_pdf'))
os.makedirs(os.path.join(Path_extracted1,'Test_pdf'))
for file in os.listdir(os.path.join(Path_extracted1,'Test_text')):
    os.remove(os.path.join(Path_extracted1,'Test_text',file))
for file in os.listdir(os.path.join(Path_extracted1,'Test_cropped_pdf')):
    os.remove(os.path.join(Path_extracted1,'Test_cropped_pdf',file))
for file in os.listdir(os.path.join(Path_extracted1,'Test_cropped_text')):
    os.remove(os.path.join(Path_extracted1,'Test_cropped_text',file))
