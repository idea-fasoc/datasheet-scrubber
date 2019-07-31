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

import re
import sys
import shutil
import os
from Address import Address
import os
from extraction import extraction
import shutil
def scrubbing_framwork(title, CNN_TABLE):
    Path_extracted=Address(1).split("\n")
    Path_extracted1=Path_extracted[0]
    datasheets_dir=os.path.join(Path_extracted1,'Test_pdf')
    datasheets_text_dir=os.path.join(Path_extracted1,'Test_text')
    datasheets_crop_pdf_dir=os.path.join(Path_extracted1,'Test_cropped_pdf')
    datasheets_crop_text_dir=os.path.join(Path_extracted1,'Test_cropped_text')
    pdf_copy_destiny=os.path.join(Path_extracted1,'All_pdf')
    text_copy_destiny=os.path.join(Path_extracted1,'All_text')
    pdf_crop_copy_destiny=os.path.join(Path_extracted1,'cropped_pdf')
    text_crop_copy_destiny=os.path.join(Path_extracted1,'cropped_text')
    copy_desired=[]
    test_files=[]
    print ('The circuits types of input datasheets are respectively: ')
    i=1
    for file in os.listdir(datasheets_dir):
        print(str(i)+') '+file+': '+title[i-1])
        print ('The extracted relevant specs are as follows:')
        print('')
        specs,pins=extraction(title[i-1],os.path.join(datasheets_dir,file),CNN_TABLE)
        for spec in specs:
            print (spec[0]+':')
            print(spec[1:len(spec)])
            print('')
        #print ('The extracted relevant pins are as follows:')
        #print (pins)
        #print('')
        print('')
        test_files.append(file)

        i+=1
    correct_flag_titles=input("Are all of the circuits types correct? Yes/No\n")
    if correct_flag_titles=='Yes':
        add_reprository=input('Great! For the datasheets that you want to add to the reprository please write the pdf rank as sorted above. When it done please write "Done". Ex: 1\n')
        while add_reprository!='Done':
            if (re.fullmatch(r'\d',add_reprository)) and (0<int(add_reprository)<i):
                copy_desired.append(int(add_reprository))
                add_reprository=input()
            while (add_reprository!='Done') and ((not re.fullmatch(r'\d',add_reprository)) or (not 0<int(add_reprository)<i)):
                add_reprository=input('The format is not acceptable or not existed file. Please try again\n')
        if add_reprository=='Done':
            for j in range(0,len(copy_desired)):
                pdfname = test_files[copy_desired[j]-1].split(".pdf")[0]
                textname = pdfname + ".txt"
                shutil.copy(os.path.join(datasheets_dir,test_files[copy_desired[j]-1]), os.path.join(pdf_copy_destiny,title[copy_desired[j]-1]))
                shutil.copy(os.path.join(datasheets_text_dir,textname), os.path.join(text_copy_destiny,title[copy_desired[j]-1]))
                shutil.copy(os.path.join(datasheets_crop_pdf_dir,test_files[copy_desired[j]-1]), os.path.join(pdf_crop_copy_destiny,title[copy_desired[j]-1]))
                shutil.copy(os.path.join(datasheets_crop_text_dir,textname), os.path.join(text_crop_copy_destiny,title[copy_desired[j]-1]))
            print('Thanks a lot for testing our software!')
            shutil.rmtree(os.path.join(Path_extracted1,'Test_pdf','CSV'))
            shutil.rmtree(os.path.join(Path_extracted1,'Test_pdf','Modified_pdf'))
            return
    elif correct_flag_titles=='No':
        corrected_titles=input('For incorrect circuits types please write the pdf rank as sorted above followed by the correct circuits types. When it done please write "Done". Ex: 1:SRAM\n')
        while corrected_titles!='Done':
            if (re.fullmatch(r'\d:(?:ADC|CDC|DCDC|LDO|PLL|SRAM|Temperature_Sensor)',corrected_titles)):
                corrected_rank=re.findall(r'(\d):',corrected_titles)[0]
               # print(corrected_rank)
                if 0<int(corrected_rank)<i:
                    new_corrected_title=corrected_titles.split(":")[1]
                #    print(new_corrected_title)
                    title[int(corrected_rank)-1]=new_corrected_title
                    corrected_titles=input()
                else:
                    corrected_titles=input('Not existed file. Please try again\n') 
            while (corrected_titles!='Done') and (not re.fullmatch(r'\d:(?:ADC|CDC|DCDC|LDO|PLL|SRAM|Temperature_Sensor)',corrected_titles)):
                corrected_titles=input('The format is not acceptable or not existed file. Please try again\n')        
        if corrected_titles=='Done':          
            add_reprository=input('Thanks a lot for your feedback! For the datasheets that you want to add to the reprository please write the pdf rank as sorted above. When it done please write "Done". Ex: 1\n')
            while add_reprository!='Done':
                if (re.fullmatch(r'\d',add_reprository)) and (0<int(add_reprository)<i):
                    copy_desired.append(int(add_reprository))
                    add_reprository=input()
                while (add_reprository!='Done') and ((not re.fullmatch(r'\d',add_reprository)) or (not 0<int(add_reprository)<i)):
                    add_reprository=input('The format is not acceptable or not existed file. Please try again\n')
            if add_reprository=='Done':
                for j in range(0,len(copy_desired)):
                    pdfname = test_files[copy_desired[j]-1].split(".pdf")[0]
                    textname = pdfname + ".txt"
                    shutil.copy(os.path.join(datasheets_dir,test_files[copy_desired[j]-1]), os.path.join(pdf_copy_destiny,title[copy_desired[j]-1]))
                    shutil.copy(os.path.join(datasheets_text_dir,textname), os.path.join(text_copy_destiny,title[copy_desired[j]-1]))
                    shutil.copy(os.path.join(datasheets_crop_pdf_dir,test_files[copy_desired[j]-1]), os.path.join(pdf_crop_copy_destiny,title[copy_desired[j]-1]))
                    shutil.copy(os.path.join(datasheets_crop_text_dir,textname), os.path.join(text_crop_copy_destiny,title[copy_desired[j]-1]))
                print('Thanks a lot for testing our software!')
                shutil.rmtree(os.path.join(Path_extracted1,'Test_pdf','CSV'))
                shutil.rmtree(os.path.join(Path_extracted1,'Test_pdf','Modified_pdf'))
                sys.exit()
        
