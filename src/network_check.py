import os
from keras.models import load_model
from pdf2image import convert_from_path
import numpy as np
import cv2

root = r"/Users/serafinakamp/Desktop/TableExt/opt_branch/datasheet-scrubber/src"

model1 = load_model(os.path.join(root, "cnn_models/stage1.h5"))
model2 = load_model(os.path.join(root, "cnn_models/stage2.h5"))

imgs = convert_from_path(os.path.join(root,"test0.pdf"),300,first_page=2,last_page=2)



X_size = 800 #part1
Y_size = 64 #part1

pTwo_size = 600 #part2
cuts_labels = 60 #part2
label_precision = 8 #AMOUNT OF PIXELS BETWEEN LABELS, GOES FROM 1/4th to 3/4ths

y_fail_num = 2

for img in imgs:
    pixel_data = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    original_pixel_data_255 = pixel_data.copy()
    print(original_pixel_data_255)
    pixel_data = cv2.normalize(pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    original_pixel_data = pixel_data.copy()

    height, width = pixel_data.shape
    print(height," ",width)
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
        print(hor_start,' ',hor_finish)
        if(1 and hor_finish - hor_start > (0.7 * original_width)): #Fix for tables that cover the entire image
            groups2.append((0, original_width))
        else:
            groups2.append((hor_start, hor_finish))

    for iter in range(len(groups)):
        final_split = original_pixel_data_255[groups[iter][0]:groups[iter][1], groups2[iter][0]:groups2[iter][1]]
        #final_splits.append(final_split)
        #these are the values im interested in
        minY = groups[iter][0]
        maxY = groups[iter][1]
        minX = groups2[iter][0]
        maxX = groups2[iter][1]
        print(groups[iter][0]," ",groups[iter][1], " ", groups2[iter][0]," ",groups2[iter][1])

        if(1):
            imgCV = cv2.resize(final_split,(1200,800))
            imgCVorig = cv2.resize(original_pixel_data,(1200,800))
            cv2.namedWindow("image")
            cv2.moveWindow("image",0,0)
            cv2.imshow('image',imgCVorig)
            cv2.waitKey(0)
            cv2.namedWindow("image2")
            cv2.moveWindow("image2",200,0)
            cv2.imshow('image2',imgCV)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
