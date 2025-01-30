#!/usr/bin/env python3

# MIT License

# Copyright (c) 2018 The University of Michigan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import pytesseract
import statistics
import os
import csv
import cv2
import concurrent.futures
import functools
import copy
import numpy as np
import argparse  # arguement parsing
import fix_pdf
import detector
import tensorflow as tf
from tensorflow.keras.models import load_model

from pdf2image import convert_from_path #poppler needs to be added and added to the path variable
from numba import jit
import time
import multiprocessing
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool as Pool

import dill
from tensorflow.keras.layers import Dense, Conv2D, Permute, MaxPooling2D, AveragePooling2D, LSTM, Reshape, Flatten, Dropout
from tensorflow.keras.layers import multiply, add, average, maximum, Concatenate, Lambda
from tensorflow.keras.models import load_model
tf.compat.v1.enable_eager_execution()

##calculate the IoU between two regions
def calc_IoU(xml,proposed):
    """
    Calculate the Intersection Over Union (IoU) between two regions.

    Args:
        xml (list): List of coordinates for the first region.
        proposed (list): List of coordinates for the second region.

    Returns:
        float: The IoU value, ranging from 0 (no overlap) to 1 (perfect overlap).
    """ 
    intersection = 0
    xmlMinX = xml[0]
    xmlMinY = xml[1]
    xmlMaxX = xml[2]
    xmlMaxY = xml[3]
    propMinX = proposed[0]
    propMinY = proposed[1]
    propMaxX = proposed[2]
    propMaxY = proposed[3]

    # Calculate the shared width and height between the two regions
    width_shared = min(propMaxX,xmlMaxX) - max(propMinX,xmlMinX)
    height_shared = min(propMaxY,xmlMaxY) - max(propMinY,xmlMinY)
    
    # If there is an overlap, calculate the intersection area
    if width_shared > 0 and height_shared > 0:
        intersection = width_shared*height_shared
    
    # Calculate the areas of the two regions
    xmlArea = (xmlMaxX-xmlMinX)*(xmlMaxY-xmlMinY)   
    propArea = (propMaxX-propMinX)*(propMaxY-propMinY)
    
    # Calculate the union area
    union = xmlArea + propArea -intersection
    
    # Return the IoU value
    return intersection/union

#for now assume picture is detected in yolo before being processe here
def yolo_model_improve(yolo_model_dir,pdf_loc,page_num,delta=5):
    """
    Improve table detection using YOLO model.This function uses a YOLO model to detect tables in a PDF page. It extracts the page as an image,
    runs the YOLO detection, and processes the results to refine the detected table regions.

    Args:
        yolo_model_dir (str): Directory of the YOLO model.
        pdf_loc (str): Path to the PDF file.
        page_num (int): Page number to process.
        delta (int): Margin for table detection.

    Returns:
        dict: Dictionary of detected tables on the page.
    """ 

    #run detection
    fix_pdf.extract_jpg(pdf_loc,page_num)
    #model_path = "/Users/serafinakamp/Desktop/YOLO_test/TrainYourOwnYOLO/Data/Model_Weights/trained_weights_1915_final.h5"
    #call = "python3 ../../src/table_extraction/detector.py --yolo_model " + model_path

    # Run YOLO detection using the provided model
    call = "python3 ../../src/table_extraction/detector.py --yolo_model " + yolo_model_dir
    os.system(call)

    tables_on_page={}
    num = 0
    #with open("../../src/table_extraction/Detection_results.csv","r") as csvfile:
    with open(os.path.join(work_loc,"Detection_results.csv"),"r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0]=="image":
                continue ##skip header lines
            key = str(num)

            # Extract page dimensions and calculate proposed table region   
            page_width = int(row[8])
            page_height = int(row[9])
            proposed=[max(int(row[2])-delta,0),max(int(row[3])-delta,0),min(int(row[4])+delta,page_width),min(int(row[5])+delta,page_height)]#minX minY maxX maxY
            top_left = (proposed[0],proposed[1])
            bot_right = (proposed[2],proposed[3])

            confidence = float(row[7])

            # Check if the proposed table region overlaps with existing tables
            if key in tables_on_page:
                max_iou = 0
                prop_overlap=[]
                found_ind = 0
                for i,prop in enumerate(tables_on_page[key]):

                    # Calculate IoU between the proposed table and existing table
                    iou = calc_IoU(prop[0],proposed)
                    if iou>max_iou:
                        max_iou = iou
                        prop_overlap = prop[0]
                        found_ind = i

                # If IoU is less than 0.1, add the proposed table as a new entry
                if max_iou < 0.1: #doesn't overlap with already proposed tables
                    tables_on_page[key].append([proposed,confidence])

                # If the proposed table has higher confidence, replace the existing table
                elif prop[1] < confidence: #confidence is higher, so delete previous table
                    tables_on_page[key].append([proposed,confidence])
                    del tables_on_page[key][found_ind]
                    print("new table is more confident")
                else:
                    print("overlap and less confident")
                # If the proposed table is not more confident, do nothing
            else: #add new key
                tables_on_page[key] = [[proposed,confidence]]
            num+=1

    return tables_on_page #return dict containing processed tables for each image

#detecting tables using current cnns
def cnn_detect(model1,model2,i):
    """
    Detect table regions in an image using a two-stage CNN (Convolutional Neural Network) approach.
    This function uses two CNN models to detect table regions in an image. The first model identifies
    potential table regions, and the second model refines the detected regions.

    Args:
        model1 (keras.Model): First CNN model used for detecting table regions.
        model2 (keras.Model): Second CNN model used for refining table regions.
        i (numpy.ndarray): Grayscale image of the PDF page as a NumPy array.

    Returns:
        tuple: A tuple containing two lists:
            - groups (list): List of vertical (y-axis) coordinates for detected table regions.
            - groups2 (list): List of horizontal (x-axis) coordinates for detected table regions.
    """
    X_size = 800 #part1
    Y_size = 64 #part1

    pTwo_size = 600 #part2
    cuts_labels = 60 #part2
    label_precision = 8 #AMOUNT OF PIXELS BETWEEN LABELS, GOES FROM 1/4th to 3/4ths

    y_fail_num = 2
    pixel_data = i
    original_pixel_data_255 = pixel_data.copy()
    pixel_data = cv2.normalize(pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    original_pixel_data = pixel_data.copy()

    height, width = pixel_data.shape
    scale = X_size/width

    pixel_data = cv2.resize(pixel_data, (X_size, int(height*scale))) #X, then Y
    bordered_pixel_data = cv2.copyMakeBorder(pixel_data,top=int(Y_size/4),bottom=int(Y_size/4),left=0,right=0,borderType=cv2.BORDER_CONSTANT,value=1)

    slice_skip_size = int(Y_size/2)
    iter = 0
    slices = []
    while((iter*slice_skip_size + Y_size) < int(height*scale+Y_size/2)):
        s_iter = iter*slice_skip_size
        slices.append(bordered_pixel_data[int(s_iter):int(s_iter+Y_size)])
        iter += 1

    slices = np.array(np.expand_dims(slices,  axis = -1))

    data = model1.predict(slices)

    conc_data = []
    for single_array in data:
        for single_data in single_array:
            conc_data.append(single_data)
    conc_data += [0 for i in range(y_fail_num+1)] #Still needed
    groups = []
    fail = y_fail_num
    group_start = 1 #start at 1 to prevent numbers below zero in groups
    for iter in range(len(conc_data)-1):
        if(conc_data[iter] < .5):
            fail += 1
        else:
            fail = 0

        if(fail >= y_fail_num):
            if(iter - group_start >= 4):
                groups.append((max(int((group_start-1)*label_precision/scale),0), int((iter+1-y_fail_num)*label_precision/scale)))
            group_start = iter


    # Refine the detected table regions using the second model  
    groups2 = []
    for group in groups:
        # check if the group is valid
        if group[0] >= group[1] or group[0] < 0 or group[1] > original_pixel_data.shape[0]:
            print(f"Invalid group range: {group}. Skipping...")
            continue

        # check if the slice is empty
        slice_data = original_pixel_data[group[0]:group[1]]
        if slice_data.size == 0:
            print(f"Warning: Empty slice for group {group}. Skipping resize.")
            continue
        temp_final_original = cv2.resize(original_pixel_data[group[0]:group[1]], (pTwo_size, pTwo_size))
        temp_final = np.expand_dims(np.expand_dims(temp_final_original,  axis = 0), axis = -1)
        data_final = model2.predict(temp_final)

        hor_start = -1
        hor_finish = 10000
        pointless, original_width = original_pixel_data.shape
        # Iterate over the data to find the start and end of the table
        for iter in range(len(data_final[0])):
            if(data_final[0][iter] > .5 and hor_start == -1):
                if(iter > 0):
                    hor_start = int((iter-0.5)*original_width/cuts_labels)
                else:
                    hor_start = int(iter*original_width/cuts_labels)
            # If the current line is above the threshold, update the end of the table   
            if(data_final[0][iter] > .5):
                hor_finish = int((iter+0.5)*original_width/cuts_labels)
        #  Handle edge cases where the table covers the entire image
        if(1 and hor_finish - hor_start > (0.7 * original_width)): #Fix for tables that cover the entire image
            groups2.append((0, original_width))
        else:
            groups2.append((hor_start, hor_finish))


    return groups, groups2 #returns all detected y vals,x vals


def cnn_yolo_combined(pdf_loc,page_num,im,model1,model2,yolo_model_dir,work_loc):
    """
    Combine YOLO and CNN models to detect tables in a PDF page.
    This function integrates YOLO (You Only Look Once) and CNN (Convolutional Neural Network) models
    to detect table regions in a PDF page. It first uses YOLO to detect potential table regions and
    then refines the results using a CNN model. The final output is a list of detected table regions.
    Args:
        pdf_loc (str): Path to the PDF file being processed.
        page_num (int): Page number of the PDF to process.
        im (numpy.ndarray): Grayscale image of the PDF page as a NumPy array.
        model1 (keras.Model): First CNN model used for detecting table regions.
        model2 (keras.Model): Second CNN model used for refining table regions.
        yolo_model_dir (str): Directory path where the YOLO model is stored.
        work_loc (str): Root directory for storing temporary files and intermediate results.

    Returns:
        tuple: A tuple containing two lists:
            - final_splits (list): List of NumPy arrays, each representing a detected table region.
            - coords (list): List of coordinates for each detected table region in the format
              [min_y, min_x, max_y, max_x].
    """
    # Use YOLO to detect table regions in the PDF page
    processed_tables = yolo_model_improve(yolo_model_dir,pdf_loc,page_num,work_loc)
    yolo_tables=[]
    all_y,all_x = cnn_detect(model1,model2,im)
    # Iterate through the table regions detected by YOLO
    num=0
    key=str(num)
    while key in processed_tables:
        yolo_tables.append(processed_tables[key])
        num+=1
        key=str(num)
    height = im.shape[0]
    width = im.shape[1]

    final_tables=[]
    #prune
    for table in yolo_tables:
        maxiou = 0
        cnn_found=[]
        yolo_coords=table[0]
        # Iterate over the detected table regions
        for i in range(len(all_y)):
            cnn_coords = [all_x[i][0],all_y[i][0],all_x[i][1],all_y[i][1]]
            top_left_cnn = (cnn_coords[0],cnn_coords[1])
            bot_right_cnn = (cnn_coords[2],cnn_coords[3])

            top_left_yolo = (yolo_coords[0][0],yolo_coords[0][1])
            bot_right_yolo = (yolo_coords[0][2],yolo_coords[0][3])

            # Calculate IoU between the CNN-detected table and the YOLO-detected table
            iou = calc_IoU(cnn_coords,yolo_coords[0])
            if iou > maxiou:
                maxiou = iou
                cnn_found=cnn_coords

        # If IoU is greater than or equal to 0.10, use the CNN-detected table   
        if maxiou >=0.10:
            final_min_x = min(cnn_found[0],yolo_coords[0][0])
            final_min_y = min(cnn_found[1],yolo_coords[0][1])
            final_max_x = max(cnn_found[2],yolo_coords[0][2])
            final_max_y = max(cnn_found[3],yolo_coords[0][3])
        # Add the merged region to the final results
            final_tables.append([final_min_x,final_min_y,final_max_x,final_max_y])
        else:#prefer yolo if no overlap
            final_tables.append(yolo_coords[0])
    #if no yolo tables take all cnn tables
    if len(yolo_tables) == 0:
        for i in range(len(all_y)):
            cnn_coords = [all_x[i][0],all_y[i][0],all_x[i][1],all_y[i][1]]
            final_tables.append(cnn_coords)
     # Extract the images and coordinates of the final detected table regions
    final_splits = []
    coords = []
    for table in final_tables:
        final_split = im[table[1]:table[3],table[0]:table[2]]
        coords.append([table[1],table[0],table[3],table[2]])
        cv2.imshow("im",final_split)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        final_splits.append(final_split)
    return final_splits,coords



def table_identifier(pixel_data, root, identify_model, identify_model2):
    """
    Identify table regions in an image using a two-stage CNN approach.
    This function uses two CNN models to identify table regions in an image. The first model detects
    potential table regions, and the second model refines the detected regions. The final output is
    a list of detected table regions and their coordinates.

    Args:
        pixel_data (numpy.ndarray): Grayscale image of the PDF page.
        root (str): Root directory for storing temporary files.
        identify_model (keras.Model): First model for identifying table regions.
        identify_model2 (keras.Model): Second model for refining table regions.

    Returns:
        tuple: Tuple containing two lists of detected table regions.
    """
     # Record the start time for performance measurement     
    start_time = time.time()
    pTwo_size = 600
    X_size = 800
    Y_size = 64
    cuts_labels = 60
    label_precision = 8
    y_fail_num = 2

    # Normalize the input image to the range [0, 1]
    original_pixel_data_255 = pixel_data.copy()
    pixel_data = cv2.normalize(pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    original_pixel_data = pixel_data.copy()

    height, width = pixel_data.shape
    scale = X_size/width

    # Resize the pixel data to the desired size
    pixel_data = cv2.resize(pixel_data, (X_size, int(height*scale))) #X, then Y
    bordered_pixel_data = cv2.copyMakeBorder(pixel_data,top=int(Y_size/4),bottom=int(Y_size/4),left=0,right=0,borderType=cv2.BORDER_CONSTANT,value=1)

    # Create slices of the pixel data for processing
    slice_skip_size = int(Y_size/2)
    iter = 0
    slices = []
    while((iter*slice_skip_size + Y_size) < int(height*scale+Y_size/2)):
        s_iter = iter*slice_skip_size
        slices.append(bordered_pixel_data[int(s_iter):int(s_iter+Y_size)])
        iter += 1
    # Prepare the slices for input to identify_model
    slices = np.array(np.expand_dims(slices,  axis = -1))
    data = identify_model.predict(slices)

    # Concatenate the data from the slices
    conc_data = []
    for single_array in data:
        for single_data in single_array:
            conc_data.append(single_data)
        conc_data += [0 for i in range(y_fail_num+1)] #Still needed

    # Group the data to find the table regions
    groups = []
    fail = y_fail_num
    group_start = 1 #start at 1 to prevent numbers below zero in groups
    for iter in range(len(conc_data)-1):
        # Check if the current data point is below the threshold
        if(conc_data[iter] < .5):
            fail += 1
        else:
            fail = 0
        # If the number of consecutive failures exceeds the threshold, finalize the group
        if(fail >= y_fail_num):
            if(iter - group_start >= 4):
                groups.append((int((group_start-1)*label_precision/scale), int((iter+1-y_fail_num)*label_precision/scale)))
            group_start = iter


    # Refine the detected table regions using the second model
    groups2 = []
    for group in groups:
        temp_final_original = cv2.resize(original_pixel_data[group[0]:group[1]], (pTwo_size, pTwo_size))
        temp_final = np.expand_dims(np.expand_dims(temp_final_original,  axis = 0), axis = -1)
        data_final = identify_model2.predict(temp_final)

        # Find the start and end of the table region    
        hor_start = -1
        hor_finish = 10000
        pointless, original_width = original_pixel_data.shape

        for iter in range(len(data_final[0])):
            
            if(data_final[0][iter] > .5 and hor_start == -1):
                if(iter > 0):
                    hor_start = int((iter-0.5)*original_width/cuts_labels)
                else:
                    hor_start = int(iter*original_width/cuts_labels)

            if(data_final[0][iter] > .5):
                hor_finish = int((iter+0.5)*original_width/cuts_labels)

        if(0 and hor_finish - hor_start > (0.7 * original_width)): #Fix for tables that cover the entire image
            groups2.append((0, original_width))
        else:
            groups2.append((hor_start, hor_finish))

    # Extract the final table regions
    final_splits = []
    coords = []
    for iter in range(len(groups)):
        final_split = original_pixel_data_255[groups[iter][0]:groups[iter][1], groups2[iter][0]:groups2[iter][1]]
        coords.append([groups[iter][0],groups2[iter][0],groups[iter][1],groups2[iter][1]])
        final_splits.append(final_split)
        if(0):
            cv2.imshow('image', final_split)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    print("--- %s seconds identify tables ---" % (time.time() - start_time))
    #time.sleep(1)
    return final_splits,coords

def mean_finder_subroutine(real, infered, infered_quality, precision, group_start, n, final_dist): #TODO BROKEN FIX
    """
     Helper function to calculate the mean position of inferred lines within a group.

    Args:
        real (list): List of real line positions.
        infered (list): List of inferred line positions.
        infered_quality (list): List of quality scores for the inferred lines.
        precision (float): Precision for line detection.
        group_start (int): Starting index of the group.
        n (int): Ending index of the group.
        final_dist (list): List to store the final line positions.

    Returns:
        None: The function modifies `final_dist` in place.
    """ 
     # Check if any real line is within the precision range of the inferred group
    bool_add = True
    for a in real:
        if(a > (infered[group_start] - precision)  and a < (infered[n] + precision)): #a real line is within y units of the group
            bool_add = False
    if(bool_add):
        # Calculate the search size
        search_size = 2
        if((infered[n] - infered[group_start]) > (1+(2*search_size))): #moving average of quality score
            size_of_group = infered[n] - infered[group_start] + 1
            max_value = 0
            average_array = [0 for i in range(search_size)]
            for iter in range(search_size, size_of_group - search_size): #find max value and get a moving average array
                temp_value = 0
                for sub_iter in range(iter-search_size, iter+search_size+1):
                    temp_value += infered_quality[sub_iter + infered[group_start]]
                average_array.append(temp_value)
                if(temp_value > max_value):
                    max_value = temp_value
        # Determine the threshold for selecting the mean position
            threshold = (max_value * .99)
            first_value = -1
            for iter in range(len(average_array)):
                if(first_value == -1 and average_array[iter] > threshold):
                    first_value = iter
                if(average_array[iter] > threshold):
                    last_value = iter
            line_loc = int((first_value+last_value)/2 + infered[group_start])
        else:   
            # If no significant peak is found, use the average of the group
            line_loc = int((infered[n] + infered[group_start])/2)
        # Add the calculated line location to the final list
        final_dist.append(line_loc)
    return

def mean_finder(real, infered, infered_quality_raw, precision, max_dim_1d):
    """
     Calculate the final distribution of line positions by combining real and inferred lines.
    Args:
        real (list): List of real line positions.
        infered (list): List of inferred line positions.
        infered_quality_raw (list): List of quality scores for the inferred lines.
        precision (float): Precision for line detection.
        max_dim_1d (int): Maximum dimension of the 1D array.

    Returns:
        list: Final list of line positions after merging real and inferred lines.
    """ 
    infered_quality = [0 for i in range(max_dim_1d)]
    for i in range(len(infered)):
        infered_quality[infered[i]] = infered_quality_raw[i]
    n = 0
    group_start = 0
    final_dist = []
    while((n+1) < len(infered)):
         # If the distance between consecutive inferred lines is greater than the precision,
        # finalize the current group and start a new group
        if (infered[n+1] > (infered[n]+precision)): #the distance needs to be within x units to be apart of the group
            mean_finder_subroutine(real, infered, infered_quality, precision, group_start, n, final_dist)
            group_start = n+1
        n += 1
        # Finalize the last group of inferred lines
    mean_finder_subroutine(real, infered, infered_quality, precision, group_start, n, final_dist) #Final Dump
    final_dist += real
    final_dist.sort()
    return final_dist

def num_of_groups(infered, i):
    """
    Count the number of groups in the inferred line positions.

    Args:
        infered (list): List of inferred line positions.
        i (int): Minimum distance between consecutive lines.

    Returns:
        int: Number of groups in the inferred line positions.
    """
    groups = 0
    if(len(infered) > 0):
        groups = 1
    for a in range(len(infered)-1):
        if(infered[a+1] > infered[a]+i):
            groups += 1
    return groups

def horizontal_line_finder(height, width, pixel_data): #normal finds black lines
    """
    Find horizontal lines in the pixel data.

    Args:
        height (int): Height of the image.
        width (int): Width of the image.
        pixel_data (numpy.ndarray): Grayscale image of the PDF page.

    Returns:
        list: List of y-coordinates where horizontal lines are detected.
    """ 
    final_out = []  
    search_dist = 3
    for y in range(search_dist, height-search_dist):
        short_line = 0
        line_dist = 0
        fails = 0
        for x in range(width):
            top = 0
            bot = 0
            for y2 in range(y-search_dist,y-1):
                top += pixel_data[y2,x]/(search_dist-1)

            for y2 in range(y+2,y+search_dist+1):
                bot += pixel_data[y2,x]/(search_dist-1)

            if((top/2+bot/2 - pixel_data[y,x]) > 30): #these are 8 bit ints need to calculate like this to avoid overflow
                line_dist += 1
                if(fails > 0):
                    fails -= 1
            elif(fails < 1): #tolerate x fails
                fails += width/8
            else:
                if(line_dist > width/16):
                    short_line += 1
                line_dist = 0

            if(line_dist > width/8 or short_line >= 4):
                final_out.append(y)
                break
    return final_out

def vertical_line_finder(height, width, pixel_data, hor_margin_lines): #normal finds black lines
    """
    Detect vertical lines in an image based on pixel intensity differences.
    It identifies lines where there is a significant contrast between the
    pixels to the left and right of the line. It also skips rows that are part of horizontal
    margin lines to avoid false detections.

    Args:
        height (int): Height of the image.
        width (int): Width of the image.
        pixel_data (numpy.ndarray): Grayscale image data as a 2D NumPy array.
        hor_margin_lines (list): List of y-coordinates representing horizontal margin lines.

    Returns:
        list: A list of x-coordinates where vertical lines are detected.
    """
    final_out = []
    search_dist = 3
    for x in range(search_dist, width-search_dist):
        line_dist = 0
        fails = 0
        for y in range(height):
            if(y not in hor_margin_lines):
                # Calculate the maximum intensity of pixels to the left of the current column
                max_left = 0
                max_right = 0
                for x2 in range(x-search_dist,x):
                    if((pixel_data[y,x2]) > max_left):
                        max_left = pixel_data[y,x2]
                # Calculate the maximum intensity of pixels to the right of the current column
                for x2 in range(x+1,x+search_dist+1):
                    if((pixel_data[y,x2]) > max_right):
                        max_right = pixel_data[y,x2]
                # Check if the current pixel is part of a vertical line
                if((max_left/2+max_right/2 - pixel_data[y,x]) > 30): #these are 8 bit ints need to calculate like this to avoid overflow
                    line_dist += 1
                    if(fails > 0):
                        fails -= 1
                elif(fails < 1): #tolerate x fails
                    fails += height/8
                else:
                    line_dist = 0
                # If a line segment is long enough, add the column to the list of detected lines
                if(line_dist > height/8):
                    final_out.append(x)
                    break
    return final_out

def real_line_margins(lines, margin_size_pixels):
    """
    Find the margins of the real lines. The margin lines
    are used to avoid false detections near the actual lines. For each detected line, it adds
    a margin of a specified number of pixels above and below the line.

    Args:
        lines (list): List of line positions.
        margin_size_pixels (int): Size of the margin in pixels.

    Returns:
        list: List of line positions with margins.
    """ 
    margin_lines = []
    for line in lines:
         # Add margin lines around the detected line
        for i in range(line-margin_size_pixels, line+margin_size_pixels):
              # Ensure the margin line is within the bounds of the image and not already in the list
            if(i not in margin_lines and i >= lines[0] and i <= lines[-1]):
                margin_lines.append(i)
    return margin_lines

def inferred_horizontal_line_finder(height, width, pixel_data, required_dist, ver_margin_lines): #finds white lines
    """
    Detect horizontal lines in an image based on pixel intensity differences.
    It identifies lines where there is a significant contrast between the
    pixels above and below the line.

    Args:
        height (int): Height of the image.
        width (int): Width of the image.
        pixel_data (numpy.ndarray): Grayscale image data as a 2D NumPy array.

    Returns:
        list: A list of y-coordinates where horizontal lines are detected.
    """
    past_array_depth = int(width/100)
    required_distance = (width) * required_dist

    inferred_line_dists = []
    inferred_quality = []
    inferred_line_thickness = 0
    # Iterate over each row of the image
    for y in range(height):
        inferred_line_dist = 0
        inferred_line_dist_max = 0
        # Initialize an array to store the past values of the pixel data    
        past_array = [0 for i in range(past_array_depth)] #### Together these find the amount of black values in the last y squares
        black_encountered = 0 ##################

        for x in range(width):
            inferred_line_dist += 1

            if(x not in ver_margin_lines): #skip over verticle lines
                if(pixel_data[y,x] < 200): #current is black
                    if(past_array[x%past_array_depth] == 0):  #past is white
                        black_encountered += 1
                    past_array[x%past_array_depth] = 1
                else: #current is white
                    if(past_array[x%past_array_depth] == 1): #past is black
                        black_encountered -= 1
                    past_array[x%past_array_depth] = 0
                # Check if the black encountered count exceeds the threshold
                if(black_encountered >= (past_array_depth/4)): #if 1/20th is black, stop this line
                    inferred_line_dist = 0
                    #pixel_data[width,height] = (0,255,0) #Line ended DEBUG
            # Update the maximum inferred line distance
            if(inferred_line_dist > inferred_line_dist_max):
                    inferred_line_dist_max = inferred_line_dist
        # Check if the inferred line distance exceeds the required distance
        if(inferred_line_dist_max > required_distance): #a ratio of the outer verticle lines
            inferred_line_thickness += 1
        else:
            inferred_line_thickness = 0
        # If the inferred line thickness is at least 1, add the line to the list
        if(inferred_line_thickness >=  1):
            inferred_line_dists.append(y)
            inferred_quality.append(inferred_line_dist_max/width)

    return inferred_line_dists, inferred_quality

def inferred_vertical_line_finder(height, width, pixel_data, required_dist, required_thick, hor_margin_lines):
    """
    Detect vertical lines in an image based on pixel intensity differences.
    It identifies lines where there is a significant contrast between the
    pixels to the left and right of the line.

    Args:
        height (int): Height of the image.
        width (int): Width of the image.
        pixel_data (numpy.ndarray): Grayscale image data as a 2D NumPy array.

    Returns:
        list: A list of x-coordinates where vertical lines are detected.
    """
    infer_line_dists = []
    inferred_quality = []
    past_array_depth = int(height/100)
    if(past_array_depth == 0):
        past_array_depth = 1
    inferred_line_thickness = 0

    lenth_req = height * required_dist

    for x in range(width):
        inferred_line_dist = 0
        inferred_line_dist_max = 0
        past_array = [0 for i in range(past_array_depth)] #### Together these find the amount of black values in the last y squares
        black_encountered = 0 ##################
        for y in range(height):
            inferred_line_dist += 1
            if(y not in hor_margin_lines): #skip over verticle lines
                if(pixel_data[y,x] < 200): #current is black
                    if(past_array[y%past_array_depth] == 0):  #past is white
                        black_encountered += 1
                    past_array[y%past_array_depth] = 1
                else: #current is white
                    if(past_array[y%past_array_depth] == 1): #past is black
                        black_encountered -= 1
                    past_array[y%past_array_depth] = 0

                if(black_encountered >= (past_array_depth/4)): #if 1/4th is black, stop this line
                    inferred_line_dist = 0
                    if(0 and required_dist == .95):
                        pixel_data[y,x] = (0) #Line ended DEBUG

            if(inferred_line_dist > inferred_line_dist_max):
                    inferred_line_dist_max = inferred_line_dist

        if(inferred_line_dist_max > lenth_req): #a ratio of the outer verticle lines
            inferred_line_thickness += 1
        else:
            inferred_line_thickness = 0

        if(inferred_line_thickness >= required_thick):
                infer_line_dists.append(x - int(required_thick/2)) #add the line where it actually is
                inferred_quality.append(inferred_line_dist_max/height)

    return infer_line_dists, inferred_quality

def merging_helper(im_arr): #This is a temporary fix and should not be needed when more training data is available
    """
    Helper function to determine if a merged image contains a table.
    It checks if any of the 100x100 sub-images in the merged image have more than 95% black pixels.

    Args:
        im_arr (list): List of 100x100 sub-images.

    Returns:
        list: A list of binary values indicating if each sub-image contains a table.
    """
    output_array = []
    for image in im_arr:
        for x in range(99,101): #if any has 95% black pixels
            black_count = 0
            for y in range(0,100):
                if(image[y, x] < 100):
                    black_count += 1

            if(black_count > 95):
                break
        if(black_count > 95):
            output_array.append(1)
        else:
            output_array.append(0)

    return output_array

def concatenate(root, pixel_data, ver_lines_final, hor_lines_final, conc_col_model, valid_cells_model):
    """
    Concatenate the detected lines to form a table.
    It normalizes the pixel data, removes duplicate lines, and then checks for table structure
    using the provided models.

    Args:
        root (str): Root directory for storing temporary images.
        pixel_data (numpy.ndarray): Grayscale image data as a 2D NumPy array.
        ver_lines_final (list): List of y-coordinates where vertical lines are detected.
        hor_lines_final (list): List of x-coordinates where horizontal lines are detected.
        conc_col_model (keras.Model): Model for predicting if a column is part of a table.
        valid_cells_model (keras.Model): Model for predicting if a cell contains data.

    Returns:
        tuple: A tuple containing two 2D arrays:
            - contains_data (numpy.ndarray): Array indicating if each cell contains data.
            - conc_col_2D (numpy.ndarray): Array indicating if each column is part of a table.
    """ 
    # Normalize the pixel data to a range of 0 to 1 
    norm_pixel_data = cv2.normalize(pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    # Remove duplicate vertical lines
    ver_lines_no_dup = []
    # Remove duplicate horizontal lines
    hor_lines_no_dup = []

    # Remove duplicate vertical lines   
    start = ver_lines_final[0]
    for i in range(1, len(ver_lines_final)):
        if(ver_lines_final[i] != ver_lines_final[i-1]+1):
            ver_lines_no_dup.append(int((start + ver_lines_final[i-1])/2))
            start = ver_lines_final[i]
    ver_lines_no_dup.append(int((start + ver_lines_final[-1])/2))

    # Remove duplicate horizontal lines 
    start = hor_lines_final[0]
    for i in range(1, len(hor_lines_final)):
         if(hor_lines_final[i] != hor_lines_final[i-1]+1):
            hor_lines_no_dup.append(int((start + hor_lines_final[i-1])/2))
            start = hor_lines_final[i]
    hor_lines_no_dup.append(int((start + hor_lines_final[-1])/2))

    #  Initialize the list to store concatenated images
    im_arr = []
    for y in range(len(hor_lines_no_dup)-1):
        for x in range(len(ver_lines_no_dup)-2):
            # Resize the sub-image to 100x100 pixels
            top_left = cv2.resize(norm_pixel_data[hor_lines_no_dup[y]:hor_lines_no_dup[y+1], ver_lines_no_dup[x]:ver_lines_no_dup[x+1]], (100, 100)) #these steps makes sure the merge line is in the same place
            top_right = cv2.resize(norm_pixel_data[hor_lines_no_dup[y]:hor_lines_no_dup[y+1], ver_lines_no_dup[x+1]:ver_lines_no_dup[x+2]], (100, 100))
            merged_data = cv2.hconcat([top_left,top_right])
            im_arr.append(merged_data)
            if(0):
                temp_data = np.expand_dims(np.array([merged_data]), axis= -1)
                print(conc_col_model.predict(temp_data))
                print("")
                cv2.imshow('image', pixel_data[hor_lines_no_dup[y]:hor_lines_no_dup[y+1], ver_lines_no_dup[x]:ver_lines_no_dup[x+2]])
                cv2.waitKey(0)
                cv2.destroyAllWindows()
    # Calculate the dimensions of the concatenated table
    y_len = len(hor_lines_no_dup)-1
    x_len = len(ver_lines_no_dup)-2
    # If no images were concatenated, assume a default table structure
    if(not im_arr): #this can occur when there are only 2 vertical lines so that nothing can possibly be concatenated
        return np.ones((y_len, 1)), np.zeros((y_len, 1)) #assume not concatenated and every cell has data, 1D array

     # Prepare the concatenated images for input to the CNN models
    im_arr = np.expand_dims(np.array(im_arr), axis= -1)
    helper_output = merging_helper(im_arr)
    pred = conc_col_model.predict(im_arr)
    pred2 = valid_cells_model.predict(im_arr)

    # Initialize the 2D arrays for the concatenated table structure 
    conc_col_2D = np.zeros((y_len, x_len)) #Y then X
    contains_data = np.zeros((y_len, x_len+1))
    # Iterate over each row and column of the concatenated table
    for y in range(y_len):
        for x in range(x_len):
            if(pred[x+y*x_len][0] > .5 and helper_output == 1):
                conc_col_2D[y][x] = 1

            if(pred2[x+y*x_len][0] > .5):
                contains_data[y][x] = 1

            if(pred2[x+y*x_len][1] > .5):
                contains_data[y][x+1] = 1

    return contains_data, conc_col_2D

def horizontal_line_crossover(hor_line, x_s, x_e, pixel_data_unchanged):
    """
    This function checks if a horizontal line crosses over a specified region in the image
    by analyzing the pixel intensity differences. It ensures that the line has a significant
    contrast between the pixels above and below the line.

    Args:
        hor_line (int): y-coordinate of the horizontal line to check.
        x_s (int): Starting x-coordinate of the region.
        x_e (int): Ending x-coordinate of the region.
        pixel_data_unchanged (numpy.ndarray): Grayscale image data as a 2D NumPy array.

    Returns:
        bool: True if the horizontal line crosses over the region, False otherwise.
    """
    # Iterate over a range of y-coordinates around the horizontal line
    for line in range(hor_line-3, hor_line+4, 3): #all have to pass the condition for crossover
        iter = x_s
        white_pixel = 0
        black_pixel = 0

        wbw = 0 #white_black_white
        while(iter < x_e):
            if(pixel_data_unchanged[line, iter] < 127):
                black_pixel += 1
                if(wbw % 2 == 1):
                    wbw += 1
            else:
                white_pixel += 1
                if(wbw % 2 == 0):
                    wbw += 1
            iter += 1
        # Calculate the average pixel intensity for the region
        white_pixel /= ((1 + x_e - x_s))
        black_pixel /= ((1 + x_e - x_s))

        # Check if the line crosses over the specified region   
        if(not(white_pixel > .05 and black_pixel > .02 and wbw >= 3)): #more than 2% of the pixels are black and more than 5% are white// white is larger so it doesnt mess up when the box perimeters are not continuous
            return False
    return True

def lines_with_widths(ver_lines_final, hor_lines_final):
    """
    Convert lists of line positions into lists of line positions with their widths. The width of a line is
    calculated as the number of consecutive pixels that form the line.

    Args:
        ver_lines_final (list): List of x-coordinates representing vertical lines.
        hor_lines_final (list): List of y-coordinates representing horizontal lines.

    Returns:
        tuple: A tuple containing two lists:
            - ver_width_line (list): List of vertical line positions with their widths.
            - hor_width_line (list): List of horizontal line positions with their widths.
    """
    ver_width_line = []
    hor_width_line = []
    # Iterate over each vertical line
    start = ver_lines_final[0]
    for i in range(1, len(ver_lines_final)):
        if(ver_lines_final[i] != ver_lines_final[i-1]+1):
            ver_width_line.append([start, ver_lines_final[i-1]-start+1])
            start = ver_lines_final[i]
    ver_width_line.append([start, ver_lines_final[-1]-start+1])
    # Iterate over each horizontal line
    start = hor_lines_final[0]
    for i in range(1, len(hor_lines_final)):
         if(hor_lines_final[i] != hor_lines_final[i-1]+1):
            hor_width_line.append([start, hor_lines_final[i-1]-start+1])
            start = hor_lines_final[i]
    # Add the last horizontal line with its width
    hor_width_line.append([start, hor_lines_final[-1]-start+1])
    return ver_width_line, hor_width_line

def hor_split(x_s, x_e, y_s, y_e, pixel_data_unchanged):
    """
    Determine if a horizontal line should be split into two lines.
    It checks if the line has a significant contrast between the pixels above and below the line.

    Args:
        x_s (int): Starting x-coordinate of the region.
        x_e (int): Ending x-coordinate of the region.
        y_s (int): Starting y-coordinate of the region.
        y_e (int): Ending y-coordinate of the region.
        pixel_data_unchanged (numpy.ndarray): Grayscale image data as a 2D NumPy array.

    Returns:
        tuple: A tuple containing two values:
            - bool: True if the line should be split, False otherwise.
            - int: The y-coordinate where the line should be split.
    """
    white_lines = [1 for i in range(y_s, y_e)]
    for y in range(y_s, y_e):
        black_count = 0
        midpoint = (x_s + x_e)/2
        half_length = (x_e - x_s)/2
        base = (x_s + x_e)/20
        for x in range(x_s, x_e):
            # Calculate the points based on the distance from the midpoint          
            if(x < midpoint): #Values in the center are more valuable
                points = base + (x - x_s)
            else:
                points = base + half_length - (x - midpoint)


            if(pixel_data_unchanged[y, x] < 100):
                black_count += points
        if(black_count > (x_e - x_s)/4):
            white_lines[y-y_s] = 0

    split_loc = 0
    wbw_count = 0
    FF = True
    temp_count = 0
    # Iterate over each pixel in the white_lines array
    for iter_num, iter in enumerate(white_lines):
        if(iter == int(FF)):
            temp_count += 1
        else:
            temp_count = 0
        # Check if the number of consecutive white pixels exceeds a threshold
        if(temp_count > 3 + (y_e - y_s)/30):# Adjust this if its not working properly
            wbw_count += 1
            temp_count = 0
            FF = not FF
            if(wbw_count == 3):
                split_loc = iter_num + y_s

    return (wbw_count >= 4), split_loc

def image_to_text(pixel_data_unchanged, root, contains_data, conc_col_2D, ver_width_line, hor_width_line, scale, ver_lines, hor_lines):
    """
    Convert the image data to text using the detected lines and table structure.
    It scales the lines and converts them to the original image size.

    Args:
        pixel_data_unchanged (numpy.ndarray): Grayscale image data as a 2D NumPy array.
        root (str): Root directory for storing temporary images.
        contains_data (numpy.ndarray): Array indicating if each cell contains data.
        conc_col_2D (numpy.ndarray): Array indicating if each column is part of a table.
        ver_width_line (list): List of vertical line positions with their widths.
        hor_width_line (list): List of horizontal line positions with their widths.
        scale (float): Scaling factor for the image.
        ver_lines (list): List of y-coordinates where vertical lines are detected.
        hor_lines (list): List of x-coordinates where horizontal lines are detected.

    Returns:
        list: A list of strings representing the text in each cell.
    """ 
    # Scale the lines to the original image size
    ver_scaled = []
    hor_scaled = []
    real_ver_lines = []
    real_hor_lines = []
    # Scale the vertical lines
    for i in ver_width_line:
        ver_scaled.append([int(i[0]*scale), int(i[1]*scale)+1])
    # Scale the horizontal lines    
    for i in hor_width_line:
        hor_scaled.append([int(i[0]*scale), int(i[1]*scale)+1])

    # Scale the real vertical lines
    for i in ver_lines:
        real_ver_lines.append(int(i * scale))

    # Scale the real horizontal lines
    for i in hor_lines:
        real_hor_lines.append(int(i * scale))

    # debug
    if(0):
        height, width = pixel_data_unchanged.shape
        #print(height)
        for ver_line in ver_scaled:
            #print(ver_line)
            cv2.line(pixel_data_unchanged, (ver_line[0],0), (ver_line[0], height), (0,255,0), 4)
        for hor_line in hor_scaled:
            cv2.line(pixel_data_unchanged, (0, hor_line[0]), (width, hor_line[0]), (0,255,0), 4)

        cv2.imshow("line", pixel_data_unchanged)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        #print(height)
        for ver_line in real_ver_lines:
            #print(ver_line)
            cv2.line(pixel_data_unchanged, (ver_line,0), (ver_line, height), (0,255,0), 4)
        for hor_line in real_hor_lines:
            cv2.line(pixel_data_unchanged, (0, hor_line), (width, hor_line), (0,255,0), 4)

        cv2.imshow("line", pixel_data_unchanged)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        y = 0
        x = 0
        while(y < (len(hor_scaled)-1)):
            while(x < len(ver_scaled)-1):
                if(contains_data[y][x]):
                    cv2.line(pixel_data_unchanged, (ver_scaled[x][0],hor_scaled[y][0]), (ver_scaled[x][0],hor_scaled[y][0]), (0, 255, 0), 3)
                x += 1
            y += 1
        cv2.imshow("line", pixel_data_unchanged)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    # Initialize the data array to store extracted text
    data_array = [[["" for k in range(2)] for i in range(len(contains_data[0]))] for j in range(len(contains_data))]

    y = 0
    y_SPLIT_extend = 0
    # Iterate over each row of the table    
    while(y < (len(hor_scaled)-1)):
        x = 0
        split_holder = []
        ANY_SPLIT = False
        while(x < len(ver_scaled)-1):
            loc = os.path.join(TempImages_dir, "i" + str(y) +"_" + str(x) + ".jpg")
            data_exists = contains_data[y][x]
            temp_x = x
            while(temp_x < len(ver_scaled)-2 and conc_col_2D[y][temp_x]):
                temp_x += 1
                data_exists = data_exists or contains_data[y][temp_x] #atleast one cell has data in the merged data
            # Check if the current row can be merged with the previous row
            y_merge = False #can only merge 1 line
            if(y < len(hor_scaled)-1 and y > 0): #LOOK TO THE PAST
               y_merge = horizontal_line_crossover(hor_scaled[y][0]+int(hor_scaled[y][1]/2), ver_scaled[x][0]+ver_scaled[x][1], ver_scaled[temp_x+1][0], pixel_data_unchanged)
            # Calculate the start and end coordinates for the current cell
            x_s = ver_scaled[x][0]+ver_scaled[x][1]+1
            x_e = ver_scaled[temp_x+1][0]
            y_s = hor_scaled[y-y_merge][0]+hor_scaled[y-y_merge][1]+1
            y_e = hor_scaled[y+1][0]

            # mark the line before split
            if(0):
                cv2.line(pixel_data_unchanged, (x_s, y_s), (x_s, y_e), (0,255,0), 2)
                cv2.line(pixel_data_unchanged, (x_e, y_s), (x_e, y_e), (0,255,0), 2)
                cv2.line(pixel_data_unchanged, (x_s, y_s), (x_e, y_s), (0,255,0), 2)
                cv2.line(pixel_data_unchanged, (x_s, y_e), (x_e, y_e), (0,255,0), 2)

            SPLIT, split_loc = hor_split(x_s, x_e, y_s, y_e, pixel_data_unchanged) # ==========

            if(SPLIT):
                ANY_SPLIT = True
                slice = [pixel_data_unchanged[y_s:split_loc, x_s:x_e], [x_s, x_e, y_s, split_loc]]
                w, h = slice[0].shape
                slice2 = [pixel_data_unchanged[split_loc:y_e, x_s:x_e],[x_s, x_e, split_loc, y_e]]
                loc2 = os.path.join(TempImages_dir, "i_B" + str(y) +"_" + str(x) + ".jpg")
                cv2.imwrite(loc2,slice2[0])
                #p_img = Image.fromarray(slice2)
                #split_holder.append(pytesseract.image_to_string(loc2, config='--psm 7'))
                split_holder.append([pytesseract.image_to_string(loc2, config='--psm 7'), slice2[1]]) # for future merge
                #split_holder.append(pytesseract.image_to_string(p_img, config='--psm 7'))
            else:
                slice = [pixel_data_unchanged[y_s:y_e, x_s:x_e],[x_s, x_e, y_s, y_e]]
                w, h = slice[0].shape
                if(data_exists and w > 0 and h > 0):
                    split_holder.append(["^ EXTEND", [-1, -1, -1, -1]])
                else:
                    split_holder.append(["", [0, 0, 0, 0]])

            if(data_exists and w > 0 and h > 0):
                cv2.imwrite(loc,slice[0])
                data_array[y-y_merge+y_SPLIT_extend][x][0] = pytesseract.image_to_string(loc, config='--psm 7')
                data_array[y-y_merge+y_SPLIT_extend][x][1] = slice[1]
                #p_img = Image.fromarray(slice)
                #data_array[y-y_merge+y_SPLIT_extend][x] = pytesseract.image_to_string(loc, config='--psm 7')
                #data_array[y-y_merge+y_SPLIT_extend][x] = pytesseract.image_to_string(p_img, config='--psm 7')

            # Handle extended cells
            if(y_merge):
                data_array[y+y_SPLIT_extend][x][0] = "^ EXTEND"
                data_array[y+y_SPLIT_extend][x][1] = [-1, -1, -1, -1]
            # Handle extended cells
            while(x < temp_x):
                split_holder.append(["^ EXTEND", [-1, -1, -1, -1]])
                data_array[y-y_merge+y_SPLIT_extend][x+1][0] = "< EXTEND"
                data_array[y-y_merge+y_SPLIT_extend][x+1][1] = [-1, -1, -1, -1]
                if(y_merge):
                    data_array[y+y_SPLIT_extend][x+1][0] = "^ EXTEND"
                    data_array[y+y_SPLIT_extend][x+1][1] = [-1, -1, -1, -1]
                x += 1
            x += 1
        y += 1
        if(ANY_SPLIT):
            data_array.insert(y+y_SPLIT_extend, split_holder)
            y_SPLIT_extend += 1
    ####ARRAY CLEANUP

    cleaned_data_array = []
    if(len(data_array) > 0):
        row_valid = [False for y in range(len(data_array))]
        col_valid = [False for x in range(len(data_array[0]))]

        # Mark valid rows and columns   
        for y in range(len(data_array)):
            for x in range(len(data_array[0])):
                if(data_array[y][x][0] != "" and data_array[y][x][0] != "< EXTEND" and data_array[y][x][0] != "^ EXTEND"):
                    col_valid[x] = True
                    row_valid[y] = True

        for y in range(len(data_array)):
            if(row_valid[y]):
                temp_array = []
                for x in range(len(data_array[0])):
                    if(col_valid[x]):
                        temp_array.append(data_array[y][x])
                cleaned_data_array.append(temp_array)
    ### merge multiple rows ###
    height, width = pixel_data_unchanged.shape
    final_merge = []

    if(not real_hor_lines):
        for row in cleaned_data_array:
            temp_row = []
            for cell_cor in row:
                temp_row.append(cell_cor[0])
            final_merge.append(temp_row)
        return final_merge

    real_intervals = []
    interval_it = 0
    real_intervals.append([0, real_hor_lines[0]])
    while(interval_it < (len(real_hor_lines) - 1)):
        real_intervals.append([real_hor_lines[interval_it], real_hor_lines[interval_it + 1]])
        interval_it += 1
    real_intervals.append([real_hor_lines[interval_it], height])

    # Initialize the row_intervals array to store the rows and their corresponding intervals    
    row_intervals = []
    for row in cleaned_data_array:
        temp_row = []
        hor_top = 0
        hor_bot = 0
        for cell_cor in row:
            if(cell_cor[0]):
                hor_top = cell_cor[1][2]
                hor_bot = cell_cor[1][3]
            temp_row.append(cell_cor[0])
        real_it = 0;
        row_num = -1;
        while(real_it < len(real_intervals)):
            if(hor_top >= real_intervals[real_it][0] and hor_bot <= real_intervals[real_it][1]):
                row_num = real_it
                break
            real_it += 1
        row_intervals.append([temp_row, [hor_top, hor_bot], row_num])
    # Merge rows within the same interval
    row_it = 0
    while(row_it < len(row_intervals)):
        cell_num = len(row_intervals[row_it][0])
        row_num = row_intervals[row_it][2]
        temp_merge = row_intervals[row_it][0]
        temp_it = row_it + 1
        CHANGE = False
        while(temp_it < len(row_intervals) and row_intervals[temp_it][2] == row_num):
            MERGE = False
            for i in range(cell_num):
                if(not row_intervals[temp_it][0][i]):
                    MERGE = True
                    break
            if(MERGE):
                for i in range(cell_num):
                    temp_merge[i] = temp_merge[i] + ' ' + row_intervals[temp_it][0][i]
                    CHANGE = True
            temp_it += 1
        final_merge.append(temp_merge)
        if(CHANGE):
            row_it = temp_it
        else:
            row_it += 1

    return final_merge

def debug(root, height, width, pixel_data, hor_lines, ver_lines, hor_lines_final, ver_lines_final, inferred_hor_lines, inferred_ver_lines, guarenteed_inf_vers, conc_col_2D, ver_width_line, hor_width_line):
    pixel_data = cv2.cvtColor(pixel_data,cv2.COLOR_GRAY2RGB)

    if(0): #infered ver
        for inferred_ver_line in inferred_ver_lines:
            cv2.line(pixel_data, (inferred_ver_line, 0), (inferred_ver_line, height), (0,255,255), 1)

    if(0): #infer_hor
        for inferred_hor_line in inferred_hor_lines:
            cv2.line(pixel_data, (0, inferred_hor_line), (width, inferred_hor_line), (0,255,255), 1)

    if(1): #final
        for hor_line in hor_lines_final:
            cv2.line(pixel_data, (0, hor_line), (width, hor_line), (0,255,0), 1)

        for ver_line in ver_lines_final:
            cv2.line(pixel_data, (ver_line, 0), (ver_line, height), (0,255,0), 1)

    if(1): #real
        for hor_line in hor_lines:
            cv2.line(pixel_data, (0, hor_line), (width, hor_line), (255,0,0), 1)

        for ver_line in ver_lines:
            cv2.line(pixel_data, (ver_line, 0), (ver_line, height), (255,0,0), 1)

    if(1): #conc fix
        for row_num, row in enumerate(conc_col_2D):
            for line_num, line in enumerate(row):
                if(line):
                    cv2.line(pixel_data, (ver_width_line[line_num+1][0], hor_width_line[row_num][0]), (ver_width_line[line_num+1][0], hor_width_line[row_num+1][0]), (255,255,255), 1)

    if(0): #write debug image
        cv2.imwrite(os.path.join(root, "DEBUG_IMAGE.png"), pixel_data)

    cv2.imshow('image',pixel_data)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Image handling function
def image_handle(image):
    import cv2
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


    #def multiprocessing_unit(image_num, image, root, identify_model, identify_model2, conc_col_model, valid_cells_model):
def multiprocessing_unit_separate_tables_reg(pdf_loc,page_num, image, root,identify_model,identify_model2):
    #load_model now in seperating processes

    #page_num = image_num + start
    print("\n\nStarting page: ", page_num)

    temp_pixel_data,coords = table_identifier(image, root, identify_model, identify_model2)
    #print(coords)
    return temp_pixel_data

# YOLO-based table extraction
def multiprocessing_unit_separate_tables_yolo(pdf_loc,page_num, image, root,identify_model,identify_model2,yolo_model_dir,work_loc):
    #load_model now in seperating processes

    #page_num = image_num + start
    print("\n\nStarting page: ", page_num)

    temp_pixel_data,coords = cnn_yolo_combined(pdf_loc,page_num,image,identify_model,identify_model2,yolo_model_dir,work_loc)
    #print(coords)
    return temp_pixel_data

# Cell identification   
def multiprocessing_unit_identify_cells(pixel_data, root):
    """
    This function identifies table cells in an image by using two CNN models. The first model
    detects potential table regions, and the second model refines the detected regions. The
    final output is a list of detected table cells and their coordinates.

    Args:
        pixel_data (numpy.ndarray): Grayscale image data as a 2D NumPy array.
        root (str): Root directory for storing temporary files and intermediate results.

    Returns:
        list: A list of detected table cells, each represented as a list of text and coordinates.
    """
    #print("entered_cells")
    # Load the models
    conc_col_model = load_model(os.path.join(root,"conc_col.h5"))
    valid_cells_model = load_model(os.path.join(root, "valid_cells.h5"))
    # Initialize the final data per table
    final_data_per_table = []
    # Copy the pixel data to avoid modifying the original image
    pixel_data_unchanged = np.copy(pixel_data)
    # Get the height and width of the image
    height, width = pixel_data.shape
    # Calculate the scaling factor
    scale = width/800
    # Resize the image to 800 width, variable height
    pixel_data = cv2.resize(pixel_data,(800, int(height/scale)))  #800 width, variable height
    # Get the new height and width of the resized image
    height, width = pixel_data.shape

    hor_lines = horizontal_line_finder(height, width, pixel_data) #cannot use margin_lines, but it is fine table cells are usally wider than they are tall
    hor_margin_lines = real_line_margins(hor_lines, 5)
    # Detect vertical lines in the image, skipping rows that are part of horizontal margin lines
    ver_lines = vertical_line_finder(height, width, pixel_data, hor_margin_lines)
    # Calculate the real line margins for the vertical lines
    ver_margin_lines = real_line_margins(ver_lines, 5)

    # Initialize variables for inferred lines and their quality
    required_dist = .95 #TODO find a number that balances speed and accuracy
    prev_groups = -1
    inferred_hor_lines = []
    inferred_hor_quality = []
    while(1): #Horizontal
        inferred_hor_lines_temp, inferred_hor_quality_temp = inferred_horizontal_line_finder(height, width, pixel_data, required_dist, ver_margin_lines) #inferred
        groups = num_of_groups(inferred_hor_lines_temp, 7) # amount of separable groups of inferred lines that exist within the possible inferred lines.
        required_dist += .04 #TODO find a number that balances speed and accuracy
        if(prev_groups > groups or groups == 0):
            break
        prev_groups = groups
        inferred_hor_lines = inferred_hor_lines_temp
        inferred_hor_quality = inferred_hor_quality_temp

    # Detect inferred vertical lines in the image
    required_dist = .65 #TODO find a number that balances speed and accuracy
    prev_groups = -1
    inferred_ver_lines = []
    inferred_ver_quality = []

    while(1): #Vertical
        inferred_ver_lines_temp, inferred_ver_quality_temp = inferred_vertical_line_finder(height, width, pixel_data, required_dist, 8, hor_margin_lines) #inferred
        groups = num_of_groups(inferred_ver_lines_temp, 15)
        required_dist += .03 #TODO find a number that balances speed and accuracy
        if(prev_groups > groups or groups == 0):
            break
        prev_groups = groups
        inferred_ver_lines = inferred_ver_lines_temp
        inferred_ver_quality = inferred_ver_quality_temp

    # Detect guaranteed inferred vertical lines
    guarenteed_inf_ver, guarenteed_ver_quality = inferred_vertical_line_finder(height, width, pixel_data, .98, 8, hor_lines)
    # Calculate the mean of the inferred vertical lines and their quality
    tempv = mean_finder(ver_lines, ([0] + guarenteed_inf_ver  + [width-1]), ([1] + guarenteed_ver_quality + [1]), 10, width) #TODO find a good number
    # Calculate the mean of the inferred vertical lines and their quality       
    ver_lines_final = mean_finder(tempv, inferred_ver_lines, inferred_ver_quality, 15, width) #this is precision not resolution add lines to the left and right //TODO find a good precision
    hor_lines_final = mean_finder(hor_lines, ([0] + inferred_hor_lines + [height-1]), ([1] + inferred_hor_quality + [1]), 7, height) #this is precision not resolution

    conc_col_2D = []
    contains_data, conc_col_2D = concatenate(root, pixel_data, ver_lines_final, hor_lines_final, conc_col_model, valid_cells_model)
    # Calculate the widths of the vertical and horizontal lines
    ver_width_line, hor_width_line = lines_with_widths(ver_lines_final, hor_lines_final)
    # Convert the image to text using the identified cells and their coordinates    
    final_data_per_table = image_to_text(pixel_data_unchanged, root, contains_data, conc_col_2D, ver_width_line, hor_width_line, scale, ver_lines, hor_lines)
    return final_data_per_table



#######################START########################
if __name__ == '__main__':
    # count time
    start_main_time = time.time()
    # Get the directory of the current script   
    pyth_dir = os.path.dirname(__file__)
    # Set the TensorFlow logging level to suppress unnecessary messages
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2'
    # Create an argument parser for command-line arguments
    parser = argparse.ArgumentParser(description='Table Extractor Tool')
    parser.add_argument('--pdf_dir', required=True, help='pdf directory')
    parser.add_argument('--work_dir', required=True, help='main work and output directory')
    parser.add_argument('--first_table_page', required=True, help='The first page that you want table extraction begins with')
    parser.add_argument('--last_table_page', required=True, help='The last page that you want table extraction ends with')
    parser.add_argument('--use_yolo',required=False,help='Use the combined yolo/cnn model to detect tables, default is False',default=False,action="store_true")
    args = parser.parse_args()

    # Set the flag for concatenating and cleaning the table data
    concatenate_clean = True

    # Set the root directory for the table extraction process   
    root = os.path.join(pyth_dir,'Table_extract_robust')
    # Set the PDF location
    pdf_loc = (args.pdf_dir).lower()
    # Set the work directory
    work_loc = args.work_dir
    # Set the start page number
    start = int(args.first_table_page)
    # Set the end page number
    cap = int(args.last_table_page)
    # Set the flag for using YOLO
    yolo = args.use_yolo
    if yolo:
        yolo_model_dir = os.path.join(pyth_dir,'yolo_helpers','keras_yolo3','trained_weights_1915_final.h5')
    pages = convert_from_path(pdf_loc, 300, first_page=start, last_page=cap)
    identify_model = load_model(os.path.join(root, "Identification_Models", "stage1.h5"))
    identify_model2 = load_model(os.path.join(root, "Identification_Models", "stage2.h5"))

    # Create a temporary directory for storing intermediate images
    TempImages_dir = os.path.join(work_loc, "TempImages")
    try:
        os.makedirs(TempImages_dir)
        print("Directory " , TempImages_dir ,  " Created ")
    except FileExistsError:
        print("Directory " , TempImages_dir ,  " already exists")
        print("Cleaning ipxact directory ...")
        if len(os.listdir(TempImages_dir)) != 0:
            for file in os.listdir(TempImages_dir):
                os.remove(os.path.join(TempImages_dir,file))

    # Print a message indicating the start of multiprocessing
    print("Multiprocesses start: \n")
    # Get the number of available CPU cores
    cpu_num = multiprocessing.cpu_count()
    print("CPU NUM",cpu_num)

    images=[]
    for i,image in enumerate(pages):
        images.append(image_handle(image))

    print("done handling images")
    # Create a multiprocessing pool with the number of available CPU cores
    pool1 = Pool(processes= cpu_num)
    # Initialize a list to store the results of the table identification process
    temp_storage = []
    # Iterate over the images and process each one
    for image_num, image in enumerate(images):
        print("Start Idendifying Tables on Page " + str(image_num + start))
        if yolo:
            temp_result = pool1.apply_async(multiprocessing_unit_separate_tables_yolo, args= (pdf_loc, image_num+start, image, root,identify_model,identify_model2,yolo_model_dir,work_loc))
        else:
            temp_result = pool1.apply_async(multiprocessing_unit_separate_tables_reg, args= (pdf_loc, image_num+start, image, root,identify_model,identify_model2))
        temp_storage.append(temp_result)
    pool1.close()
    pool1.join()

    print("\n") 
    # Create a multiprocessing pool with the number of available CPU cores
    pool2 = Pool(processes= cpu_num)
    # Initialize a list to store the results of the table identification process
    all_tables = []
    # Initialize a counter for the number of tables processed
    count = 0
    # Iterate over the results of the table identification process
    for tables in temp_storage:
        count += 1
        print("Start Extracting Content in Table " + str(count))
        for table_pixel in tables.get():
            temp_data_per_table = pool2.apply_async(multiprocessing_unit_identify_cells, args= (table_pixel, root))
            all_tables.append(temp_data_per_table)
    pool2.close()
    pool2.join()

    # Initialize an empty list to store all table data
    array = []
    # Iterate over the results of the table identification process
    for temp in all_tables:
        temp_row = temp.get()
        for cell in temp_row:
            array.append(cell)

    #debug part
    if(0):
        for table in all_tables:
            cv2.imshow('image', table)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    # Concatenate and clean the table data
    if(concatenate_clean):
        cleaned_array = []
        for row in array:
            if(len(row) < 9):
                # Initialize a flag to check if the row contains the "^ EXTEND" keyword
                has_extend = False
                # Iterate over the cells in the row
                for cell in row:
                    if(cell == "^ EXTEND"):
                        has_extend = True

                # If the row contains the "^ EXTEND" keyword, concatenate the row with the last row in the cleaned_array    
                if(has_extend):
                    # Iterate over the cells in the row
                    for cell_num, cell in enumerate(row):
                        # If the cell is not the "^ EXTEND" keyword and the cell number is less than the length of the last row in the cleaned_array, concatenate the cell with the last row in the cleaned_array
                        if(cell != "^ EXTEND" and cell_num < len(cleaned_array[-1])):
                            cleaned_array[-1][cell_num] += (" " + cell)
                else:
                    # If the row does not contain the "^ EXTEND" keyword, append the row to the cleaned_array
                    cleaned_array.append(row)

        # Write the cleaned table data to a CSV file
        with open(os.path.join(work_loc, "concatenate_table.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(cleaned_array)
    # Calculate the total time taken for the table extraction process
    end_main_time = time.time()
    total_time = end_main_time-start_main_time
    minutes = float(total_time)/60
    print("--- %s seconds ---" % total_time)
    print("--- %s minutes ---" % minutes)