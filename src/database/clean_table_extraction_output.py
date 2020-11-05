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

#Change path to the folder with all csv files from table extracor
directory = '/Users/zinebbenameur/Desktop/datasheet-scrubber/tests/integration/concatenate*.csv'

i = 0
for filename in glob.glob(directory):
    print("---------------------------------------------")
    print("------------", filename , "------------------")
    print("---------------------------------------------")
    i = i+1
    try:
        df = pd.read_csv(filename) #csv file which you want to import
        #print("replacing . by , in " , filename )
        df.columns = df.columns.str.replace(r"[.]", ",")
        #find columns containing current
        colNames_current = [col for col in df.columns if 'current' in col]
        colNames_voltage = [col for col in df.columns if 'voltage' in col]
        colNames_temp = [col for col in df.columns if 'temperature' in col]
        colNames_band = [col for col in df.columns if 'bandwidth' in col]
        colNames_freq = [col for col in df.columns if 'frequency' in col]
        print('colNames_voltage', colNames_voltage)  
        print('colNames_current', colNames_current)
        print('colNames_temp', colNames_temp)  
        print('colNames_band', colNames_band)
        print('colNames_freq', colNames_freq)
        #8N3QV01LG-0113CDI8-ND
        try:  
            df = df.drop(["Quantity Available","Factory Stock", "@ qty","Minimum Quantity", "Packaging", "Part Status", "Image" , "Manufacturer Part Number", "Package / Case", "Supplier Device Package"], axis=1)    
            #Change to path to the folder with all csv files
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
    except:
        pass