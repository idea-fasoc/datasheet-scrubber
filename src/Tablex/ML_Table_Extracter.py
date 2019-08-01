from PIL import Image
import pytesseract
import statistics
import pdf2image #poppler needs to be added and added to the path variable
import os
import csv
import pdfminer
import cv2
import multiprocessing
import functools
import copy
from ML import table_split


def mean_finder(real, infered, precision):
    ###find the center line in groups
    n = 0
    group_start = 0
    final_dist = []
    while((n+1) < len(infered)):
        if (infered[n+1] > (infered[n]+precision)): #the distance needs to be within x units to be apart of the group
            bool_add = True
            for a in real:              
                if(a > (infered[group_start] - precision)  and a < (infered[n] + precision)): #a real line is within y units of the group
                    bool_add = False 
                    
            if(bool_add):
                temp_array = infered[group_start:n+1]
                final_dist.append(int(statistics.mean(temp_array))) #add the mean line

            group_start = n+1
        n += 1

    try: ##one final dump required
        bool_add = True
        for a in real:              
            if(abs(infered[group_start] - a) < precision or abs(infered[n] - a) < precision): #a real line is within y units of the group
                bool_add = False
        if(bool_add):
            temp_array = infered[group_start:n+1] 
            final_dist.append(int(statistics.mean(temp_array)))
    except:
       pass##########################

    final_dist += real
    final_dist.sort()
    return final_dist


def inferred_vertical_line_finder(y_pos, x_pos, pixel_data, resolution, required_dist, thick_div, hor_lines):
    inver_line_dists = []
    inferred_line_thickness = 0
    y_dist = (y_pos[1] - y_pos[0]) * required_dist
    for x in range(x_pos[0], x_pos[1]):
        line_dist = 0
        line_dist_max = 0

        y = y_pos[0]
        while(y < y_pos[1]):
            line_dist += 1
          
            if((y not in hor_lines) and (pixel_data[x,y][0] + pixel_data[x,y][1] + pixel_data[x,y][2] < 255)): #current is black
                line_dist = 0

            if(line_dist > line_dist_max):
                    line_dist_max = line_dist

            y += 1

        if(line_dist_max > y_dist):
            inferred_line_thickness += 1
        else:
            inferred_line_thickness = 0

        if(inferred_line_thickness >= resolution/thick_div):
            inver_line_dists.append(x)
    
    return inver_line_dists


def inferred_horizontal_line_finder(size, pixel_data, resolution, ver_lines_final, start, end, real_ver): #finds white lines
    y = 0
    #print(real_ver)
    inferred_line_dists = []
     
    inferred_line_thickness = 0

    for space_iter in range(len(start)):
        for y in range(start[space_iter], end[space_iter]):

            inferred_line_dist = 0 
            inferred_line_dist_max = 0

            past_array = [0 for i in range(int(resolution/6))] #### Together these find the amount of black values in the last y squares
            black_encountered = 0 ##################
        
            if(len(ver_lines_final[space_iter]) > 0): #needed for segements without any verticle lines
                x = ver_lines_final[space_iter][0]
            
                while(x < ver_lines_final[space_iter][-1]):
                    inferred_line_dist += 1

                    if(x not in real_ver[space_iter]): #skip over verticle lines
                        if(pixel_data[x,y][0] + pixel_data[x,y][1] + pixel_data[x,y][2] < 255): #current is black
                            if(past_array[x%int(resolution/6)] == 0):  #past is white
                                black_encountered += 1
                            past_array[x%int(resolution/6)] = 1
                        else: #current is white
                            if(past_array[x%int(resolution/6)] == 1): #past is black
                                black_encountered -= 1
                            past_array[x%int(resolution/6)] = 0

                        if(black_encountered >= (resolution/150)):
                            #inferred_line_dist_max = 0 
                            inferred_line_dist = 0
                            #pixel_data[x,y] = (0,255,0) #Line ended DEBUG
                    #else:
                        #print("herex")

                    if(inferred_line_dist > inferred_line_dist_max):
                            inferred_line_dist_max = inferred_line_dist

                    x += 1

                required_distance = (ver_lines_final[space_iter][-1] - ver_lines_final[space_iter][0]) * .9 #must be 90% of the total distance

                if(inferred_line_dist_max > required_distance): #a ratio of the outer verticle lines
                    inferred_line_thickness += 1
                else:
                    inferred_line_thickness = 0

                if(inferred_line_thickness >= resolution/300):
                    inferred_line_dists.append(y)
    
    return inferred_line_dists


def space_finder(size, pixel_data, resolution): #finds white spaces
    y = 0
    hor_line_dists = []
    final_out = []
    for y in range(size[1]):
        line_dist = 0
        line_dist_max = 0
        for x in range(size[0]):
            if((pixel_data[x,y][0] + pixel_data[x,y][1] + pixel_data[x,y][2]) > 600):
                line_dist += 1
            else:
                line_dist = 0 
               
            if(line_dist > line_dist_max):
                    line_dist_max = line_dist

        hor_line_dists.append(line_dist_max)


    thickness = 0
    for z in range(len(hor_line_dists)):
        if(hor_line_dists[z] > .9 * size[0]):
            thickness += 1 
        else:
            thickness = 0

        if(thickness > resolution/100):
                final_out.append(z-1)
                
    return final_out


def horizontal_line_finder(size, pixel_data, resolution, start, end): #normal finds black/white lines, other finds white spaces
    y = 0
    hor_line_dists = []
    final_out = []
    for iter in range(len(start)):
        for y in range(start[iter], end[iter]):
            line_dist = 0
            line_dist_max = 0
            for x in range(size[0]):
                if((pixel_data[x,y][0] + pixel_data[x,y][1] + pixel_data[x,y][2]) < 500):
                    line_dist += 1
                else:
                    line_dist = 0 
               
                if(line_dist > line_dist_max):
                        line_dist_max = line_dist

            if(line_dist_max > 1.5*resolution):
                final_out.append(y)
    
    return final_out


def vertical_line_finder(y_pos, size, pixel_data, resolution):
    ver_lines = []

    if(y_pos[1] - y_pos[0] > 3*resolution): #allows for very small tables to work, caps size
        required_size = resolution / 2
    else:
        required_size = (y_pos[1] - y_pos[0]) / 6
    
    for x in range(size[0]):
        line_dist = 0
        line_dist_max = 0

        y = y_pos[0]
        while(y < y_pos[1]):
            if((pixel_data[x,y][0] + pixel_data[x,y][1] + pixel_data[x,y][2]) < 500):
                line_dist += 1
            else:
                line_dist = 0 
                
            if(line_dist > line_dist_max):
                    line_dist_max = line_dist

            y += 1

        if(line_dist_max > required_size):
            ver_lines.append(x)
    
    return ver_lines


def check_box(start, end, pixel_data):
    y = start[1]
    count = 0
    while(y < end[1]):
        x = start[0]
        while(x < end[0]): 
            if((pixel_data[x,y][0] + pixel_data[x,y][1] + pixel_data[x,y][2]) < 255): #this counts the amount of rows with text
                count += 1
                break
            x += 1
        y += 1

    useless = False
    if(count <= 6): #require 6 rows // this is to remove the  "--" character
       useless = True
    
    #####debug
    y = start[1]
    if(useless):
        while(y < end[1]):
            x = start[0]
            while(x < end[0]): 
                pixel_data[x,y] = (0,255,255)
                x += 1
            y += 1
    ######

    return useless


def image_to_text(start, end, img, i, j, Root):
    loc = os.path.join(Root, "ModImages", "TempImages", "i" + str(i) +"_" + str(j) + ".jpg")
    slice = img.crop((start[0], start[1], end[0], end[1]))
    slice = slice.convert('L') # convert image to black and white
    slice.save(loc)

    #slice2 = cv2.imread(loc)
    #slice2 = cv2.medianBlur(slice2, 3)
    #retval, slice2 = cv2.threshold(slice2,220,255,cv2.THRESH_BINARY)
    #cv2.imwrite(loc, slice2)

    return pytesseract.image_to_string(loc, config='--psm 7')


def vertical_line_crossover(i, ver_lines, y_s, y_e, pixel_data): #TODO make scalable with resolution
    lines_to_skip = 0
    while(1):
        g = -3
        merged = False
        while (g < 4): #look 3 to the left and 3 to the right if any line is inconsitant then it is these cells are merged
            iter = y_s
            white_pixel = 0
            black_pixel = 0
            while(iter < y_e):      
                if((pixel_data[ver_lines[i+1] + g,iter][0] + pixel_data[ver_lines[i+1] + g,iter][1] + pixel_data[ver_lines[i+1] + g,iter][2]) < 255):
                    black_pixel += 1
                else:
                    white_pixel += 1
                #pixel_data[ver_lines[i] + g,iter] = (255,0,255) #debug##############
                iter += 1

            white_pixel /= ((1 + y_e - y_s))
            black_pixel /= ((1 + y_e - y_s))
        
            if(white_pixel > .05 and black_pixel > .02): #more than 2% of the pixels are black and more than 5% are white// white is larger so it doesnt mess up when the box perimeters are not continuous
                merged = True
                break
            g += 1

        if(merged):
            lines_to_skip += 1
            i += 1 #jump to new thick line
            while(i + 1 < len(ver_lines) and ver_lines[i] == (ver_lines[i+1] - 1)): #go to the right of thick lines
                i += 1
            if(i == len(ver_lines) - 1):
                return lines_to_skip, i - 1 #i - 1 to fix out of range
        else:
            #print(lines_to_skip, " ", i)
            return lines_to_skip, i


def horizontal_line_crossover(j, hor_lines, x_s, x_e, pixel_data):
    iter = x_s
    white_pixel = 0
    black_pixel = 0

    wbw = 0 #white_black_white
    while(iter < x_e):      
        if((pixel_data[iter,hor_lines[j+1]][0] + pixel_data[iter,hor_lines[j+1]][1] + pixel_data[iter,hor_lines[j+1]][2]) < 255):
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
        
    if(white_pixel > .05 and black_pixel > .02 and wbw >= 3): #more than 2% of the pixels are black and more than 5% are white// white is larger so it doesnt mess up when the box perimeters are not continuous
        j += 1 #jump to new thick line
        while(j + 1 < len(hor_lines) and hor_lines[j] == (hor_lines[j+1] - 1)): #go to the right of thick lines
            j += 1
        if(j == len(hor_lines) - 1):
            return True, j - 1 #i - 1 to fix out of range
        else:
            return True, j
    else:
        return False, j
        

def horizontal_line_split(j, x_start, x_end, hor_line, pixel_data, resolution): #TODO make scalable with resolution //Only can split 2 rows

    y_iter = hor_line[j] + 1

    y_start_const = hor_line[j] + 1

    whiteBlack_array = [1 for i in range(hor_line[j+1] - (hor_line[j] + 1))] ##point of part 1

    while(y_iter < hor_line[j+1]): #finds which lines contains black values
        iter = x_start

        past_array = [0 for i in range(int(resolution/6))]
        black_encountered = 0
        while(iter < x_end):      
            if(pixel_data[iter,y_iter][0] + pixel_data[iter,y_iter][1] + pixel_data[iter,y_iter][2] < 255): #current is black
                if(past_array[iter%int(resolution/6)] == 0):  #past is white
                    black_encountered += 1
                past_array[iter%int(resolution/6)] = 1
            else: #current is white
                if(past_array[iter%int(resolution/6)] == 1): #past is black
                    black_encountered -= 1
                past_array[iter%int(resolution/6)] = 0

            if(black_encountered > (resolution/300)): #2 black squares
                whiteBlack_array[y_iter-y_start_const] = 0
                break

            iter += 1
        y_iter += 1

    required_thickness = resolution/60

    ###########################part 2
    black0_pass = False
    white_pass = False
    black1_pass = False

    white_count = 0
    black_count = 0

    white_line_start = 0
    white_line_end = 0

    for number, iter in enumerate(whiteBlack_array):
        if(black0_pass and not white_pass):
            if(iter == 1):
                white_count += 1
            else:
                if(white_count > required_thickness):
                    white_pass = True
                    white_line_end = number
                white_count = 0
        else: #for black0_pass and black1_pass
            if(iter == 0):
                black_count += 1
            else:
                if(black_count > required_thickness):
                    if(black0_pass):
                        black1_pass = True
                    else:
                        black0_pass = True
                        white_line_start = number
                black_count = 0  

    line_split_loc = int((white_line_start + white_line_end)/2+y_start_const)
    split = False
    if(white_line_end > white_line_start):
        split = True
    
    return split, line_split_loc


def table_locator(white_hor, table_loc):
    start_array = []
    end_array = []

    bool_array = []
    for iter in table_loc:
        if(iter >= .5):
            bool_array.append(True)
        else:
            bool_array.append(False)

    for iter in range(3, len(table_loc)): #removes single and double Falses
        if((bool_array[iter] and bool_array[iter-3])):
            bool_array[iter-1] = True
            bool_array[iter-2] = True

    iter = 0
    last_line = False
    while(iter < len(bool_array)):
        if(last_line != bool_array[iter]):
            if(bool_array[iter] == True):
                start_array.append((30*iter) + 75)
            else:
                end_array.append((30*iter) + 75)
        last_line = bool_array[iter]
        iter += 1

    
    for iter in range(len(start_array)):
        abs_dist = []
        for hor_iter in white_hor:
            abs_dist.append(abs(hor_iter - start_array[iter])) 
        if(len(abs_dist) > 0 and min(abs_dist) < 100):
            start_array[iter] = white_hor[abs_dist.index(min(abs_dist))] #return closest white line

    for iter in range(len(end_array)):
        abs_dist = []
        for hor_iter in white_hor:
            abs_dist.append(abs(hor_iter - end_array[iter])) 
        if(len(abs_dist) > 0 and min(abs_dist) < 100):
            end_array[iter] = white_hor[abs_dist.index(min(abs_dist))] #return closest white line


    moving_max_dist = len(start_array)
    iter = 0
    while(iter < moving_max_dist): #fixes the case where the the start and end are in the same spot
        if(start_array[iter] >= end_array[iter]):
            del start_array[iter]
            del end_array[iter]
            moving_max_dist -= 1
        else:
            iter += 1

    return start_array, end_array


def master(a, pages_in, final_data_array, resolution, table_loc, Root):   
    print("Thread Started: ", a)
    page = pages_in[a]
    middle_data_array = []
    page.save(os.path.join(Root, "Images", "out_" + str(a) +".jpg"), 'JPEG')
    page = Image.open(os.path.join(Root, "Images", "out_" + str(a) + ".jpg")) #cannot just use page.load() this is probably because it needs the JPEG format		

    pixel_data = page.load()  
    white_hor = space_finder(page.size, pixel_data, resolution)
    table_start, table_end = table_locator(white_hor, table_loc[a])

    ####Debug
    page_in_copy = copy.deepcopy(pages_in[a])
    pixel_data_copy = page_in_copy.load()

    iter = 0
    n = 0
    while(n < len(table_start)):
        while(iter != table_start[n]):
            for x in range(page_in_copy.size[0]):
                pixel_data_copy[x,iter] = (255,0,0)
            iter += 1
        iter = table_end[n]
        n += 1

    while(iter < page_in_copy.size[1]):
        for x in range(page_in_copy.size[0]):
            pixel_data_copy[x,iter] = (255,0,0)
        iter += 1
    page_in_copy.save(os.path.join(Root, "ModImages", "a_" + str(a) + ".jpg"))
    ########Debug




    #print("Spaces: ", white_hor) 
    print(table_start, table_end)

    if(len(table_start) == 0):
        return

    
    inferred_ver_lines = []
    ver_lines = []

    hor_lines = horizontal_line_finder(page.size, pixel_data, resolution, table_start, table_end)

    for n in range(len(table_start)):
        ver_lines.append(vertical_line_finder((table_start[n], table_end[n]),page.size, pixel_data, resolution)) #real

        last_line = 0      
        inferred_ver_lines_temp = []
        for ver_line_iter in ver_lines[n]: #look at every section between Vertical lines

            required_dist = .75 #TODO find a number that balances speed and accuracy
            portion_covered = 2

            while(portion_covered > .75): #find a good number
                temp = inferred_vertical_line_finder((table_start[n], table_end[n]), (last_line, ver_line_iter), pixel_data, resolution, required_dist, 20, hor_lines) #inferred
                portion_covered = len(temp) / (ver_line_iter - last_line)
                required_dist += .05 #TODO find a number that balances speed and accuracy

            inferred_ver_lines_temp += temp
            last_line = ver_line_iter
        inferred_ver_lines.append(inferred_ver_lines_temp)

    ver_lines_final = []
    guarenteed_inf_ver = []
    for n in range(len(table_start)): #Find the correct verticle lines
        guarenteed_inf_ver.append(inferred_vertical_line_finder((table_start[n], table_end[n]), (0, page.size[0]), pixel_data, resolution, .95, 10, hor_lines)) #inject inf_ver that might have been wrongfully removed; Thicker line required USED TO BE .99
        tempv = mean_finder(ver_lines[n], guarenteed_inf_ver[n], resolution/15) #TODO find a good number
        if(len(tempv) > 0):                
            ver_lines_final.append(mean_finder(tempv, ([0] + inferred_ver_lines[n] + [page.size[0]-10]), int(resolution/5))) #this is precision not resolution add lines to the left and right //TODO find a good precision
        else:
            ver_lines_final.append([])
            guarenteed_inf_ver.append([])


    
    inferred_hor_lines = inferred_horizontal_line_finder(page.size, pixel_data, resolution, ver_lines_final, table_start, table_end, ver_lines)
    hor_lines_final = mean_finder(hor_lines, inferred_hor_lines, resolution/20) #this is precision not resolution


    print("Hor Lines: ", hor_lines)
    print("Ver Lines: ", ver_lines)
    print("Hor Lines Final: ", hor_lines_final)
    print("Ver Lines Final: ", ver_lines_final)

    ########################################################################################################################################################################################################
    j = 0
    n = 0
    hor_cell_skip = []
    while (j < len(hor_lines_final)):

        while(j + 1 < len(hor_lines_final) and hor_lines_final[j] == (hor_lines_final[j+1] - 1)): #go to the bottom of thick lines
            j += 1
        if(j + 1 == len(hor_lines_final)):
            break

        ###find which ver lines to use
        while(hor_lines_final[j+1] > table_end[n]):
            if(len(middle_data_array) > 0 and middle_data_array[-1] != "END OF TABLE"):
                middle_data_array.append("END OF TABLE")
            n += 1 
            j += 1 #go to next line
            print("N: ", n)

        i = 0
        first_data_array = []

        one_cell_split = False
        cell_holder = []
        while (i < len(ver_lines_final[n])):

            while(i + 1 < len(ver_lines_final[n]) and ver_lines_final[n][i] == (ver_lines_final[n][i+1] - 1)): #go to the right of thick lines
                i += 1
            if(i == len(ver_lines_final[n]) - 1):
                break
 
            if(len(hor_cell_skip) > 0 and i == hor_cell_skip[0]): #skip a specific cell if there was hor_crossover
                del hor_cell_skip[0]
                empty = True
            else:
                empty = check_box((ver_lines_final[n][i] + 1, hor_lines_final[j] + 1), (ver_lines_final[n][i+1], hor_lines_final[j+1]), pixel_data)

            if(empty): #empty
                first_data_array.append('-')
                cell_holder.append('-')
            else:
                old_x = i
                lines_to_skip, i = vertical_line_crossover(i, ver_lines_final[n],  hor_lines_final[j] + 1, hor_lines_final[j+1], pixel_data) #code for combining 2 or more cells in a row
                single_hor_crossover, temp_j = horizontal_line_crossover(j, hor_lines_final, ver_lines_final[n][i]+1, ver_lines_final[n][i+1], pixel_data)
                split, line_split_loc = horizontal_line_split(j, ver_lines_final[n][old_x]+1, ver_lines_final[n][i+1], hor_lines_final, pixel_data, resolution) #code for spliting exactly 2 row segments (This occurs when there should be an inferred hor line)    

                if(single_hor_crossover):
                    hor_cell_skip.append(i)

                #assume either single_hor or split not both
                if(split):
                    one_cell_split = True
                    data = image_to_text((ver_lines_final[n][old_x] + 1, hor_lines_final[j] + 1), (ver_lines_final[n][i+1], line_split_loc), page, i, j, Root)    
                    cell_holder.append(image_to_text((ver_lines_final[n][old_x] + 1, line_split_loc), (ver_lines_final[n][i+1], hor_lines_final[j + 1]), page, i, j + .5, Root))
                else:
                    data = image_to_text((ver_lines_final[n][old_x] + 1, hor_lines_final[j] + 1), (ver_lines_final[n][i+1], hor_lines_final[temp_j + 1]), page, i, j, Root)
                    cell_holder.append('-')

                first_data_array.append(data) #send x loc to the back

                for nuy in range(lines_to_skip):
                    first_data_array.append('-')    
                    cell_holder.append('-')
                
            i += 1
        #print(first_data_array)
        middle_data_array.append(first_data_array)
        if(one_cell_split):
            middle_data_array.append(cell_holder)
        j += 1
    final_data_array.append(middle_data_array)

    #####debug#########################################
    if(1):
        for n in hor_lines_final: #horizontal line
            for x in range(page.size[0]):
                pixel_data[x,n] = (255,0,255)


        y = table_start[0]
        for n in range(len(table_start)): 
            while(y < table_end[n]):
                for v in ver_lines_final[n]: #final verticle lines
                    pixel_data[v,y] = (255,0,255)
                y += 1
            if(n < len(table_start) - 1):
                y = table_start[n + 1]



    page.save(os.path.join(Root, "ModImages", "x_" + str(a) + ".jpg"))


    #for n in inferred_hor_lines:
    #    for x in range(page.size[0]):
    #        pixel_data[x,n] = (255,0,255)


    y = table_start[0]
    for n in range(len(table_start)): 
        while(y < table_end[n]):
            for v in inferred_ver_lines[n]: #inferred_ver_lines
                pixel_data[v,y] = (255,0,255)
            for v in guarenteed_inf_ver[n]: #guarenteed_inf_ver
                pixel_data[v,y] = (0,0,255)
            y += 1
        if(n < len(table_start) - 1):
            y = table_start[n + 1]

    for n in table_start: #white spaces
        for x in range(page.size[0]):
            pixel_data[x,n] = (255,0,0)
            pixel_data[x,n+1] = (255,0,0)
            pixel_data[x,n+2] = (255,0,0)

    for n in table_end: #white spaces
        for x in range(page.size[0]):
            pixel_data[x,n] = (255,0,0)
            pixel_data[x,n+1] = (255,0,0)
            pixel_data[x,n+2] = (255,0,0)

    for y in range(page.size[1]):
        if(y%100 == 0):
            for x in range(20):
                pixel_data[x,y] = (0,0,0)
        elif(y%50 == 0):
            for x in range(10):
                pixel_data[x,y] = (0,0,0)
    page.save(os.path.join(Root, "ModImages", "i_" + str(a) + ".jpg"))

    ######################################################
    middle_data_array.append("END OF TABLE")

    while([] in middle_data_array):
        middle_data_array.remove([])


    #print(middle_data_array)
    last_end = 0
    y = 0
    temp_y = 0 #declared here so I can use it later
    clean_array_final = []
    while(y < len(middle_data_array) - 1): #jump between different tables on a page
        skip = []
        for x in range (len(middle_data_array[y])): #cover the x axis
            temp_y = y   
            useless = True
            while(middle_data_array[temp_y] != "END OF TABLE"): #y axis of a particular table
                #print(temp_y, " ", x)
                #print(middle_data_array[temp_y])
                try:
                    if(middle_data_array[temp_y][x] != "-" and middle_data_array[temp_y][x] != " "):
                        useless = False
                except:
                    pass
                temp_y += 1

            if(useless):
                skip.append(x)

        temp_y = y
        while(middle_data_array[temp_y] != "END OF TABLE"):
            temp = []
            for number, x in enumerate(middle_data_array[temp_y]):
                if(number not in skip):
                    temp.append(x)

            clean_array_final.append(temp)
            temp_y += 1

        clean_array_final.append([])
        y = temp_y + 1
                


    #print(clean_array_final)

    with open(os.path.join(Root, "CSV", "x" + str(a) + ".csv"), mode='w') as write:
        writer = csv.writer(write, delimiter=',', lineterminator = '\n')
        for data in clean_array_final:
            writer.writerow(data)
    print("Thread Ended: ", a)
    return



    #######################################################
##############################START#####################################
if __name__ == '__main__': 
    resolution = 300 #do not change
    Root =  r"C:/Users/Zach/Downloads/Setup_Folders" #enter your local location to the setup folder
    pdf_file = os.path.join(Root, "PDFs", "AD678_c.pdf") #change the last " " to the PDF you wish to test
    
    splitter = table_split(pdf_file, Root)
    table_loc = splitter.return_data()

    pages = pdf2image.convert_from_path(pdf_file, resolution)
    final_data_array_out = [] 

    
    prod_x = functools.partial(master, pages_in = pages, final_data_array = final_data_array_out, resolution = resolution, table_loc = table_loc, Root = Root)
    

    if(0):#####DEBUG##########
        prod_x(0)
    else:
        pool = multiprocessing.Pool(multiprocessing.cpu_count() )
        try:
            pool.map(prod_x, range(0, len(pdf_file)))
        except:
            pass
        pool.close()
