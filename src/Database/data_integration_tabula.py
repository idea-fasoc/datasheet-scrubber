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
 
file = "/Users/zinebbenameur/Desktop/datasheet-scrubber/src/Database/test.pdf"
 
tables = tabula.read_pdf(file, pages = "all", multiple_tables = True)

category = open("category.txt", "r")
print(category.read())

# output all the tables in the PDF to a CSV
tabula.convert_into(file, "tabula_pdf.csv", pages = "all")

#tabula.convert_into_by_batch("/Users/zinebbenameur/Desktop/datasheet-scrubber/src/Database", output_format = "json", pages = "all")

#read 1st line of csv
with open('tabula_pdf.csv', newline='') as f:
  reader = csv.reader(f)
  row1 = next(reader)


print(row1)


def longestCommonPrefix(self, strs):
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

sub = ""
def findsub(text): 
    global sub
    if text == "ADC":
        sub = "AD"
    return sub

def findnames(header, sub):
    print(category)
    res = [i for i in header if sub in i] 
    return res

findnames(row1, findsub(str(category)))


#connect to local DB
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#specify the name of the database
mydb = myclient["config"]
#specify the name of the collection, here my collection is "test2"
mycol = mydb["test2"]

#for x in mycol.find({},{ "Datasheets": /.*AD678.*/ }):
# print(x)




#transform data in csv file
#check with Zach

#df = pd.read_csv(table)
#df['Subcategory'] = subcategory

   
#mycol.insert_many(df.to_dict('records'))
