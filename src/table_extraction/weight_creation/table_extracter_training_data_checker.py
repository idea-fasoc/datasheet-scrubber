import pytesseract
import os
import csv
import pdfminer
import cv2
import concurrent.futures
import functools
import copy
import xml.etree.ElementTree as ET

import numpy as np


root = r"/Users/serafinakamp/Desktop/TableExt/datasheet-scrubber/src/Table_Extraction_Weight_Creation"
dim = 800

xmls = os.listdir(os.path.join(root, "xml_bound_train"))
imgs = os.listdir(os.path.join(root, "img_bound_train"))
xmls.sort()
imgs.sort()



for x in range(10):
    img = cv2.imread(os.path.join(root, "img_bound_train", imgs[x]))
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width, channels = img.shape

    test_cells = ET.parse(os.path.join(root, "xml_bound_train", xmls[x]))
    data = test_cells.getroot()

    #label each table
    for table in data:
        points_array2D = []
        extra_data = [""]
        for num, child in enumerate(table[:]):
            if(num > 0):
                points = child[0].attrib["points"]
                extra_data.append(child.attrib)
            else:
                points = child.attrib["points"]
            points_arr = []
            temp_str = ""
            ff = False
            for char in points:
                if(char.isdigit()):
                    temp_str += char
                else:
                    if(ff):
                        points_arr.append((num_storage, int(temp_str)))
                    else:
                        num_storage = int(temp_str)
                    temp_str = ""
                    ff = not ff
            points_arr += [(num_storage, int(temp_str)), points_arr[0]] #last added to complete the rectangle

            points_array2D.append(points_arr)
            print(points_array2D)

        for num, xdx in enumerate(points_array2D):
            for i in range(4):
                cv2.line(img, xdx[i], xdx[i+1], (0,255,0), 2)

    img = cv2.resize(img,(500,600))
    cv2.imshow('image',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
