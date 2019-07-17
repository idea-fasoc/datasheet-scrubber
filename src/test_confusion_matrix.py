import os
import shutil
from Address import Address
from title_decision_confusion_matrix import title_decision_confusion_matrix
from confusion_matrix import confusionMatrix
import numpy as np
division_group=10
#class_num=15
class_num=13
Path_extracted=Address(1).split("\n")
Path_extracted1=Path_extracted[0]
#Path_extracted1 = r"D:\All_pdf\test"
list_counter=0
#list_test_case=['ADC', 'PLL', 'DCDC','CDC','Temperature_Sensor','SRAM','LDO','BDRT','counters','DAC','Delay_Line','DSP','IO','Opamp','Digital_Potentiometers']
list_test_case=['ADC', 'PLL', 'DCDC','CDC','Temperature_Sensor','SRAM','LDO','BDRT','counters','DSP','IO','Opamp','Digital_Potentiometers']
Total_Total_matrix=np.zeros(shape=(class_num,class_num))
for test_case in list_test_case:
    source_pdf_Dir1=os.path.join(Path_extracted1,os.path.join('All_pdf',test_case))
    destination_pdf1=os.path.join(Path_extracted1,'Test_pdf')
    source_pdf_Dir2=os.path.join(Path_extracted1,'Test_pdf')
    destination_pdf2=os.path.join(Path_extracted1,os.path.join('All_pdf',test_case))
    file_list_pdf=os.listdir(source_pdf_Dir1)

    source_txt_Dir1=os.path.join(Path_extracted1,os.path.join('All_text',test_case))
    destination_txt1=os.path.join(Path_extracted1,'Test_text')
    source_txt_Dir2=os.path.join(Path_extracted1,'Test_text')
    destination_txt2=os.path.join(Path_extracted1,os.path.join('All_text',test_case))
    file_list_txt=os.listdir(source_txt_Dir1)

    source_pdf_cropped_Dir1=os.path.join(Path_extracted1,os.path.join('cropped_pdf',test_case))
    destination_pdf_cropped1=os.path.join(Path_extracted1,'Test_cropped_pdf')
    source_pdf_cropped_Dir2=os.path.join(Path_extracted1,'Test_cropped_pdf')
    destination_pdf_cropped2=os.path.join(Path_extracted1,os.path.join('cropped_pdf',test_case))
    file_list_pdf_cropped=os.listdir(source_pdf_cropped_Dir1)

    source_txt_cropped_Dir1=os.path.join(Path_extracted1,os.path.join('cropped_text',test_case))
    destination_txt_cropped1=os.path.join(Path_extracted1,'Test_cropped_text')
    source_txt_cropped_Dir2=os.path.join(Path_extracted1,'Test_cropped_text')
    destination_txt_cropped2=os.path.join(Path_extracted1,os.path.join('cropped_text',test_case))
    file_list_txt_cropped=os.listdir(source_txt_cropped_Dir1)

    tested_num=0
    Total_conf_matrix=np.zeros(shape=(class_num,class_num))
    Total_perf_matrix=np.zeros(shape=(class_num,class_num))
    N=len(file_list_pdf)
    
    while tested_num+N//division_group<N:
        inner_counter=0
        for i in range(tested_num,tested_num+N//division_group):
            source1=os.path.join(source_pdf_Dir1,file_list_pdf[i])
            shutil.move(source1, destination_pdf1)
            source1=os.path.join(source_txt_Dir1,file_list_txt[i])
            shutil.move(source1, destination_txt1)
            source1=os.path.join(source_pdf_cropped_Dir1,file_list_pdf_cropped[i])
            shutil.move(source1, destination_pdf_cropped1)
            source1=os.path.join(source_txt_cropped_Dir1,file_list_txt_cropped[i])
            shutil.move(source1, destination_txt_cropped1)
            inner_counter+=1
        gussed_title=title_decision_confusion_matrix()
        #print(gussed_title)
        correct_title=[test_case]*inner_counter
        conf_matrix=confusionMatrix(correct_title,gussed_title)
        #print(conf_matrix)
        #print('****************')
        Total_conf_matrix+=conf_matrix
        
        file_list_pdf2=os.listdir(source_pdf_Dir2)
        file_list_txt2=os.listdir(source_txt_Dir2)
        file_list_pdf_cropped2=os.listdir(source_pdf_cropped_Dir2)
        file_list_txt_cropped2=os.listdir(source_txt_cropped_Dir2)
        for f in file_list_pdf2:
            source2=os.path.join(source_pdf_Dir2,f)
            shutil.move(source2, destination_pdf2)
        for f in file_list_txt2:
            source2=os.path.join(source_txt_Dir2,f)
            shutil.move(source2, destination_txt2)
        for f in file_list_pdf_cropped2:
            source2=os.path.join(source_pdf_cropped_Dir2,f)
            shutil.move(source2, destination_pdf_cropped2)
        for f in file_list_txt_cropped2:
            source2=os.path.join(source_txt_cropped_Dir2,f)
            shutil.move(source2, destination_txt_cropped2)
        tested_num+=N//division_group

    additional_tag=True
    inner_counter=0
    for i in range(tested_num, N):
        inner_counter+=1
        additional_tag=True
        source1=os.path.join(source_pdf_Dir1,file_list_pdf[i])
        shutil.move(source1, destination_pdf1)
        source1=os.path.join(source_txt_Dir1,file_list_txt[i])
        shutil.move(source1, destination_txt1)
        source1=os.path.join(source_pdf_cropped_Dir1,file_list_pdf_cropped[i])
        shutil.move(source1, destination_pdf_cropped1)
        source1=os.path.join(source_txt_cropped_Dir1,file_list_txt_cropped[i])
        shutil.move(source1, destination_txt_cropped1)
    if additional_tag:
        gussed_title=title_decision_confusion_matrix()
        correct_title=[test_case]*inner_counter
        conf_matrix=confusionMatrix(correct_title,gussed_title)
        #print(conf_matrix)
        #print('****************')
        Total_conf_matrix+=conf_matrix
        file_list_pdf2=os.listdir(source_pdf_Dir2)
        file_list_txt2=os.listdir(source_txt_Dir2)
        file_list_pdf_cropped2=os.listdir(source_pdf_cropped_Dir2)
        file_list_txt_cropped2=os.listdir(source_txt_cropped_Dir2)
        for f in file_list_pdf2:
            source2=os.path.join(source_pdf_Dir2,f)
            shutil.move(source2, destination_pdf2)
        for f in file_list_txt2:
            source2=os.path.join(source_txt_Dir2,f)
            shutil.move(source2, destination_txt2)
        for f in file_list_pdf_cropped2:
            source2=os.path.join(source_pdf_cropped_Dir2,f)
            shutil.move(source2, destination_pdf_cropped2)
        for f in file_list_txt_cropped2:
            source2=os.path.join(source_txt_cropped_Dir2,f)
            shutil.move(source2, destination_txt_cropped2)
    #print('...............')
    #print(Total_conf_matrix)
    #print('.*.*.*.*.*.*.*.')
    for i in range(0,class_num):
        Total_conf_matrix[list_counter][i]/=N
    list_counter+=1
    #print(test_case+':')
    #print(Total_conf_matrix)
    Total_Total_matrix+=Total_conf_matrix
diagonal_sum = 0
for i in range(0,class_num):
    diagonal_sum+=Total_Total_matrix[i][i]
print('Confusion Matrix:')
print(Total_Total_matrix)
