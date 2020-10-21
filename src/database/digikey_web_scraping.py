from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import pandas as pd
import time
import shutil
import re
import os
import glob

#WEB SCRAPING FOR DIGIKEY WEBSITE USING SELENIUM LIBRARY and CHROME DRIVER

#Replace with another category
category = 'integrated-circuits-ics'
#Replace with path where you want to download csv files
download_folder = "/Users/zinebbenameur/Desktop/Desktop - MacBook Pro/Fasoc/csv_tables"
#files containing the links to urls
links_urls = "/Users/zinebbenameur/Desktop/Desktop - MacBook Pro/Fasoc/links_and_type.csv"



#Read urls
df = pd.read_csv(links_urls, usecols=[0,1], names=['colA', 'colB'], header=None)
#url_extender = r"?FV=ffe00300&quantity=0&ColumnSort=1&page=" + str(1) + "&pageSize=500"
urls = df['colA']
sub_category = df['colB']
print("URLS", urls)
#print("sub", sub_category)
chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : download_folder}
chromeOptions.add_experimental_option("prefs",prefs)
#Replace with path to chrome driver
chromedriver = "/usr/local/bin/chromedriver"
driver = webdriver.Chrome(executable_path=chromedriver, options=chromeOptions)

#Iterate through all urls from the csv file
for url in urls:
    print("I enter the for loop")
    #add extension to the URL in order to scrap pages with 500 elements
    url_extender = r"?FV=ffe00300&quantity=0&ColumnSort=1&page=" + str(1) + "&pageSize=500"
    print("I will scrap this url", url)
    driver.get(url+ url_extender)
    driver.maximize_window()
    current_page = WebDriverWait(driver, 200).until(ec.visibility_of_element_located((By.CLASS_NAME, "current-page")))
    print("CURRENT_PAGE", current_page.text)
    nb_pages = (current_page.text).partition("/")[2] 
    print("nb_pages", nb_pages)
    for i in range(1, int(nb_pages)+1):
        url_extender = r"?FV=ffe00300&quantity=0&ColumnSort=1&page=" + str(i) + "&pageSize=500"
        #Extract subcategory from url
        start = category +'/'
        end = '/'
        subcategory = url[url.find(start)+len(start):url.rfind(end)]
        print("subcategory", subcategory)
        driver.get(url+ url_extender)
        driver.maximize_window()
        try:              
            # wait for Fastrack item to appear, then click it
            fastrack = WebDriverWait(driver, 300).until(ec.visibility_of_element_located((By.CLASS_NAME, "download-table")))
            WebDriverWait(driver, 300)
            driver.execute_script("arguments[0].scrollIntoView()", fastrack)
            #click on the download button
            fastrack.click()
            WebDriverWait(driver, 300)
            time.sleep(15)
            #Replace with path where you downloaded files
            Initial_path = download_folder
            list_of_files = glob.glob(download_folder +'/*.csv') # * means all if need specific format then *.csv
            #search the latest file downloaded
            latest_file = max(list_of_files, key=os.path.getctime)
            # filename = max([Initial_path + "\\" + f for f in os.listdir(Initial_path)],key=os.path.getctime)
            #rename with more appropriate name
            shutil.move(latest_file,os.path.join(Initial_path,subcategory + "_" + str(i) + ".csv"))
            print("file renamed")
        except Exception:
            pass
    print('Deleting the URL from the file', url)
    #we erase the link from the file in order to make sure we did not miss any link during the scraping process
    df.drop(df.index[0], inplace = True)
    df.to_csv(links_urls, index=False, header=None)

