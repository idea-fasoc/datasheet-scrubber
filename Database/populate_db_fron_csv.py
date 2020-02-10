from pymongo import MongoClient
import pandas as pd
from selenium import webdriver
import pandas as pd
import time
import glob

#Change path to the folder with all csv files
directory = '/Users/zinebbenameur/Desktop/Desktop - MacBook Pro/Fasoc/filesall/*.csv'


client = MongoClient()
#specify the name of the database
db=client.config
#specify the name of the collection, here my collection is "test2"
Digikey_py = db.test2

i = 0

for filename in glob.glob(directory):
    print("------------", filename , "------------------")
    i = i+1
    df = pd.read_csv(filename) #csv file which you want to import
    try:
        #Delete all element we don't need from the csv files
        df = df.drop(["Quantity Available","Factory Stock","Unit Price (USD)", "@ qty","Minimum Quantity" ], axis=1)
        #Extract the subcategory
        #Change to path to the folder with all csv files
        start = '/Users/zinebbenameur/Desktop/Desktop - MacBook Pro/Fasoc/filesall/'
        end = '_'
        #Add new subcategory column in the csv
        subcategory = filename[filename.find(start)+len(start):filename.rfind(end)]
        
        
        #subcategory = filename.split('_')[1]
        df['Category'] = "IC"
        df['Subcategory'] = subcategory
        df.columns = df.columns.str.replace("[.]", ",")
    except:
        pass
    #Insert record in the DB
    Digikey_py.insert_many(df.to_dict('records'))


print("----- TOTAL NUMBER OF CSV inserted------",i)
