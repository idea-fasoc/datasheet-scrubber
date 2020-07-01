import keras
import tensorflow as tf
from keras.layers import Dense, Conv2D, Permute, MaxPooling2D, Flatten, Reshape, Dropout, Concatenate
import os
import numpy as np
import cv2
import xml.etree.ElementTree as ET
import copy
from keras.models import load_model, Model
from sklearn.model_selection import train_test_split
import math as m
import random
import sys




###trying to implement RoI layer GOOGLE COLAB !! - change to RoI Align using bilinear interpolation
class RoI(keras.layers.Layer):
    def __init__(self,pool_height=2,pool_width=2,mode="align",**kwargs):
        self.pool_height = pool_height
        self.pool_width = pool_width
        self.mode=mode #align or pool
        super(RoI,self).__init__(**kwargs)
    #dont need this
    def build(self, input_shape):
        return


    def compute_output_shape(self,input_shape):
        feature_map, rois_shape = input_shape
        batch_size = rois_shape[0]
        if self.mode == "pool":
            output_shape = (batch_size,rois_shape[1],self.pool_height,self.pool_width,feature_map[-1])
        elif self.mode == "align":
            output_shape = (batch_size,rois_shape[1],self.pool_height,self.pool_width,4,feature_map[-1])
        else:
            assert(self.mode == "align" or self.mode == "pool")
        return output_shape

    #image_batch_input[batch_size x img_width x img_height]
    #rois_batch_input[batch_size x n_rois_per_image x 4], each roi: [minX,minY,maxX,maxY]
    def call(self,input):
        #call function to apply element-wise
        if self.mode == "pool":
            def max_regions(input):
                return RoI.all_rois(input[0],input[1],self.pool_height,self.pool_width)
            final = tf.map_fn(max_regions,input,dtype=tf.float32)
        elif self.mode == "align":
            def interpol_regions(input):
                return RoI.align_all(input[0],input[1],self.pool_height,self.pool_width)
            final = tf.map_fn(interpol_regions,input,dtype=tf.float32)
        else:
            assert(self.mode == "align" or self.mode == "pool")
        return final

    @staticmethod
    def all_rois(image,rois,pool_height,pool_width):
        #call function on one element
        def max_of_one_region(roi):
            return RoI.one_roi(image,roi,pool_height,pool_width)
        #maps is a stack of 10 regions of dimension pool_height x pool_width
        maps = tf.map_fn(max_of_one_region,rois,dtype=tf.float32)
        return maps

    @staticmethod
    def one_roi(image,roi,pool_height,pool_width):
        minX = tf.cast(roi[0],'int32')
        minY = tf.cast(roi[1],'int32')
        maxX = tf.cast(roi[2],'int32')
        maxY = tf.cast(roi[3],'int32')
        dx = tf.cast(((maxX-minX)/pool_width),'int32')
        dy = tf.cast(((maxY-minY)/pool_height),'int32')
        areas = [[
        (minX + w*dx,
        minX + (w+1)*dx if w+1 < pool_width else maxX,
        minY + h*dy,
        minY + (h+1)*dy if h+1 < pool_height else maxY)
        for w in range(pool_width)]
        for h in range(pool_height)]

        def max_areas(vals):
            return tf.math.reduce_max(image[vals[2]:vals[3],vals[0]:vals[1],:],axis=[0,1])
        stacked_features = tf.stack([[max_areas(vals) for vals in row] for row in areas])

        return stacked_features

    @staticmethod
    def align_all(image,rois,pool_height,pool_width):
        #align one region at a time
        def align_one_region(roi):
            return RoI.one_region(image,roi,pool_height,pool_width)
        all_regions = tf.map_fn(align_one_region,rois,dtype="float32")
        return all_regions

    @staticmethod
    def one_region(image,roi,pool_height,pool_width):
        minX = tf.cast(roi[0],'float32')
        minY = tf.cast(roi[1],'float32')
        maxX = tf.cast(roi[2],'float32')
        maxY = tf.cast(roi[3],'float32')
        dx = tf.cast(((maxX-minX)/pool_width),'float32')
        dy = tf.cast(((maxY-minY)/pool_height),'float32')

        #2x2x4 tensor to represent 4 central points in each pool region (assumes 2x2 pool region - FIX)
        # 4 points ordered like topleft,topright,botleft,botright (same as region ordering)
        areas = [[[[minX+dx/4,minY+dy/4],[minX+3*dx/4,minY+dy/4],[minX+dx/4,minY+3*dy/4],[minX+3*dx/4,minY+3*dy/4]],
        [[minX+5*dx/4,minY+dy/4],[minX+7*dx/4,minY+dy/4],[minX+5*dx/4,minY+3*dy/4],[minX+7*dx/4,minY+3*dy/4]]],
        [[[minX+dx/4,minY+5*dy/4],[minX+3*dx/4,minY+5*dy/4],[minX+dx/4,minY+7*dy/4],[minX+3*dx/4,minY+7*dy/4]],
        [[minX+5*dx/4,minY+5*dy/4],[minX+7*dx/4,minY+5*dy/4],[minX+5*dx/4,minY+7*dy/4],[minX+7*dx/4,minY+7*dy/4]]]]


        #calc bilinear interpolation for a single point (x,y)
        def bilin_interpol(point):
            return RoI.calc_bilin_interpol_val(image,point,minX,minY,maxX,maxY)
        stacked_vals = tf.stack([[[bilin_interpol(point) for point in points] for points in row] for row in areas])
        return stacked_vals

    @staticmethod
    def calc_bilin_interpol_val(image,point,minX,maxX,minY,maxY):
        x = point[0]
        y = point[1]


        #implement as python function
        @tf.function(experimental_compile=False)
        def get_poss_neighbors(x,y,minX,minY,maxX,maxY):
            x_floor = tf.math.floor(x)
            y_floor = tf.math.floor(y)
            x_floor = tf.cast(x_floor,'int32')
            y_floor = tf.cast(y_floor,'int32')
            minX = tf.cast(minX,'int32')
            minY = tf.cast(minY,'int32')
            maxX = tf.cast(maxX,'int32')
            maxY = tf.cast(maxY,'int32')
            poss_neighbors=[]
            if (x_floor-1) < minX:
                if (y_floor-1) < minY: #top left corner (4 possible)(5 extra to match shape)
                    poss_neighbors=[[x_floor,y_floor],[x_floor+1,y_floor],[x_floor,y_floor+1],[x_floor+1,y_floor+1],
                                    [x_floor,y_floor+2],[x_floor+1,y_floor+2],[x_floor,y_floor+3],[x_floor+1,y_floor+3],[x_floor+2,y_floor+2]]
                elif (y_floor+1) > maxY: #bottom left corner (4 possible) (5 extra to match shape)
                    poss_neighbors=[[x_floor,y_floor],[x_floor+1,y_floor],[x_floor,y_floor-1],[x_floor+1,y_floor-1],
                                    [x_floor,y_floor+2],[x_floor+1,y_floor+2],[x_floor,y_floor+3],[x_floor+1,y_floor+3],[x_floor+2,y_floor+2]]
                else: #left edge (6 possible) (3 extra to match shape)
                    poss_neighbors=[[x_floor,y_floor-1],[x_floor+1,y_floor-1],
                                    [x_floor,y_floor],[x_floor+1,y_floor],
                                    [x_floor,y_floor+1],[x_floor+1,y_floor+1],
                                    [x_floor,y_floor+2],[x_floor+1,y_floor+2],[x_floor+2,y_floor+2]]
            elif (x_floor+1) > maxX:
                if (y_floor-1) < minY: #top right corner (4 possible) (5 extra to match shape)
                    poss_neighbors=[[x_floor-1,y_floor],[x_floor,y_floor],[x_floor-1,y_floor+1],[x_floor,y_floor+1],
                                    [x_floor,y_floor+2],[x_floor+1,y_floor+2],[x_floor,y_floor+3],[x_floor+1,y_floor+3],[x_floor+2,y_floor+2]]
                elif (y_floor+1) > maxY: #bottom right corner (4 possible) (5 extra to match shape)
                    poss_neighbors=[[x_floor-1,y_floor-1],[x_floor,y_floor-1],[x_floor-1,y_floor],[x_floor,y_floor],
                                    [x_floor,y_floor+2],[x_floor+1,y_floor+2],[x_floor,y_floor+3],[x_floor+1,y_floor+3],[x_floor+2,y_floor+2]]
                else: #right edge (6 possible) (3 extra to match shape)
                    poss_neighbors=[[x_floor-1,y_floor-1],[x_floor,y_floor-1],
                                    [x_floor-1,y_floor],[x_floor,y_floor],
                                    [x_floor-1,y_floor+1],[x_floor,y_floor+1],
                                    [x_floor,y_floor+2],[x_floor+1,y_floor+2],[x_floor+2,y_floor+2]]
            elif (y_floor-1) < minY: #top edge (6 possible) (3 extra to match shape)
                poss_neighbors = [[x_floor-1,y_floor],[x_floor,y_floor],[x_floor+1,y_floor],
                                    [x_floor-1,y_floor+1],[x_floor,y_floor+1],[x_floor+1,y_floor+1],
                                    [x_floor,y_floor+2],[x_floor+1,y_floor+2],[x_floor+2,y_floor+2]]
            elif (y_floor+1) > maxY: #bottom edge (6 possible) (3 extra to match shape)
                poss_neighbors=[[x_floor-1,y_floor-1],[x_floor,y_floor-1],[x_floor+1,y_floor-1],
                                [x_floor-1,y_floor],[x_floor,y_floor],[x_floor+1,y_floor],
                                [x_floor,y_floor+2],[x_floor+1,y_floor+2],[x_floor+2,y_floor+2]]
            else: #all middle cases (9 possible)
                poss_neighbors=[[x_floor-1,y_floor-1],[x_floor,y_floor-1],[x_floor+1,y_floor-1],
                                [x_floor-1,y_floor],[x_floor,y_floor],[x_floor+1,y_floor],
                                [x_floor-1,y_floor+1],[x_floor,y_floor+1],[x_floor+1,y_floor+1]]
            #fill in dist list
            dists=[]
            for p_n in poss_neighbors:
                x_nb = tf.cast(p_n[0],'float32')+0.5
                y_nb = tf.cast(p_n[1],'float32')+0.5
                dists.append((x_nb-x)**2+(y_nb-y)**2)

            assert(len(dists)==len(poss_neighbors))

            #now reduce to top 4
            while len(poss_neighbors) >4:
                i=4 #assume first 4 are true set and start comparing dists after
                while i < len(poss_neighbors):
                    j=0 #compare against first 4
                    while j < 4:
                        if dists[i] < dists[j]: #swap if find smaller dist
                            temp = tf.gather(poss_neighbors,j).numpy()
                            tf.gather(poss_neighbors,j).numpy()=tf.gather(poss_neighbors,i).numpy()
                            tf.gather(poss_neighbors,i) = temp
                            break
                        j=int(j+1)
                i=int(i+1)
            #want to return in order Q11,Q21,Q12,Q22 (i think it does this by design) it doesnt bc swap
            return poss_neighbors[:4]

        input = [x,y,minX,minY,maxX,maxY]
        neighbors = tf.py_function(func=get_poss_neighbors,inp=input,Tout = [tf.float32])




        print("success") #now we have 4 closest neighbor cells

        @tf.function(experimental_compile=False)
        def extract_neighbor_info(neighbors):
            #define quadrants
            Q11 = (tf.cast(neighbors[0][0],'int32'),tf.cast(neighbors[0][1],'int32'))
            Q21 = (tf.cast(neighbors[1][0],'int32'),tf.cast(neighbors[1][1],'int32'))
            Q12 = (tf.cast(neighbors[2][0],'int32'),tf.cast(neighbors[2][1],'int32'))
            Q22 = (tf.cast(neighbors[3][0],'int32'),tf.cast(neighbors[3][1],'int32'))

            #define points
            x1 = neighbors[0][0]+0.5
            x2 = neighbors[1][0]+0.5
            y1 = neighbors[0][1]+0.5
            y2 = neighbors[2][1]+0.5

            return Q11,Q21,Q12,Q22,x1,x2,y1,y2
        Q11,Q21,Q12,Q22,x1,x2,y1,y2 = tf.py_function(func=extract_neighbor_info,inp=[neighbors],
        Tout=[tf.int32,tf.int32,tf.int32,tf.int32,tf.float32,tf.float32,tf.float32,tf.float32])

        factor = 1/((x2-x1)*(y2-y1))
        X2 = x2-x
        X1 = x-x1
        Y2 = y2-y
        Y1 = y-y1

        full_tensor = tf.add(tf.math.multiply(X2,tf.add(tf.math.multiply(Y2,image[Q11,:]),tf.math.multiply(Y1,image[Q12,:]))),
                            tf.math.multiply(X1,tf.add(tf.math.multiply(Y2,image[Q21,:]),tf.math.multiply(Y1,image[Q22,:]))))
        final = tf.stop_gradient(tf.math.multiply(factor,full_tensor))
        return final #return shape is (num_filters)




#custom loss (l1 reg) for bounding box regression
def custom_loss(y_actual,y_pred):

    loss = tf.reduce_sum(tf.abs(tf.subtract(y_actual,y_pred)))
    #epsilon to protect against large loss values - take 50% of difference
    epsilon = 0.5
    total_loss = tf.math.scalar_mul(epsilon,loss)
    return total_loss

def calc_IoU(xml,proposed):
    intersection = 0
    xmlMinX = xml[0]
    xmlMinY = xml[2]
    xmlMaxX = xml[1]
    xmlMaxY = xml[3]
    propMinX = proposed[0]
    propMinY = proposed[1]
    propMaxX = proposed[2]
    propMaxY = proposed[3]
    width_shared = min(propMaxX,xmlMaxX) - max(propMinX,xmlMinX)
    height_shared = min(propMaxY,xmlMaxY) - max(propMinY,xmlMinY)
    if width_shared > 0 and height_shared > 0:
        intersection = width_shared*height_shared
    xmlArea = (xmlMaxX-xmlMinX)*(xmlMaxY-xmlMinY)
    propArea = (propMaxX-propMinX)*(propMaxY-propMinY)
    union = xmlArea + propArea - intersection
    return intersection/union

def get_proposed_regions(region):
    minX = region[0]
    minY = region[1]
    maxX = region[2]
    maxY = region[3]

    proposed_list = [region]
    scale = 2
    proposed_list.append([minX,minY,int(maxX/scale),int(maxY/scale)])
    proposed_list.append([minX,minY,int(maxX*scale),int(maxY*scale)])
    proposed_list.append([int(minX/scale),int(minY/scale),maxX,maxY])
    proposed_list.append([int(minX*scale),int(minY*scale),maxX,maxY])
    proposed_list.append([int(minX*scale),minY,int(maxX*scale),maxY])
    proposed_list.append([int(minX/scale),minY,int(maxX/scale),maxY])
    proposed_list.append([minX,int(minY*scale),maxX,int(maxY*scale)])
    proposed_list.append([minX,int(minY/scale),maxX,int(maxY/scale)])
    proposed_list.append([minX+(scale*10),minY+(scale*10),maxX-(scale*10),maxY-(scale*10)])

    return proposed_list

def draw_prop(image,prop):
    minX = region[0]
    minY = region[1]
    maxX = region[2]
    maxY = region[3]

    top_left = (minX,minY)
    top_right = (maxX,minY)
    bot_left = (minX,maxY)
    bot_right = (maxX,maxY)
    cv2.line(image, top_left, bot_left, (0,255,0), 5)
    cv2.line(image, top_left, top_right, (0,255,0), 5)
    cv2.line(image, bot_left, bot_right, (0,255,0), 5)
    cv2.line(image, top_right, bot_right, (0,255,0), 5)

    return image

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

def resize(X_size,Y_size, pixel_data, locs): #locs = [minX,minY,maxX,maxY]
    height, width = pixel_data.shape
    scaleX = X_size/width
    scaleY = Y_size/height
    temp_image = pixel_data.copy()
    mod_height = int(height*scaleX)

    temp_image = cv2.resize(temp_image, (X_size, Y_size)) #X, then Y
    for loc in locs:

        orig_x_dist = loc[2]-loc[0]
        orig_y_dist = loc[3]-loc[1]
        loc[0] = m.ceil(loc[0]*scaleX)
        loc[1] = m.ceil(loc[1]*scaleX)
        loc[2] = m.ceil(scaleX*orig_x_dist+loc[0])
        loc[3] = m.ceil(scaleY*orig_y_dist+loc[1])


        top_left = (loc[0],loc[1])
        top_right = (loc[2],loc[1])
        bot_left = (loc[0],loc[3])
        bot_right = (loc[2],loc[3])
        mid_x_min = (int((loc[2]+loc[0])/2),loc[1])
        mid_x_max = (int((loc[2]+loc[0])/2),loc[3])
        mid_y_min = (loc[0],int((loc[3]+loc[1])/2))
        mid_y_max = (loc[2],int((loc[3]+loc[1])/2))
        #print("window size: " ,str(mid_y_min[1] - top_left[1])," x ",str(mid_x_min[0]-top_left[0]))
        '''
        cv2.line(copy_image, top_left, bot_left, (0,255,0), 3)
        cv2.line(copy_image, top_left, top_right, (0,255,0), 3)
        cv2.line(copy_image, bot_left, bot_right, (0,255,0), 3)
        cv2.line(copy_image, top_right, bot_right, (0,255,0), 3)
        cv2.line(copy_image, mid_x_min, mid_x_max, (0,255,0), 3)
        cv2.line(copy_image, mid_y_min, mid_y_max, (0,255,0), 3)
        cv2.imshow('image', copy_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        '''

    return temp_image, locs

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
root_folder = r"/Users/serafinakamp/Desktop/TableExt/opt_branch/datasheet-scrubber/src"
image_folder_loc = "/Users/serafinakamp/Desktop/TableExt/datasheet-scrubber/src/Table_Extraction_Weight_Creation/img_bound_train"
xml_folder_loc = "/Users/serafinakamp/Desktop/TableExt/datasheet-scrubber/src/Table_Extraction_Weight_Creation/xml_bound_train"

image_locs = []
xml_locs = []

imgs = os.listdir(image_folder_loc)
xmls = os.listdir(xml_folder_loc)

imgs.sort()
xmls.sort()


for file in imgs[:10]:
    image_locs.append(os.path.join(image_folder_loc, file))

for file in xmls[:10]:
    xml_locs.append(os.path.join(xml_folder_loc, file))
print(len(image_locs))

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

    '''
    pixel_data = resize(X_size, pixel_data, table_locs)
    slices, s_lables = label_creater(pixel_data, label_precision, Y_size, table_locs)
    conc_data += slices
    conc_labels += s_lables
    s2, l2 = part_two_creation(original_pixel_data, table_locs_original, pTwo_size, cuts_labels)
    conc_data2 += s2
    conc_labels2 += l2
    '''
'''
conc_data2 = np.array(np.expand_dims(conc_data2,  axis = -1))
conc_labels2 = np.array(conc_labels2)
conc_data = np.array(np.expand_dims(conc_data,  axis = -1))
conc_labels = np.array(conc_labels)
##############################
'''



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

    model.save(r"/Users/serafinakamp/Desktop/TableExt/opt_branch/datasheet-scrubber/src/cnn_models/stage1.h5")

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

    model.save(r"/Users/serafinakamp/Desktop/TableExt/opt_branch/datasheet-scrubber/src/cnn_models/stage2.h5")

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

##Create bounding boxes for each image using part 1/2
total_prec = 0
total_recall = 0

if(1): #wrapper
    model1 = load_model(os.path.join(root_folder, r"cnn_models/stage1.h5"))
    model2 = load_model(os.path.join(root_folder, r"cnn_models/stage2.h5"))
    y_fail_num = 2

    image_label = []
    input_image = []
    input_roi=[]
    num_roi = 10 #fixed number of rois

    for i_num, i in enumerate(image_locs):
        print(i_num+1, " of ", len(image_locs))
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


        #testing ROI layers

        #[minX,minY,maxX,maxY] follows [groups2[i][0],groups[i][0],groups2[i][1],groups[i][1]]

        #final_splits = []
        xml_locs = table_locs_hold[i_num] #list of 4 element arrays [minX, maxX, minY, maxY]

        data_shared = 0
        all_roi_coords=[]
        start_ind = len(image_label)
        #add real data and add a copy of image for each real table
        for xml_box in xml_locs:
            input_image.append(original_pixel_data)
            all_roi_coords.append([xml_box[0],xml_box[2],xml_box[1],xml_box[3]])
        #add generated coordinates
        for iter in range(len(groups)):
            final_split = original_pixel_data_255[groups[iter][0]:groups[iter][1], groups2[iter][0]:groups2[iter][1]]
            all_roi_coords.append([groups2[iter][0],groups[iter][0],groups2[iter][1],groups[iter][1]])
            input_image.append(original_pixel_data)
            #final_splits.append(final_split)
            '''
            for xml_temp in xml_locs:
                dx = min(xml_temp[1], groups2[iter][1]) - max(xml_temp[0], groups2[iter][0])
                dy = min(xml_temp[3], groups[iter][1]) - max(xml_temp[2], groups[iter][0])
                if (dx>=0) and (dy>=0):
                    data_shared += dx*dy
            '''
            if(0):
                cv2.imshow('image', final_split)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                cv2.imshow('image', original_pixel_data_255[xml_locs[0][2]:xml_locs[0][3], xml_locs[0][0]:xml_locs[0][1]])
                cv2.waitKey(0)
                cv2.destroyAllWindows()

        #for each location in all roi coords, propose 10 scaled regions around location
        for region in all_roi_coords:
            copy_image = original_pixel_data
            proposed_regions = get_proposed_regions(region)

            #create labels for RoI - 1 if IoU is very close to 1 (say >0.92)
            max_IoU = 0
            coords = []
            for prop in proposed_regions:
                for xml_box in xml_locs:
                    IoU = calc_IoU(xml_box,prop)
                    if IoU > max_IoU:
                        max_IoU = IoU
                        coords=prop
            if max_IoU > 0.92:
                image_label.append([1.,coords])
            else:
                image_label.append([0.,region])
            input_roi.append(proposed_regions)

            '''
            #print out image and label information
            copy_image,extra = resize(500,600,copy_image,proposed_regions)
            print(image_label[-1])
            print(input_roi[-1])
            cv2.imshow('image', copy_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            '''



        '''
        #randomly place correct coordinates and set labels
        for table_ind in range(len(xml_locs)):
            proposed_regions = []
            #deep copy
            for coords in all_roi_coords:
                proposed_regions.append(coords)
            #pad to num_roi RoI
            while len(proposed_regions) < num_roi:
                rand_ind = math.floor(random.random()*len(proposed_regions))
                #scale by random number
                rand_scale = random.random()
                proposed_regions.append([proposed_regions[rand_ind][0],proposed_regions[rand_ind][1],int(proposed_regions[rand_ind][2]/rand_scale),int(proposed_regions[rand_ind][3]/rand_scale)])
            #if greater than 10, essentially a dropout layers
            while len(proposed_regions) > num_roi:
                random.seed()
                rand_ind = math.floor(random.random()*len(all_roi_coords))
                #dont remove ground truth
                if rand_ind == table_ind:
                    continue
                proposed_regions.pop(rand_ind)
            assert(len(proposed_regions)==num_roi)
            #randomly shuffle ground truth
            rand_ind = math.floor(random.random()*len(proposed_regions))
            temp_coords = proposed_regions[rand_ind]
            proposed_regions[rand_ind] = proposed_regions[table_ind]
            proposed_regions[table_ind] = temp_coords
            input_roi.append(proposed_regions)
            #update label
            image_label[start_ind+table_ind][rand_ind] = 1
            loc=[proposed_regions[rand_ind][0],proposed_regions[rand_ind][1],proposed_regions[rand_ind][2],proposed_regions[rand_ind][3]]
            temp_image = input_image[start_ind]
            top_left = (loc[0],loc[1])
            top_right = (loc[2],loc[1])
            bot_left = (loc[0],loc[3])
            bot_right = (loc[2],loc[3])
            cv2.line(temp_image, top_left, bot_left, (0,255,0), 5)
            cv2.line(temp_image, top_left, top_right, (0,255,0), 5)
            cv2.line(temp_image, bot_left, bot_right, (0,255,0), 5)
            cv2.line(temp_image, top_right, bot_right, (0,255,0), 5)
            temp_image = cv2.resize(temp_image,(400,600))
            print(loc)
            cv2.imshow('image', temp_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            '''

        '''
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
        '''
        break




    for i,im in enumerate(input_image):
        input_image[i],input_roi[i]=resize(200,300,im,input_roi[i])
    assert(len(input_image)==len(input_roi))
    assert(len(input_image)==len(image_label))


    #x=tf.constant([[[15,2,3],[2,3,4],[1,23,6]],[[2,3,5],[1,2,7],[3,3,10]]])
    #x=tf.constant([2,2,1,3])
    #print(tf.reduce_sum(x))

    #PART 3 - testing RoI
    if(1):
        x_train,x_valid,y_train,y_valid = train_test_split(input_image,image_label,test_size=0.1,shuffle=False)
        roi_train=[]
        roi_valid=[]
        y_classify_train=[]
        y_bound_train=[]
        y_classify_valid=[]
        y_bound_valid=[]
        valid_ind=0
        for i,r in enumerate(input_roi):
            if i < len(x_train):
                roi_train.append(r)
                x_train[i] = np.expand_dims(x_train[i],axis=-1)
                y_classify_train.append(y_train[i][0])
                y_bound_train.append(y_train[i][1])
            else:
                roi_valid.append(r)
                x_valid[valid_ind] = np.expand_dims(x_valid[valid_ind],axis=-1)
                y_classify_valid.append(y_valid[valid_ind][0])
                y_bound_valid.append(y_valid[valid_ind][1])
                valid_ind=valid_ind+1
        assert(len(x_train)==len(roi_train))
        assert(len(x_valid)==len(roi_valid))
        print(y_bound_train)

        image_input = keras.layers.Input(shape=(300,200,1), name="image_input")
        bound_box = keras.layers.Input(shape=(10,4), name="bound_box")


        ##TODO implement final CNN to add roi layer
        conv = Conv2D(16,(3,3),activation="relu",padding="same")(image_input)
        conv = Conv2D(16,(3,3),activation="relu",padding="same")(conv)
        conv = Conv2D(16,(3,3),activation="relu",padding="same")(conv)
        conv = Dropout(0.2)(conv)
        conv = keras.models.Model(inputs=image_input,outputs=conv)
        conv.save(r"/Users/serafinakamp/Desktop/TableExt/opt_branch/datasheet-scrubber/src/cnn_models/conv_test.h5")
        #tf.keras.backend.print_tensor(conv.output)

        roi = RoI(2,2,mode="align")([conv.output,bound_box])

        dense = Dense(16, activation="relu")(roi)
        dense = Dense(16,activation="relu")(dense)
        dense = Flatten()(dense)
        dense_class = Dense(1024, activation="relu")(dense)
        dense_bound = Dense(1024, activation="relu")(dense)
        out_classifier = Dense(1,activation="sigmoid",name="classify")(dense_class)
        out_bound_box = Dense(4,activation="relu",name="bound")(dense_bound)

        model= keras.models.Model(inputs=[image_input,bound_box], outputs=[out_classifier,out_bound_box])
        losses={
            "classify" : keras.losses.binary_crossentropy,
            "bound" : custom_loss,
        }
        loss_weights={"classify":1,"bound":1}
        model.compile(loss=losses, loss_weights=loss_weights,optimizer=keras.optimizers.Adam(learning_rate=1e-8), metrics=["accuracy"])
        print(model.summary())
        model.fit(x=[x_train,roi_train], y=[y_classify_train,y_bound_train], validation_data = ([x_valid,roi_valid], [y_classify_valid,y_bound_valid]),batch_size=1, epochs = 1)

        model.save(r"/Users/serafinakamp/Desktop/TableExt/opt_branch/datasheet-scrubber/src/cnn_models/roi_test.h5")

    if (0):
        model3 = load_model(os.path.join(root_folder, r"cnn_models/roi_test.h5"),custom_objects={"RoI":RoI})

        image = np.array(input_image[0])
        image = np.expand_dims(image,axis=-1)
        image = np.expand_dims(image,axis=0)
        roi_in = np.array(input_roi[0])
        roi_in = np.expand_dims(roi_in,axis=0)
        predictions = model3.predict([image,roi_in])
        print(predictions)
    if (0):
        conv = load_model(os.path.join(root_folder, r"cnn_models/conv_test.h5"))
        for i in range(len(input_image)):
            images=conv.predict(np.expand_dims(np.expand_dims(input_image[i],axis=0),axis=-1))
            images = np.reshape(images,(1,32,300,200))
            for image in images[0]:
                cv2.imshow('image', input_image[i])
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                cv2.imshow('image', image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()


    #print(total_prec / len(image_locs))
    #print(total_recall / len(image_locs))
