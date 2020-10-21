from PIL import Image
import pytesseract
import statistics
import pdf2image #poppler needs to be added and added to the path variable
import os
import csv
import pdfminer
import cv2
import concurrent.futures
import functools
import copy
import xml.etree.ElementTree as ET

import numpy as np

###########ADVANCED LINE FINDER#########################	
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
                line_dist = 0	
            if(line_dist > width/8):	
                final_out.append(y)  	
                break	
    return final_out	
def vertical_line_finder(height, width, pixel_data): #normal finds black lines	
    final_out = [] 	
    search_dist = 3	
    for x in range(search_dist, width-search_dist):	
        line_dist = 0	
        fails = 0	
        for y in range(height):  	
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
def concatenate(root, pixel_data, ver_lines_final, hor_lines_final):	
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
    conc_col = load_model(os.path.join(root, "conc_col.h5"))	
    im_arr = []	
    for y in range(len(hor_lines_no_dup)-1):	
        for x in range(len(ver_lines_no_dup)-2):	
            top_left = cv2.resize(norm_pixel_data[hor_lines_no_dup[y]:hor_lines_no_dup[y+1], ver_lines_no_dup[x]:ver_lines_no_dup[x+1]], (100, 100)) #these steps makes sure the merge line is in the same place	
            top_right = cv2.resize(norm_pixel_data[hor_lines_no_dup[y]:hor_lines_no_dup[y+1], ver_lines_no_dup[x+1]:ver_lines_no_dup[x+2]], (100, 100))	
            merged_data = cv2.hconcat([top_left,top_right])	
            im_arr.append(merged_data) 	
            if(0):	
                #print(ver_lines_no_dup[x], " ", ver_lines_no_dup[x+2])	
                #print(hor_lines_no_dup[y], " ", hor_lines_no_dup[y+1])	
                temp_data = np.expand_dims(np.array([merged_data]), axis= -1)	
                print(conc_col.predict(temp_data))	
                print("")	
                cv2.imshow('image', pixel_data[hor_lines_no_dup[y]:hor_lines_no_dup[y+1], ver_lines_no_dup[x]:ver_lines_no_dup[x+2]])	
                cv2.waitKey(0)	
                cv2.destroyAllWindows()	
    y_len = len(hor_lines_no_dup)-1	
    x_len = len(ver_lines_no_dup)-2	
    if(not im_arr): #this can occur when there are only 2 vertical lines so that nothing can possibly be concatenated	
        return np.ones((y_len, 1)), np.zeros((y_len, 1)), ver_lines_no_dup, hor_lines_no_dup #assume not concatenated and every cell has data, 1D array	
    im_arr = np.expand_dims(np.array(im_arr), axis= -1)	
    pred = conc_col.predict(im_arr)	
   	
    conc_col_2D = np.zeros((y_len, x_len)) #Y then X	
    contains_data = np.zeros((y_len, x_len+1))	
    for y in range(y_len): 	
        for x in range(x_len): 	
            if(pred[x+y*x_len][0] > .5):	
                conc_col_2D[y][x] = 1	
            if(pred[x+y*x_len][1] > .5):	
                contains_data[y][x] = 1	
            if(pred[x+y*x_len][2] > .5):	
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
########################################################


def vertical_line_crossover(pixel_data): #TODO make scalable with resolution
    g = 97
    merged = False
    while (g < 104): #look 3 to the left and 3 to the right if any line is inconsitant then it is these cells are merged
        iter = 0
        white_pixel = 0
        black_pixel = 0
        while(iter < 100):      
            if((pixel_data[iter,g]) < .5):
                black_pixel += 1
            else:
                white_pixel += 1
            iter += 1
        
        white_pixel /= 100
        black_pixel /= 100
        if(white_pixel > .05 and black_pixel > .05):
            merged = True
            break
        g += 1
    return merged

def line_finder(line_0__row_1, multiple_locs, multiple_min_vals, multiple_max_vals):
    max_val = 0
    for data in multiple_locs:
        for item in data:
            if item > max_val:
                max_val = item

    #left lines.... | | | |    //choose min value
    #right lines...   | | | |  //choose max value
    left_line_arr = [100000 for i in range(max_val+2)] #2 more line than max value, max value is for number of cells
    right_line_arr = [-1 for i in range(max_val+2)] #2 more line than max value, max value is for number of cells

    for i in range(len(multiple_locs)):   
        if(multiple_min_vals[i][line_0__row_1] < left_line_arr[(multiple_locs[i][0])]):
            left_line_arr[(multiple_locs[i][0])] = multiple_min_vals[i][line_0__row_1] #last value not used

        if(multiple_max_vals[i][line_0__row_1] > right_line_arr[(multiple_locs[i][1] + 1)]):
            right_line_arr[(multiple_locs[i][1] + 1)] = multiple_max_vals[i][line_0__row_1] #offset 1, first value not used


    final_line_arr = []
    for i in range(max_val+2):
        temp_data = 0
        count = 0
        if(left_line_arr[i] != 100000 or right_line_arr[i] != -1): #atleast one is valid
            if(left_line_arr[i] != 100000):
                temp_data += left_line_arr[i]
                count += 1
            if(right_line_arr[i] != -1):
                temp_data += right_line_arr[i]
                count += 1

            temp_data /= count
            final_line_arr.append(temp_data)

    return final_line_arr

def preproccessing(x, xmls, imgs, root, dim):
    multiple_min_vals = []
    multiple_max_vals = []

    multiple_row_locs = []
    multiple_col_locs = []
    test_cells = ET.parse(os.path.join(root, type + "xml", xmls[x]))
    data = test_cells.getroot()[0]
    try:
        for num, child in enumerate(data):
            if(num == 0): #here to get table dims
                points = child.attrib["points"]
            else:
                multiple_row_locs.append([int(child.attrib["start-row"]), int(child.attrib["end-row"])])
                multiple_col_locs.append([int(child.attrib["start-col"]), int(child.attrib["end-col"])])

                points = child[0].attrib["points"]
            min_vals = [10000, 10000]
            max_vals = [0, 0]
            temp_str = ""
            ff = False
            for char in points:   
                if(char.isdigit()): 
                    temp_str += char  
                else:
                    if("-" in temp_str):
                        temp_str = "0"
                    if(min_vals[ff] > int(temp_str)):
                        min_vals[ff] = int(temp_str)
                    if(max_vals[ff] < int(temp_str)):
                        max_vals[ff] = int(temp_str)
                    temp_str = ""
                    ff = not ff
            multiple_min_vals.append(min_vals)
            multiple_max_vals.append(max_vals) #parse XML

        img = cv2.imread(os.path.join(root, type + "images", imgs[x]))
        img = img[multiple_min_vals[0][1]:multiple_max_vals[0][1], multiple_min_vals[0][0]:multiple_max_vals[0][0]] #y_min, y_max, x_min, x_max
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        height, width = img.shape
        X_scale = dim/width

        Y_scale = dim/width	
        new_height = int(Y_scale*height)	
        pixel_data = cv2.resize(img,(dim,new_height)) 	
        if(0): ###XML LINE GENERATION	
            cols = line_finder(0, multiple_col_locs, multiple_min_vals[1:], multiple_max_vals[1:])	
            rows = line_finder(1, multiple_row_locs, multiple_min_vals[1:], multiple_max_vals[1:])	
            for i in range(len(cols)):	
                cols[i] = int((cols[i] - multiple_min_vals[0][0])*X_scale) #shift cols to table loc	
                if(cols[i] < 0):	
                    cols[i] = 0	
                if(cols[i] > dim - 1):	
                    cols[i] = dim - 1	
            for i in range(len(rows)):	
                rows[i] = int((rows[i] - multiple_min_vals[0][1])*Y_scale) #shift rows to table loc	
                if(rows[i] < 0):	
                    rows[i] = 0	
                if(rows[i] > new_height - 1):	
                    rows[i] = dim - 1   	
        else: ###ADVANCED LINE GENERATION	
            height, width = pixel_data.shape	
            scale = width/800	
            pixel_data = cv2.resize(pixel_data,(800, int(height/scale)))  #800 width, variable height	
            height, width = pixel_data.shape	
            print(pixel_data.shape)	
            hor_lines = horizontal_line_finder(height, width, pixel_data)	
            ver_lines = vertical_line_finder(height, width, pixel_data)	
            hor_margin_lines = real_line_margins(hor_lines, 5)	
            ver_margin_lines = real_line_margins(ver_lines, 5)	
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
                #print("INF HOR ", inferred_hor_lines)	
            required_dist = .75 #TODO find a number that balances speed and accuracy	
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

            cols = []
            rows = []
            start = ver_lines_final[0]
            for i in range(1, len(ver_lines_final)):
                if(ver_lines_final[i] != ver_lines_final[i-1]+1):
                    cols.append(int((start + ver_lines_final[i-1])/2))
                    start = ver_lines_final[i] 
            cols.append(int((start + ver_lines_final[-1])/2))

            start = hor_lines_final[0]
            for i in range(1, len(hor_lines_final)):
                 if(hor_lines_final[i] != hor_lines_final[i-1]+1):
                    rows.append(int((start + hor_lines_final[i-1])/2))
                    start = hor_lines_final[i] 
            rows.append(int((start + hor_lines_final[-1])/2))

    except:
        print("FAILURE")
        return 1, None, None, None, None, None

    col_min_max = []	
    row_min_max = []	
    for i in range(1, len(multiple_min_vals)):	
        col_min_max.append(((multiple_min_vals[i][0]-multiple_min_vals[0][0])*X_scale, (multiple_max_vals[i][0]-multiple_min_vals[0][0])*X_scale))	
        row_min_max.append(((multiple_min_vals[i][1]-multiple_min_vals[0][1])*Y_scale, (multiple_max_vals[i][1]-multiple_min_vals[0][1])*Y_scale))



    return 0, pixel_data, cols, rows, col_min_max, row_min_max

def training_data_concatenate_cols(img, cols, col_min_max, rows, row_min_max, DATA_concatenate, LABELS_concatenate):
    norm_image = cv2.normalize(img, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    amount_cols = len(cols) - 1
    amount_rows = len(rows) - 1

    amount_cols_conc = amount_cols - 1
    amount_rows_conc = amount_rows - 1

    if(amount_cols_conc < 0 or amount_rows_conc < 0):
        return

    #THESE ARE LINE POSs NOT CELL
    col_conc = np.zeros((amount_rows, amount_cols_conc)) #this matrix is rows by col_lines (| | | => | |)
    contains_data = np.zeros((amount_rows, amount_cols))

    for i in range(len(col_min_max)): #create matrixes
        c_m_m = col_min_max[i]
        r_m_m = row_min_max[i]

        for x in range(1, len(cols)-1): #remove boundries
            col = cols[x]
            if(col > c_m_m[0] and col < c_m_m[1]): #overlap
                for y in range(len(rows)-1):
                    row_min = rows[y]
                    row_max = rows[y+1]
                    if(row_max > r_m_m[0] and row_min < r_m_m[1]):
                        col_conc[y][x-1] = 1
        
        for x in range(len(cols)-1):
            col_min = cols[x]
            col_max = cols[x+1]
            if(col_max > c_m_m[0] and col_min < c_m_m[1]):
                for y in range(len(rows)-1):
                    row_min = rows[y]
                    row_max = rows[y+1]
                    if(row_max > r_m_m[0] and row_min < r_m_m[1]):
                        contains_data[y][x] = 1

    #print(col_conc)
    #print(contains_data)
    for x in range(amount_cols-1):
        for y in range(amount_rows-1):
            top_left = cv2.resize(norm_image[rows[y]:rows[y+1], cols[x]:cols[x+1]], (100, 100)) #these steps makes sure the merge line is in the same place
            top_right = cv2.resize(norm_image[rows[y]:rows[y+1], cols[x+1]:cols[x+2]], (100, 100))
            merged_data = cv2.hconcat([top_left,top_right])

            second_check = vertical_line_crossover(merged_data)

            label_out = [(col_conc[y][x] and second_check), contains_data[y][x], contains_data[y][x+1]] #CONC, LEFT contains, RIGHT, contains
            
            DATA_concatenate.append(merged_data) 
            #DATA_concatenate.append([top_right, top_left, bot_left, bot_right]) 
            
            LABELS_concatenate.append(label_out)
            if(0): #and 1 in label_out):
                print(label_out)
                cv2.imshow('image',merged_data)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
#############################
root = r"C:\Users\Zach\Downloads\Table_extract_robust"
type = "modern_" #"modern_" or "old_"
dim = 800

DATA_rows = []
LABELS_rows = []

DATA_concatenate_cols = []
LABELS_concatenate_cols = []

xmls = os.listdir(os.path.join(root, type + "xml"))
imgs = os.listdir(os.path.join(root, type + "images"))

for x in range(0, len(imgs)): 
    print(x)
    failure, img, cols, rows, col_min_max, row_min_max = preproccessing(x, xmls, imgs, root, dim) #proportional

    if(failure):
        continue

    if(0):
        for i in range(len(rows)):
            cv2.line(img, (-1, rows[i]), (dim, rows[i]), (0,0,0), 2)
        for i in range(len(cols)):
            cv2.line(img, (cols[i], -1), (cols[i], dim), (0,0,0), 2)
        cv2.imshow('image',img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    training_data_concatenate_cols(img, cols, col_min_max, rows, row_min_max, DATA_concatenate_cols, LABELS_concatenate_cols)
        


DATA_rows = np.expand_dims(np.array(DATA_rows), axis= -1)
LABELS_rows = np.array(LABELS_rows)
np.save(os.path.join(root, "DATA_rows"), DATA_rows)
np.save(os.path.join(root, "LABELS_rows"), LABELS_rows)


if(1):
    DATA_concatenate_cols = np.expand_dims(DATA_concatenate_cols, axis= -1)
    LABELS_concatenate_cols = np.array(LABELS_concatenate_cols)
    np.save(os.path.join(root, "DATA_concatenate_cols"), DATA_concatenate_cols)
    np.save(os.path.join(root, "LABELS_concatenate_cols"), LABELS_concatenate_cols)




