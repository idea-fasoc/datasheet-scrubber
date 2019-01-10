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

from pdf_to_text import pdf_to_text
import os
from Address import Address
from pdf_cropper_title import pdf_cropper_title
Path_extracted=Address(1).split("\n")
Path_extracted1=Path_extracted[0]
categories=['ADC','CDC','DCDC','SRAM','Temperature_Sensor','PLL','LDO']
for i in range (0,len(categories)):
    pdfDir=os.path.join(Path_extracted1,os.path.join('All_pdf',categories[i]))
    txtDir=os.path.join(Path_extracted1,os.path.join('All_text',categories[i]))
    cropped_pdfDir=os.path.join(Path_extracted1,os.path.join('cropped_pdf',categories[i]))
    cropped_texDir=os.path.join(Path_extracted1,os.path.join('cropped_text',categories[i]))
    os.makedirs(txtDir)
    os.makedirs(cropped_pdfDir)
    os.makedirs(cropped_texDir)
    pdf_to_text(pdfDir,txtDir)
    pdf_cropper_title(pdfDir,cropped_pdfDir)
    pdf_to_text(cropped_pdfDir,cropped_texDir)
