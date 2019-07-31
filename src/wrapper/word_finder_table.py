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

import PyPDF2
import csv
import sys
import decision_extractor_table_xy
import decision_extractor_table_xx
import os
import os.path
from CSV_cleaner import CSV_cleaner
from Address import Address


    

def word_finder_table(source_pdf_path,y,exception_list):
    typ_result={}
    max_result={}
    min_result={}

    Path_extracted=Address(1).split("\n")
    Path_extracted1=Path_extracted[0]

    destination_pdf_path=os.path.join(Path_extracted1,'Modified_pdf')
    source_csv_path=destination_pdf_path
    destination_csv_path=os.path.join(Path_extracted1,'Test_pdf','CSV')

    last_directory_word_spliting_pdf=source_pdf_path.split(chr(92)) #splits by forward slash
    last_pdf_directory_word=last_directory_word_spliting_pdf[-1] #gets last index 
    last_directory_word_spliting_csv=last_pdf_directory_word.split(".")
    last_csv_directory_word=last_directory_word_spliting_csv[0]+"."+"csv"

    #Counting number of pdf pages

    pfr = PyPDF2.PdfFileReader(open(source_pdf_path, "rb"))
    number_page=pfr.getNumPages()
    for page in range(0,number_page):#k’th CSV page start with k=1
        all_row=[]
        typ_row_counter=[]
        typ_column_counter=[]
        max_row_counter=[]
        max_column_counter=[]
        min_row_counter=[]
        min_column_counter=[]

        typ_row_counter_xx=[]
        typ_column_counter_xx=[]
        max_row_counter_xx=[]
        max_column_counter_xx=[]
        min_row_counter_xx=[]
        min_column_counter_xx=[]
        x_main_row_counter=[]
        x_main_column_counter=[]
        x_main_list=["specification","version"]
        x_accessories1_row_counter=[]
        x_accessories1_column_counter=[]
        x_accessories1_list=["test condition","temp"]
        xy_id_row=[]
        xy_id_column=[]
        xy_id_list=["condition", "conditions", "test condition", "test conditions"]
        x_accessories2_row_counter=[]
        x_accessories2_column_counter=[]
        x_accessories2_list=["unit"]
        y_row_counter=[]
        y_column_counter=[]
        title=[]
        
        destination_csv_extraction_path=os.path.join(destination_csv_path,str(page),last_csv_directory_word) 
        size=os.path.getsize(destination_csv_extraction_path)
        
        if size!=0:#CSV file size > 0 KB?Yes 
            CSV_cleaner(destination_csv_path, last_csv_directory_word, destination_csv_extraction_path,page);
            with open(destination_csv_extraction_path, 'r') as csvfile:
                csv_file = csv.reader(csvfile)
                #Save row and column number of “typ”, “max”, “this work” “min”, unit “typ”,  unit “max”,  unit “min”,  “specification”, “version”, “test condition”, “temp”, “unit”
                for row_counter, row in enumerate(csv_file):
                    all_row.append(row)
                    for column_counter, word in enumerate (row):
                        word=word.lower()#Prettify table
                        if ("typ " == word[:4]) | (" typ" == word[-4:]) | ("typ" == word) | ("typ." == word) | ("typ1" == word):
                            typ_row_counter.append(row_counter)
                            typ_column_counter.append(column_counter)
                        if ("max " == word[:4]) | (" max" == word[-4:]) | ("max" == word) | ("max." == word) | ("max1" == word):
                            max_row_counter.append(row_counter)
                            max_column_counter.append(column_counter)
                        if ("min " == word[:4]) | (" min" == word[-4:]) | ("min" == word) | ("min." == word) | ("min1" == word):
                            min_row_counter.append(row_counter)
                            min_column_counter.append(column_counter)

                        ##NOT USED###############
                        if "lsb typ" in word:##need to generalize not only for lsb ##not used
                            typ_row_counter_xx.append(row_counter)
                            typ_column_counter_xx.append(column_counter)
                        if "lsb max" in word:##need to generalize not only for lsb ##not used
                            max_row_counter_xx.append(row_counter)
                            max_column_counter_xx.append(column_counter)
                        if "lsb min" in word:##need to generalize not only for lsb ##not used
                            min_row_counter_xx.append(row_counter)
                            min_column_counter_xx.append(column_counter)
                        #########################

                        for element in x_main_list:
                            if element in word:
                                x_main_row_counter.append(row_counter)
                                x_main_column_counter.append(column_counter)
                        for element in x_accessories1_list:
                            if element in word:
                                x_accessories1_row_counter.append(row_counter)
                                x_accessories1_column_counter.append(column_counter)
                        for element in x_accessories2_list:
                            if element in word:
                                x_accessories2_row_counter.append(row_counter)
                                x_accessories2_column_counter.append(column_counter)
                        for element in xy_id_list:
                            le = len(element)
                            if element == word or (len(word) > len(element) and (word[:le] == element or word[-le:] == element)):
                                xy_id_row.append(row_counter)
                                xy_id_column.append(column_counter)
                                break

                        if (y in word) and all(ex not in word for ex in exception_list): #ignore "word" if it contains an exception
                            y_row_counter.append(row_counter)
                            y_column_counter.append(column_counter)
                            
         #   print("Keyword y: ", y_row_counter, " x: ", y_column_counter)     

          
            #Determine table type: YX or YY
            ## change xx to YY and xy to YX, x with y for variable names               
            if all(elem in typ_row_counter for elem in y_row_counter) or all(elem in max_row_counter for elem in y_row_counter) or all(elem in min_row_counter for elem in y_row_counter):#All rows including spec, includes typ? or All rows including spec, includes max? or All rows including spec, includes min? Yes            
              #  print("xx on page: ", page)
                #Report row and column number of “specification”, “version”, “test condition”, “temp”, “unit”, spec, “max”, “min”, “typ”
                max_single_dic=decision_extractor_table_xx.decision_extractor_table_xx(all_row,x_main_row_counter,x_main_column_counter,x_accessories1_row_counter,x_accessories1_column_counter,x_accessories2_row_counter,x_accessories2_column_counter,"max","lsb",y_row_counter,y_column_counter,y)        
                min_single_dic=decision_extractor_table_xx.decision_extractor_table_xx(all_row,x_main_row_counter,x_main_column_counter,x_accessories1_row_counter,x_accessories1_column_counter,x_accessories2_row_counter,x_accessories2_column_counter,"min","lsb",y_row_counter,y_column_counter,y)        
                typ_single_dic=decision_extractor_table_xx.decision_extractor_table_xx(all_row,x_main_row_counter,x_main_column_counter,x_accessories1_row_counter,x_accessories1_column_counter,x_accessories2_row_counter,x_accessories2_column_counter,"typ","lsb",y_row_counter,y_column_counter,y)        
            else:#All rows including spec, includes typ? or All rows including spec, includes max? or All rows including spec, includes min? No
               # print("xy on page: ", page)
                #Report row and column number of “max”, “min”, “typ”, “this work”, spec
                max_single_dic=decision_extractor_table_xy.decision_extractor_table_xy(all_row,max_row_counter,max_column_counter,"max",y_row_counter,y_column_counter,y, xy_id_row, xy_id_column) 
                min_single_dic=decision_extractor_table_xy.decision_extractor_table_xy(all_row,min_row_counter,min_column_counter,"min",y_row_counter,y_column_counter,y, xy_id_row, xy_id_column) 
                typ_single_dic=decision_extractor_table_xy.decision_extractor_table_xy(all_row,typ_row_counter,typ_column_counter,"typ",y_row_counter,y_column_counter,y, xy_id_row, xy_id_column)
                ###this_work_single_dic=decision_extractor_table_xy.decision_extractor_table_xy(all_row,this_work_row_counter,this_work_column_counter,"this work",y_row_counter,y_column_counter,y)

            for key, value in max_single_dic.items():  
                if key !="nothing":
                    max_result[key]=value
            for key, value in min_single_dic.items():
                if key !="nothing":
                    min_result[key]=value
            for key, value in typ_single_dic.items():
                if key !="nothing":
                    typ_result[key]=value
            ##write else        
    return max_result,min_result,typ_result##add this work
