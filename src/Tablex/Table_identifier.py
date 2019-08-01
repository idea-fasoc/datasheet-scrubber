from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Conv2D
from keras.models import model_from_json
import keras
import pdf2image #poppler needs to be added and added to the path variable
from PIL import Image
import os
import cv2
import numpy
import copy
from sklearn.model_selection import train_test_split
from keras.utils import plot_model

def image_spliter(pdfs, verticle_size, a, Root):
    data = []
    print(len(pdfs))
    for pdf_num, pdf in enumerate(pdfs):
        for iter in range(len(pdf)):
            img = pdf[iter]

            if(a == 0):
                debug_loc = os.path.join(Root, "Identifier", "Split", "Pdf") + str(pdf_num) + r"\page" + str(iter)
                if not os.path.exists(os.path.join(Root, "Identifier", "Split", "Pdf") + str(pdf_num)):
                    os.mkdir(os.path.join(Root, "Identifier", "Split", "Pdf") + str(pdf_num))
            else:
                debug_loc = os.path.join(Root, "Identifier", "Split", "Test_Pdf")
                if not os.path.exists(os.path.join(Root, "Identifier", "Split", "Test_Pdf")):
                    os.mkdir(os.path.join(Root, "Identifier", "Split", "Test_Pdf"))
            print(debug_loc)

            if not os.path.exists(debug_loc):
                os.mkdir(debug_loc)

            y_iter = 0
            while(y_iter + verticle_size <= img.size[1]):
                slice = img.crop((0, y_iter, img.size[0], y_iter + verticle_size))
                slice = slice.resize((850, verticle_size), Image.NEAREST) #THIS WILL NOT WORK IF RES IS CHANGED
                slice.save(debug_loc + "\\" + str(y_iter) +".png", 'png')

                slice = cv2.imread(debug_loc + "\\" + str(y_iter) +".png", 0)
                cv2.imwrite(debug_loc + "\\" + str(y_iter) +".png", slice) #debug

            
                data.append(slice)
                y_iter += verticle_size / 2

    data = numpy.array(data, dtype="float") / 255.0
    return(data)
       


def table_finder(verticle_size, split_amount, pdf_files, Root):   #finds the labels/// Needs to be named " i_ "
    address = os.path.join(Root, "Custom")

    labels = []
    for file in pdf_files:
        dir = file.split("\\")[-1] #get the pdf name
        dir = dir.split(".")[0] #remove_pdf
        print(file)
        for file_loc in range( len(os.listdir(os.path.join(address, dir)))):
            file = "i_" + str(file_loc) + ".png"
            print(file)
            locs = []
            img = Image.open(os.path.join(address, dir, file))

            single_label = [0 for i in range(split_amount)]
            y_dist = int(img.size[1]/(verticle_size/2) - 1) #minus one is because the last gets cut off
            temp_labels = [copy.deepcopy(single_label) for i in range(y_dist)]
            pixel_data = img.load()

            prev_red = False
            for y in range(img.size[1]):
                if(pixel_data[0,y][0] > 200 and pixel_data[0,y][1] < 100 and pixel_data[0,y][2] < 100): #is red
                    if(not prev_red):
                        locs.append(y)
                    prev_red = True
                else:
                    prev_red = False

            for x in range(0,len(locs),2):
                start = int((locs[x] - 25) / ((verticle_size/2)/split_amount)) + 1 #round up //-25 accounts for the starting offset can segfault
                end = int((locs[x+1] - 25) / ((verticle_size/2)/split_amount)) #round down
                #print(start, " ", end)
                while(start < end):
                    #print(int(start/split_amount), " ", int(start%split_amount))
                    if(int(start/split_amount) >= len(temp_labels)):
                        break
                    temp_labels[int(start/split_amount)][int(start%split_amount)] = 1
                    start += 1
            
            labels += temp_labels
           # print(temp_labels)

    labels = numpy.array(labels, dtype="float")
    return labels
        





#################START
resolution = 100
verticle_size = int(resolution)
split_amount = 5

rebuild = False #Change to rebuild the network
reextract = False #Change to add new documents

Root = r"C:\Users\Zach\Downloads\Setup_Folders" #Change to your local address of the setup folder

if(rebuild):
    pdfs = []
    pdf_files = [os.path.join(Root,"PDFs","AD7183.pdf"), os.path.join(Root,"PDFs","CS5345.pdf"), os.path.join(Root,"PDFs","AD7690.pdf"),os.path.join(Root,"PDFs","ak5354_f02e.pdf"),os.path.join(Root,"PDFs","ak5386_f00e.pdf"),
                 os.path.join(Root,"PDFs","Decent_0.pdf"), os.path.join(Root,"PDFs","AD7829-1.pdf"), os.path.join(Root,"PDFs","t1.pdf"), os.path.join(Root,"PDFs","1792825203308455ak5381et.pdf"), os.path.join(Root,"PDFs","1696922288940353ak5394avs.pdf"),
                 os.path.join(Root,"PDFs","awr1243.pdf"), os.path.join(Root,"PDFs","drv5011.pdf"), os.path.join(Root,"PDFs","opt3007.pdf"), os.path.join(Root,"PDFs","test_ERI.pdf"), os.path.join(Root,"PDFs","random_table0.pdf"),
                 os.path.join(Root,"PDFs","3ad4002-4006-4010.pdf"), os.path.join(Root,"PDFs","74AHC_AHCT1G125.pdf"), os.path.join(Root,"PDFs","74AHC_AHCT125.pdf"), os.path.join(Root,"PDFs","74AHC1G126.pdf"), os.path.join(Root,"PDFs","74ALVC_ALVCH16245.pdf"),
                 os.path.join(Root,"PDFs","751cd00002389.pdf"), os.path.join(Root,"PDFs","21294C.pdf"), os.path.join(Root,"PDFs","233316f.pdf"), os.path.join(Root,"PDFs","DA6510_007.pdf"), os.path.join(Root,"PDFs","MC10EL33-D.pdf"),
                 os.path.join(Root,"PDFs","AD678_c.pdf"),os.path.join(Root,"PDFs","real_image_0.pdf"), os.path.join(Root,"PDFs","AD7482.pdf"), os.path.join(Root,"PDFs","fn3082.pdf"), #os.path.join(Root,"PDFs","4334805033475836ad7770.pdf")
                 os.path.join(Root,"PDFs","AD7656A-1.pdf"),os.path.join(Root,"PDFs","AD7683.pdf"),os.path.join(Root,"PDFs","AD7690.pdf"),os.path.join(Root,"PDFs","AD7982.pdf"),#, #os.path.join(Root,"PDFs","ad7768-7768-4.pdf")
                 os.path.join(Root,"PDFs","AD7992.pdf"),os.path.join(Root,"PDFs","AD9446.pdf"),os.path.join(Root,"PDFs","AD9461.pdf"),os.path.join(Root,"PDFs","hmxadc9225.pdf"), #os.path.join(Root,"PDFs","adc12dl3200.pdf")
                 os.path.join(Root,"PDFs","adc0803-04.pdf"),os.path.join(Root,"PDFs","ads1015.pdf"), #os.path.join(Root,"PDFs","adc0808-n.pdf") os.path.join(Root,"PDFs","ADC1005S060.pdf") os.path.join(Root,"PDFs","ADC1443D.pdf")
                 os.path.join(Root,"PDFs","ads1261.pdf"),os.path.join(Root,"PDFs","ads5263.pdf"),os.path.join(Root,"PDFs","ads8254.pdf")] #To be replaced with your own training data if you wish to reextract




    if(reextract): ###add new pdf
        for pdf_file in pdf_files:
            pdfs.append(pdf2image.convert_from_path(pdf_file, resolution))
        data = numpy.expand_dims(image_spliter(pdfs, verticle_size, 0, Root), axis = 3)
        labels = table_finder(verticle_size, split_amount, pdf_files, Root)
        numpy.save(os.path.join(Root, "Identifier", "DATA"), data)
        numpy.save(os.path.join(Root, "Identifier", "LABELS"), labels)
    else:
        data = numpy.load(os.path.join(Root, "Identifier", "DATA.npy"))
        labels = numpy.load(os.path.join(Root, "Identifier", "DATA.npy"))


    x_train, x_valid, y_train, y_valid = train_test_split(data, labels, test_size = 0.2, shuffle = True)

    ###################
    keras_input = keras.layers.Input(shape=(int(verticle_size),850,1))

    window_a = Conv2D(32, kernel_size=(20, 20), activation='relu')(keras_input)
    window_a = keras.layers.MaxPooling2D(pool_size=(4, 4))(window_a)
    window_a = Conv2D(128, (5, 5), activation='relu')(window_a)
    window_a = keras.layers.MaxPooling2D(pool_size=(4, 4))(window_a)
    window_a = keras.layers.Flatten()(window_a)
    window_a = Dense(1024, activation='sigmoid')(window_a)
   
    ver_line_finder = Conv2D(4, kernel_size=(50, 6), activation='relu')(keras_input)
    ver_line_finder = keras.layers.MaxPooling2D(pool_size=(10, 10))(ver_line_finder)
    ver_line_finder = Conv2D(64, (5, 5), activation='relu')(ver_line_finder)
    ver_line_finder = keras.layers.Flatten()(ver_line_finder)
    ver_line_finder = Dense(1024, activation='sigmoid')(ver_line_finder)

    hor_line_finder = Conv2D(4, kernel_size=(6, 50), activation='relu')(keras_input)
    hor_line_finder = keras.layers.MaxPooling2D(pool_size=(10, 10))(hor_line_finder)
    hor_line_finder = Conv2D(64, (5, 5), activation='relu')(hor_line_finder)
    hor_line_finder = keras.layers.Flatten()(hor_line_finder)
    hor_line_finder = Dense(1024, activation='sigmoid')(hor_line_finder)

    merged = keras.layers.concatenate([window_a, ver_line_finder, hor_line_finder])
    merged = keras.layers.Dropout(0.5)(merged)
    merged = Dense(4096, activation='relu')(merged)
    merged = keras.layers.Dropout(0.5)(merged)
    merged = Dense(4096, activation='relu')(merged)
    merged = keras.layers.Dropout(0.2)(merged)
    out = Dense(split_amount, activation='sigmoid')(merged)

    model = keras.models.Model(inputs=keras_input, outputs=out)
    #########################

    model.compile(loss=keras.losses.binary_crossentropy, optimizer = 'adadelta', metrics=['accuracy'])

    model.fit(x_train, y_train, validation_data = (x_valid, y_valid), epochs = 80, batch_size = 64)


    # Save the weights
    model.save_weights(os.path.join(Root, "Identifier", "model_weights.h5"))

    # Save the model architecture
    with open(os.path.join(Root, "Identifier", "model_architecture.json"), 'w') as f:
        f.write(model.to_json())
else:
    with open(os.path.join(Root, "Identifier", "model_architecture.json"), 'r') as f:
        model = model_from_json(f.read())

    model.load_weights(os.path.join(Root, "Identifier", "model_weights.h5"))


##############################Test Pdf#############################

Test_Pdf = [os.path.join(Root,"PDFs","op_amp.pdf")] #final pdf is for test
Test_pages = pdf2image.convert_from_path(Test_Pdf, resolution)

im_test = Test_pages[3]

Test_page = [[im_test]]
Test_data = numpy.expand_dims(image_spliter(Test_page, verticle_size, 1, Root), axis = 3)
results = model.predict(Test_data)


############Debug###########
for result_num, result in enumerate(results):
    print(result_num * 50, " ", result)



pixel_data = im_test.load()

for result_num, result in enumerate(results):
    for part_num, part in enumerate(result):
        if(part < .5):
            start = int(( (result_num * verticle_size) + (part_num * (verticle_size / split_amount)) ) / 2) + 25
            end = int(start + (.5 * verticle_size / split_amount))
            for y in range(start, end):
                for x in range(im_test.size[0]):
                    pixel_data[x,y] = (255,0,0)

im_test.save(os.path.join(Root, "Identifier", "Debug.png"), 'png')