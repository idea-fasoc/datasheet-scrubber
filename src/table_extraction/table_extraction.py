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
from keras.models import load_model

from pdf2image import convert_from_path ##poppler needs to be added and added to the path variable
from numba import jit
import time
import multiprocessing


def table_identifier(pixel_data, root, identify_model, identify_model2):
    #start_time = time.time()
    pTwo_size = 600
    X_size = 800
    Y_size = 64
    cuts_labels = 60
    label_precision = 8
    y_fail_num = 2

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
    data = identify_model.predict(slices)
        
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


 

    groups2 = []
    for group in groups:
        temp_final_original = cv2.resize(original_pixel_data[group[0]:group[1]], (pTwo_size, pTwo_size))
        temp_final = np.expand_dims(np.expand_dims(temp_final_original,  axis = 0), axis = -1)
        data_final = identify_model2.predict(temp_final)

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

    final_splits = []
    for iter in range(len(groups)):
        final_split = original_pixel_data_255[groups[iter][0]:groups[iter][1], groups2[iter][0]:groups2[iter][1]]
        final_splits.append(final_split)
        if(0):
            cv2.imshow('image', final_split)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    #print("--- %s seconds identify tables ---" % (time.time() - start_time))
    #time.sleep(1)
    return final_splits

def mean_finder_subroutine(real, infered, infered_quality, precision, group_start, n, final_dist): #TODO BROKEN FIX
    bool_add = True
    for a in real:    
        if(a > (infered[group_start] - precision)  and a < (infered[n] + precision)): #a real line is within y units of the group
            bool_add = False
    if(bool_add):
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
            
            threshold = (max_value * .99)
            first_value = -1
            for iter in range(len(average_array)):
                if(first_value == -1 and average_array[iter] > threshold):
                    first_value = iter
                if(average_array[iter] > threshold):
                    last_value = iter
            line_loc = int((first_value+last_value)/2 + infered[group_start])  
        else:
            line_loc = int((infered[n] + infered[group_start])/2)
        final_dist.append(line_loc)
    return

def mean_finder(real, infered, infered_quality_raw, precision, max_dim_1d):
    infered_quality = [0 for i in range(max_dim_1d)]
    for i in range(len(infered)):
        infered_quality[infered[i]] = infered_quality_raw[i]
    n = 0
    group_start = 0
    final_dist = []
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
    groups = 0
    if(len(infered) > 0):
        groups = 1
    for a in range(len(infered)-1):
        if(infered[a+1] > infered[a]+i):
            groups += 1
    return groups

def horizontal_line_finder(height, width, pixel_data): #normal finds black lines
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
    final_out = [] 
    search_dist = 3
    for x in range(search_dist, width-search_dist):
        line_dist = 0
        fails = 0
        for y in range(height):
            if(y not in hor_margin_lines):
                max_left = 0
                max_right = 0
                for x2 in range(x-search_dist,x):
                    if((pixel_data[y,x2]) > max_left):
                        max_left = pixel_data[y,x2]

                for x2 in range(x+1,x+search_dist+1):
                    if((pixel_data[y,x2]) > max_right):
                        max_right = pixel_data[y,x2]

                if((max_left/2+max_right/2 - pixel_data[y,x]) > 30): #these are 8 bit ints need to calculate like this to avoid overflow
                    line_dist += 1
                    if(fails > 0):
                        fails -= 1
                elif(fails < 1): #tolerate x fails
                    fails += height/8
                else:
                    line_dist = 0 

                if(line_dist > height/8):
                    final_out.append(x)  
                    break      
    return final_out

def real_line_margins(lines, margin_size_pixels):
    margin_lines = []
    for line in lines:
        for i in range(line-margin_size_pixels, line+margin_size_pixels):
            if(i not in margin_lines and i >= lines[0] and i <= lines[-1]):
                margin_lines.append(i)
    return margin_lines
     
def inferred_horizontal_line_finder(height, width, pixel_data, required_dist, ver_margin_lines): #finds white lines
    past_array_depth = int(width/100)
    required_distance = (width) * required_dist

    inferred_line_dists = []  
    inferred_quality = []
    inferred_line_thickness = 0
    for y in range(height):
        inferred_line_dist = 0 
        inferred_line_dist_max = 0

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

        if(inferred_line_dist_max > required_distance): #a ratio of the outer verticle lines
            inferred_line_thickness += 1
        else:
            inferred_line_thickness = 0

        if(inferred_line_thickness >=  1):
            inferred_line_dists.append(y)
            inferred_quality.append(inferred_line_dist_max/width)
    
    return inferred_line_dists, inferred_quality

def inferred_vertical_line_finder(height, width, pixel_data, required_dist, required_thick, hor_margin_lines):
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
    norm_pixel_data = cv2.normalize(pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    ver_lines_no_dup = []
    hor_lines_no_dup = []

    start = ver_lines_final[0]
    for i in range(1, len(ver_lines_final)):
        if(ver_lines_final[i] != ver_lines_final[i-1]+1):
            ver_lines_no_dup.append(int((start + ver_lines_final[i-1])/2))
            start = ver_lines_final[i] 
    ver_lines_no_dup.append(int((start + ver_lines_final[-1])/2))

    start = hor_lines_final[0]
    for i in range(1, len(hor_lines_final)):
         if(hor_lines_final[i] != hor_lines_final[i-1]+1):
            hor_lines_no_dup.append(int((start + hor_lines_final[i-1])/2))
            start = hor_lines_final[i] 
    hor_lines_no_dup.append(int((start + hor_lines_final[-1])/2))


    im_arr = []
    for y in range(len(hor_lines_no_dup)-1):
        for x in range(len(ver_lines_no_dup)-2):
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

    y_len = len(hor_lines_no_dup)-1
    x_len = len(ver_lines_no_dup)-2
    if(not im_arr): #this can occur when there are only 2 vertical lines so that nothing can possibly be concatenated
        return np.ones((y_len, 1)), np.zeros((y_len, 1)) #assume not concatenated and every cell has data, 1D array


    im_arr = np.expand_dims(np.array(im_arr), axis= -1)
    helper_output = merging_helper(im_arr)
    pred = conc_col_model.predict(im_arr)
    pred2 = valid_cells_model.predict(im_arr)
   

    conc_col_2D = np.zeros((y_len, x_len)) #Y then X
    contains_data = np.zeros((y_len, x_len+1))
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
    ver_width_line = []
    hor_width_line = []

    start = ver_lines_final[0]
    for i in range(1, len(ver_lines_final)):
        if(ver_lines_final[i] != ver_lines_final[i-1]+1):
            ver_width_line.append([start, ver_lines_final[i-1]-start+1])
            start = ver_lines_final[i] 
    ver_width_line.append([start, ver_lines_final[-1]-start+1])

    start = hor_lines_final[0]
    for i in range(1, len(hor_lines_final)):
         if(hor_lines_final[i] != hor_lines_final[i-1]+1):
            hor_width_line.append([start, hor_lines_final[i-1]-start+1])
            start = hor_lines_final[i] 
    hor_width_line.append([start, hor_lines_final[-1]-start+1])
    return ver_width_line, hor_width_line

def hor_split(x_s, x_e, y_s, y_e, pixel_data_unchanged):
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

    for iter_num, iter in enumerate(white_lines):
        if(iter == int(FF)):
            temp_count += 1
        else:
            temp_count = 0

        if(temp_count > 3 + (y_e - y_s)/30):# Adjust this if its not working properly
            wbw_count += 1
            temp_count = 0
            FF = not FF
            if(wbw_count == 3):
                split_loc = iter_num + y_s

    return (wbw_count >= 4), split_loc

def image_to_text(pixel_data_unchanged, root, contains_data, conc_col_2D, ver_width_line, hor_width_line, scale, ver_lines, hor_lines):
    ver_scaled = []
    hor_scaled = []
    real_ver_lines = []
    real_hor_lines = []

    for i in ver_width_line:
        ver_scaled.append([int(i[0]*scale), int(i[1]*scale)+1])

    for i in hor_width_line:
        hor_scaled.append([int(i[0]*scale), int(i[1]*scale)+1])
    
    for i in ver_lines:
        real_ver_lines.append(int(i * scale))
    
    for i in hor_lines:
        real_hor_lines.append(int(i * scale))

    # debug
    if(0):
        height, width = pixel_data_unchanged.shape
        print(height)
        for ver_line in ver_scaled:
            print(ver_line)
            cv2.line(pixel_data_unchanged, (ver_line[0],0), (ver_line[0], height), (0,255,0), 4)
        for hor_line in hor_scaled:
            cv2.line(pixel_data_unchanged, (0, hor_line[0]), (width, hor_line[0]), (0,255,0), 4)
        
        cv2.imshow("line", pixel_data_unchanged)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        print(height)
        for ver_line in real_ver_lines:
            print(ver_line)
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

    data_array = [[["" for k in range(2)] for i in range(len(contains_data[0]))] for j in range(len(contains_data))]
    #print(data_array)

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

            y_merge = False #can only merge 1 line
            if(y < len(hor_scaled)-1 and y > 0): #LOOK TO THE PAST
               y_merge = horizontal_line_crossover(hor_scaled[y][0]+int(hor_scaled[y][1]/2), ver_scaled[x][0]+ver_scaled[x][1], ver_scaled[temp_x+1][0], pixel_data_unchanged)

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
                #loc2 = os.path.join(root, "TempImages", "i_B" + str(y) +"_" + str(x) + ".jpg")
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

            if(y_merge):
                data_array[y+y_SPLIT_extend][x][0] = "^ EXTEND"
                data_array[y+y_SPLIT_extend][x][1] = [-1, -1, -1, -1]
             
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
    #print(data_array)
    ####ARRAY CLEANUP
    
    cleaned_data_array = []
    if(len(data_array) > 0):
        row_valid = [False for y in range(len(data_array))]
        col_valid = [False for x in range(len(data_array[0]))]


        for y in range(len(data_array)):
            for x in range(len(data_array[0])):
                #print(data_array[y][x])
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
        #print(final_merge)
        return final_merge
    
    real_intervals = []
    interval_it = 0
    real_intervals.append([0, real_hor_lines[0]])
    while(interval_it < (len(real_hor_lines) - 1)):
        real_intervals.append([real_hor_lines[interval_it], real_hor_lines[interval_it + 1]])
        interval_it += 1
    real_intervals.append([real_hor_lines[interval_it], height])
    #print(real_intervals)

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
    
    row_it = 0
    while(row_it < len(row_intervals)):
        #print(row_intervals[row_it])
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
        # print(temp_merge)
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
 
#def multiprocessing_unit(image_num, image, root, identify_model, identify_model2, conc_col_model, valid_cells_model):
def multiprocessing_unit_separate_tables(image_num, image, root):
    #load_model now in seperating processes
    #print("entered_tables")
    identify_model = load_model(os.path.join(root, r"Identification_Models", "stage1.h5"))
    identify_model2 = load_model(os.path.join(root, r"Identification_Models", "stage2.h5"))

    #page_num = image_num + start
    #print("\n\nStarting page: ", page_num)

    image = np.array(image)	
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    temp_pixel_data = table_identifier(image, root, identify_model, identify_model2)
    return temp_pixel_data

def multiprocessing_unit_identify_cells(pixel_data, root):
    #print("entered_cells")
    conc_col_model = load_model(os.path.join(root, "conc_col.h5"))
    valid_cells_model = load_model(os.path.join(root, "valid_cells.h5"))
    final_data_per_table = []

    pixel_data_unchanged = np.copy(pixel_data)

    height, width = pixel_data.shape
    scale = width/800
    pixel_data = cv2.resize(pixel_data,(800, int(height/scale)))  #800 width, variable height
    height, width = pixel_data.shape

    hor_lines = horizontal_line_finder(height, width, pixel_data) #cannot use margin_lines, but it is fine table cells are usally wider than they are tall
    hor_margin_lines = real_line_margins(hor_lines, 5)
        
    ver_lines = vertical_line_finder(height, width, pixel_data, hor_margin_lines)
    ver_margin_lines = real_line_margins(ver_lines, 5)

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

    guarenteed_inf_ver, guarenteed_ver_quality = inferred_vertical_line_finder(height, width, pixel_data, .98, 8, hor_lines) #inject inf_ver that might have been wrongfully removed; Thicker line required USED TO BE .99
    tempv = mean_finder(ver_lines, ([0] + guarenteed_inf_ver  + [width-1]), ([1] + guarenteed_ver_quality + [1]), 10, width) #TODO find a good number   

    ver_lines_final = mean_finder(tempv, inferred_ver_lines, inferred_ver_quality, 15, width) #this is precision not resolution add lines to the left and right //TODO find a good precision
    hor_lines_final = mean_finder(hor_lines, ([0] + inferred_hor_lines + [height-1]), ([1] + inferred_hor_quality + [1]), 7, height) #this is precision not resolution

    conc_col_2D = []
    contains_data, conc_col_2D = concatenate(root, pixel_data, ver_lines_final, hor_lines_final, conc_col_model, valid_cells_model)
    ver_width_line, hor_width_line = lines_with_widths(ver_lines_final, hor_lines_final)

    final_data_per_table = image_to_text(pixel_data_unchanged, root, contains_data, conc_col_2D, ver_width_line, hor_width_line, scale, ver_lines, hor_lines)
    return final_data_per_table



#######################START########################
if __name__ == '__main__':
    # count time
    start_main_time = time.time()

    pyth_dir = os.path.dirname(__file__)
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2'
    parser = argparse.ArgumentParser(description='Table Extractor Tool')
    parser.add_argument('--weight_dir', required=True, help='weight directory')
    parser.add_argument('--pdf_dir', required=True, help='pdf directory')
    parser.add_argument('--work_dir', required=True, help='main work and output directory')
    parser.add_argument('--first_table_page', required=True, help='The first page that you want table extraction begins with')
    parser.add_argument('--last_table_page', required=True, help='The last page that you want table extraction ends with')
    args = parser.parse_args()

    concatenate_clean = True

    root = args.weight_dir
    #root = r"/Users/Renee/Desktop/research/Data_Scrubber/Table_extract_robust"
    pdf_loc = (args.pdf_dir).lower()
    #pdf_loc = r"/Users/Renee/Desktop/research/Data_Scrubber/Table_extract_robust/test_pdfs/test1.pdf"
    #print(pdf_loc)
    start = int(args.first_table_page)
    #start = 1
    cap = int(args.last_table_page)
    #cap = 8
    pages = convert_from_path(pdf_loc, 300, first_page=start, last_page=cap)

    TempImages_dir = os.path.join(args.work_dir, "TempImages")
    #TempImages_dir = os.path.join(r"/Users/Renee/Desktop/work_output", "TempImages")
    try:
        os.makedirs(TempImages_dir)
        print("Directory " , TempImages_dir ,  " Created ") 
    except FileExistsError:
        print("Directory " , TempImages_dir ,  " already exists")
        print("Cleaning ipxact directory ...")
        if len(os.listdir(TempImages_dir)) != 0:
            for file in os.listdir(TempImages_dir):
                os.remove(os.path.join(TempImages_dir,file))

    print("Multiprocesses start: \n")

    cpu_num = multiprocessing.cpu_count()
    pool1 = multiprocessing.Pool(processes= cpu_num)
    temp_storage = []
    for image_num, image in enumerate(pages):
        print("Start Idendifying Tables on Page " + str(image_num + start))
        temp_result = pool1.apply_async(multiprocessing_unit_separate_tables, args= (image_num, image, root))
        temp_storage.append(temp_result)
    pool1.close()
    pool1.join()

    print("\n")

    pool2 = multiprocessing.Pool(processes= cpu_num)
    all_tables = []
    count = 0
    for tables in temp_storage:
        count += 1
        print("Start Extracting Content in Table " + str(count))
        for table_pixel in tables.get():
            #print(table_pixel)
            temp_data_per_table = pool2.apply_async(multiprocessing_unit_identify_cells, args= (table_pixel, root))
            all_tables.append(temp_data_per_table)
    pool2.close()
    pool2.join()

    array = []
    for temp in all_tables:
        temp_row = temp.get()
        #print(temp_tables)
        for cell in temp_row:
            array.append(cell)

    #debug part
    if(0):
        print(len(all_tables))
        for table in all_tables:
            cv2.imshow('image', table)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

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
    
        with open(os.path.join(args.work_dir, "concatenate_table.csv"), "w", newline="") as f:
        #with open(os.path.join(r"/Users/Renee/Desktop/work_output", "concatenate_table.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(cleaned_array)
    
    print("--- %s seconds ---" % (time.time() - start_main_time))
