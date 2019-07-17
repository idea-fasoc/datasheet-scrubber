import pandas as pd
from urllib import request


def datasheet_download(filepath, destinationpath):
    data = pd.read_csv(filepath)

    data = data['Datasheets']
    data = data.drop_duplicates()
    opener = request.build_opener()
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    request.install_opener(opener)
    i = 0
    for element in data:
        string_element = ''.join(element)
        print(string_element)
        request.urlretrieve(string_element, destinationpath + "file" + str(i) + ".pdf")
        i += 1


datasheet_download(r'C:\Users\whatsthenext\Desktop\download.csv', r'C:\Users\whatsthenext\Desktop\source\ ')
