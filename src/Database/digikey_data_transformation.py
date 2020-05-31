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

#Change path to the folder with all csv files
directory = '/Users/zinebbenameur/Desktop/Desktop - MacBook Pro/Fasoc/filesall/*.csv'
client = MongoClient()
#specify the name of the database
db=client.config
#specify the name of the collection, here my collection is "test2"
Digikey_py = db.with_index_price


#Ppython program to check if two  
# to get unique values from list 
# using numpy.unique  

  
# function to get unique values 
def unique(list1): 
    x = np.array(list1) 
    print(np.unique(x)) 

i = 0

for filename in glob.glob(directory):
    #print("------------", filename , "------------------")
    i = i+1
    df = pd.read_csv(filename) #csv file which you want to import
    #print("replacing . by , in " , filename )
    df.columns = df.columns.str.replace(r"[.]", ",")
    #find columns containing current
    colNames_current = [col for col in df.columns if 'Current' in col]
    colNames_voltage = [col for col in df.columns if 'Voltage -' in col]
    colNames_temp = [col for col in df.columns if 'Temperature' in col]
    #print("******column names containing current*****", colNames_current)
    print("******column names containing voltage*****", colNames_voltage)
    print("******column names containing temperature*****", colNames_temp)
    

    try:  
        df = df.drop(["Quantity Available","Factory Stock", "@ qty","Minimum Quantity" ], axis=1)         
        if 'Operating Temperature' in df.columns:
            #print("----- Split temperature------",i)
            df[['min Operating Temp (°C)','max Operating Temp (°C)']] = df['Operating Temperature'].str.split('~',expand=True,)
            df['min Operating Temp (°C)'] = df['min Operating Temp (°C)'].str.replace("°C", "")
            df['max Operating Temp (°C)'] = df['max Operating Temp (°C)'].str.replace("°C", "")
            df['max Operating Temp (°C)'] = df['max Operating Temp (°C)'].str.replace(r"\(.*\)","")
            df = df.drop(["Operating Temperature"], axis=1)

        if 'Sensing Temperature' in df.columns:
            #print("----- Split temperature------",i)
            df[['min Sensing Temp (°C)','max Sensing Temp (°C)']] = df['Sensing Temperature'].str.split('~', n = 1, expand=True,)
            df['min Sensing Temp (°C)'] = df['min Sensing Temp (°C)'].str.replace("°C", "")
            df['max Sensing Temp (°C)'] = df['max Sensing Temp (°C)'].str.replace("°C", "")
            df['max Sensing Temp (°C)'] = df['max Sensing Temp (°C)'].str.replace(r"\(.*\)","")
            df = df.drop(["Sensing Temperature"], axis=1)


        if 'Voltage - Supply' in df.columns:            
            #print("------Split supply voltage")
            df[['min Voltage - Supply (V)','max Voltage - Supply (V)']] = df['Voltage - Supply'].str.split('~', n = 1, expand=True,)
            df['min Voltage - Supply (V)'] = df['min Voltage - Supply (V)'].str.replace("V", "")
            df['max Voltage - Supply (V)'] = df['max Voltage - Supply (V)'].str.replace("V", "")
            df = df.drop(["Voltage - Supply"], axis=1)

        if 'Voltage - Supply, Single/Dual (±)' in df.columns:
            df[['min Voltage - Supply (V)','max Voltage - Supply (V)']] = df['Voltage - Supply, Single/Dual (±)'].str.split('~', n = 1, expand=True,)
            df['min Voltage - Supply (V)'] = df['min Voltage - Supply (V)'].str.split('V').str[0]
            df['max Voltage - Supply (V)'] = df['max Voltage - Supply (V)'].str.split('V').str[0]
            df['min Voltage - Supply (V)'] = df['min Voltage - Supply (V)'].str.replace("V", "")
            df['max Voltage - Supply (V)'] = df['max Voltage - Supply (V)'].str.replace("V", "")
            df = df.drop(["Voltage - Supply, Single/Dual (±)"], axis=1)
            

        if 'Slew Rate' in df.columns:
           df['Slew Rate (V/µs)'] = df['Slew Rate'].str.replace("V/µs", "")
           df = df.drop(["Slew Rate"], axis=1)

        if 'Temperature Coefficient (Typ)' in df.columns:
            df['Temperature Coefficient (Typ) (ppm/°C)'] = df['Temperature Coefficient (Typ)'].str.split('ppm/°C').str[0]
            df = df.drop(["Temperature Coefficient (Typ)"], axis=1)

        if 'Temperature Coefficient' in df.columns:
            df['Temperature Coefficient (ppm/°C)'] = df['Temperature Coefficient'].str.split('ppm/°C').str[0]
            df = df.drop(["Temperature Coefficient"], axis=1)

        
        for elm in colNames_current:
            print("I enter the for loop for : ", str(elm))
            if str(elm) in str(df.columns) :
                print("elm is in df.columns", str(elm))
                for k in range(len(df[str(elm)])):
                    if df[str(elm)][k] != "Adjustable" and df[str(elm)][k] != "-":
                        res = re.findall('(\d+|\D+)', df[str(elm)][k])
                        j = len(res)
                        if str(res[j-1]) == "µA":
                            #print("case where unit is µA")
                            unit = str(res[j-1])
                            df[str(elm)][k] = 0.001 * float(str(df[str(elm)][k]).replace(unit, ''))
                        elif str(res[j-1]) == "A":   
                            print("case where unit is A")
                            unit = str(res[j-1])                    
                            df.at[k,str(elm)] = 1000 * float(str(df[str(elm)][k]).replace(unit, ''))
                        elif str(res[j-1]) == "mA":
                            print("case where unit is mA")
                            unit = str(res[j-1])
                            df.at[k,str(elm)] = str(df[str(elm)][k]).replace(unit, '')
                        elif str(res[j-1]) == "nA":
                            print("case where unit is nA")
                            unit = str(res[j-1])
                            df[str(elm)][k] = 0.0000010 * float(str(df[str(elm)][k]).replace(unit, ''))
                        else:
                            print("SOMETHING DIFFERENT")
                #rename column by adding the unit
                df.rename({str(elm): str(elm) + ' (mA)'}, axis=1, inplace=True)    
            else:
                continue
        for elm in colNames_voltage:
            print("I enter the for loop for : ", str(elm))
            if str(elm) in str(df.columns) :
                print("elm is in df.columns", str(elm))
                print("len(df[str(elm)])", len(df[str(elm)]))
                for k in range(len(df[str(elm)])):
                    print("value of k", k)
                    print("SPLITTING this", df[str(elm)][k])
                    if df[str(elm)][k] != "-":
                        print("not - ")
                        res = re.findall('(\d+|\D+)', df[str(elm)][k])
                        j = len(res)
                        if str(res[j-1]) == "V":
                            print("case where unit is V")
                            unit = str(res[j-1])
                            df.at[k,str(elm)] = str(df[str(elm)][k]).replace(unit, '')
                        elif str(res[j-1]) == "mV":
                            print("case where unit is mV")
                            unit = str(res[j-1])
                            df.at[k,str(elm)] = 0.001 * float(str(df[str(elm)][k]).replace(unit, ''))
                        elif str(res[j-1]) == "µV":
                            print("case where unit is µV")
                            unit = str(res[j-1])
                            df.at[k,str(elm)] = 1e-6 * float(str(df[str(elm)][k]).replace(unit, ''))
                        elif str(res[j-1]) == "nV":
                            print("case where unit is nV")
                            unit = str(res[j-1])
                            df.at[k,str(elm)] = 1.0E-9 * float(str(df[str(elm)][k]).replace(unit, ''))                    
                        else:
                            print("SOMETHING DIFFERENT")
                df.rename({str(elm): str(elm) + ' (V)'}, axis=1, inplace=True)    
                #df = df.drop([str(elm)], axis=1)            
            else:
                continue

        #change units in place
        #df['Discounted_Price'] = df['Cost'] - (0.1 * df['Cost']) 
        #Delete all element we don't need from the csv files
        #print("----- Delete all element we don't need from the csv files------",i)
        #df.columns = df.columns.str.replace("[.]", ",")
    except:
        pass


    #Insert record in the DB
    Digikey_py.insert_many(df.to_dict('records'), bypass_document_validation=True)
    #Add indexing on price value
    db.with_index_price.create_index('Unit Price (USD)')

print("----- TOTAL NUMBER OF CSV modified------",i)