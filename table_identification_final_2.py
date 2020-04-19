import keras
from keras.layers import Dense, Conv2D, Permute, MaxPooling2D, Flatten, Reshape, Dropout, Concatenate
import os
import numpy as np
import cv2
import xml.etree.ElementTree as ET
import copy 
from keras.models import load_model
from sklearn.model_selection import train_test_split

def get_coordinates_from_string(str):
    min_vals = [10000, 10000]
    max_vals = [0,0]

    on_X = True
    temp = ""
    for char in str:
        if(char == "," or char == " "):
            if(int(temp) < min_vals[not on_X]):
                min_vals[not on_X] = int(temp)
            if(int(temp) > max_vals[not on_X]):
                max_vals[not on_X] = int(temp)
            on_X = not on_X
            temp = ""
        else:
            temp += char

    return min_vals, max_vals

#######read from xml
def table_locations(xml_loc):
    locs = []
    tree = ET.parse(xml_loc)
    root = tree.getroot()
    i = 0
    while(1):
        try:
            data = root[i][0].attrib["points"]
            min_vals, max_vals = get_coordinates_from_string(data)
            locs.append([min_vals[0], max_vals[0], min_vals[1], max_vals[1]])
        except:
            break  
        i += 1
    return locs #list of 4 element arrays [minX, maxX, minY, maxY]

def resize(X_size, pixel_data, locs):
    height, width = pixel_data.shape
    scale = X_size/width
    temp_image = pixel_data.copy()
    mod_height = int(height*scale)

    temp_image = cv2.resize(temp_image, (X_size, mod_height)) #X, then Y
    for loc in locs:
        loc[0] *= scale
        loc[1] *= scale
        loc[2] *= scale
        loc[3] *= scale
    #cv2.imshow('image', temp_image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return temp_image #, locs

def label_creater(pixel_data, label_precision, Y_size, locs):
    height, width = pixel_data.shape
    raw_labels = np.zeros(int(height/label_precision))

    for table in locs:
        for y in range(int(table[2]/label_precision), int(table[3]/label_precision)+1):
            raw_labels[y] = 1

    s_labels = []
    slices = []
    label_skip_size = int(Y_size/(2*label_precision))
    label_bias = int(Y_size/(4*label_precision))

    slice_skip_size = int(Y_size/2)
    
    iter = 0
    while((iter*slice_skip_size + Y_size) < height):
        s_iter = iter*slice_skip_size
        l_iter = iter*label_skip_size + label_bias

        slices.append(pixel_data[int(s_iter):int(s_iter+Y_size)])
        s_labels.append(raw_labels[l_iter:l_iter+label_skip_size])
        iter += 1

    return slices, s_labels

def part_two_creation(original_pixel_data, table_locs_original, pTwo_size, cuts_labels):
    slices = []
    labels = []
    table_iter = 0

    height, width = original_pixel_data.shape
    x_scale = pTwo_size/width

    while(table_iter < len(table_locs_original)):
        label_temp = np.zeros(cuts_labels)

        temp_slice = original_pixel_data[table_locs_original[table_iter][2]:table_locs_original[table_iter][3]]
        temp_slice = cv2.resize(temp_slice, (pTwo_size, pTwo_size)) #X, then Y
        slices.append(temp_slice)

        if(table_iter + 1 < len(table_locs_original)): #For the case where two tables are next to one another
            if(table_locs_original[table_iter+1][2] <= table_locs_original[table_iter][3]):
                for x in range(int(cuts_labels*table_locs_original[table_iter][0]/width), int(cuts_labels*table_locs_original[table_iter][1]/width)+1):
                    label_temp[x] = 1

                for x in range(int(cuts_labels*table_locs_original[table_iter+1][0]/width), int(cuts_labels*table_locs_original[table_iter+1][1]/width)+1):
                    label_temp[x] = 1
                
                labels.append(label_temp)
                table_iter += 2
                continue

        for x in range(int(cuts_labels*table_locs_original[table_iter][0]/width), int(cuts_labels*table_locs_original[table_iter][1]/width)+1):
            label_temp[x] = 1
        labels.append(label_temp)
        table_iter += 1

    return slices, labels

########Start
root_folder = r"C:\Users\Zach\Downloads\Table_extract_robust"
image_folder_loc = os.path.join(root_folder, "modern_images")
xml_folder_loc = os.path.join(root_folder, "modern_xml")

image_locs = []
xml_locs = []

for file in os.listdir(image_folder_loc):
    image_locs.append(os.path.join(image_folder_loc, file))

for file in os.listdir(xml_folder_loc):
    xml_locs.append(os.path.join(xml_folder_loc, file))

conc_data, conc_data2 = [], []
conc_labels, conc_labels2 = [], []
X_size = 800 #part1
Y_size = 64 #part1

pTwo_size = 600 #part2
cuts_labels = 60 #part2
label_precision = 8 #AMOUNT OF PIXELS BETWEEN LABELS, GOES FROM 1/4th to 3/4ths

table_locs_hold = []

for i in range(len(image_locs)):
    img_loc = image_locs[i]
    xml_loc = xml_locs[i]
    pixel_data = cv2.imread(img_loc, 0)

    pixel_data = cv2.normalize(pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    original_pixel_data = pixel_data.copy()

    table_locs = table_locations(xml_loc)
    table_locs_original = copy.deepcopy(table_locs) 
    table_locs_hold.append(table_locs_original)

    pixel_data = resize(X_size, pixel_data, table_locs)

    slices, s_lables = label_creater(pixel_data, label_precision, Y_size, table_locs)
    conc_data += slices
    conc_labels += s_lables

    s2, l2 = part_two_creation(original_pixel_data, table_locs_original, pTwo_size, cuts_labels)
    conc_data2 += s2
    conc_labels2 += l2

conc_data2 = np.array(np.expand_dims(conc_data2,  axis = -1))
conc_labels2 = np.array(conc_labels2)

conc_data = np.array(np.expand_dims(conc_data,  axis = -1))
conc_labels = np.array(conc_labels)
##############################




if(0):
    output_size = int(Y_size/(2*label_precision))
    x_train, x_valid, y_train, y_valid = train_test_split(conc_data, conc_labels, test_size = 0.1, shuffle = False)
    keras_input = keras.layers.Input(shape=(Y_size,X_size,1), name='keras_input')

    conv = Conv2D(32, (5,5), activation="relu")(keras_input)
    conv = MaxPooling2D((2,2))(conv)
    conv = Conv2D(32, (5,5), activation="relu")(conv)
    conv = MaxPooling2D((2,2))(conv)

    conv_holder = []

    for i in range(3):
        conv_test = Flatten()(conv)
        conv_holder.append(Dense(output_size, activation="sigmoid")(conv_test))

        temp0 = Conv2D(64, (3,3), activation="relu", padding='same')(conv)
        temp1 = Conv2D(64, (3,3), activation="relu", padding='same')(temp0)
        temp2 = Conv2D(64, (3,3), activation="relu", padding='same')(temp1)
        temp3 = Conv2D(64, (3,3), activation="relu", padding='same')(temp2)

        conv = MaxPooling2D((2,2))(temp3)
        conv = Dropout(0.2)(conv)

        
    denseLayer = Flatten()(conv)
    denseLayer = Dense(512, activation="relu")(denseLayer)
    denseLayer = Dense(512, activation="relu")(denseLayer)

    out = Dense(output_size, activation="sigmoid")(denseLayer)

    model_train = keras.models.Model(inputs=keras_input, outputs=[out] + conv_holder)

    Training_VAR = 3
    model_train.compile(loss=keras.losses.binary_crossentropy, loss_weights = [1] + [1/Training_VAR for i in range(Training_VAR)], optimizer='adam',  metrics=['accuracy'])
    model_train.fit(x_train, [y_train for i in range(Training_VAR+1)], validation_data = (x_valid, [y_valid for i in range(Training_VAR+1)]), epochs = 75)


    model = keras.models.Model(inputs=keras_input, outputs=out)
    model.compile(loss=keras.losses.binary_crossentropy, optimizer='adam', metrics=["accuracy"])

    model.save(r"C:\Users\Zach\Downloads\Table_extract_robust\Identification_Models\stage1.h5")    

    if(0):  #debug
        bias = Y_size/4

        for im_num in range(len(x_valid)):
            test_data = model.predict(np.expand_dims(x_valid[im_num],  axis = 0))[0]
            img = x_valid[im_num]

            for data_loc in range(len(test_data)):
                if(test_data[data_loc] > .5):
                    start_points = (0, int(bias + data_loc*label_precision)+1)
                    end_points = (X_size, int(bias + (data_loc+1)*label_precision)-1)
                    img = cv2.rectangle(img, start_points, end_points, 0, 1) 

            cv2.imshow('image', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows() #PART 1

if(0): #PART 2
    x_train, x_valid, y_train, y_valid = train_test_split(conc_data2, conc_labels2, test_size = 0.1, shuffle = False)
    keras_input = keras.layers.Input(shape=(pTwo_size,pTwo_size,1), name='keras_input')
    conv = Conv2D(32, (5,5), activation="relu")(keras_input)
    conv = MaxPooling2D((2,2))(conv)
    conv = Conv2D(32, (5,5), activation="relu")(conv)
    conv = MaxPooling2D((2,2))(conv)

    for i in range(2):
        temp0 = Conv2D(64, (3,3), activation="relu", padding='same')(conv)
        temp1 = Conv2D(64, (3,3), activation="relu", padding='same')(temp0)
        temp2 = Conv2D(64, (3,3), activation="relu", padding='same')(temp1)
        temp3 = Conv2D(64, (3,3), activation="relu", padding='same')(temp2)

        conv = Concatenate(axis = -1)([conv, temp3])
        conv = MaxPooling2D((2,2))(conv)
        conv = Conv2D(64, (3,3), activation="relu")(conv)
        conv = Dropout(0.2)(conv)
        
    denseLayer = Flatten()(conv)
    denseLayer = Dense(512, activation="relu")(denseLayer)
    denseLayer = Dense(512, activation="relu")(denseLayer)
    out = Dense(cuts_labels, activation="sigmoid")(denseLayer)


    model = keras.models.Model(inputs=keras_input, outputs=out)
    model.compile(loss=keras.losses.binary_crossentropy, optimizer='adam', metrics=["accuracy"])
    model.fit(x_train, y_train, validation_data = (x_valid, y_valid), epochs = 20)

    model.save(r"C:\Users\Zach\Downloads\Table_extract_robust\Identification_Models\stage2.h5")   

    if(0):  #debug
        for im_num in range(len(x_valid)):
            test_data = model.predict(np.expand_dims(x_valid[im_num],  axis = 0))[0]
            img = x_valid[im_num]

            for data_loc in range(len(test_data)):
                if(test_data[data_loc] > .5):
                    start_points = (int(data_loc*pTwo_size/cuts_labels)+1, 0)
                    end_points = (int((data_loc+1)*pTwo_size/cuts_labels)-1, pTwo_size)
                    img = cv2.rectangle(img, start_points, end_points, 0, 1) 

            cv2.imshow('image', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows() #PART 2

total_prec = 0
total_recall = 0

if(1): #wrapper
    model1 = load_model(os.path.join(root_folder, r"Identification_Models\stage1.h5"))
    model2 = load_model(os.path.join(root_folder, r"Identification_Models\stage2.h5"))
    y_fail_num = 2
    for i_num, i in enumerate(image_locs):
        pixel_data = cv2.imread(i, 0)
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
                    groups.append((int((group_start-1)*label_precision/scale), int((iter+1-y_fail_num)*label_precision/scale)))
                group_start = iter

 

        groups2 = []
        for group in groups:
            temp_final_original = cv2.resize(original_pixel_data[group[0]:group[1]], (pTwo_size, pTwo_size))
            temp_final = np.expand_dims(np.expand_dims(temp_final_original,  axis = 0), axis = -1)
            data_final = model2.predict(temp_final)

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

        #final_splits = []
        xml_locs = table_locs_hold[i_num] #list of 4 element arrays [minX, maxX, minY, maxY]

        data_shared = 0
        for iter in range(len(groups)):
            final_split = original_pixel_data_255[groups[iter][0]:groups[iter][1], groups2[iter][0]:groups2[iter][1]]
            #final_splits.append(final_split)

            for xml_temp in xml_locs:
                dx = min(xml_temp[1], groups2[iter][1]) - max(xml_temp[0], groups2[iter][0])
                dy = min(xml_temp[3], groups[iter][1]) - max(xml_temp[2], groups[iter][0])
                if (dx>=0) and (dy>=0):
                    data_shared += dx*dy
            if(0):
                cv2.imshow('image', final_split)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                print(xml_locs)
                cv2.imshow('image', original_pixel_data_255[xml_locs[0][2]:xml_locs[0][3], xml_locs[0][0]:xml_locs[0][1]])
                cv2.waitKey(0)
                cv2.destroyAllWindows()

        total_predicted_area = 0

        for iter in range(len(groups)):
            total_predicted_area += (groups2[iter][1] - groups2[iter][0]) * (groups[iter][1] - groups[iter][0])

        total_real_data = 0
        for xml_temp in xml_locs:
            total_real_data += (xml_temp[1] - xml_temp[0]) * (xml_temp[3] - xml_temp[2])

        #total_data -= total_predicted_area + total_real_data - data_shared
        #print(data_shared / total_data)

        print("Prec: ", data_shared/total_predicted_area)
        print("Recall: ", data_shared/total_real_data)

        total_prec += data_shared/total_predicted_area
        total_recall += data_shared/total_real_data

    print(total_prec / len(image_locs))
    print(total_recall / len(image_locs))
            



