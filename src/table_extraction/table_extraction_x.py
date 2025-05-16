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
from paddleocr import PaddleOCR
from pdf2image import (
    convert_from_path,
)  # poppler needs to be added and added to the path variable
from numba import jit
import time
import multiprocessing
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool as Pool
import os
import dill
import tarfile
from paddleocr import PaddleOCR
from tensorflow.keras.layers import (
    Dense,
    Conv2D,
    Permute,
    MaxPooling2D,
    AveragePooling2D,
    LSTM,
    Reshape,
    Flatten,
    Dropout,
)
from tensorflow.keras.layers import multiply, add, average, maximum, Concatenate, Lambda
from tensorflow.keras.models import load_model
from typing import Optional

tf.compat.v1.enable_eager_execution()


##calculate the IoU between two regions
def calc_IoU(xml, proposed):
    """
    Calculate the Intersection Over Union (IoU) between two regions.
    This function calculates the IoU between two regions by finding the intersection and union of the two regions.
    Args:
        xml (list): List of coordinates representing the first region.
        proposed (list): List of coordinates representing the second region.
    Returns:
        float: IoU between the two regions.
    """
    intersection = 0
    # Unpack coordinates of the first box
    xmlMinX = xml[0]  # Ground-truth top-left x
    xmlMinY = xml[1]  # Ground-truth top-left y
    xmlMaxX = xml[2]  # Ground-truth bottom-right x
    xmlMaxY = xml[3]  # Ground-truth bottom-right y

    # Unpack coordinates of the second box
    propMinX = proposed[0]  # Predicted top-left x
    propMinY = proposed[1]  # Predicted top-left y
    propMaxX = proposed[2]  # Predicted bottom-right x
    propMaxY = proposed[3]  # Predicted bottom-right y

    # Compute intersection area (if boxes overlap)
    width_shared = min(propMaxX, xmlMaxX) - max(propMinX, xmlMinX)
    height_shared = min(propMaxY, xmlMaxY) - max(propMinY, xmlMinY)
    if width_shared > 0 and height_shared > 0:
        intersection = width_shared * height_shared

    # Compute area of each box
    xmlArea = (xmlMaxX - xmlMinX) * (xmlMaxY - xmlMinY)
    propArea = (propMaxX - propMinX) * (propMaxY - propMinY)

    # Compute union area
    union = xmlArea + propArea - intersection

    # Compute IoU
    return intersection / union


# for now assume picture is detected in yolo before being processe here
def yolo_model_improve(yolo_model_dir, pdf_loc, page_num, delta=5):
    """
    Use a YOLO model to detect table regions in a PDF page.

    This function:
    - Converts the specified PDF page into an image (using fix_pdf.extract_jpg)
    - Runs a YOLO detection model via command line (detector.py)
    - Parses the resulting bounding boxes and confidence scores
    - Merges or filters bounding boxes based on overlap (IoU) and confidence

    Args:
        yolo_model_dir (str): Path to the YOLO model directory used by detector.py
        pdf_loc (str): Path to the PDF file to extract the image from
        page_num (int): Page number in the PDF to process (0-indexed)
        delta (int): Optional. Number of pixels to expand each bounding box border. Default is 5.

    Returns:
        dict: A dictionary of detected tables.
              Format: { '0': [ [ [xmin, ymin, xmax, ymax], confidence ], ... ] }
    """
    # run detection
    fix_pdf.extract_jpg(pdf_loc, page_num)
    # model_path = "/Users/serafinakamp/Desktop/YOLO_test/TrainYourOwnYOLO/Data/Model_Weights/trained_weights_1915_final.h5"
    # call = "python3 ../../src/table_extraction/detector.py --yolo_model " + model_path

    call = (
        "python3 ../../src/table_extraction/detector.py --yolo_model " + yolo_model_dir
    )
    os.system(call)
    # Initialize an empty dictionary to store detected tables
    tables_on_page = {}
    num = 0
    # with open("../../src/table_extraction/Detection_results.csv","r") as csvfile:
    with open(os.path.join(work_loc, "Detection_results.csv"), "r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == "image":
                continue  # skip header lines
            key = str(num)
            page_width = int(row[8])  # Width of page
            page_height = int(row[9])  # Height of page
            proposed = [
                max(int(row[2]) - delta, 0),  # xmin
                max(int(row[3]) - delta, 0),  # ymin
                min(int(row[4]) + delta, page_width),  # xmax
                min(int(row[5]) + delta, page_height),  # ymax
            ]
            top_left = (proposed[0], proposed[1])  # top left corner
            bot_right = (proposed[2], proposed[3])  # bottom right corner

            confidence = float(row[7])  # confidence score

        min_confidence_threshold = (
            0.3  # reduce the confidence threshold to 0.3, allow low confidence tables
        )
        # if confidence score is greater than the minimum confidence threshold, then add the table to the list of tables
        if confidence > min_confidence_threshold:
            if key in tables_on_page:
                max_iou = 0  # initialize max iou to 0
                prop_overlap = []  # initialize prop overlap to an empty list
                found_ind = 0  # initialize found index to 0
                for i, prop in enumerate(tables_on_page[key]):
                    iou = calc_IoU(prop[0], proposed)
                    if iou > max_iou:
                        max_iou = iou
                        prop_overlap = prop[0]
                        found_ind = i
                if max_iou < 0.2:  # no too much overlap
                    tables_on_page[key].append([proposed, confidence])
                elif (
                    prop[1] < confidence
                ):  # if the new detected table is more confident, replace the old table
                    tables_on_page[key].append([proposed, confidence])
                    del tables_on_page[key][found_ind]
                    print("new table is more confident")
                else:
                    print("overlap and less confident")
            else:  # new table
                tables_on_page[key] = [[proposed, confidence]]
            num += 1

    return tables_on_page  # return dict containing processed tables for each image


# detecting tables using current cnns
def cnn_detect(model1, model2, i):
    """
    Detect tables using two CNN models.
    This function uses two CNN models to detect tables in an image. The first model detects potential table regions,
    and the second model refines the detected regions. The final output is a list of detected table regions and their coordinates.
    Args:
        model1 (keras.Model): First model for detecting table regions.
        model2 (keras.Model): Second model for refining table regions.
        i (numpy.ndarray): Grayscale image data as a 2D NumPy array.
    Returns:
        tuple: Tuple containing two lists of detected table regions.
    """
    X_size = 800  # Target width for resizing input image # original is 800
    Y_size = 64  # Target height for resizing input image # original is 64

    pTwo_size = 600  # Size for resizing input region for model2
    cuts_labels = 60  # Number of horizontal segments for model2 output
    label_precision = 8  # AMOUNT OF PIXELS BETWEEN LABELS, GOES FROM 1/4th to 3/4ths, Vertical granularity in pixels for label resolution Control the accuracy of mapping the detection output of model 1 to the original map coordinates

    y_fail_num = 2  # Number of consecutive failures allowed in model1 Controlling the tolerance of blank areas in model 1 to prevent false positives
    pixel_data = i  # Grayscale image data as a 2D NumPy array
    original_pixel_data_255 = pixel_data.copy()  # copy of the original pixel data
    pixel_data = cv2.normalize(
        pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F
    )
    original_pixel_data = pixel_data.copy()  # copy of the original pixel data

    height, width = pixel_data.shape  # height and width of the image
    scale = X_size / width  # scale factor for the image

    pixel_data = cv2.resize(pixel_data, (X_size, int(height * scale)))  # X, then Y
    # add a border to the image
    bordered_pixel_data = cv2.copyMakeBorder(
        pixel_data,  # image to add border to
        top=int(Y_size / 4),  # top border
        bottom=int(Y_size / 4),  # bottom border
        left=0,  # left border
        right=0,  # right border
        borderType=cv2.BORDER_CONSTANT,  # border type
        value=1,  # border value
    )

    # slice the image into smaller pieces
    slice_skip_size = int(Y_size / 2)  # size of the slice
    iter = 0  # iterator
    slices = []  # list of slices
    while (iter * slice_skip_size + Y_size) < int(height * scale + Y_size / 2):
        s_iter = iter * slice_skip_size  # slice iterator
        slices.append(
            bordered_pixel_data[int(s_iter) : int(s_iter + Y_size)]
        )  # add the slice to the list
        iter += 1  # increment the iterator

    slices_resized = []  # list of resized slices
    # resize the slices to the model's expected size
    for slice in slices:
        resized = cv2.resize(
            slice, (800, 64)
        )  # resize the slice to the model's expected size
        slices_resized.append(resized)

    slices_resized = np.array(np.expand_dims(slices_resized, axis=-1))
    data = model1.predict(slices_resized)
    # concatenate data
    conc_data = []
    # Threshold for the model
    threshold = 0.1  # original is 0.5 i will try 0.3 The lower the value, the more sensitive the detection is and the more false positives are possible
    for single_array in data:
        for single_data in single_array:
            conc_data.append(single_data)
    conc_data += [0 for i in range(y_fail_num + 1)]  # Still needed
    # Initialize groups list
    groups = []
    fail = y_fail_num
    group_start = 1  # start at 1 to prevent numbers below zero in groups
    for iter in range(len(conc_data) - 1):
        if conc_data[iter] < threshold:
            fail += 1
        else:
            fail = 0

        if fail >= y_fail_num:
            if iter - group_start >= 4:
                groups.append(
                    [
                        max(
                            int((group_start - 1) * label_precision / scale),
                            int((iter + 1 - y_fail_num) * label_precision / scale),
                        )
                    ]
                )
            group_start = iter

    # Refine each vertical group with model2 to determine horizontal bounds
    groups2 = []
    for group in groups:
        temp_final_original = cv2.resize(
            original_pixel_data[group[0] : group[1]], (pTwo_size, pTwo_size)
        )
        # Display the resized input to model2
        cv2.imshow("Resized Input to model2", temp_final_original)
        cv2.waitKey(0)
        temp_final = np.expand_dims(
            np.expand_dims(temp_final_original, axis=0), axis=-1
        )
        data_final = model2.predict(temp_final)
        column_threshold = 0.1  # original is 0.5 try 0.4 Controls whether a horizontal coordinate is accepted as a boundary
        hor_start = -1
        hor_finish = 10000
        pointless, original_width = original_pixel_data.shape

        # find the start and end of the horizontal lines
        for iter in range(len(data_final[0])):
            if data_final[0][iter] > column_threshold and hor_start == -1:
                if iter > 0:
                    hor_start = int((iter - 0.5) * original_width / cuts_labels)
                else:
                    hor_start = int(iter * original_width / cuts_labels)
            print(
                f"Predicted hor_start: {hor_start}, hor_finish: {hor_finish}, Image Width: {original_width}"
            )
            if data_final[0][iter] > 0.5:
                hor_finish = int((iter + 0.5) * original_width / cuts_labels)

        # If the horizontal bounds are greater than 70% of the original width, add the entire image as a group
        if 1 and hor_finish - hor_start > (
            0.7 * original_width
        ):  # Fix for tables that cover the entire image
            groups2.append((0, original_width))
        else:
            groups2.append((hor_start, hor_finish))

    return groups, groups2  # returns all detected y vals,x vals


def cnn_yolo_combined(pdf_loc, page_num, im, model1, model2, yolo_model_dir, work_loc):
    """
    Combine YOLO and CNN models to detect tables in an image.
    This function uses YOLO to detect table regions and then refines the detection using a CNN model.
    The final output is a list of detected table regions and their coordinates.
    Args:
        pdf_loc (str): Path to the PDF file.
        page_num (int): Page number of the PDF to process.
        im (numpy.ndarray): Grayscale image data as a 2D NumPy array.
        model1 (keras.Model): First model for detecting table regions.
        model2 (keras.Model): Second model for refining table regions.
        yolo_model_dir (str): Path to the YOLO model directory.
        work_loc (str): Path to the working directory.
    Returns:
        tuple: Tuple containing two lists of detected table regions.
    """
    processed_tables = yolo_model_improve(
        yolo_model_dir, pdf_loc, page_num, work_loc
    )  # pdf_loc :When processing a different document
    yolo_tables = []
    all_y, all_x = cnn_detect(model1, model2, im)

    num = 0
    key = str(num)
    while key in processed_tables:
        yolo_tables.append(processed_tables[key])
        num += 1
        key = str(num)
    height = im.shape[0]
    width = im.shape[1]

    final_tables = []
    # prune
    for table in yolo_tables:
        maxiou = 0
        cnn_found = []
        yolo_coords = table[0]
        # find the best cnn table
        for i in range(len(all_y)):
            cnn_coords = [all_x[i][0], all_y[i][0], all_x[i][1], all_y[i][1]]
            top_left_cnn = (cnn_coords[0], cnn_coords[1])
            bot_right_cnn = (cnn_coords[2], cnn_coords[3])

            top_left_yolo = (yolo_coords[0][0], yolo_coords[0][1])
            bot_right_yolo = (yolo_coords[0][2], yolo_coords[0][3])

            iou = calc_IoU(cnn_coords, yolo_coords[0])
            if iou > maxiou:
                maxiou = iou
                cnn_found = cnn_coords

        if maxiou >= 0.10:
            final_min_x = min(cnn_found[0], yolo_coords[0][0])
            final_min_y = min(cnn_found[1], yolo_coords[0][1])
            final_max_x = max(cnn_found[2], yolo_coords[0][2])
            final_max_y = max(cnn_found[3], yolo_coords[0][3])

            final_tables.append([final_min_x, final_min_y, final_max_x, final_max_y])
        else:  # prefer yolo if no overlap
            final_tables.append(yolo_coords[0])
    # if no yolo tables take all cnn tables
    if len(yolo_tables) == 0:
        for i in range(len(all_y)):
            cnn_coords = [all_x[i][0], all_y[i][0], all_x[i][1], all_y[i][1]]
            final_tables.append(cnn_coords)
    # get final final_splits
    final_splits = []
    coords = []
    for table in final_tables:
        final_split = im[table[1] : table[3], table[0] : table[2]]
        coords.append([table[1], table[0], table[3], table[2]])
        cv2.imshow("im", final_split)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        final_splits.append(final_split)
    return final_splits, coords


def split_by_white_gap_for_table(
    image, min_gap_ratio=0.05, debug=False, debug_save=False, save_prefix="debug_gap"
):  # Minimum ratio of image width to be considered a valid white gap (e.g., 5% of width)	Increase if you want only larger gaps to count as valid (e.g., to avoid splitting by small spaces)
    """
        Splits a page image into two parts by detecting a large vertical white gap from the center.

    This function scans from the center of the image toward both the left and right sides
    to locate a wide vertical white gap — typically representing space between two distinct
    regions such as a table on one side and a non-table component (e.g., circuit diagram or text)
    on the other. Once a sufficiently large gap is found, the image is split into two sub-images.

    This method is particularly useful for separating tables from adjacent visual content in
    scanned documents or technical datasheets.

    Args:
        image (np.ndarray): The input image (either grayscale or BGR color).
        min_gap_ratio (float, optional): The minimum width of a white gap as a fraction of the total
            image width to be considered valid for splitting. Default is 0.05 (i.e., 5% of the page width).
        debug (bool, optional): If True, displays intermediate images such as the binarized image
            and the resulting split parts in OpenCV windows for debugging purposes. Default is False.
        debug_save (bool, optional): If True, saves the binary mask and the left/right split images
            to disk using the specified filename prefix. Default is False.
        save_prefix (str, optional): Filename prefix used when saving debug images. Only relevant
            if debug_save is True. Default is "debug_gap".

    Returns:
        tuple:
            - left_img (np.ndarray): The left portion of the image split at the white gap.
            - right_img (np.ndarray): The right portion of the image split at the white gap.


    Notes:
        - This method assumes the presence of significant whitespace between content regions.
        - If no valid gap is found, the image is split down the center by default.
        - Ideal for use in preprocessing pipelines for table detection and document layout analysis.
    """
    # Convert color image to grayscale if needed
    height, width = image.shape[:2]
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Binarize the image using Otsu's thresholding
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Identify fully white columns in the binary image
    white_cols = np.all(binary == 255, axis=0)

    # from middle to both sides
    mid = width // 2
    min_blank_width = int(width * min_gap_ratio)

    # Find the gap side
    def find_gap_side(start, step):
        run_start = None
        for i in range(start, 0 if step < 0 else width, step):
            if white_cols[i]:
                if run_start is None:
                    run_start = i
            else:
                if run_start is not None:
                    gap_width = abs(i - run_start)
                    if gap_width >= min_blank_width:
                        return run_start + gap_width // 2
                    run_start = None
        return None

    # Find the gap side
    left_cut = find_gap_side(mid, -1)
    right_cut = find_gap_side(mid, 1)

    # Find the cut column
    cut_col = (
        left_cut
        if left_cut is not None
        else (right_cut if right_cut is not None else mid)
    )

    # Split the image into left and right parts
    left_img = image[:, :cut_col]
    right_img = image[:, cut_col:]

    # Display the binary, left, and right images for debugging
    if debug:
        cv2.imshow("Binary", binary)
        cv2.imshow("Left", left_img)
        cv2.imshow("Right", right_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    # Save the binary, left, and right images for debugging
    if debug_save:
        cv2.imwrite(f"{save_prefix}_binary.png", binary)
        cv2.imwrite(f"{save_prefix}_left.png", left_img)
        cv2.imwrite(f"{save_prefix}_right.png", right_img)
    # Return the left and right images
    return left_img, right_img


def table_identifier(pixel_data, root, identify_model, identify_model2):
    start_time = time.time()   
    pTwo_size = 600                     #Target size to resize the cropped region for the second CNN.
    X_size = 800                        #Target width for the first CNN.
    Y_size = 64                         #Target height for the first CNN.
    cuts_labels = 60                    #Number of horizontal cuts for the first CNN.
    label_precision = 8                 #Precision for the first CNN.
    y_fail_num = 3                      #Number of consecutive failures allowed for the first CNN.

    original_pixel_data_255 = pixel_data.copy()
    pixel_data = cv2.normalize(pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    original_pixel_data = pixel_data.copy()

    height, width = pixel_data.shape
    scale = X_size / width

    pixel_data = cv2.resize(pixel_data, (X_size, int(height * scale)))
    bordered_pixel_data = cv2.copyMakeBorder(pixel_data, top=int(Y_size / 4), bottom=int(Y_size / 4),
                                             left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=1)

    gray_pixel_data = (pixel_data * 255).astype(np.uint8)
    num_of_detected_lines = count_text_lines(gray_pixel_data)
    threshold = 6

    if num_of_detected_lines > threshold:
        dynamic_factor = max(1.5, min(2.2, num_of_detected_lines / 120))
    else:
        dynamic_factor = max(2.2, min(3.2, num_of_detected_lines / 80))

    slice_skip_size = min(int(Y_size / 2), max(int(Y_size / 3), int(Y_size / dynamic_factor)))

    slices = []
    iter = 0
    while (iter * slice_skip_size + Y_size) < int(height * scale + Y_size / 2):
        s_iter = iter * slice_skip_size
        slices.append(bordered_pixel_data[int(s_iter):int(s_iter + Y_size)])
        iter += 1

    slices = np.array(np.expand_dims(slices, axis=-1))
    data = identify_model.predict(slices)

    conc_data = []
    for single_array in data:
        for single_data in single_array:
            conc_data.append(single_data)

    conc_data += [0 for _ in range(y_fail_num + 1)]

    groups = []
    column_threshold = 0.08
    fail = y_fail_num
    group_start = 1

    for iter in range(len(conc_data) - 1):
        if conc_data[iter] < column_threshold:
            fail += 1
        else:
            fail = 0

        if fail >= y_fail_num:
            if iter - group_start >= 4:
                groups.append((int((group_start - 1) * label_precision / scale),
                               int((iter + 1 - y_fail_num) * label_precision / scale)))
            group_start = iter

    groups2 = []
    final_splits = []
    coords = []

    image_height = original_pixel_data.shape[0]
    pointless, original_width = original_pixel_data.shape

    for group in groups:
        start, end = group
        if end <= start or end > image_height:
            print(f"[Warning] Skipping invalid group: ({start}, {end}), image height={image_height}")
            continue

        cropped = original_pixel_data[start:end]
        if cropped.shape[0] == 0:
            print(f"[Warning] Empty slice at ({start}, {end}), skipping.")
            continue

        try:
            temp_final_original = cv2.resize(cropped, (pTwo_size, pTwo_size))
        except cv2.error as e:
            print(f"[Error] OpenCV resize failed for slice {group}: {e}")
            continue

        temp_final = np.expand_dims(np.expand_dims(temp_final_original, axis=0), axis=-1)
        data_final = identify_model2.predict(temp_final)

        hor_start = -1
        hor_finish = 10000

        for iter in range(len(data_final[0])):
            if data_final[0][iter] > column_threshold and hor_start == -1:
                hor_start = int(iter * original_width / cuts_labels) if iter == 0 else int((iter - 0.5) * original_width / cuts_labels)
            if data_final[0][iter] > column_threshold:
                hor_finish = int((iter + 0.5) * original_width / cuts_labels)

        if hor_finish - hor_start > (0.7 * original_width):
            groups2.append((0, original_width))
        else:
            groups2.append((hor_start, hor_finish))

       # final split
        final_split = original_pixel_data_255[start:end, groups2[-1][0]:groups2[-1][1]]
        final_splits.append(final_split)
        coords.append([start, groups2[-1][0], end, groups2[-1][1]])

    print("--- %s seconds identify tables ---" % (time.time() - start_time))
    
    debug_save_path = os.path.join(root, "debug_table_regions")
    os.makedirs(debug_save_path, exist_ok=True)

    # FOR DEBUG
    debug_image = original_pixel_data_255.copy() 
    if len(debug_image.shape) == 2:
        debug_image = cv2.cvtColor(debug_image, cv2.COLOR_GRAY2BGR)

    # add safety length protection
    min_len = min(len(groups), len(groups2))
    for i in range(min_len):
        y1, y2 = groups[i]
        x1, x2 = groups2[i]
        cv2.rectangle(debug_image, (x1, y1), (x2, y2), (0, 0, 255), 2)

    save_path = os.path.join(debug_save_path, "table_detected_regions.jpg")
   
    return final_splits, coords


# improve count_text_lines
def count_text_lines(image):
    # binary
    binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)[1]

    # horizontal projection
    horizontal_projection = np.sum(binary, axis=1).astype(np.float32)

    # convert 1D to 2D and filter
    projection_2d = horizontal_projection[:, np.newaxis]
    smoothed_projection = cv2.GaussianBlur(projection_2d, (5, 5), 0)
    smoothed_projection = smoothed_projection[:, 0]

    #  find regions above a certain threshold (text lines)
    mean_val = np.mean(smoothed_projection)
    return np.count_nonzero(smoothed_projection > mean_val * 0.5)


def is_double_column(image, threshold_ratio=0.015, white_thresh=245):
    """
    Determines whether the given document image follows a double-column layout.

    This function analyzes the vertical center of the input image to check for a large vertical white gap.
    If the region near the vertical center contains a high proportion of white pixels, the function
    assumes that the page is split into two columns (e.g., as in academic papers or journals).

    Args:
        image (np.ndarray): Input image (grayscale or BGR). This is typically a scanned document page.
        threshold_ratio (float, optional): The width of the center band (as a fraction of the image width)
            used to assess for white space. A typical value is 0.01–0.03. Default is 0.015.
        white_thresh (int, optional): The pixel intensity threshold above which a pixel is considered "white".
            Grayscale values range from 0 (black) to 255 (white). Default is 245.

    Returns:
        bool: True if the page is likely double-column based on detected white space; False otherwise.

    Notes:
        - This function assumes the central vertical gap is relatively clean and white.
        - Adjust `white_thresh` lower (e.g., 230) for noisier scans with light gray backgrounds.
        - Adjust `threshold_ratio` higher (e.g., 0.02–0.03) to allow more flexibility if the white gap is wider or off-center.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    height, width = gray.shape
    band_width = int(width * threshold_ratio)
    mid_x = width // 2
    left = mid_x - band_width
    right = mid_x + band_width
    print("run")

    center_band = gray[:, left:right]
    white_ratio = np.mean(center_band > white_thresh)
    if white_ratio > 0.95:
        print(f"yes")
    return white_ratio > 0.95


def mean_finder_subroutine(
    real, infered, infered_quality, precision, group_start, n, final_dist
):  # TODO BROKEN FIX
    """
    Calculate the mean position of inferred lines within a group.
    This function calculates the mean position of inferred lines within a group by averaging the positions
    of the lines that are above a specified threshold. The final output is a list of mean positions.
    Args:
        real (list): List of real line positions.
        infered (list): List of inferred line positions.
        infered_quality (list): List of quality scores for the inferred lines.
        precision (float): Precision for line detection.Smaller value = more sensitive to duplication, fewer new lines added. Larger value = more lines added, but higher risk of duplicates.
        group_start (int): Starting index of the group.
        n (int): Ending index of the group.
        final_dist (list): List to store the final line positions.
    Returns:
        None: The function modifies `final_dist` in place.
    """
    # Check if there's any real line close to this inferred group.
    # If yes, skip adding to final_dist to avoid duplicate lines.
    bool_add = True
    for a in real:
        if a > (infered[group_start] - precision) and a < (
            infered[n] + precision
        ):  # a real line is within y units of the group
            bool_add = False
    if bool_add:
        # If this group is wide enough, use quality-based moving average
        search_size = 2
        if (infered[n] - infered[group_start]) > (
            1 + (2 * search_size)
        ):  # moving average of quality score
            size_of_group = infered[n] - infered[group_start] + 1
            max_value = 0
            average_array = [0 for i in range(search_size)]
            # Find max value and get a moving average array
            for iter in range(
                search_size, size_of_group - search_size
            ):  # find max value and get a moving average array
                temp_value = 0
                for sub_iter in range(iter - search_size, iter + search_size + 1):
                    temp_value += infered_quality[sub_iter + infered[group_start]]
                average_array.append(temp_value)
                if temp_value > max_value:
                    max_value = temp_value

            threshold = max_value * 0.99
            first_value = -1
            for iter in range(len(average_array)):
                if first_value == -1 and average_array[iter] > threshold:
                    first_value = iter
                if average_array[iter] > threshold:
                    last_value = iter
            # Calculate the line location
            line_loc = int((first_value + last_value) / 2 + infered[group_start])
        else:
            line_loc = int((infered[n] + infered[group_start]) / 2)
        final_dist.append(line_loc)
    return


def mean_finder(real, infered, infered_quality_raw, precision, max_dim_1d):
    """
    Calculate the mean position of inferred lines.
    This function calculates the mean position of inferred lines by grouping them based on their positions
    and then averaging the positions of the lines within each group. The final output is a list of mean positions.
    Args:
        real (list): List of real line positions.
        infered (list): List of inferred line positions.
        infered_quality_raw (list): List of quality scores for the inferred lines.
        precision (float): Precision for line detection.Increase → merge more lines, but may merge incorrectly; Decrease → finer grouping, risk of missed merges.
        max_dim_1d (int): Maximum dimension of the 1D array.
    Returns:
        list: List of mean positions of the inferred lines.
    """
    infered_quality = [0 for i in range(max_dim_1d)]
    for i in range(len(infered)):
        infered_quality[infered[i]] = infered_quality_raw[i]
    n = 0
    group_start = 0
    final_dist = []
    while (n + 1) < len(infered):
        # If the next inferred line is greater than the current inferred line plus the precision
        if infered[n + 1] > (
            infered[n] + precision
        ):  # the distance needs to be within x units to be apart of the group
            mean_finder_subroutine(
                real, infered, infered_quality, precision, group_start, n, final_dist
            )
            group_start = n + 1
        n += 1
    mean_finder_subroutine(
        real, infered, infered_quality, precision, group_start, n, final_dist
    )  # Final Dump
    # Append the real lines to the final distance
    final_dist += real
    # Sort the final distance
    final_dist.sort()
    return final_dist


def num_of_groups(infered, i):
    """
    Calculate the number of groups in a list of inferred line positions.
    This function calculates the number of groups in a list of inferred line positions by counting
    the number of times the lines are separated by more than a specified distance.
    Args:
        infered (list): List of inferred line positions.
        i (float): Distance threshold for separating groups.
    Returns:
        int: Number of groups in the list.
    """
    groups = 0
    if len(infered) > 0:
        groups = 1
    for a in range(len(infered) - 1):
        # If the next inferred line is greater than the current inferred line plus the distance threshold
        if infered[a + 1] > infered[a] + i:
            # Increment the number of groups
            groups += 1
    return groups


def horizontal_line_finder(height, width, pixel_data):  # normal finds black lines
    """
    Find horizontal lines in an image using a simple thresholding approach.
    This function finds horizontal lines in an image by checking for significant changes in pixel intensity
    across the image. The final output is a list of line positions.
    Args:
        height (int): Height of the image.
        width (int): Width of the image.
        pixel_data (numpy.ndarray): Grayscale image data as a 2D NumPy array.
    Returns:
        list: List of positions of horizontal lines in the image.
    """
    final_out = []
    search_dist = 3
    # search for horizontal lines
    for y in range(search_dist, height - search_dist):
        short_line = 0
        line_dist = 0
        fails = 0
        # search for horizontal lines
        for x in range(width):
            top = 0
            bot = 0
            # search for horizontal lines
            for y2 in range(y - search_dist, y - 1):
                top += pixel_data[y2, x] / (search_dist - 1)
            for y2 in range(y + 2, y + search_dist + 1):
                bot += pixel_data[y2, x] / (search_dist - 1)

            if (
                top / 2 + bot / 2 - pixel_data[y, x]
            ) > 30:  # these are 8 bit ints need to calculate like this to avoid overflow
                line_dist += 1
                if fails > 0:
                    fails -= 1
            elif fails < 1:  # tolerate x fails
                fails += width / 8
            else:
                if line_dist > width / 16:
                    short_line += 1
                line_dist = 0
            # if the line distance is greater than 1/8th of the width or there are 4 short lines, then add the line to the list
            if line_dist > width / 8 or short_line >= 4:
                final_out.append(y)
                break
    return final_out


def vertical_line_finder(
    height, width, pixel_data, hor_margin_lines
):  # normal finds black lines
    """
    Find vertical lines in an image using a simple thresholding approach.
    This function finds vertical lines in an image by checking for significant changes in pixel intensity
    across the image. The final output is a list of line positions.
    Args:
        height (int): Height of the image.
        width (int): Width of the image.
        pixel_data (numpy.ndarray): Grayscale image data as a 2D NumPy array.
        hor_margin_lines (list): List of y-coordinates representing horizontal margin lines.
    Returns:
        list: List of positions of vertical lines in the image.
    """
    final_out = []
    search_dist = 3
    # search for vertical lines
    for x in range(search_dist, width - search_dist):
        line_dist = 0
        fails = 0
        # search for vertical lines
        for y in range(height):
            if y not in hor_margin_lines:
                max_left = 0
                max_right = 0
                # search for vertical lines
                for x2 in range(x - search_dist, x):
                    if (pixel_data[y, x2]) > max_left:
                        max_left = pixel_data[y, x2]
                # search for vertical lines
                for x2 in range(x + 1, x + search_dist + 1):
                    if (pixel_data[y, x2]) > max_right:
                        max_right = pixel_data[y, x2]
                # search for vertical lines
                if (
                    max_left / 2 + max_right / 2 - pixel_data[y, x]
                ) > 30:  # these are 8 bit ints need to calculate like this to avoid overflow
                    line_dist += 1
                    if fails > 0:
                        fails -= 1
                elif fails < 1:  # tolerate x fails
                    fails += height / 8
                else:
                    line_dist = 0

                if line_dist > height / 8:
                    final_out.append(x)
                    break
    return final_out


def real_line_margins(lines, margin_size_pixels):
    """
    Calculate the margins for real lines.
    This function calculates the margins for real lines by adding a specified number of pixels
    to each side of the line. The final output is a list of line positions with added margins.
    Args:
        lines (list): List of line positions.
        margin_size_pixels (int): Number of pixels to add to each side of the line.
    Returns:
        list: List of line positions with added margins.
    """
    margin_lines = []
    for line in lines:
        for i in range(line - margin_size_pixels, line + margin_size_pixels):
            if i not in margin_lines and i >= lines[0] and i <= lines[-1]:
                margin_lines.append(i)
    return margin_lines


def inferred_horizontal_line_finder(
    height, width, pixel_data, required_dist, ver_margin_lines
):  # finds white lines
    """
    Find inferred horizontal lines in an image.
    This function finds inferred horizontal lines in an image by checking for significant changes in pixel intensity
    across the image. The final output is a list of line positions.
    Args:
        height (int): Height of the image.
        width (int): Width of the image.
        pixel_data (numpy.ndarray): Grayscale image data as a 2D NumPy array.
        required_dist (float): Required distance for detecting a line.
        ver_margin_lines (list): List of y-coordinates representing vertical margin lines.
    Returns:
        tuple: Tuple containing two lists. The first list contains the inferred line positions, and the second list contains the inferred line quality scores.
    """
    past_array_depth = int(width / 100)
    required_distance = (width) * required_dist
    # search for inferred horizontal lines
    inferred_line_dists = []
    inferred_quality = []
    inferred_line_thickness = 0
    for y in range(height):
        inferred_line_dist = 0
        inferred_line_dist_max = 0

        # search for inferred horizontal lines
        past_array = [0 for i in range(past_array_depth)]

        # Together these find the amount of black values in the last y squares
        black_encountered = 0

        for x in range(width):
            inferred_line_dist += 1
            # search for inferred horizontal lines
            if x not in ver_margin_lines:  # skip over verticle lines
                if pixel_data[y, x] < 200:  # current is black
                    if past_array[x % past_array_depth] == 0:  # past is white
                        black_encountered += 1
                    past_array[x % past_array_depth] = 1
                else:  # current is white
                    if past_array[x % past_array_depth] == 1:  # past is black
                        black_encountered -= 1
                    past_array[x % past_array_depth] = 0

                if black_encountered >= (
                    past_array_depth / 4
                ):  # if 1/20th is black, stop this line
                    inferred_line_dist = 0
                    # pixel_data[width,height] = (0,255,0) #Line ended DEBUG
            # search for inferred horizontal lines
            if inferred_line_dist > inferred_line_dist_max:
                inferred_line_dist_max = inferred_line_dist

        # search for inferred horizontal lines
        if (
            inferred_line_dist_max > required_distance
        ):  # a ratio of the outer verticle lines
            inferred_line_thickness += 1
        else:
            inferred_line_thickness = 0
        # search for inferred horizontal lines
        if inferred_line_thickness >= 1:
            inferred_line_dists.append(y)
            inferred_quality.append(inferred_line_dist_max / width)

    return inferred_line_dists, inferred_quality


def inferred_vertical_line_finder(
    height, width, pixel_data, required_dist, required_thick, hor_margin_lines
):
    """
    Find inferred vertical lines in an image.
    This function finds inferred vertical lines in an image by checking for significant changes in pixel intensity
    across the image. The final output is a list of line positions.
    Args:
        height (int): Height of the image.
        width (int): Width of the image.
        pixel_data (numpy.ndarray): Grayscale image data as a 2D NumPy array.
        required_dist (float): Required distance for detecting a line. Higher → more strict;  May miss short lines.
        required_thick (float): Required thickness for detecting a line.Higher → more robust lines; May miss thin lines.
        hor_margin_lines (list): List of y-coordinates representing horizontal margin lines.
    Returns:
        tuple: Tuple containing two lists. The first list contains the inferred line positions, and the second list contains the inferred line quality scores.
    """
    # search for inferred vertical lines
    infer_line_dists = []
    inferred_quality = []
    past_array_depth = int(height / 100)
    if past_array_depth == 0:
        past_array_depth = 1
    inferred_line_thickness = 0
    # search for inferred vertical lines
    lenth_req = height * required_dist
    # search for inferred vertical lines
    for x in range(width):
        inferred_line_dist = 0
        inferred_line_dist_max = 0
        past_array = [
            0 for i in range(past_array_depth)
        ]  # Together these find the amount of black values in the last y squares
        black_encountered = 0
        # search for inferred vertical lines
        for y in range(height):
            inferred_line_dist += 1
            if y not in hor_margin_lines:  # skip over verticle lines
                if pixel_data[y, x] < 200:  # current is black
                    if past_array[y % past_array_depth] == 0:  # past is white
                        black_encountered += 1
                    past_array[y % past_array_depth] = 1
                else:  # current is white
                    if past_array[y % past_array_depth] == 1:  # past is black
                        black_encountered -= 1
                    past_array[y % past_array_depth] = 0

                if black_encountered >= (
                    past_array_depth / 4
                ):  # if 1/4th is black, stop this line
                    inferred_line_dist = 0
                    if 0 and required_dist == 0.95:
                        pixel_data[y, x] = 0  # Line ended DEBUG

            if inferred_line_dist > inferred_line_dist_max:
                inferred_line_dist_max = inferred_line_dist

        if inferred_line_dist_max > lenth_req:  # a ratio of the outer verticle lines
            inferred_line_thickness += 1
        else:
            inferred_line_thickness = 0

        if inferred_line_thickness >= required_thick:
            infer_line_dists.append(
                x - int(required_thick / 2)
            )  # add the line where it actually is
            inferred_quality.append(inferred_line_dist_max / height)

    return infer_line_dists, inferred_quality


def merging_helper(im_arr):
    """
    Heuristically determines whether an image slice contains a dominant vertical black line.

    This helper function inspects each image in a list of small image slices and checks for a
    strongly black vertical band (e.g., part of a table border or structural column). Specifically,
    it scans columns 99 and 100 and counts how many of the top 100 pixels are very dark.

    If more than 95 out of 100 pixels in either column are darker than a threshold (value < 100),
    it marks the image as containing a significant black structure.

    Args:
        im_arr (List[np.ndarray]): A list of grayscale image slices (2D NumPy arrays).

    Returns:
        List[int]: A list of binary indicators (0 or 1) for each image:
            - 1 indicates the image contains a strong black vertical feature.
            - 0 indicates no such feature was found.
    """
    # This is a temporary fix and should not be needed when more training data is available
    output_array = []
    for image in im_arr:
        for x in range(99, 101):  # if any has 95% black pixels
            black_count = 0
            for y in range(0, 100):
                if image[y, x] < 100:
                    black_count += 1

            if black_count > 95:
                break
        if black_count > 95:
            output_array.append(1)
        else:
            output_array.append(0)

    return output_array


def concatenate(
    root,
    pixel_data,
    ver_lines_final,
    hor_lines_final,
    conc_col_model,
    valid_cells_model,
):
    """
    Concatenate tables in an image using two CNN models.
    This function uses two CNN models to concatenate tables in an image. The first model detects potential table regions,
    and the second model refines the detection. The final output is a list of detected table regions and their coordinates.
    Args:
        root (str): Path to the working directory.
        pixel_data (numpy.ndarray): Grayscale image data as a 2D NumPy array.
        ver_lines_final (list): List of vertical line positions.
        hor_lines_final (list): List of horizontal line positions.
        conc_col_model (keras.Model): First model for detecting table regions.
        valid_cells_model (keras.Model): Second model for refining table regions.
    Returns:
        tuple: Tuple containing two lists of detected table regions.
    """
    # Normalize the pixel data to be between 0 and 1
    norm_pixel_data = cv2.normalize(
        pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F
    )
    ver_lines_no_dup = []
    hor_lines_no_dup = []
    # Remove duplicate lines
    start = ver_lines_final[0]
    for i in range(1, len(ver_lines_final)):
        if ver_lines_final[i] != ver_lines_final[i - 1] + 1:
            ver_lines_no_dup.append(int((start + ver_lines_final[i - 1]) / 2))
            start = ver_lines_final[i]
    ver_lines_no_dup.append(int((start + ver_lines_final[-1]) / 2))
    # Remove duplicate lines
    start = hor_lines_final[0]
    for i in range(1, len(hor_lines_final)):
        if hor_lines_final[i] != hor_lines_final[i - 1] + 1:
            hor_lines_no_dup.append(int((start + hor_lines_final[i - 1]) / 2))
            start = hor_lines_final[i]
    hor_lines_no_dup.append(int((start + hor_lines_final[-1]) / 2))

    # search for the final splits
    im_arr = []
    for y in range(len(hor_lines_no_dup) - 1):
        for x in range(len(ver_lines_no_dup) - 2):
            top_left = cv2.resize(
                norm_pixel_data[
                    hor_lines_no_dup[y] : hor_lines_no_dup[y + 1],
                    ver_lines_no_dup[x] : ver_lines_no_dup[x + 1],
                ],
                (100, 100),
            )  # these steps makes sure the merge line is in the same place
            top_right = cv2.resize(
                norm_pixel_data[
                    hor_lines_no_dup[y] : hor_lines_no_dup[y + 1],
                    ver_lines_no_dup[x + 1] : ver_lines_no_dup[x + 2],
                ],
                (100, 100),
            )
            merged_data = cv2.hconcat([top_left, top_right])
            im_arr.append(merged_data)
            if 0:
                temp_data = np.expand_dims(np.array([merged_data]), axis=-1)
                print(conc_col_model.predict(temp_data))
                print("")
                cv2.imshow(
                    "image",
                    pixel_data[
                        hor_lines_no_dup[y] : hor_lines_no_dup[y + 1],
                        ver_lines_no_dup[x] : ver_lines_no_dup[x + 2],
                    ],
                )
                cv2.waitKey(0)
                cv2.destroyAllWindows()
    # search for the final splits
    y_len = len(hor_lines_no_dup) - 1
    x_len = len(ver_lines_no_dup) - 2
    if (
        not im_arr
    ):  # this can occur when there are only 2 vertical lines so that nothing can possibly be concatenated
        return np.ones((y_len, 1)), np.zeros(
            (y_len, 1)
        )  # assume not concatenated and every cell has data, 1D array

    # search for the final splits
    im_arr = np.expand_dims(np.array(im_arr), axis=-1)
    helper_output = merging_helper(im_arr)
    pred = conc_col_model.predict(im_arr)
    pred2 = valid_cells_model.predict(im_arr)

    conc_col_2D = np.zeros((y_len, x_len))  # Y then X
    contains_data = np.zeros((y_len, x_len + 1))
    for y in range(y_len):
        for x in range(x_len):
            if pred[x + y * x_len][0] > 0.5 and helper_output == 1:
                conc_col_2D[y][x] = 1

            if pred2[x + y * x_len][0] > 0.5:
                contains_data[y][x] = 1

            if pred2[x + y * x_len][1] > 0.5:
                contains_data[y][x + 1] = 1

    return contains_data, conc_col_2D


def horizontal_line_crossover(hor_line, x_s, x_e, pixel_data_unchanged):
    """
    Check for horizontal line crossover.
    This function checks for a horizontal line crossover by counting the number of black and white pixels
    in a specified range of the image. The final output is a boolean indicating whether a crossover is detected.
    Args:
        hor_line (int): Position of the horizontal line.
        x_s (int): Starting x-coordinate.
        x_e (int): Ending x-coordinate.
        pixel_data_unchanged (numpy.ndarray): Grayscale image data as a 2D NumPy array.
    Returns:
        bool: True if a crossover is detected, False otherwise.
    """

    for line in range(
        hor_line - 3, hor_line + 4, 3
    ):  # all have to pass the condition for crossover
        iter = x_s
        white_pixel = 0
        black_pixel = 0

        wbw = 0  # white_black_white
        while iter < x_e:
            if pixel_data_unchanged[line, iter] < 127:
                black_pixel += 1
                if wbw % 2 == 1:
                    wbw += 1
            else:
                white_pixel += 1
                if wbw % 2 == 0:
                    wbw += 1
            iter += 1

        white_pixel /= 1 + x_e - x_s
        black_pixel /= 1 + x_e - x_s

        if not (
            white_pixel > 0.05 and black_pixel > 0.02 and wbw >= 3
        ):  # more than 2% of the pixels are black and more than 5% are white// white is larger so it doesnt mess up when the box perimeters are not continuous
            return False
    return True


def lines_with_widths(ver_lines_final, hor_lines_final):
    """
    Calculate the widths of vertical and horizontal lines.
    This function calculates the widths of vertical and horizontal lines by grouping the lines
    and then averaging the positions of the lines within each group. The final output is a list of mean positions.
    Args:
        ver_lines_final (list): List of vertical line positions.
        hor_lines_final (list): List of horizontal line positions.
    Returns:
        tuple: Tuple containing two lists. The first list contains the widths of vertical lines, and the second list contains the widths of horizontal lines.
    """
    ver_width_line = []
    hor_width_line = []

    start = ver_lines_final[0]
    for i in range(1, len(ver_lines_final)):
        if ver_lines_final[i] != ver_lines_final[i - 1] + 1:
            ver_width_line.append([start, ver_lines_final[i - 1] - start + 1])
            start = ver_lines_final[i]
    ver_width_line.append([start, ver_lines_final[-1] - start + 1])

    start = hor_lines_final[0]
    for i in range(1, len(hor_lines_final)):
        if hor_lines_final[i] != hor_lines_final[i - 1] + 1:
            hor_width_line.append([start, hor_lines_final[i - 1] - start + 1])
            start = hor_lines_final[i]
    hor_width_line.append([start, hor_lines_final[-1] - start + 1])
    return ver_width_line, hor_width_line


def hor_split(x_s, x_e, y_s, y_e, pixel_data_unchanged):
    """
    Check for horizontal line split.
    This function checks for a horizontal line split by counting the number of black pixels
    in a specified range of the image. The final output is a boolean indicating whether a split is detected.
    Args:
        x_s (int): Starting x-coordinate.
        x_e (int): Ending x-coordinate.
        y_s (int): Starting y-coordinate.
        y_e (int): Ending y-coordinate.
        pixel_data_unchanged (numpy.ndarray): Grayscale image data as a 2D NumPy array.
    Returns:
        tuple: Tuple containing a boolean indicating whether a split is detected, and the position of the split if detected.
    """
    white_lines = [1 for i in range(y_s, y_e)]
    for y in range(y_s, y_e):
        black_count = 0
        midpoint = (x_s + x_e) / 2
        half_length = (x_e - x_s) / 2
        base = (x_s + x_e) / 20
        for x in range(x_s, x_e):

            if x < midpoint:  # Values in the center are more valuable
                points = base + (x - x_s)
            else:
                points = base + half_length - (x - midpoint)

            if pixel_data_unchanged[y, x] < 100:
                black_count += points
        if black_count > (x_e - x_s) / 4:
            white_lines[y - y_s] = 0

    split_loc = 0
    wbw_count = 0
    FF = True
    temp_count = 0

    for iter_num, iter in enumerate(white_lines):
        if iter == int(FF):
            temp_count += 1
        else:
            temp_count = 0

        if temp_count > 3 + (y_e - y_s) / 30:  # Adjust this if its not working properly
            wbw_count += 1
            temp_count = 0
            FF = not FF
            if wbw_count == 3:
                split_loc = iter_num + y_s

    return (wbw_count >= 4), split_loc






def image_to_text(
    pixel_data_unchanged,
    root,
    contains_data,
    conc_col_2D,
    ver_width_line,
    hor_width_line,
    scale,
    ver_lines,
    hor_lines,
):
    """
    Convert an image to text using line positions and widths.
    This function converts an image to text by scaling the line positions and widths, and then using these scaled values
    to extract text from the image. The final output is a list of text strings.
    Args:
        pixel_data_unchanged (numpy.ndarray): Grayscale image data as a 2D NumPy array.
        root (str): Path to the working directory.
        contains_data (numpy.ndarray): 2D array indicating which cells contain data.
        conc_col_2D (numpy.ndarray): 2D array indicating which cells are merged.
        ver_width_line (list): List of widths of vertical lines.
        hor_width_line (list): List of widths of horizontal lines.
        scale (float): Scaling factor for the image.
        ver_lines (list): List of vertical line positions.
        hor_lines (list): List of horizontal line positions.
    Returns:
        list: List of text strings extracted from the image.
    """
    # use ocr with better error handling
    try:
        ocr = safe_paddleocr_init(model_root="models", lang="en")
    except Exception as e:
        print(f"OCR initialization error: {e}")
        # use alternative ocr method
        ocr = PaddleOCR(use_angle_cls=True, lang="en", use_gpu=False)

    ver_scaled = []
    hor_scaled = []
    real_ver_lines = []
    real_hor_lines = []

    for i in ver_width_line:
        ver_scaled.append([int(i[0] * scale), int(i[1] * scale) + 1])

    for i in hor_width_line:
        hor_scaled.append([int(i[0] * scale), int(i[1] * scale) + 1])

    for i in ver_lines:
        real_ver_lines.append(int(i * scale))

    for i in hor_lines:
        real_hor_lines.append(int(i * scale))

    data_array = [
        [["" for k in range(2)] for i in range(len(contains_data[0]))]
        for j in range(len(contains_data))
    ]

    y = 0
    y_SPLIT_extend = 0

    while y < (len(hor_scaled) - 1):
        x = 0
        split_holder = []
        ANY_SPLIT = False
        while x < len(ver_scaled) - 1:
            loc = os.path.join(TempImages_dir, "i" + str(y) + "_" + str(x) + ".jpg")
            data_exists = contains_data[y][x]
            temp_x = x
            while temp_x < len(ver_scaled) - 2 and conc_col_2D[y][temp_x]:
                temp_x += 1
                data_exists = (
                    data_exists or contains_data[y][temp_x]
                )  # atleast one cell has data in the merged data

            y_merge = False  # can only merge 1 line
            if y < len(hor_scaled) - 1 and y > 0:  # LOOK TO THE PAST
                y_merge = horizontal_line_crossover(
                    hor_scaled[y][0] + int(hor_scaled[y][1] / 2),
                    ver_scaled[x][0] + ver_scaled[x][1],
                    ver_scaled[temp_x + 1][0],
                    pixel_data_unchanged,
                )

            x_s = ver_scaled[x][0] + ver_scaled[x][1] + 1
            x_e = ver_scaled[temp_x + 1][0]
            y_s = hor_scaled[y - y_merge][0] + hor_scaled[y - y_merge][1] + 1
            y_e = hor_scaled[y + 1][0]

            # determine if the cell is split
            SPLIT, split_loc = hor_split(x_s, x_e, y_s, y_e, pixel_data_unchanged)
            if SPLIT:
                ANY_SPLIT = True
                # handle split cell
                slice = [
                    pixel_data_unchanged[y_s:split_loc, x_s:x_e],
                    [x_s, x_e, y_s, split_loc],
                ]
                w, h = slice[0].shape

                # handle second part of cell
                slice2 = [
                    pixel_data_unchanged[split_loc:y_e, x_s:x_e],
                    [x_s, x_e, split_loc, y_e],
                ]
                loc2 = os.path.join(
                    TempImages_dir, "i_B" + str(y) + "_" + str(x) + ".jpg"
                )

                # save debug image
                cv2.imwrite(loc2, slice2[0])

                # handle split cell image preprocessing
                try:
                    cell_img = slice2[0].copy()

                    # 1. ensure image size is enough
                    if (
                        cell_img.size > 0
                        and cell_img.shape[0] > 5
                        and cell_img.shape[1] > 5
                    ):
                        # 2. image enhancement
                        # enhance contrast
                        cell_img = cv2.normalize(
                            cell_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX
                        )

                        # adaptive threshold can handle uneven lighting
                        _, binary = cv2.threshold(
                            cell_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                        )

                        # apply morphological operation to remove noise
                        kernel = np.ones((2, 2), np.uint8)
                        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

                        # 4. noise reduction
                        cell_img = cv2.fastNlMeansDenoising(cell_img, None, 10, 7, 21)

                        # 5. add padding to prevent text from being truncated
                        cell_img = cv2.copyMakeBorder(
                            cell_img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255
                        )

                        # 6. convert to RGB (PaddleOCR needs)
                        cell_img_rgb = cv2.cvtColor(cell_img, cv2.COLOR_GRAY2RGB)

                        # 7. save enhanced image for debugging
                        debug_path = os.path.join(
                            TempImages_dir, f"debug_i_B{y}_{x}.jpg"
                        )
                        cv2.imwrite(debug_path, cell_img_rgb)

                        # 8. execute ocr and record result - use modified ocr call method
                        recognized_text = ocr.ocr(cell_img_rgb)
                        recognized_text = extract_text_from_paddle_result(
                            recognized_text, min_conf=0.2
                        )  # 降低阈值
                        print(f"  - Final text: '{recognized_text}'")
                    else:
                        print(
                            f"Split cell({y},{x}) too small: {cell_img.shape if cell_img.size > 0 else 'empty'}"
                        )
                        recognized_text = ""
                except Exception as e:
                    print(f"OCR error on split cell({y},{x}): {e}")
                    recognized_text = ""

                split_holder.append([recognized_text, slice2[1]])
            else:
                slice = [pixel_data_unchanged[y_s:y_e, x_s:x_e], [x_s, x_e, y_s, y_e]]
                w, h = slice[0].shape
                if data_exists and w > 0 and h > 0:
                    split_holder.append(["^ EXTEND", [-1, -1, -1, -1]])
                else:
                    split_holder.append(["", [0, 0, 0, 0]])

            if data_exists and w > 0 and h > 0:
                # save original image
                cv2.imwrite(loc, slice[0])

                # main cell image preprocessing
                try:
                    cell_img = slice[0].copy()

                    # same image enhancement process, add processing steps
                    if (
                        cell_img.size > 0
                        and cell_img.shape[0] > 5
                        and cell_img.shape[1] > 5
                    ):
                        # enhance contrast
                        cell_img = cv2.normalize(
                            cell_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX
                        )

                        # try adaptive threshold
                        binary = cv2.adaptiveThreshold(
                            cell_img,
                            255,
                            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                            cv2.THRESH_BINARY,
                            11,
                            2,
                        )

                        # morphological operation to reduce noise
                        kernel = np.ones((2, 2), np.uint8)
                        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

                        # significantly scale up large images
                        if cell_img.shape[0] < 30 or cell_img.shape[1] < 100:
                            scale_factor = max(3.0, 150.0 / cell_img.shape[1])
                            cell_img = cv2.resize(
                                cell_img,
                                None,
                                fx=scale_factor,
                                fy=scale_factor,
                                interpolation=cv2.INTER_CUBIC,
                            )

                        # noise reduction
                        cell_img = cv2.fastNlMeansDenoising(cell_img, None, 10, 7, 21)

                        # add white margin to ensure text is not truncated
                        cell_img = cv2.copyMakeBorder(
                            cell_img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255
                        )

                        # convert to RGB
                        cell_img_rgb = cv2.cvtColor(cell_img, cv2.COLOR_GRAY2RGB)
                        binary_rgb = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)

                        # save enhanced image
                        debug_path = os.path.join(
                            TempImages_dir, f"debug_i_{y}_{x}.jpg"
                        )
                        binary_path = os.path.join(
                            TempImages_dir, f"binary_i_{y}_{x}.jpg"
                        )
                        cv2.imwrite(debug_path, cell_img_rgb)
                        cv2.imwrite(binary_path, binary_rgb)

                        # ===== improved ocr call method =====
                        # 1. try normal ocr
                        ocr_result1 = ocr.ocr(cell_img_rgb)
                        text1 = extract_text_from_paddle_result(ocr_result1)

                        # 2. try binary image
                        ocr_result2 = ocr.ocr(binary_rgb, cls=True)
                        text2 = extract_text_from_paddle_result(
                            ocr_result2, min_conf=0.1
                        )

                        candidates = [text1, text2]
                        lengths = [len(t) for t in candidates]
                        recognized_text = candidates[lengths.index(max(lengths))]

                        # if all methods fail, try lower confidence
                        if not recognized_text:
                            for result in [ocr_result1, ocr_result2]:
                                text = extract_text_from_paddle_result(
                                    result, min_conf=0.2
                                )
                                if text:
                                    recognized_text = text
                                    break

                        print(f"  - Final text for cell({y},{x}): '{recognized_text}'")
                    else:
                        print(
                            f"Main cell({y},{x}) too small: {cell_img.shape if cell_img.size > 0 else 'empty'}"
                        )
                        recognized_text = ""
                except Exception as e:
                    print(f"OCR error on main cell({y},{x}): {e}")
                    recognized_text = ""

                data_array[y - y_merge + y_SPLIT_extend][x][0] = recognized_text
                data_array[y - y_merge + y_SPLIT_extend][x][1] = slice[1]

            if y_merge:
                data_array[y + y_SPLIT_extend][x][0] = "^ EXTEND"
                data_array[y + y_SPLIT_extend][x][1] = [-1, -1, -1, -1]

            while x < temp_x:
                split_holder.append(["^ EXTEND", [-1, -1, -1, -1]])
                data_array[y - y_merge + y_SPLIT_extend][x + 1][0] = "< EXTEND"
                data_array[y - y_merge + y_SPLIT_extend][x + 1][1] = [-1, -1, -1, -1]
                if y_merge:
                    data_array[y + y_SPLIT_extend][x + 1][0] = "^ EXTEND"
                    data_array[y + y_SPLIT_extend][x + 1][1] = [-1, -1, -1, -1]
                x += 1
            x += 1
        y += 1
        if ANY_SPLIT:
            data_array.insert(y + y_SPLIT_extend, split_holder)
            y_SPLIT_extend += 1

    ####ARRAY CLEANUP

    # array cleanup and convert to final format
    final_merge = []
    for row in data_array:
        final_row = []
        for cell in row:
            final_row.append(cell[0])  # get text content
        final_merge.append(final_row)

    return final_merge


def extract_text_from_paddle_result(ocr_result, min_conf=0.5):
    """
    extract text from paddle ocr result
    """
    if not ocr_result:
        return ""

    recognized_text = ""

    # handle different versions of paddle ocr result
    try:

        if isinstance(ocr_result, list):
            for line in ocr_result:
                if isinstance(line, list):
                    for item in line:
                        if isinstance(item, list) and len(item) == 2:
                            # the first element is coordinates, the second element is (text, confidence) tuple
                            if isinstance(item[1], tuple) and len(item[1]) >= 2:
                                text = item[1][0]  # get text
                                conf = item[1][1]  # get confidence
                                if conf > min_conf:
                                    if recognized_text:
                                        recognized_text += " "
                                    recognized_text += text

        # handle possible alternative formats
        if not recognized_text and isinstance(ocr_result, list):
            flat_text = []

            def extract_from_nested(item):
                if isinstance(item, str):
                    flat_text.append(item)
                elif isinstance(item, (list, tuple)):
                    for sub_item in item:
                        extract_from_nested(sub_item)
                elif isinstance(item, dict) and "text" in item:
                    flat_text.append(item["text"])

            extract_from_nested(ocr_result)
            recognized_text = " ".join(flat_text)

    except Exception as e:
        print(f"Error extracting text from OCR result: {e}")

    return recognized_text


def extract_text_from_paddle_result(ocr_result, min_conf=0.5):
    """
    extract text from paddle ocr result
    """
    if not ocr_result:
        return ""

    recognized_text = ""

    # handle different versions of paddle ocr result
    try:

        if isinstance(ocr_result, list):
            for line in ocr_result:
                if isinstance(line, list):
                    for item in line:
                        if isinstance(item, list) and len(item) == 2:
                            # the first element is coordinates, the second element is (text, confidence) tuple
                            if isinstance(item[1], tuple) and len(item[1]) >= 2:
                                text = item[1][0]  # get text
                                conf = item[1][1]  # get confidence
                                if conf > min_conf:
                                    if recognized_text:
                                        recognized_text += " "
                                    recognized_text += text

        # handle possible alternative formats
        if not recognized_text and isinstance(ocr_result, list):
            flat_text = []

            def extract_from_nested(item):
                if isinstance(item, str):
                    flat_text.append(item)
                elif isinstance(item, (list, tuple)):
                    for sub_item in item:
                        extract_from_nested(sub_item)
                elif isinstance(item, dict) and "text" in item:
                    flat_text.append(item["text"])

            extract_from_nested(ocr_result)
            recognized_text = " ".join(flat_text)

    except Exception as e:
        print(f"Error extracting text from OCR result: {e}")

    return recognized_text


def contains_wide_table(image, min_width_ratio=0.85, min_height_ratio=0.1):
    """
    Determine whether there is a large rectangular structure in the image that spans
    most of the page width and is not too short in height.
    This is used to detect full-width tables and avoid misclassifying horizontal boxes
    or diagram headers as tables.

    Args:
        image (np.ndarray): Input image (grayscale or BGR color).
        min_width_ratio (float): Minimum width ratio relative to the full page width (default is 85%).
        min_height_ratio (float): Minimum height ratio relative to the page height (default is 10%).

    Returns:
        bool: True if a wide rectangular structure likely representing a full-width table is found; False otherwise.
    """

    if image.ndim == 3 and image.shape[2] == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    height, width = binary.shape
    min_h_thresh = height * min_height_ratio

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        if w >= width * min_width_ratio and h >= min_h_thresh:
            return True  # if the width is greater than 85% of the page width and the height is greater than 10% of the page height, then it is a wide table

    return False


def split_if_double_column(
    image,
    save_debug_dir=None,
    debug=True,
    page_num=None,
    slice_idx=None,
    threshold_ratio=0.03,
    white_thresh=240,
):
    """
    Detects a wide white band near the vertical center of the image and splits it into two columns if found.
    Returns [left_img, right_img] if split occurs, otherwise [image].
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image.copy()
    height, width = gray.shape

    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    half_band = int(width * threshold_ratio)
    start = max((width // 2) - half_band, 0)
    end = min((width // 2) + half_band, width)
    center_band = binary[:, start:end]

    # allow some non-pure white pixels (tolerance)
    white_mask = np.mean(center_band > white_thresh, axis=0) > 0.98

    # find the longest white run
    runs = []
    run_start = None
    for idx, is_white in enumerate(white_mask):
        if is_white and run_start is None:
            run_start = idx
        elif not is_white and run_start is not None:
            runs.append((run_start, idx - 1))
            run_start = None
    if run_start is not None:
        runs.append((run_start, len(white_mask) - 1))

    longest = None
    max_len = 0
    for s, e in runs:
        length = e - s + 1
        if length > max_len:
            max_len = length
            longest = (s, e)

    if debug:
        print(
            f"[DEBUG] Found {len(runs)} white run(s). Longest = {max_len} px. Threshold = {half_band} px."
        )

    if longest and max_len >= half_band:
        band_center = start + (longest[0] + longest[1]) // 2
        left = image[:, :band_center]
        right = image[:, band_center:]

        if save_debug_dir:
            os.makedirs(save_debug_dir, exist_ok=True)
            debug_img = image.copy()
            cv2.line(debug_img, (band_center, 0), (band_center, height), (0, 0, 255), 2)
            filename = (
                f"page{page_num}_slice{slice_idx}_split.png"
                if page_num is not None and slice_idx is not None
                else "split_preview.png"
            )
            cv2.imwrite(os.path.join(save_debug_dir, filename), debug_img)
            if debug:
                print(
                    f"[DEBUG] Saved split debug image at: {os.path.join(save_debug_dir, filename)}"
                )

        return [left, right]

    else:
        if debug:
            print("[DEBUG] No suitable white gap found. Skip splitting.")
            if save_debug_dir:
                os.makedirs(save_debug_dir, exist_ok=True)
                preview_name = (
                    f"page{page_num}_slice{slice_idx}_nosplit.png"
                    if page_num is not None
                    else "nosplit_preview.png"
                )
                cv2.imwrite(os.path.join(save_debug_dir, preview_name), image)

        return [image]


def safe_paddleocr_init(model_root="models", lang="en", use_angle_cls=True):
    return PaddleOCR(
        use_angle_cls=False,
        lang="en",
        det_db_box_thresh=0.3,
        det_db_unclip_ratio=3.0,
        drop_score=0.2,
        show_log=False,
        use_gpu=False,
    )


def image_handle(image):
    import cv2

    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


# def multiprocessing_unit(image_num, image, root, identify_model, identify_model2, conc_col_model, valid_cells_model):
def multiprocessing_unit_separate_tables_reg(
    pdf_loc, page_num, image, root, identify_model, identify_model2
):
    # load_model now in seperating processes

    # page_num = image_num + start
    print("\n\nStarting page: ", page_num)

    temp_pixel_data, coords = table_identifier(
        image, root, identify_model, identify_model2
    )
    # print(coords)
    return temp_pixel_data


def multiprocessing_unit_separate_tables_yolo(
    pdf_loc,
    page_num,
    image,
    root,
    identify_model,
    identify_model2,
    yolo_model_dir,
    work_loc,
):
    # load_model now in seperating processes

    # page_num = image_num + start
    print("\n\nStarting page: ", page_num)

    temp_pixel_data, coords = cnn_yolo_combined(
        pdf_loc,
        page_num,
        image,
        identify_model,
        identify_model2,
        yolo_model_dir,
        work_loc,
    )
    # print(coords)
    return temp_pixel_data


def multiprocessing_unit_identify_cells(pixel_data, root):
    """
    Identify cells in an image using two CNN models.
    This function uses two CNN models to identify cells in an image. The first model detects potential table regions,
    and the second model refines the detection. The final output is a list of detected table regions and their coordinates.
    Args:
        pixel_data (numpy.ndarray): Grayscale image data as a 2D NumPy array.
        root (str): Path to the working directory.
    Returns:
        list: List of detected table regions and their coordinates.
    """

    conc_col_model = load_model(os.path.join(root, "conc_col.h5"))
    valid_cells_model = load_model(os.path.join(root, "valid_cells.h5"))
    final_data_per_table = []

    pixel_data_unchanged = np.copy(pixel_data)

    height, width = pixel_data.shape
    scale = width / 800
    pixel_data = cv2.resize(pixel_data, (800, int(height / scale)))  # 800 width, variable height
    height, width = pixel_data.shape

    hor_lines = horizontal_line_finder(
        height, width, pixel_data
    )  # cannot use margin_lines, but it is fine table cells are usally wider than they are tall
    hor_margin_lines = real_line_margins(hor_lines, 5)

    ver_lines = vertical_line_finder(height, width, pixel_data, hor_margin_lines)
    ver_margin_lines = real_line_margins(ver_lines, 5)

    required_dist = 0.95  # TODO find a number that balances speed and accuracy
    prev_groups = -1
    inferred_hor_lines = []
    inferred_hor_quality = []
    while 1:  # Horizontal
        inferred_hor_lines_temp, inferred_hor_quality_temp = (
            inferred_horizontal_line_finder(
                height, width, pixel_data, required_dist, ver_margin_lines
            )
        )  # inferred
        groups = num_of_groups(
            inferred_hor_lines_temp, 7
        )  # amount of separable groups of inferred lines that exist within the possible inferred lines.
        required_dist += 0.04  # TODO find a number that balances speed and accuracy
        if prev_groups > groups or groups == 0:
            break
        prev_groups = groups
        inferred_hor_lines = inferred_hor_lines_temp
        inferred_hor_quality = inferred_hor_quality_temp

    required_dist = 0.45  # TODO find a number that balances speed and accuracy
    prev_groups = -1
    inferred_ver_lines = []
    inferred_ver_quality = []

    while 1:  # Vertical
        inferred_ver_lines_temp, inferred_ver_quality_temp = (
            inferred_vertical_line_finder(
                height, width, pixel_data, required_dist, 8, hor_margin_lines
            )
        )  # inferred
        groups = num_of_groups(inferred_ver_lines_temp, 10)
        required_dist += 0.015  # TODO find a number that balances speed and accuracy
        if prev_groups > groups or groups == 0:
            break
        prev_groups = groups
        inferred_ver_lines = inferred_ver_lines_temp
        inferred_ver_quality = inferred_ver_quality_temp

    guarenteed_inf_ver, guarenteed_ver_quality = inferred_vertical_line_finder(
        height, width, pixel_data, 0.98, 8, hor_lines
    )  # inject inf_ver that might have been wrongfully removed; Thicker line required USED TO BE .99
    tempv = mean_finder(
        ver_lines,
        ([0] + guarenteed_inf_ver + [width - 1]),
        ([1] + guarenteed_ver_quality + [1]),
        10,
        width,
    )  # TODO find a good number

    ver_lines_final = mean_finder(
        tempv, inferred_ver_lines, inferred_ver_quality, 10, width
    )  # this is precision not resolution add lines to the left and right //TODO find a good precision
    # hor_lines_final = mean_finder(hor_lines, ([0] + inferred_hor_lines + [height-1]), ([1] + inferred_hor_quality + [1]), 7, height) #this is precision not resolution
    hor_lines_final = mean_finder(
        hor_lines,
        ([0] + inferred_hor_lines + [height - 1]),
        ([1] + inferred_hor_quality + [1]),
        7,
        height,
    )

    if 0 not in hor_lines_final:
        hor_lines_final.insert(0, 0)
    if (height - 1) not in hor_lines_final:
        hor_lines_final.append(height - 1)

    table_index = len(final_data_per_table)

    debug_img = cv2.cvtColor((pixel_data * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    for x in ver_lines_final:
        cv2.line(debug_img, (x, 0), (x, height), (0, 255, 0), 1)
    for y in hor_lines_final:
        cv2.line(debug_img, (0, y), (width, y), (255, 0, 0), 1)
    cv2.imwrite(os.path.join(root, f"debug_lines_{table_index}.png"), debug_img)

    conc_col_2D = []
    contains_data, conc_col_2D = concatenate(
        root,
        pixel_data,
        ver_lines_final,
        hor_lines_final,
        conc_col_model,
        valid_cells_model,
    )
    ver_width_line, hor_width_line = lines_with_widths(ver_lines_final, hor_lines_final)

    final_data_per_table = image_to_text(
        pixel_data_unchanged,
        root,
        contains_data,
        conc_col_2D,
        ver_width_line,
        hor_width_line,
        scale,
        ver_lines,
        hor_lines,
    )

    return final_data_per_table


if __name__ == "__main__":
    # count time
    start_main_time = time.time()

    pyth_dir = os.path.dirname(__file__)
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    parser = argparse.ArgumentParser(description="Table Extractor Tool")
    parser.add_argument(
        "--use_double_column_split",
        action="store_true",
        help="Whether to split pages by double column layout",
    )
    parser.add_argument(
        "--use_gap_split",
        action="store_true",
        help="Whether to apply white gap splitting before cell recognition",
    )
    parser.add_argument("--pdf_dir", required=True, help="pdf directory")
    parser.add_argument(
        "--work_dir", required=True, help="main work and output directory"
    )
    parser.add_argument(
        "--first_table_page",
        required=True,
        help="The first page that you want table extraction begins with",
    )
    parser.add_argument(
        "--last_table_page",
        required=True,
        help="The last page that you want table extraction ends with",
    )
    parser.add_argument(
        "--use_yolo",
        required=False,
        help="Use the combined yolo/cnn model to detect tables, default is False",
        default=False,
        action="store_true",
    )
    args = parser.parse_args()

    concatenate_clean = True

    root = os.path.join(pyth_dir, "Table_extract_robust")
    pdf_loc = (args.pdf_dir).lower()
    work_loc = args.work_dir
    start = int(args.first_table_page)
    cap = int(args.last_table_page)
    yolo = args.use_yolo
    use_double_column_split = args.use_double_column_split
    use_gap_split = args.use_gap_split
    if yolo:
        yolo_model_dir = os.path.join(
            pyth_dir, "yolo_helpers", "keras_yolo3", "trained_weights_1915_final.h5"
        )
    pages = convert_from_path(pdf_loc, 300, first_page=start, last_page=cap)
    identify_model = load_model(
        os.path.join(root, "Identification_Models", "stage1.h5")
    )
    identify_model2 = load_model(
        os.path.join(root, "Identification_Models", "stage2.h5")
    )

    TempImages_dir = os.path.join(work_loc, "TempImages")
    try:
        os.makedirs(TempImages_dir)
        print("Directory ", TempImages_dir, " Created ")
    except FileExistsError:
        print("Directory ", TempImages_dir, " already exists")
        print("Cleaning ipxact directory ...")
        if len(os.listdir(TempImages_dir)) != 0:
            for file in os.listdir(TempImages_dir):
                os.remove(os.path.join(TempImages_dir, file))

    print("Multiprocesses start: \n")
    cpu_num = multiprocessing.cpu_count()
    print("CPU NUM", cpu_num)

    #  #load images
    images = []
    for i, image in enumerate(pages):
        img_np = image_handle(image)

        if is_double_column(img_np):  # Auto-detect double-column layout
            if contains_wide_table(img_np):
                print(
                    f"Page {i + start} is double column BUT has a wide table — skip splitting."
                )
                images.append(img_np)
            else:
                print(f"Page {i + start} is true double column. Splitting...")
                slices = split_if_double_column(
                    img_np,
                    save_debug_dir=os.path.join(root, "debug_table_regions"),
                    debug=True,
                    page_num=start + i,
                    slice_idx=0,
                )
                for idx, part in enumerate(slices):
                    images.append(part)
        else:
            images.append(img_np)
        # if use_double_column_split:
        #     if is_double_column(img_np):
        #         print(f"Page {i + start} is detected as double column. Splitting...")
        #         slices = split_if_double_column(img_np, save_debug_dir=os.path.join(root, "debug_table_regions"), debug=True, page_num=start + i, slice_idx=0)
        #         for idx, part in enumerate(slices):
        #             images.append(part)
        #     else:
        #         images.append(img_np)
        # else:
        #     images.append(img_np)

    print("done handling images")
    pool1 = Pool(processes=cpu_num)
    temp_storage = []

    for image_num, image in enumerate(images):
        print("Start Idendifying Tables on Page " + str(image_num + start))
        if yolo:
            temp_result = pool1.apply_async(
                multiprocessing_unit_separate_tables_yolo,
                args=(
                    pdf_loc,
                    image_num + start,
                    image,
                    root,
                    identify_model,
                    identify_model2,
                    yolo_model_dir,
                    work_loc,
                ),
            )
        else:
            temp_result = pool1.apply_async(
                multiprocessing_unit_separate_tables_reg,
                args=(
                    pdf_loc,
                    image_num + start,
                    image,
                    root,
                    identify_model,
                    identify_model2,
                ),
            )
        temp_storage.append(temp_result)
    pool1.close()
    pool1.join()

    print("\n")
    pool2 = Pool(processes=cpu_num)
    all_tables = []
    count = 0
    for tables in temp_storage:
        count += 1
        # print("Start Extracting Content in Table " + str(count))
        # # for i, table_pixel in enumerate(tables.get()):

        # #             left_img, _ = split_by_white_gap_for_table(table_pixel, debug_save=True, save_prefix=f'debug_gap_table_{count}_{i}')
        # #             temp_data_per_table = pool2.apply_async(multiprocessing_unit_identify_cells, args= (left_img, root))
        # #             all_tables.append(temp_data_per_table)

        # split_by_white_gap_for_table
        # for table_pixel in tables.get():
        #     temp_data_per_table = pool2.apply_async(multiprocessing_unit_identify_cells, args= (table_pixel, root))
        #     all_tables.append(temp_data_per_table)
        print("Start Extracting Content in Table", count)
        for i, table_pixel in enumerate(tables.get()):
            if use_gap_split:
                left_img, _ = split_by_white_gap_for_table(
                    table_pixel,
                    debug_save=True,
                    save_prefix=f"debug_gap_table_{count}_{i}",
                )
                temp_data = pool2.apply_async(
                    multiprocessing_unit_identify_cells, args=(left_img, root)
                )
            else:
                temp_data = pool2.apply_async(
                    multiprocessing_unit_identify_cells, args=(table_pixel, root)
                )
            all_tables.append(temp_data)
    pool2.close()
    pool2.join()

    array = []
    for temp in all_tables:
        temp_row = temp.get()
        for cell in temp_row:
            array.append(cell)

    # debug part
    if 0:
        for table in all_tables:
            cv2.imshow("image", table)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    if concatenate_clean:
        cleaned_array = []
        for row in array:
            if len(row) > 2:
                has_extend = False
                for cell in row:
                    if cell == "^ EXTEND":
                        has_extend = True

                if has_extend:
                    for cell_num, cell in enumerate(row):

                        if cell != "^ EXTEND" and cell_num < len(cleaned_array[-1]):
                            cleaned_array[-1][cell_num] += " " + cell
                else:
                    cleaned_array.append(row)

        with open(
            os.path.join(work_loc, "concatenate_table.csv"), "w", newline=""
        ) as f:
            writer = csv.writer(f)
            writer.writerows(cleaned_array)
    end_main_time = time.time()
    total_time = end_main_time - start_main_time
    minutes = float(total_time) / 60
    print("--- %s seconds ---" % total_time)
    print("--- %s minutes ---" % minutes)
