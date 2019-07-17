import os
from Address import Address
Path_extracted=Address(1).split("\n")
Path_extracted1=Path_extracted[0]
pdf_dir = os.path.join(Path_extracted1,os.path.join('All_pdf','DSP'))
text_dir = os.path.join(Path_extracted1,os.path.join('All_text','DSP'))
cropped_pdf_dir = os.path.join(Path_extracted1,os.path.join('cropped_pdf','DSP'))
suma=0
for file in os.listdir(pdf_dir):
    text_name1=file.split('.pdf')
    text_name=text_name1[0]+'.txt'
    #print(text_name)
    #print('***************')
    if not os.path.isfile(os.path.join(text_dir,text_name)):
        print(text_name)
        print('+++++++++++')
        suma+=1
print(suma)
suma=0
for file in os.listdir(pdf_dir):
    text_name1=file.split('.pdf')
    text_name=text_name1[0]+'.txt'
    #print(text_name)
    #print('***************')
    if not os.path.exists(os.path.join(cropped_pdf_dir,file)):
        print(file)
        print('+++++++++++')
        suma+=1
print(suma)
