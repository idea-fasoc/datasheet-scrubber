import os
from pdf2image import convert_from_path ##poppler needs to be added and added to the path variable
import cv2
import numpy as np
import argparse

def extract_jpg(pdf,page):
    TempImages_dir = "../../src/table_extraction/TempPDF"
    try:
        os.makedirs(TempImages_dir)
    except FileExistsError:
        if len(os.listdir(TempImages_dir)) != 0:
            for file in os.listdir(TempImages_dir):
                os.remove(os.path.join(TempImages_dir,file))

    image = convert_from_path(pdf, 300, first_page=page, last_page=page)

    for im in image:
        cv2.imwrite("../../src/table_extraction/TempPDF/temp.jpg",np.array(im))


if __name__ == "__main__":
    # Delete all default flags
    parser = argparse.ArgumentParser(description="extract a page from a pdf and save as image for yolo detection")
    """
    Command line options
    """

    #CNN model paths
    parser.add_argument("-p", "--pdf_loc",type=str,help="path to pdf location of detection, defualt is cwd/test.pdf",default=os.path.join(os.getcwd(),"test.pdf"))

    #YOLO detected image path
    parser.add_argument("-n", "--page_num",type=int,help="page num to detect tables on, default is 1",default=1)

    FLAGS = parser.parse_args() #to parse arguments

    pdf = FLAGS.pdf_loc
    page = FLAGS.page_num

    TempImages_dir = "TempPDF"
    try:
        os.makedirs(TempImages_dir)
    except FileExistsError:
        if len(os.listdir(TempImages_dir)) != 0:
            for file in os.listdir(TempImages_dir):
                os.remove(os.path.join(TempImages_dir,file))

    image = convert_from_path(pdf, 300, first_page=page, last_page=page)

    for im in image:
        cv2.imwrite("TempPDF/temp.jpg",np.array(im))
