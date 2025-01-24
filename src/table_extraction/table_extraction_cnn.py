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
import pytesseract          # for OCR
import statistics           # for statistics
import os                   # for file operations
import csv                  # for csv operations
import cv2                  # for image processing
import concurrent.futures   # for concurrent execution
import functools            # for functional programming
import copy                 # for deep copying
import numpy as np          # for numerical operations
import argparse             # arguement parsing
import tensorflow as tf     # for machine learning
from tensorflow.keras.models import load_model # for loading models

from pdf2image import convert_from_path #poppler needs to be added and added to the path variable


def table_identifier(pixel_data, root, identify_model, identify_model2):
    """
    Identify the table region in the image using two models.

    Args:
        pixel_data (numpy.ndarray): Grayscale image of the PDF page.
        root (str): Root directory for saving temporary files.
        identify_model (keras.Model): Model for identifying table regions (stage 1).
        identify_model2 (keras.Model): Model for refining table regions (stage 2).

    Returns:
        list: Extracted table content as a 2D list.
    """ 
    # Define constants for the table identifier
    pTwo_size = 600
    X_size = 800
    Y_size = 64
    cuts_labels = 60
    label_precision = 8
    y_fail_num = 2

    # Copy the pixel data for later use 
    original_pixel_data_255 = pixel_data.copy()

    # Normalize the pixel data to be between 0 and 1
    pixel_data = cv2.normalize(pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    original_pixel_data = pixel_data.copy()
    # Get the height and width of the pixel data
    height, width = pixel_data.shape
    # Calculate the scale factor for resizing the image
    scale = X_size/width
    pixel_data = cv2.resize(pixel_data, (X_size, int(height*scale))) #X, then Y
    bordered_pixel_data = cv2.copyMakeBorder(pixel_data,top=int(Y_size/4),bottom=int(Y_size/4),left=0,right=0,borderType=cv2.BORDER_CONSTANT,value=1)

    # Image slicing
    slice_skip_size = int(Y_size/2)
    iter = 0
    slices = []
    while((iter*slice_skip_size + Y_size) < int(height*scale+Y_size/2)):
        s_iter = iter*slice_skip_size
        slices.append(bordered_pixel_data[int(s_iter):int(s_iter+Y_size)])
        iter += 1  

    slices = np.array(np.expand_dims(slices,  axis = -1))
    data = identify_model.predict(slices)
    # Concatenate the data
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
                groups.append((int((group_start-1)*label_precision/scale), int((iter+1-y_fail_num)*label_precision/scale)))
            group_start = iter


 
    # With the second model, the left and right boundaries of the table are further determined.
    groups2 = []
    for group in groups:
        temp_final_original = cv2.resize(original_pixel_data[group[0]:group[1]], (pTwo_size, pTwo_size))
        temp_final = np.expand_dims(np.expand_dims(temp_final_original,  axis = 0), axis = -1)
        data_final = identify_model2.predict(temp_final)

        # Initialize the start and finish of the table
        hor_start = -1
        hor_finish = 10000
        pointless, original_width = original_pixel_data.shape

        # Iterate through the data to find the start and finish of the table
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

    final_splits = []
    # Iterate through the groups to get the final splits
    for iter in range(len(groups)):
        final_split = original_pixel_data_255[groups[iter][0]:groups[iter][1], groups2[iter][0]:groups2[iter][1]]
        # Append the final split to the list
        final_splits.append(final_split)
        if(0):
            cv2.imshow('image', final_split)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    return final_splits

# This function is used to find precise line positions during table recognition.
def mean_finder_subroutine(real, infered, infered_quality, precision, group_start, n, final_dist): #TODO BROKEN FIX
    """
    Find precise line positions during table recognition.

    Args:
        real (list): List of real line positions.
        infered (list): List of inferred line positions.
        infered_quality (list): List of quality scores for the inferred lines.
        precision (float): Precision for line detection.
        group_start (int): Starting index of the group.
        n (int): Ending index of the group.
        final_dist (list): List to store the final line positions.

    Returns:
        None
    """ 

    bool_add = True

    for a in real:    
        if(a > (infered[group_start] - precision)  and a < (infered[n] + precision)): #a real line is within y units of the group
            bool_add = False

    # If the real line is within the inferred group, add it to the final distance
    if(bool_add):  
        search_size = 2

        # If the inferred group is larger than the search size, calculate the moving average of the quality score
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

            # Calculate the threshold for the moving average
            threshold = (max_value * .99)
            first_value = -1
            for iter in range(len(average_array)):
                if(first_value == -1 and average_array[iter] > threshold):
                    first_value = iter
                if(average_array[iter] > threshold):
                    last_value = iter
            # Calculate the line location
            line_loc = int((first_value+last_value)/2 + infered[group_start])  
        else:
            # If the inferred group is not larger than the search size, calculate the line location as the average of the inferred group
            line_loc = int((infered[n] + infered[group_start])/2)
        final_dist.append(line_loc)
    return



def mean_finder(real, infered, infered_quality_raw, precision, max_dim_1d):
    """
    Find precise line positions during table recognition.

    Args:
        real (list): List of real line positions.
        infered (list): List of inferred line positions.
        infered_quality_raw (list): List of quality scores for the inferred lines.
        precision (float): Precision for line detection.
        max_dim_1d (int): Maximum dimension of the 1D array.

    Returns:
        list: List of final line positions.
    """
    # Initialize the inferred quality array
    infered_quality = [0 for i in range(max_dim_1d)]
    # Iterate through the inferred lines to populate the inferred quality array
    for i in range(len(infered)):
        infered_quality[infered[i]] = infered_quality_raw[i]
    n = 0
    group_start = 0
    final_dist = []
    # Iterate through the inferred lines to find the groups
    while((n+1) < len(infered)):
        if (infered[n+1] > (infered[n]+precision)): #the distance needs to be within x units to be apart of the group
            mean_finder_subroutine(real, infered, infered_quality, precision, group_start, n, final_dist)
            group_start = n+1
        n += 1
    mean_finder_subroutine(real, infered, infered_quality, precision, group_start, n, final_dist) #Final Dump
    final_dist += real
    final_dist.sort()
    return final_dist




def num_of_groups(infered, i):
    """
    Find the number of groups in the inferred lines.

    Args:
        infered (list): List of inferred line positions.
        i (float): Precision for line detection.

    Returns:
        int: Number of groups in the inferred lines.
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
    Detect horizontal table lines in the image by analyzing pixel values.

    Args:
        height (int): Height of the image.
        width (int): Width of the image.
        pixel_data (numpy.ndarray): Grayscale pixel data of the image.

    Returns:
        list: List of y-coordinates where horizontal table lines are detected.
    """
    final_out = [] 
    search_dist = 3 

    # Iterate through the height to find the horizontal lines
    for y in range(search_dist, height-search_dist):
        short_line = 0
        line_dist = 0
        fails = 0 

        # Iterate through the width to find the horizontal lines
        for x in range(width): 
            top = 0
            bot = 0
            # Iterate through the width to find the horizontal lines
            for y2 in range(y-search_dist,y-1):
                top += pixel_data[y2,x]/(search_dist-1)
            # Iterate through the width to find the horizontal lines
            for y2 in range(y+2,y+search_dist+1):
                bot += pixel_data[y2,x]/(search_dist-1)

            # If the average of the top and bottom is greater than the pixel data, increment the line distance
            if((top/2+bot/2 - pixel_data[y,x]) > 30): #these are 8 bit ints need to calculate like this to avoid overflow
                line_dist += 1
                if(fails > 0):
                    fails -= 1
            # If the fails are less than 1, increment the fails
            elif(fails < 1): #tolerate x fails
                fails += width/8
            else:
                # If the line distance is greater than the width divided by 16, increment the short line counter
                if(line_dist > width/16):
                    short_line += 1
                # Reset the line distance
                line_dist = 0

            # If the line distance is greater than the width divided by 8 or the short line counter is greater than 4, append the y value to the final output and break
            if(line_dist > width/8 or short_line >= 4):
                final_out.append(y)  
                break
    return final_out


def vertical_line_finder(height, width, pixel_data, hor_margin_lines): #normal finds black lines
    """
    Detect vertical table lines in the image by analyzing pixel values.

    Args:
        height (int): Height of the image.
        width (int): Width of the image.
        pixel_data (numpy.ndarray): Grayscale pixel data of the image.
        hor_margin_lines (list): List of y-coordinates where horizontal margin lines are detected.

    Returns:
        list: List of x-coordinates where vertical table lines are detected.
    """
    final_out = [] 
    search_dist = 3

    # Iterate through the width to find the vertical lines
    for x in range(search_dist, width-search_dist):
        line_dist = 0
        fails = 0

        # Iterate through the height to find the vertical lines
        for y in range(height):
            if(y not in hor_margin_lines):
                max_left = 0
                max_right = 0
                # Iterate through the width to find the vertical lines
                for x2 in range(x-search_dist,x):
                    if((pixel_data[y,x2]) > max_left):
                        max_left = pixel_data[y,x2]

                # Iterate through the width to find the vertical lines
                for x2 in range(x+1,x+search_dist+1):
                    if((pixel_data[y,x2]) > max_right):
                        max_right = pixel_data[y,x2]

                # If the average of the max left and max right is greater than the pixel data, increment the line distance
                if((max_left/2+max_right/2 - pixel_data[y,x]) > 30): #these are 8 bit ints need to calculate like this to avoid overflow
                    line_dist += 1
                    if(fails > 0):
                        fails -= 1
                # If the fails are less than 1, increment the fails
                elif(fails < 1): #tolerate x fails
                    fails += height/8
                else:
                    # Reset the line distance
                    line_dist = 0 

                # If the line distance is greater than the height divided by 8, append the x value to the final output and break
                if(line_dist > height/8):
                    final_out.append(x)  
                    break      
    return final_out


def real_line_margins(lines, margin_size_pixels):
    """
    Calculate the margin range around detected table lines to avoid duplicate detection.

    Args:
        lines (list): List of detected table line positions.
        margin_size_pixels (int): Size of the margin range around each table line (in pixels).

    Returns:
        list: List of pixel positions within the margin range of the detected table lines.
    """
    margin_lines = []
    for line in lines:
        for i in range(line-margin_size_pixels, line+margin_size_pixels):
            # If the line is not already in the margin lines and is within the range of the lines, add it to the margin lines
            if(i not in margin_lines and i >= lines[0] and i <= lines[-1]):
                margin_lines.append(i)
    return margin_lines



def inferred_horizontal_line_finder(height, width, pixel_data, required_dist, ver_margin_lines): #finds white lines
    """
    Infer horizontal table lines in the image by analyzing pixel values.

    Args:
        height (int): Height of the image.
        width (int): Width of the image.
        pixel_data (numpy.ndarray): Grayscale pixel data of the image.
        required_dist (float): Minimum length ratio for a line to be considered a table line.
        ver_margin_lines (list): List of vertical margin lines to skip during detection.

    Returns:
        tuple: A tuple containing two lists:
            - inferred_line_dists: List of y-coordinates where inferred horizontal lines are detected.
            - inferred_quality: List of quality scores for the inferred horizontal lines.
    """
    past_array_depth = int(width/100)
    required_distance = (width) * required_dist

    inferred_line_dists = []  
    inferred_quality = []
    inferred_line_thickness = 0
    # Iterate through the height to find the inferred lines
    for y in range(height):
        inferred_line_dist = 0 
        inferred_line_dist_max = 0
        # Initialize the past array and the black encountered counter
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

                if(black_encountered >= (past_array_depth/4)): #if 1/20th is black, stop this line
                    inferred_line_dist = 0
                    #pixel_data[width,height] = (0,255,0) #Line ended DEBUG

            if(inferred_line_dist > inferred_line_dist_max):
                    inferred_line_dist_max = inferred_line_dist

        # If the inferred line distance is greater than the required distance, increment the inferred line thickness
        if(inferred_line_dist_max > required_distance): #a ratio of the outer verticle lines
            inferred_line_thickness += 1
        else:
            inferred_line_thickness = 0

        # If the line thickness meets the threshold, consider it a valid inferred line
        if(inferred_line_thickness >=  1):
            inferred_line_dists.append(y)
            inferred_quality.append(inferred_line_dist_max/width)
    
    return inferred_line_dists, inferred_quality

def inferred_vertical_line_finder(height, width, pixel_data, required_dist, required_thick, hor_margin_lines):
    """
    Detect inferred vertical table lines in the image by analyzing pixel values.

    Args:
        height (int): Height of the image.
        width (int): Width of the image.
        pixel_data (numpy.ndarray): Grayscale pixel data of the image.
        required_dist (float): Required distance for a line to be considered a table line.
        required_thick (int): Required thickness for a line to be considered a table line.
        hor_margin_lines (list): List of y-coordinates where horizontal margin lines are detected.

    Returns:
            tuple: A tuple containing two lists:
            - infer_line_dists: List of x-coordinates where inferred vertical lines are detected.
            - inferred_quality: List of quality scores for the inferred vertical lines.
    """ 
    infer_line_dists = []
    inferred_quality = []
    past_array_depth = int(height/100)
    if(past_array_depth == 0):
        past_array_depth = 1
    inferred_line_thickness = 0

    # Calculate the required distance for a line to be considered a table line
    lenth_req = height * required_dist

    # Iterate through the width to find the inferred lines  
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
            # If the line thickness meets the threshold, consider it a valid inferred line
        if(inferred_line_thickness >= required_thick):
                infer_line_dists.append(x - int(required_thick/2)) #add the line where it actually is
                inferred_quality.append(inferred_line_dist_max/height)

    return infer_line_dists, inferred_quality

def merging_helper(im_arr): #This is a temporary fix and should not be needed when more training data is available
    """
    Helper function to determine if a merged image contains a table.

    Args:
        im_arr (list): List of merged image arrays.

    Returns:
        list: List of binary values indicating if a table is present in each merged image.
    """ 
    output_array = []
    for image in im_arr:
        for x in range(99,101): #if any has 95% black pixels
            black_count = 0
            for y in range(0,100):
                if(image[y, x] < 100):
                    black_count += 1
            # If the black count is greater than 95, break the loop and append 1 to the output array    
            if(black_count > 95):
                break
        # If the black count is greater than 95, append 1 to the output array
        if(black_count > 95):
            output_array.append(1)
        else:
            output_array.append(0)

    return output_array

def concatenate(root, pixel_data, ver_lines_final, hor_lines_final, conc_col_model, valid_cells_model):
    """
    Concatenate the table into a single image and predict the presence of data and columns.

    Args:
        root (str): Root directory for storing temporary images.
        pixel_data (numpy.ndarray): Grayscale pixel data of the image.
        ver_lines_final (list): List of x-coordinates where vertical table lines are detected.
        hor_lines_final (list): List of y-coordinates where horizontal table lines are detected.
        conc_col_model (keras.Model): Model for predicting column concatenation.
        valid_cells_model (keras.Model): Model for predicting valid cells.

    Returns:
        tuple: Tuple containing the presence of data and columns.
    """ 
    norm_pixel_data = cv2.normalize(pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    ver_lines_no_dup = []
    hor_lines_no_dup = []
    # Remove duplicate lines from the vertical and horizontal line lists
    start = ver_lines_final[0]
    for i in range(1, len(ver_lines_final)):
        # If the current line is not consecutive, add the previous line to the list and update the start
        if(ver_lines_final[i] != ver_lines_final[i-1]+1):
            ver_lines_no_dup.append(int((start + ver_lines_final[i-1])/2))
            start = ver_lines_final[i] 
    ver_lines_no_dup.append(int((start + ver_lines_final[-1])/2))
    # Remove duplicate lines from the horizontal line list
    start = hor_lines_final[0]
    for i in range(1, len(hor_lines_final)):
        # If the current line is not consecutive, add the previous line to the list and update the start
        if(hor_lines_final[i] != hor_lines_final[i-1]+1):
            hor_lines_no_dup.append(int((start + hor_lines_final[i-1])/2))
            start = hor_lines_final[i] 
    hor_lines_no_dup.append(int((start + hor_lines_final[-1])/2))

    # Initialize the merged image array
    im_arr = []
    for y in range(len(hor_lines_no_dup)-1):
        for x in range(len(ver_lines_no_dup)-2):
            # Resize the top left and top right parts of the image to 100x100 pixels
            top_left = cv2.resize(norm_pixel_data[hor_lines_no_dup[y]:hor_lines_no_dup[y+1], ver_lines_no_dup[x]:ver_lines_no_dup[x+1]], (100, 100)) #these steps makes sure the merge line is in the same place
            top_right = cv2.resize(norm_pixel_data[hor_lines_no_dup[y]:hor_lines_no_dup[y+1], ver_lines_no_dup[x+1]:ver_lines_no_dup[x+2]], (100, 100))
            merged_data = cv2.hconcat([top_left,top_right])
            im_arr.append(merged_data) 
            if(0):
                # Expand the dimensions of the merged data to match the input shape of the model
                temp_data = np.expand_dims(np.array([merged_data]), axis= -1)
                print(conc_col_model.predict(temp_data))
                print("")
                cv2.imshow('image', pixel_data[hor_lines_no_dup[y]:hor_lines_no_dup[y+1], ver_lines_no_dup[x]:ver_lines_no_dup[x+2]])
                cv2.waitKey(0)
                cv2.destroyAllWindows()

    # Calculate the length of the horizontal and vertical lines
    y_len = len(hor_lines_no_dup)-1
    x_len = len(ver_lines_no_dup)-2
    # If the merged image array is empty, return a 1D array of ones and zeros
    if(not im_arr): #this can occur when there are only 2 vertical lines so that nothing can possibly be concatenated
        return np.ones((y_len, 1)), np.zeros((y_len, 1)) #assume not concatenated and every cell has data, 1D array

    # Expand the dimensions of the merged data to match the input shape of the model    
    im_arr = np.expand_dims(np.array(im_arr), axis= -1)
    # Predict the presence of data and columns using the merging helper function
    helper_output = merging_helper(im_arr)
    # Predict the presence of data and columns using the models
    pred = conc_col_model.predict(im_arr)
    pred2 = valid_cells_model.predict(im_arr)
   
    # Initialize the 2D arrays for column concatenation and data presence
    conc_col_2D = np.zeros((y_len, x_len)) #Y then X
    contains_data = np.zeros((y_len, x_len+1))
    for y in range(y_len): 
        for x in range(x_len): 
            # If the prediction for column concatenation is greater than 0.5 and the helper output is 1, set the corresponding cell to 1
            if(pred[x+y*x_len][0] > .5 and helper_output == 1):
                conc_col_2D[y][x] = 1

            # If the prediction for valid cells is greater than 0.5, set the corresponding cell to 1
            if(pred2[x+y*x_len][0] > .5):
                contains_data[y][x] = 1

            # If the second prediction for valid cells is greater than 0.5, set the corresponding cell to 1
            if(pred2[x+y*x_len][1] > .5):
                contains_data[y][x+1] = 1

    return contains_data, conc_col_2D

def horizontal_line_crossover(hor_line, x_s, x_e, pixel_data_unchanged):
    """
    Check if a horizontal table line crosses a specific region.

    Args:
        hor_line (int): The y-coordinate of the horizontal table line.
        x_s (int): The starting x-coordinate of the region.
        x_e (int): The ending x-coordinate of the region.
        pixel_data_unchanged (numpy.ndarray): The original pixel data of the image (not normalized).

    Returns:
        bool: True if the horizontal line crosses the region, False otherwise.
    """
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

        white_pixel /= ((1 + x_e - x_s))
        black_pixel /= ((1 + x_e - x_s))
        
        if(not(white_pixel > .05 and black_pixel > .02 and wbw >= 3)): #more than 2% of the pixels are black and more than 5% are white// white is larger so it doesnt mess up when the box perimeters are not continuous
            return False
    return True

def lines_with_widths(ver_lines_final, hor_lines_final):
    """
    Calculate the widths of the vertical and horizontal lines.

    Args:
        ver_lines_final (list): List of x-coordinates where vertical lines are detected.
        hor_lines_final (list): List of y-coordinates where horizontal lines are detected.

    Returns:
        tuple: A tuple containing two lists:
            - ver_width_line: List of widths of the vertical lines.
            - hor_width_line: List of widths of the horizontal lines.
    """
    ver_width_line = []
    hor_width_line = []

    # Calculate the widths of the vertical lines
    start = ver_lines_final[0]
    for i in range(1, len(ver_lines_final)):
        if(ver_lines_final[i] != ver_lines_final[i-1]+1):
            ver_width_line.append([start, ver_lines_final[i-1]-start+1])
            start = ver_lines_final[i] 
    # Add the last width to the list
    ver_width_line.append([start, ver_lines_final[-1]-start+1])

    # Calculate the widths of the horizontal lines
    start = hor_lines_final[0]
    for i in range(1, len(hor_lines_final)):
        if(hor_lines_final[i] != hor_lines_final[i-1]+1):
            hor_width_line.append([start, hor_lines_final[i-1]-start+1])
            start = hor_lines_final[i] 
    # Add the last width to the list
    hor_width_line.append([start, hor_lines_final[-1]-start+1])
    return ver_width_line, hor_width_line

def hor_split(x_s, x_e, y_s, y_e, pixel_data_unchanged):
    """
    Determine if a horizontal line should be split.

    Args:
        x_s (int): The starting x-coordinate of the region.
        x_e (int): The ending x-coordinate of the region.
        y_s (int): The starting y-coordinate of the region.
        y_e (int): The ending y-coordinate of the region.
        pixel_data_unchanged (numpy.ndarray): The original pixel data of the image (not normalized).

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
    # Iterate through the white_lines array to find the split location
    for iter_num, iter in enumerate(white_lines):
        # If the current value is equal to the flag, increment the temp_count
        if(iter == int(FF)):
            temp_count += 1
        else:
            temp_count = 0

        # If the temp_count is greater than 3 + (y_e - y_s)/30, increment the wbw_count and reset the temp_count
        if(temp_count > 3 + (y_e - y_s)/30):# Adjust this if its not working properly
            wbw_count += 1
            temp_count = 0
            FF = not FF
            if(wbw_count == 3):
                split_loc = iter_num + y_s

    return (wbw_count >= 4), split_loc

def image_to_text(pixel_data_unchanged, root, contains_data, conc_col_2D, ver_width_line, hor_width_line, scale):
    """
    Convert the image to text using the detected table lines and data.

    Args:
        pixel_data_unchanged (numpy.ndarray): The original pixel data of the image (not normalized).
        root (str): Root directory for storing temporary images.
        contains_data (numpy.ndarray): The presence of data in the image.
        conc_col_2D (numpy.ndarray): The presence of column concatenation in the image.
        ver_width_line (list): List of widths of the vertical lines.
        hor_width_line (list): List of widths of the horizontal lines.
        scale (float): The scaling factor for the image.

    Returns:
        list: A list of lists containing the extracted text.
    """
    ver_scaled = []
    hor_scaled = []

    # Scale the vertical lines
    for i in ver_width_line:
        ver_scaled.append([int(i[0]*scale), int(i[1]*scale)+1])

    # Scale the horizontal lines    
    for i in hor_width_line:
        hor_scaled.append([int(i[0]*scale), int(i[1]*scale)+1])


    data_array = [["" for i in range(len(contains_data[0]))] for j in range(len(contains_data))]  
    y = 0
    y_SPLIT_extend = 0
    while(y < (len(hor_scaled)-1)):
        x = 0
        split_holder = []
        ANY_SPLIT = False
        while(x < len(ver_scaled)-1):
            #loc = os.path.join(root, "TempImages", "i" + str(y) +"_" + str(x) + ".jpg")
            loc = os.path.join(TempImages_dir, "i" + str(y) +"_" + str(x) + ".jpg")
            data_exists = contains_data[y][x]
            temp_x = x  
            while(temp_x < len(ver_scaled)-2 and conc_col_2D[y][temp_x]):
                temp_x += 1
                data_exists = data_exists or contains_data[y][temp_x] #atleast one cell has data in the merged data
         # Handle row-spanning cells
            y_merge = False #can only merge 1 line
            if(y < len(hor_scaled)-1 and y > 0): #LOOK TO THE PAST
               y_merge = horizontal_line_crossover(hor_scaled[y][0]+int(hor_scaled[y][1]/2), ver_scaled[x][0]+ver_scaled[x][1], ver_scaled[temp_x+1][0], pixel_data_unchanged)
            # Calculate the start and end coordinates for the current cell
            x_s = ver_scaled[x][0]+ver_scaled[x][1]+1
            x_e = ver_scaled[temp_x+1][0]
            y_s = hor_scaled[y-y_merge][0]+hor_scaled[y-y_merge][1]+1
            y_e = hor_scaled[y+1][0]
            
             # Check if the cell needs to be split
            SPLIT, split_loc = hor_split(x_s, x_e, y_s, y_e, pixel_data_unchanged) # ==========
            # Determine if a horizontal line should be split
            if(SPLIT):
                ANY_SPLIT = True
                slice = pixel_data_unchanged[y_s:split_loc, x_s:x_e]
                w, h = slice.shape
                slice2 = pixel_data_unchanged[split_loc:y_e, x_s:x_e] 
                #loc2 = os.path.join(root, "TempImages", "i_B" + str(y) +"_" + str(x) + ".jpg")
                loc2 = os.path.join(TempImages_dir, "i_B" + str(y) +"_" + str(x) + ".jpg")
                cv2.imwrite(loc2,slice2)   
                split_holder.append(pytesseract.image_to_string(loc2, config='--psm 7'))
            else:
                # If no splitting is needed, extract content from the entire cell
                slice = pixel_data_unchanged[y_s:y_e, x_s:x_e]
                w, h = slice.shape
                if(data_exists and w > 0 and h > 0):
                    split_holder.append("^ EXTEND")
                else:
                    split_holder.append("")

            # If the data exists and the width and height are greater than 0, write the image and add the text to the data array
            if(data_exists and w > 0 and h > 0):
                cv2.imwrite(loc,slice)
                data_array[y-y_merge+y_SPLIT_extend][x] = pytesseract.image_to_string(loc, config='--psm 7')
            # If the line is merged, add the text to the data array
            if(y_merge):
                data_array[y+y_SPLIT_extend][x] = "^ EXTEND" 
            # If cell splitting is needed, insert the split content
            while(x < temp_x):
                split_holder.append("^ EXTEND")
                data_array[y-y_merge+y_SPLIT_extend][x+1] = "< EXTEND"
                if(y_merge):
                    data_array[y+y_SPLIT_extend][x+1] = "^ EXTEND"  
                x += 1
            x += 1
        y += 1
        # If cell splitting is needed, insert the split content
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
                if(data_array[y][x] != "" and data_array[y][x] != "< EXTEND" and data_array[y][x] != "^ EXTEND"):
                    col_valid[x] = True
                    row_valid[y] = True

        # Remove invalid rows and columns
        for y in range(len(data_array)):
            if(row_valid[y]):
                temp_array = []
                for x in range(len(data_array[0])):
                    if(col_valid[x]):
                        temp_array.append(data_array[y][x])
                cleaned_data_array.append(temp_array)
    ################
    return cleaned_data_array

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

def run_main(image, root, identify_model, identify_model2, conc_col_model, valid_cells_model):
    """
    Process a single image (PDF page) to extract table content.

    Args:
        image (numpy.ndarray): Grayscale image of the PDF page.
        root (str): Root directory for saving temporary files.
        identify_model (keras.Model): Model for identifying table regions (stage 1).
        identify_model2 (keras.Model): Model for refining table regions (stage 2).
        conc_col_model (keras.Model): Model for detecting column concatenation.
        valid_cells_model (keras.Model): Model for detecting valid cells.

    Returns:
        list: Extracted table content as a 2D list.
    """
    #   Identify the table region in the image
    conc_pixel_data = table_identifier(image, root, identify_model, identify_model2)
    final_data = []
    #   Process each identified table region
    for pixel_data in conc_pixel_data:
        #   Copy the pixel data to avoid modifying the original
        pixel_data_unchanged = np.copy(pixel_data)
        # Resize the image to a fixed width (800 pixels) for consistent processing
        height, width = pixel_data.shape
        scale = width/800
        pixel_data = cv2.resize(pixel_data,(800, int(height/scale)))  #800 width, variable height
        height, width = pixel_data.shape
        #   Find horizontal lines in the image
        hor_lines = horizontal_line_finder(height, width, pixel_data) #cannot use margin_lines, but it is fine table cells are usally wider than they are tall
        hor_margin_lines = real_line_margins(hor_lines, 5)
        
        ver_lines = vertical_line_finder(height, width, pixel_data, hor_margin_lines)
        ver_margin_lines = real_line_margins(ver_lines, 5)

        #   Set the required distance for horizontal line inference 
        required_dist = .85 #TODO find a number that balances speed and accuracy
        prev_groups = -1
        inferred_hor_lines = []
        inferred_hor_quality = []
        while(1): #Horizontal
            inferred_hor_lines_temp, inferred_hor_quality_temp = inferred_horizontal_line_finder(height, width, pixel_data, required_dist, ver_margin_lines) #inferred
            groups = num_of_groups(inferred_hor_lines_temp, 7)
            required_dist += .04 #TODO find a number that balances speed and accuracy
            if(prev_groups > groups or groups == 0):
                break
            prev_groups = groups
            inferred_hor_lines = inferred_hor_lines_temp
            inferred_hor_quality = inferred_hor_quality_temp
        #   Set the required distance for vertical line inference
        required_dist = .65 #TODO find a number that balances speed and accuracy
        prev_groups = -1
        inferred_ver_lines = []
        inferred_ver_quality = []
        #   Add inferred vertical lines
        while(1): #Vertical
            inferred_ver_lines_temp, inferred_ver_quality_temp = inferred_vertical_line_finder(height, width, pixel_data, required_dist, 8, hor_margin_lines) #inferred
            groups = num_of_groups(inferred_ver_lines_temp, 15)
            required_dist += .03 #TODO find a number that balances speed and accuracy
            if(prev_groups > groups or groups == 0):
                break
            prev_groups = groups
            inferred_ver_lines = inferred_ver_lines_temp
            inferred_ver_quality = inferred_ver_quality_temp

            #   Add guaranteed inferred vertical lines
        guarenteed_inf_ver, guarenteed_ver_quality = inferred_vertical_line_finder(height, width, pixel_data, .98, 8, hor_lines) #inject inf_ver that might have been wrongfully removed; Thicker line required USED TO BE .99
        tempv = mean_finder(ver_lines, ([0] + guarenteed_inf_ver  + [width-1]), ([1] + guarenteed_ver_quality + [1]), 10, width) #TODO find a good number   
        #  Refine the final vertical and horizontal lines
        ver_lines_final = mean_finder(tempv, inferred_ver_lines, inferred_ver_quality, 15, width) #this is precision not resolution add lines to the left and right //TODO find a good precision
        hor_lines_final = mean_finder(hor_lines, ([0] + inferred_hor_lines + [height-1]), ([1] + inferred_hor_quality + [1]), 7, height) #this is precision not resolution

        #   Detect column concatenation and valid cells
        conc_col_2D = []
        contains_data, conc_col_2D = concatenate(root, pixel_data, ver_lines_final, hor_lines_final, conc_col_model, valid_cells_model)
        ver_width_line, hor_width_line = lines_with_widths(ver_lines_final, hor_lines_final)
        #  Extract text content from the table
        final_data.append(image_to_text(pixel_data_unchanged, root, contains_data, conc_col_2D, ver_width_line, hor_width_line, scale))
    return final_data 

#######################START########################    
pyth_dir = os.path.dirname(__file__)
# Gets the directory path of the current script.
parser = argparse.ArgumentParser(description='Table Extractor Tool')
#parser.add_argument('--weight_dir', required=True, help='weight directory')
parser.add_argument('--pdf_dir', required=True, help='pdf directory')
parser.add_argument('--work_dir', required=True, help='main work and output directory')
parser.add_argument('--first_table_page', required=True, help='The first page that you want table extraction begins with')
parser.add_argument('--last_table_page', required=True, help='The last page that you want table extraction ends with')
args = parser.parse_args()

concatenate_clean = True

# Sets flags for whether to clean and merge table data.
root = os.path.join(pyth_dir,'Table_extract_robust')
pdf_loc = (args.pdf_dir).lower()
start = int(args.first_table_page)
cap = int(args.last_table_page)
pages = convert_from_path(pdf_loc, 300, first_page=start, last_page=cap)

# Create a temporary directory path. Extract the basic name of PDF file.
TempImages_dir = os.path.join(args.work_dir, "TempImages")
pdf_name = ((os.path.basename(args.pdf_dir)).split('.pdf'))[0]

try:
    os.makedirs(TempImages_dir)
    print("Directory " , TempImages_dir ,  " Created ") 
except FileExistsError:
    print("Directory " , TempImages_dir ,  " already exists")
    print("Cleaning ipxact directory ...")
    if len(os.listdir(TempImages_dir)) != 0:
        for file in os.listdir(TempImages_dir):
            os.remove(os.path.join(TempImages_dir,file))

# Create a temporary directory and clear its contents if it already exists.
identify_model = load_model(os.path.join(root, r"Identification_Models", "stage1.h5"))
identify_model2 = load_model(os.path.join(root, r"Identification_Models", "stage2.h5"))
conc_col_model = load_model(os.path.join(root, "conc_col.h5"), compile = False)
valid_cells_model = load_model(os.path.join(root, "valid_cells.h5"))
# Load the pretrained model.
array = []
for image_num, image in enumerate(pages):
    page_num = image_num + start
    print("\n\nStarting page: ", page_num)

    image = np.array(image)	
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    temp_array = run_main(image, root, identify_model, identify_model2, conc_col_model, valid_cells_model)

    # Combine all extracted data from each page
    a = []
    for small_array in temp_array:
        a += small_array

    # If not concatenating, write the extracted data to a CSV file for the current page
    if(not concatenate_clean):
        with open(os.path.join(root, ("P" + str(page_num) + ".csv")), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(a)
    else:
        array += a
# Process each page of PDF image, extract table content and save.
if(concatenate_clean):
    cleaned_array = []
    for row in array:
        if(len(row) < 9):
            has_extend = False
            for cell in row:
                if(cell == "^ EXTEND"):
                    has_extend = True

            if(has_extend):
                for cell_num, cell in enumerate(row):
                    if(cell != "^ EXTEND" and cell_num < len(cleaned_array[-1])):
                        cleaned_array[-1][cell_num] += (" " + cell)
            else:
                cleaned_array.append(row)
    
    with open(os.path.join(args.work_dir, pdf_name + ".csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(cleaned_array)