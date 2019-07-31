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
import re
import csv

def replacer(string):
    temp = string
    chars = " ?.+-" + chr(177)
    for c in chars:
        temp = temp.replace(c,"")
    return temp

def CSV_cleaner(destination_csv_path, last_csv_directory_word, destination_csv_extraction_path,page):    
    xy_error_col=[]
    xy_error_col_amount=[]
    xy_master_word=[]
    xy_useful_columns=[]
    temp_extraction_path=os.path.join(destination_csv_path,str(page),last_csv_directory_word.split(".")[0] + "_temp.csv") #for xy error
    with open(destination_csv_extraction_path, 'r') as csvfile: #new stuff
        csv_file = csv.reader(csvfile)
        for row_counter, row in enumerate(csv_file):
            for column_counter, word in enumerate (row):
                word=word.lower()#Prettify table
                temp = word.replace(".","")
                useful_col = 0
                xy_Error = 0 #attempt to split up incorrectly merged columns    
                if ("typ " == temp[:4]) | (" typ " in temp) | (" typ" == temp[-4:]):
                    xy_Error += 1
                    useful_col += 1;
                if ("max " == temp[:4]) | (" max " in temp) | (" max" == temp[-4:]):
                    xy_Error += 1
                    useful_col += 1;
                if ("min " == temp[:4]) | (" min " in temp) | (" min" == temp[-4:]):
                    xy_Error += 1
                    useful_col += 1;
                if ("specification " == temp[:14]) | (" specification " in temp) | (" specification" == temp[-14:]):
                    xy_Error += 1
                if ("unit " == temp[:5]) | (" unit " in temp) | (" unit" == temp[-5:]):
                    xy_Error += 1
                if ("conditions " == temp[:11]) | (" conditions " in temp) | (" conditions" == temp[-11:]):
                    xy_Error += 1
                if ("condition " == temp[:10]) | (" condition " in temp) | (" condition" == temp[-10:]):
                    xy_Error += 1
                if ("parameter " == temp[:10]) | (" parameter " in temp) | (" parameter" == temp[-10:]):
                    xy_Error += 1
                if("min to max" in temp): #exception
                    xy_Error = 0

                if((xy_Error > 1) & (column_counter not in xy_error_col)): #trying to fix error with xy_tables
                    xy_error_col.append(column_counter)  
                    xy_error_col_amount.append(xy_Error)
                    xy_useful_columns.append(useful_col)
                    xy_master_word.append(word)  #the word in question
                  #  print("Error(s) on page: ", page, " Severity: ", xy_Error)
                   # print(word)
   # print(xy_error_col)
    if(xy_error_col):
        with open(destination_csv_extraction_path, 'r') as csvfile:
            with open(temp_extraction_path, 'w', newline='') as csvout:
                writer = csv.writer(csvout, delimiter=',')
                csv_file = csv.reader(csvfile)
                for row in csv_file:            #go row by row
                    holder = []
                    counter = 0
                    for word in (row):          
                        if(counter not in xy_error_col):        #non-broken case
                            holder.append(word)
                        elif(("grade" in word.lower()) or (word[-4:].lower() == "msps")): #exception for titles
                            holder.append(word)
                            for i in range(xy_error_col_amount[xy_error_col.index(counter)]-1):
                                holder.append("")
                        else:
                            words = word.split(' ')
                            number_of_expected_words = xy_error_col_amount[xy_error_col.index(counter)]
                            number_of_useless_cols = number_of_expected_words - xy_useful_columns[xy_error_col.index(counter)]

                            if(len(words) < number_of_expected_words): #logic to fix movement errors (MORE HEADERS THAN WORDS) //ADD more cases 
                                if(number_of_useless_cols == 0):
                                    if(number_of_expected_words - len(words) == 2): #all 3(min,temp,max) assumes that order; give to temp
                                        words.insert(0, "")                            
                                else:
                                    iterator = 0;
                                    for i in xy_master_word:
                                        if(i.lower() is not "min" and i.lower() is not "typ" and i.lower() is not "max"):
                                            if(words[iterator].replace("?","").replace(chr(177),"") is not float): #new remove ? and plus minus
                                                words.insert(0, "")
                                                iterator += 1
                            elif(len(words) > number_of_expected_words): #(MORE WORDS THAN HEADERS)
                               # if((xy_useful_columns[xy_error_col.index(counter)] == 3)): #all 3 (min,temp,max)
                                if(xy_master_word[0] is not "min" and xy_master_word[0] is not "typ" and xy_master_word[0] is not "max"):
                                    list_to_remove = []
                                    iterator = 0
                                    for sub_word in words[:-1]: #find how many fake columns belong to the first column
                                        if((replacer(sub_word).isdigit() or sub_word is '-') and (replacer(words[iterator+1]).isdigit() or (words[iterator+1]) is '-')): 
                                            break;
                                        iterator += 1
                                    if(all(replacer(x).isdigit() for x in words[iterator:])): #experimental fix for when the fake column has a number in it
                                        while(len(words)-iterator+1 > number_of_expected_words-1):
                                            iterator += 1
                                    for i in range(1, iterator-1): #move the fake columns over
                                        words[0] += words[1]
                                        del words[1]

                            for i in range(number_of_expected_words):  #iterate for the number of errors//fixes the csv here
                                try:
                                    holder.append(words[i])  
                                except:
                                    holder.append("")
                        counter = counter + 1
                    writer.writerow(holder)
        old_file = os.path.join(destination_csv_path,str(page),last_csv_directory_word.split(".")[0] + "old.csv")
        if os.path.exists(old_file):
            os.remove(old_file)
        os.rename(destination_csv_extraction_path, old_file) #for debugging
        os.rename(temp_extraction_path,destination_csv_extraction_path)#end of new stuff
