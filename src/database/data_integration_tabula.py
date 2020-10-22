#!/usr/bin/env python3

# MIT License

# Copyright (c) 2018 The University of Michigan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.


# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import tabula
import csv
import pymongo
from pymongo import MongoClient
import pandas as pd
from selenium import webdriver
import pandas as pd
import time
import glob
from pymongo import ASCENDING
from pymongo import DESCENDING
from pymongo import TEXT
import re
import numpy as np 

#Path to pdf file - datasheet 
#file = "/Users/zinebbenameur/Desktop/datasheet-scrubber/src/Database/test.pdf"
file = "/Users/zinebbenameur/Desktop/datasheet-scrubber/src/Database/micro.pdf"

#extract all tables from PDF using tabula 
tables = tabula.read_pdf(file, pages = 1, multiple_tables = True)

#catgegory recognition output
category_file = open("category.txt", "r")
category = str(category_file.read())
print("category", category)

# output the tables in the PDF to a CSV 
#we only need the first page as it contains the name of the component
tabula.convert_into(file, "tabula_pdf.csv", pages = 1)

#tabula.convert_into_by_batch("/Users/zinebbenameur/Desktop/datasheet-scrubber/src/Database", output_format = "json", pages = "all")

#converting CSV to Text file
text_list = []
txt_file = "tabula.txt"
csv_file = "tabula_pdf.csv"

#CSV conversion
with open(csv_file, "r") as my_input_file:
    for line in my_input_file:
        line = line.split(",", 2)
        text_list.append(" ".join(line))

with open(txt_file, "w") as my_output_file:
    my_output_file.write("#1\n")
    my_output_file.write("double({},{})\n".format(len(text_list), 2))
    for line in text_list:
        my_output_file.write("  " + line)
    print('File Successfully written.')

#storing txt content is a string  
full_file = open(txt_file, "r")
full_text = str(full_file.read())


# Finding Words with both alphabets and numbers longer than 5 characters
# Using regex 
res = re.findall(r'([A-Za-z]+[\d@]+[\w@]*|[\d@]+[A-Za-z]+[\w@]*)', full_text) 
res_filteres = [component for component in res if len (component) > 5]
          
# printing result  
print("Words with alphabets and numbers : " + str(res_filteres))


#find longuest common prefix within the list of possible components
def longestCommonPrefix(strs):
      """
      :type strs: List[str]
      :rtype: str
      """
      if len(strs) == 0:
         return ""
      current = strs[0]
      for i in range(1,len(strs)):
         temp = ""
         if len(current) == 0:
            break
         for j in range(len(strs[i])):
            if j<len(current) and current[j] == strs[i][j]:
               temp+=current[j]
            else:
               break
         current = temp
      return current

#Find subcategory based on category
#need to add dictionary TODO
sub = ""
def findsub(text): 
    global sub
    if text == "ADC":
        sub = "AD"
    else:
        sub = ""
    return sub

def findnames(header, sub):
    res = [i for i in header if sub in i] 
    return res

subcategory = findsub(category)

#print("subcategory",subcategory)
#list_of_components = findnames(row1, subcategory)

prefix = longestCommonPrefix(res_filteres)

print("prefix", prefix)

#connect to local DB
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#specify the name of the database
mydb = myclient["config"]
#specify the name of the collection, here my collection is "test2"
mycol = mydb["test2"]


myquery = {
"Manufacturer Part Number": {
"$regex": prefix
}
}

mydoc = mycol.find(myquery)
docs = mycol.count_documents(myquery)

print ("Database ", mycol.name, "contains", docs, "documents with the prefix ", prefix)

#print documents
#for x in mydoc:
#  print(x)



#for x in mycol.find({},{ "Datasheets": /.*AD678.*/ }):
# print(x)




#transform data in csv file
#check with Zach

#df = pd.read_csv(table)
#df['Subcategory'] = subcategory

   
#mycol.insert_many(df.to_dict('records'))