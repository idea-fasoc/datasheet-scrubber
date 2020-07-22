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
#directory = '/Users/zinebbenameur/Desktop/Desktop - MacBook Pro/Fasoc/filesall/*.csv'
client = MongoClient()
#specify the name of the database
db=client.config
#specify the name of the collection, here my collection is "test2"
Digikey_py = db.digikey


#Ppython program to check if two  
# to get unique values from list 
# using numpy.unique  

def stripNum(str):
  return float("".join([i for i in str if i in '1234567890.-']))  
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
    colNames_current = [col for col in df.columns if 'Current -' in col]
    colNames_voltage = [col for col in df.columns if 'Voltage -' in col]
    colNames_temp = [col for col in df.columns if 'Temperature' in col]
    colNames_band = [col for col in df.columns if 'Gain Bandwidth Product' in col]
    colNames_freq = [col for col in df.columns if 'Frequency' in col]
    print('colNames_voltage', colNames_voltage)  
    print('colNames_current', colNames_current)
    #8N3QV01LG-0113CDI8-ND
    try:  
        df = df.drop(["Quantity Available","Factory Stock", "@ qty","Minimum Quantity", "Packaging", "Part Status", "Image" , "Manufacturer Part Number", "Package / Case", "Supplier Device Package"], axis=1)    
        #Change to path to the folder with all csv files
        start = '/Users/zinebbenameur/Desktop/Desktop - MacBook Pro/Fasoc/filesall/'
        end = '_'
        #Add new subcategory column in the csv
        subcategory = filename[filename.find(start)+len(start):filename.rfind(end)]
        
        
        #subcategory = filename.split('_')[1]
        df['Category'] = "IC"
        df['Subcategory'] = subcategory     
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

        if 'Current - Peak Output (Source, Sink)' in df.columns:
            df[['Current - Peak Output Source (A)','Current - Peak Output Sink (A)']] = df['Current - Peak Output (Source, Sink)'].str.split(',',expand=True,)
            df['Current - Peak Output Source (A)'] = df['Current - Peak Output Source (A)'].str.replace("A", "")
            df['Current - Peak Output Sink (A)'] = df['Current - Peak Output Sink (A)'].str.replace("A", "")
            df = df.drop(["Current - Peak Output (Source, Sink)"], axis=1)


        if 'Logic Voltage - VIL, VIH' in df.columns:            
            #print("------Split supply voltage")
            df[['Logic Voltage - VIL (V)','Logic Voltage - VIH (V)']] = df['Logic Voltage - VIL, VIH'].str.split(',', n = 1, expand=True,)
            df['Logic Voltage - VIL (V)'] = df['Logic Voltage - VIL (V)'].str.replace("V", "")
            df['Logic Voltage - VIH (V)'] = df['Logic Voltage - VIH (V)'].str.replace("V", "")
            df = df.drop(["Logic Voltage - VIL, VIH"], axis=1)
        

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

        if 'Accuracy' in df.columns:
            df['Accuracy (°C)'] = df['Accuracy'].str.split('°C').str[0]

        try:
            for elm in colNames_freq:
                print("I enter the for loop for : ", str(elm))
                if str(elm) in str(df.columns) :
                    print("elm is in df.columns", str(elm))
                    for k in range(len(df[str(elm)])):
                        if df[str(elm)][k] != "-":
                            res = re.findall('(\d+|\D+)', df[str(elm)][k])
                            j = len(res)
                            if str(res[j-1]) == "kHz":
                                print("case where unit is kHz")
                                unit = str(res[j-1])
                                df.at[k,str(elm)] = 0.001 * float(str(df[str(elm)][k]).replace(unit, ''))
                            elif str(res[j-1]) == "MHz":
                                print("case where unit is MHz")
                                unit = str(res[j-1])
                                df.at[k,str(elm)] = str(df[str(elm)][k]).replace(unit, '')
                            else:
                                print("SOMETHING DIFFERENT")
                    df.rename({str(elm): str(elm) + ' (MHz)'}, axis=1, inplace=True)              
                else:
                    continue
        except:
            print("warning something wrong")
            pass     
        try:
            for elm in colNames_band :
                print("I enter the for loop for : ", str(elm))
                if str(elm) in str(df.columns) :
                    print("elm is in df.columns", str(elm))
                    for k in range(len(df[str(elm)])):
                        if df[str(elm)][k] != "-":
                            res = re.findall('(\d+|\D+)', df[str(elm)][k])
                            j = len(res)
                            if str(res[j-1]) == "kHz":
                                print("case where unit is kHz")
                                unit = str(res[j-1])
                                df.at[k,str(elm)] = 0.001 * float(str(df[str(elm)][k]).replace(unit, ''))
                            elif str(res[j-1]) == "MHz":
                                print("case where unit is MHz")
                                unit = str(res[j-1])
                                df.at[k,str(elm)] = str(df[str(elm)][k]).replace(unit, '')
                            else:
                                print("SOMETHING DIFFERENT")
                    df.rename({str(elm): str(elm) + ' (MHz)'}, axis=1, inplace=True)              
                else:
                    continue
        except:
            pass
        print("************ENTER CURRENT*******")
        print (" STRING ELEMENY", elm)        
        try:
            for elm in colNames_current:
                print("I enter the for loop for : ", str(elm))
                if str(elm) in str(df.columns) :
                    print("elm is in df.columns", str(elm))
                    for k in range(len(df[str(elm)])):
                        if df[str(elm)][k] != "Adjustable" and df[str(elm)][k] != "-":
                            res = re.findall('(\d+|\D+)', df[str(elm)][k])
                            j = len(res)
                            if str(res[j-1]) == "µA":
                                print("case where unit is µA")
                                unit = str(res[j-1])
                                df.at[k,str(elm)] = 0.001 * float(str(df[str(elm)][k]).replace(unit, ''))
                                print("NEW VALUE   : ", df[str(elm)][k] )
                            elif str(res[j-1]) == "A":   
                                print("case where unit is A")
                                unit = str(res[j-1])                    
                                df.at[k,str(elm)] = 1000 * float(str(df[str(elm)][k]).replace(unit, ''))
                                print("NEW VALUE   : ", df[str(elm)][k] )
                            elif str(res[j-1]) == "pA":   
                                print("case where unit is pA")
                                unit = str(res[j-1])                    
                                df.at[k,str(elm)] = 1e-9 * float(str(df[str(elm)][k]).replace(unit, ''))
                                print("NEW VALUE   : ", df[str(elm)][k] )
                            elif str(res[j-1]) == "mA":
                                print("case where unit is mA")
                                print("old value", df[str(elm)][k])
                                unit = str(res[j-1])
                                print("test", df[str(elm)][k])                            
                                df.at[k,str(elm)] = str(df[str(elm)][k]).replace(unit, '')
                            elif str(res[j-1]) == "nA":
                                print("case where unit is nA")
                                unit = str(res[j-1])
                                df.at[k,str(elm)] = 0.0000010 * float(str(df[str(elm)][k]).replace(unit, ''))
                                print("NEW VALUE   : ", df[str(elm)][k] )
                            else:
                                print("SOMETHING DIFFERENT")
                    df.rename({str(elm): str(elm) + ' (mA)'}, axis=1, inplace=True)               
                else:
                    continue
        except:
            pass
        try:        
            for elm in colNames_voltage:
                print("I enter the for loop for : ", str(elm))
                if str(elm) in str(df.columns) and (str(elm) != 'Voltage - Supply' or  str(elm) != 'Voltage - Supply, Single/Dual (±)' or str(elm) != 'Logic Voltage - VIL, VIH'):
                    print("elm is in df.columns", str(elm))
                    for k in range(len(df[str(elm)])):
                        if df[str(elm)][k] != "-":
                            print("not - ")
                            res = re.findall('(\d+|\D+)', df[str(elm)][k])
                            j = len(res)                   
                            print("*****RESULT*****", str(res))
                            if str(res[j-1]) == "V":
                                print("case where unit is V")
                                print("old value", df[str(elm)][k])
                                unit = str(res[j-1])
                                print("test", df[str(elm)][k])                            
                                df.at[k,str(elm)] = str(df[str(elm)][k]).replace(unit, '')
                                print("NEW VALUE   : ", df[str(elm)][k])
                            elif str(res[j-1]) == "mV":
                                print("case where unit is mV")
                                print("old value", df[str(elm)][k])
                                unit = str(res[j-1])
                                print("test", df[str(elm)][k])                            
                                df.at[k,str(elm)] = 0.001 * float(str(df[str(elm)][k]).replace(unit, ''))
    
                            elif str(res[j-1]) == "µV":
                                print("case where unit is µV")
                                print("old value", df[str(elm)][k])
                                unit = str(res[j-1])
                                print("test", df[str(elm)][k])                            
                                df.at[k,str(elm)] = 1e-6 * float(str(df[str(elm)][k]).replace(unit, ''))
                        
                            elif str(res[j-1]) == "nV":
                                print("case where unit is nV")
                                unit = str(res[j-1])
                                print("test", df[str(elm)][k])                            
                                df.at[k,str(elm)] = 1.0E-9 * float(str(df[str(elm)][k]).replace(unit, ''))
                        
                        
                            else:
                                print("SOMETHING DIFFERENT")
                    df.rename({str(elm): str(elm) + ' (V)'}, axis=1, inplace=True)        
                else:
                    continue
        except:
            pass 
  
    
    except:
        pass
    
    colNames_current_new = [col for col in df.columns if 'Current' in col]
    colNames_voltage_new = [col for col in df.columns if 'Voltage' in col]
    colNames_temp_new = [col for col in df.columns if 'Temp' in col]
    colNames_band_new = [col for col in df.columns if 'Gain Bandwidth Product' in col]
    colNames_freq_new = [col for col in df.columns if 'Frequency' in col]
    colNames_acc_new = [col for col in df.columns if 'Accuracy' in col]
    colNames_price_new = [col for col in df.columns if 'Price' in col]
    colNames_slew_new = [col for col in df.columns if 'Slew' in col]
    all_columns = colNames_slew_new + colNames_price_new+ colNames_current_new + colNames_voltage_new + colNames_temp_new + colNames_band_new + colNames_freq_new + colNames_acc_new
    for elm in all_columns:
        for k in range(len(df[str(elm)])):
            try:
                if df.at[k,str(elm)] != '-':
                    df.at[k,str(elm)] = stripNum(str(df[str(elm)][k]))
                else:
                    continue
                #df[str(elm)] = stripNum(df[str(elm)])
            except:
                pass
        print ("AFTER   : ", df.dtypes)

    #Insert record in the DB
    Digikey_py.insert_many(df.to_dict('records'), bypass_document_validation=True)
    db.digikey_transformed.create_index('Unit Price (USD)')

print("----- TOTAL NUMBER OF CSV modified and inserted------",i)