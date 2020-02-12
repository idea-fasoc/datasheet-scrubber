import requests
from bs4 import BeautifulSoup
import pandas as pd

#url containing the list of ICs suncategories
url = 'https://www.digikey.com/products/ics/en'
reqs = requests.get(url)
soup = BeautifulSoup(reqs.text, 'lxml')
#will be used to construct the final url
pre = "https://www.digikey.com"

#create list of urls
list_urls = []
text = []
for a in soup.select("ul.catfiltersub li"):
    list_urls.append(pre + a.a.get('href'))
    text.append(a.a.text.strip())

#create dataframe woth both lists
df= pd.DataFrame(list(zip(list_urls,text)))
#drop last 2 rows as it contains accessories and kits
df.drop(df.tail(2).index,inplace=True)

#export to csv file
export_csv = df.to_csv (r'links_and_type.csv', index = None, header=False)
