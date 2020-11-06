from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Conv2D
from keras.models import model_from_json
from sklearn.model_selection import train_test_split
import keras
import numpy

import pickle

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import os

def remake(single_data, x_list): #DEBUG ONLY
    x_max = len(single_data[0])
    y_max = len(single_data)

    output = []

    for word_depth in range(x_max):
        found = False
        for unique_words in range(y_max):
            if(single_data[unique_words][word_depth] == 1):
                found = True
                output.append(x_list[unique_words])
                break
        if(not found):
            output.append("N\A")
    print(output)
    print(output[4:8])
    return


def clean(temp_raw_data):   
    temp_raw_data = temp_raw_data.lower()

    raw_data = ""
    for char in temp_raw_data:
        if(ord(char) < 128):
            raw_data += char
        else:
            raw_data += " "

    raw_data = raw_data.strip()

    #########################################################
    long_string = ""
    start = 0
    space_count = 0
    last_char = ""
    for char_num, character in enumerate(raw_data): #remove tables/diagrams ##TODO IMPROVE
        if(character == "\n" and last_char == "\n"):
            if(space_count >= 2):
               long_string += raw_data[start:char_num]
            start = char_num + 1
            space_count = 0
        elif(character == " "):
            space_count += 1
        last_char = character
    ###########################################################



    tokens = word_tokenize(raw_data)
    #print(len(tokens))


    ###################################################################
    last_item = ""
    for item_num, item in enumerate(tokens): #fix hyphenated words
        if(len(last_item) > 1 and last_item[-1] == "-"):
            item = last_item[:-1] + item
            del tokens[item_num - 1]
        last_item = item
    #################################################################



    ############Replace numbers with NUMBER###########################
    number_array = []
    for item_num, item in enumerate(tokens): #fix hyphenated words
        has_num = False
        alpha_count = 0
        for char in item:
            if(char.isdigit()):
                has_num = True
            elif(char.isalpha()):
                alpha_count += 1

        if(has_num and alpha_count < 2):
            number_array.append([item_num, item])
            tokens[item_num] = "NUMBER"

    return tokens, number_array
    ##################################################################

def convert(fname):
    print("PDF START: ", fname, " -------------------------------------------------------------------------------------")
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, 'utf-8', laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    with open(fname, 'rb') as infile:
        for page_num, page in enumerate(PDFPage.get_pages(infile)):
            if(page_num < 1): #first x page(s)
                interpreter.process_page(page)
                text = output.getvalue()
    converter.close()  
    output.close
    return text 

def arrays_creater(single_pdf, x_list, output_window, type_array):
    split_array = []

    single_array2D = []      
    for word in x_list:
        single_array1D = [0 for x in range(len(single_pdf))]
        for item_count in range(0,len(single_pdf)):
            if(single_pdf[item_count] == word):
                single_array1D[item_count] = 1
        single_array2D.append(single_array1D)   

    massive_array = []
    for iter in range(0,len(single_pdf)-11,output_window):
        temp_array2D = []
        for word in x_list:
            temp_array1D = [0 for x in range(12)]
            for item_count in range(0,12):
                if(single_pdf[item_count+iter] == word):
                    temp_array1D[item_count] = 1
            temp_array2D.append(temp_array1D)     
        massive_array.append([temp_array2D, type_array])
    return massive_array

def phrase_locator(input_data, many_pharses, par_num, output_window): #one pdf

    temp_array = [-1 for x in range(len(input_data))]
    for pharses in many_pharses:
        for pharse in pharses[1:]:
            pharse = pharse.lower()
            pharse = pharse.strip()
                
            raw_pharse = ""
            for char in pharse:
                if(ord(char) < 128):
                    raw_pharse += char
                else:
                    raw_pharse += " "

            tokens = word_tokenize(raw_pharse)

            useful_phrase = False #Actually fix cases like 18-bit TODODODOODODODOD0
            for item_num, item in enumerate(tokens): #modify the pharse to be in the same format
                has_num = False
                alpha_count = 0
                for char in item:
                    if(char.isdigit()):
                        has_num = True
                    elif(char.isalpha()):
                        alpha_count += 1

                if(has_num and alpha_count < 2):
                    useful_phrase = True
                    tokens[item_num] = "NUMBER"
            
            if (useful_phrase and len(tokens) >= 3):
                num_loc = tokens.index("NUMBER")
                subtract_len = (len(tokens)) - num_loc
                match = 0        
                for word_count, word in enumerate(input_data):
                    if(match >= len(tokens)):
                        temp_array[word_count - subtract_len] = pharses[0]
                        match = 0
                        print("PHRASE: ", tokens)
                        print(word_count - subtract_len, " ", pharses[0])
                    else:
                        if(tokens[match] in input_data[word_count]):
                            match += 1
                        else:
                            match = 0

    massive_array = []
    center_finder = int((12-output_window)/2)
    for iter in range(center_finder,len(temp_array)-7,output_window): #TODO 7 IS BAD FIND A GOOD NUMBER WITH OUTPUTWINDOW INVOLVED
        small_array = [[0 for x in range(output_window)] for y in range(par_num)]
        for item_count in range(0,output_window):
            par_identify = temp_array[item_count+iter]
            if(par_identify > -1):
                small_array[par_identify][item_count] = 1  
        massive_array.append(small_array)

    return massive_array

def conversion(retrieve_labels, parameter_num):
    print(retrieve_labels)
    keys = ["Input Supply Voltage Range", "Resolution", "Sampling Frequency", "Temperature", "SNR",
            "INL", "DNL", "Conversion Rate", "Input Voltage", "Output Voltage",
            "Load Current", "Input Capacitance Range", "Output Frequency", "Reference Frequency", "Bandwidth",
            "Dropout Voltage", "Quiescent Current in Shutdown", "PSRR", "Output Current", "RMS",
            "Row", "Column", "Access Time", "Temperature Range", "Temperature Resolution"]
    mod_labels = []
    for key_num, key in enumerate(keys):
        if(key_num >= parameter_num):
            break
        if(key in retrieve_labels):
            mod_labels.append([key_num] + retrieve_labels[key])
    return mod_labels

def reversion(number):
    keys = ["Input Supply Voltage Range", "Resolution", "Sampling Frequency", "Temperature", "SNR",
            "INL", "DNL", "Conversion Rate", "Input Voltage", "Output Voltage",
            "Load Current", "Input Capacitance Range", "Output Frequency", "Reference Frequency", "Bandwidth",
            "Dropout Voltage", "Quiescent Current in Shutdown", "PSRR", "Output Current", "RMS",
            "Row", "Column", "Access Time", "Temperature Range", "Temperature Resolution"]
    return keys[number]



#with open(r"C:\Users\Zach\Downloads\training_set_ADC\3ad4002-4006-4010.p", "rb") as file:
#        temp = (pickle.load(file))
#        print("Here: ", temp)
#stop = input()
#############START############################
unique_words = 2500
output_window = 4 #need to change crop_amount manually to change this
parameter_num = 25 #MAX 25
reConvert = False
reBuild = True

Type = ["ADC", "CDC", "DCDC", "PLL", "LDO", "SRAM", "Temp_Sen"] 

folder_locs = [os.path.join(r"C:\Users\Zach\Downloads\Text_extract", Type_iter, "PDFs") for Type_iter in Type]
result_locs = [os.path.join(r"C:\Users\Zach\Downloads\Text_extract", Type_iter, "Results") for Type_iter in Type]


pdf_file_locs = [] #2D array of pdf file locations

full_type_array = []
for folder_iter, folder in enumerate(folder_locs):
    type_array = [0 for x in range(len(Type))]
    type_array[folder_iter] = 1
    for file in os.listdir(folder):
        pdf_file_locs.append(os.path.join(folder, file))
        full_type_array.append(type_array)

retrieve_labels = []
for folder in result_locs:
    for file in os.listdir(folder):
        with open(os.path.join(folder, file), "rb") as file_loc:
            retrieve_labels.append(conversion(pickle.load(file_loc), parameter_num))
print(retrieve_labels)

if(reConvert):
    raw_data = []
    for pdf_file in pdf_file_locs:
        try:
            raw_data.append(convert(pdf_file))
        except:
            print("FAIL") #If one fails they entire program will break

    with open(r"C:\Users\Zach\Downloads\Text_extract\raw_data.txt", "wb") as file:
        pickle.dump(raw_data, file)
    with open(r"C:\Users\Zach\Downloads\Text_extract\full_type_array.txt", "wb") as file:
        pickle.dump(full_type_array, file)
else:
    with open(r"C:\Users\Zach\Downloads\Text_extract\raw_data.txt", "rb") as file:
        raw_data = pickle.load(file)
    with open(r"C:\Users\Zach\Downloads\Text_extract\full_type_array.txt", "rb") as file:
        full_type_array = pickle.load(file)

#print(full_type_array)

if(reBuild):
    if(1): #temp
        ##############################################################find which words to use
        word_list = []
        clean_data = []
        temp_nums_array = []



        for raw in raw_data:
            temp_clean, temp_nums = clean(raw)
            clean_data.append(temp_clean)
            temp_nums_array += temp_nums
            word_list += temp_clean


        freq = (nltk.FreqDist(word_list)).most_common(unique_words)
        x_list = []
        for tup in freq:
            x_list.append(str(tup[0]))
        print(x_list)
        #################################################################

        data = []
        labels = []
        for item_count, item in enumerate(clean_data):
            labels += phrase_locator(item, retrieve_labels[item_count], parameter_num, output_window)
            data += arrays_creater(item, x_list, output_window, full_type_array[item_count])
        #print(clean_data)
        #print(labels)
        labels = numpy.array(labels)
        

        
        

        ##########trim data########################################################
        pos_data_buffer = 0
        trimmed_labels = []
        trimmed_data = []
        for iter_num, iter in enumerate(labels): #1 useful : 7 useless
            if(1 in iter):
                pos_data_buffer += 15 #Change this for debugging
                trimmed_labels.append(iter)
                trimmed_data.append(data[iter_num])
            else:
                if(pos_data_buffer >= 1):
                    trimmed_labels.append(iter)
                    trimmed_data.append(data[iter_num])
                    pos_data_buffer -= 1

        trimmed_labels = numpy.array(trimmed_labels)
        trimmed_data = numpy.array(trimmed_data)
        #######################################################################    
        numpy.save(r"C:\Users\Zach\Downloads\Text_extract\DATA", trimmed_data)
        numpy.save(r"C:\Users\Zach\Downloads\Text_extract\LABELS", trimmed_labels)
    else:
        trimmed_data = numpy.load(r"C:\Users\Zach\Downloads\Text_extract\DATA.npy")
        trimmed_labels = numpy.load(r"C:\Users\Zach\Downloads\Text_extract\LABELS.npy")



    #print(trimmed_labels)
    x_train, x_valid, y_train, y_valid = train_test_split(trimmed_data, trimmed_labels, test_size = 0.2, shuffle = True)

    double_train = [[],[]]
    for array in x_train:
        double_train[0].append(array[0])
        double_train[1].append(array[1])

    double_train[0] = numpy.expand_dims(numpy.array(double_train[0]), axis = 3)
    double_train[1] = numpy.array(double_train[1])


    double_valid = [[],[]]
    for array in x_valid:
        double_valid[0].append(array[0])
        double_valid[1].append(array[1])

    double_valid[0] = numpy.expand_dims(numpy.array(double_valid[0]), axis = 3)
    double_valid[1] = numpy.array(double_valid[1])


    #crop_amount = int((12 - output_window) / 2) #I HAVE TO HARD CODE THIS TO SAVE THE MODEL
    print("Starting Convolution") 

    keras_input = keras.layers.Input(shape=(unique_words,12,1), name='keras_input')
    keras_input2 = keras.layers.Input(shape = (len(Type),), name='keras_input2' )


    #########Type#########
    Type_shutdown_net = (Dense(parameter_num, activation='sigmoid'))(keras_input2)

    pharse_check_a = Conv2D(512, kernel_size=(unique_words, 2), strides = (1,1), activation='relu')(keras_input)
    pharse_check_a2 = keras.layers.MaxPooling2D(pool_size=(1,11), strides = (1,1))(pharse_check_a) #TODO TRY WITHOUT
    pharse_check_a3 = keras.layers.Flatten()(pharse_check_a2) 

    pharse_check_b = Conv2D(512, kernel_size=(unique_words, 4), strides = (1,1), activation='relu')(keras_input)
    pharse_check_b2 = keras.layers.MaxPooling2D(pool_size=(1,9), strides = (1,1))(pharse_check_b)
    pharse_check_b3 = keras.layers.Flatten()(pharse_check_b2)

    pharse_check_c = Conv2D(512, kernel_size=(unique_words, 6), strides = (1,1), activation='relu')(keras_input)
    pharse_check_c2 = keras.layers.MaxPooling2D(pool_size=(1,7), strides = (1,1))(pharse_check_c)
    pharse_check_c3 = keras.layers.Flatten()(pharse_check_c2)

    pharse_check_d = Conv2D(512, kernel_size=(unique_words, 8), strides = (1,1), activation='relu')(keras_input)
    pharse_check_d2 = keras.layers.MaxPooling2D(pool_size=(1,5), strides = (1,1))(pharse_check_d)
    pharse_check_d3 = keras.layers.Flatten()(pharse_check_d2)

    merged_phase_check = keras.layers.concatenate([pharse_check_a3, pharse_check_b3, pharse_check_c3, pharse_check_d3, keras_input2], axis=-1)
    pharse_check3 = (Dense(2048, activation='relu'))(merged_phase_check)
    pharse_check4 = (Dense(2048, activation='relu'))(pharse_check3) 
    pharse_check5 = (Dense(parameter_num, activation='sigmoid'))(pharse_check4)
    pharse_check6 = keras.layers.multiply([Type_shutdown_net,pharse_check5])
    #########Type#########


    #########POS#############
    number_loc = keras.layers.Lambda(lambda input : input[:,0,4:12-4,0])(keras_input) #REQUIRE A NUMBER/// This needs NUMBER to be in the top slot //THE 4s should be crop amount

    cropped_data = keras.layers.Cropping2D(cropping=((0, 0), (4, 4)))(keras_input) #removes data outside of the output window //The 4s should be crop amont
    real_data_a = Conv2D(256, kernel_size=(unique_words, 1), strides = (1,1), activation='relu')(cropped_data)
    real_data_a2 = keras.layers.Flatten()(real_data_a)
    real_data_b = Conv2D(256, kernel_size=(unique_words, 2), strides = (1,1), activation='relu')(cropped_data)
    real_data_b2 = keras.layers.Flatten()(real_data_b)
    real_data_c = keras.layers.Flatten()(cropped_data)
    real_data_c2 = (Dense(2048, activation='relu'))(real_data_c)

    large_data = Conv2D(512, kernel_size=(unique_words, 4), activation='relu')(keras_input)
    large_data2 = keras.layers.Flatten()(large_data) #input not cropped

    merged_phase_check = keras.layers.concatenate([real_data_a2, real_data_b2, real_data_c2, large_data2], axis=-1)
    real_data3 = (Dense(1024, activation='relu'))(merged_phase_check)
    merged_phase_check2 = keras.layers.concatenate([real_data3, pharse_check6, keras_input2], axis=-1)

    real_data4 = (Dense(512, activation='relu'))(merged_phase_check2) 
    real_data5 = (Dense(512, activation='relu'))(real_data4) 
    real_data6 = (Dense(output_window, activation='sigmoid'))(real_data5)
    real_data7 = keras.layers.multiply([number_loc,real_data6])
    #########POS############

    exact_loc = keras.layers.RepeatVector(parameter_num)(real_data7)
    type = keras.layers.RepeatVector(output_window)(pharse_check6)
    type2 = keras.layers.Permute((2,1))(type)

    merged = keras.layers.multiply([exact_loc,type2])

    model = keras.models.Model(inputs=[keras_input, keras_input2], outputs=merged)
    

    model.compile(loss=keras.losses.binary_crossentropy, optimizer = 'adadelta', metrics=['accuracy'])
    model.fit({'keras_input': double_train[0], 'keras_input2' : double_train[1]}, y_train, validation_data = ({'keras_input': double_valid[0], 'keras_input2' : double_valid[1]}, y_valid), epochs = 6000, batch_size = 256)


    # Save the weights
    model.save_weights(r"C:\Users\Zach\Downloads\Text_extract\model_weights.h5")
     # Save the model architecture
    with open(r"C:\Users\Zach\Downloads\Text_extract\model_architecture.json", 'w') as f:
        f.write(model.to_json())
    with open(r"C:\Users\Zach\Downloads\Text_extract\x_list.txt", "wb") as file:
        pickle.dump(x_list, file)
    numpy.save(r"C:\Users\Zach\Downloads\Text_extract\x_valid0", double_valid[0])
    numpy.save(r"C:\Users\Zach\Downloads\Text_extract\x_valid1", double_valid[1])
    numpy.save(r"C:\Users\Zach\Downloads\Text_extract\y_valid", y_valid)
else:
    with open(r"C:\Users\Zach\Downloads\Text_extract\model_architecture.json", 'r') as f:
        model = model_from_json(f.read())
    model.load_weights(r"C:\Users\Zach\Downloads\Text_extract\model_weights.h5")
    with open(r"C:\Users\Zach\Downloads\Text_extract\x_list.txt", "rb") as file:
        x_list = pickle.load(file)
    double_valid = [numpy.load(r"C:\Users\Zach\Downloads\Text_extract\x_valid0.npy"), numpy.load(r"C:\Users\Zach\Downloads\Text_extract\x_valid1.npy")]
    y_valid = numpy.load(r"C:\Users\Zach\Downloads\Text_extract\y_valid.npy")

model.summary()

#################TEST###############
final_results = model.predict(double_valid)

TP = 0
TN = 0
FP = 0
FN = 0
for sr_num, single_result in enumerate(final_results):
    large_index = sr_num * output_window
    print("------------------------------------ " + str(sr_num))
    
    for par_num, par in enumerate(single_result):
        for res_num, result in enumerate(par):
            if((result >= .5 and y_valid[sr_num][par_num][res_num] == 1)):
                print("SUCCESS")
                TP += 1
            elif((result < .5 and y_valid[sr_num][par_num][res_num] == 1)):
                print("FAIL_FN")
                FN += 1
                #print(single_result)
                #print(y_valid[sr_num])
                #print("")
            elif(result >= .5 and y_valid[sr_num][par_num][res_num] == 0):
                print("FAIL_FP")
                FP += 1
                #print(single_result)
                #print(y_valid[sr_num])
                #print("")
            else:
                TN += 1


print("Precision: ", TP/(TP+FP))
print("Recall: ", TP/(TP+FN))
print("Accuracy: ", (TP+TN)/(TP+TN+FP+FN))

while(1):
    num = int(input("Enter a number: "))
    if(num == -1):
        break
    print(Type[numpy.argmax(double_valid[1][num])])
    print(y_valid[num])
    remake(double_valid[0][num], x_list)
    for item_iter, item in enumerate(final_results[num]):
        print(reversion(item_iter), " ", item)
    print("")
    

####################################


#########DEBUG##################################
loc = "124si3500"
test_pdf = os.path.join(r"C:\Users\Zach\Downloads\Text\DCDC", (loc + ".pdf")) #other location
#test_pdf = os.path.join(r"C:\Users\Zach\Downloads\Text_extract\ADC\PDFs", (loc + ".pdf"))
test_clean, temp_nums = clean(convert(test_pdf))

print(test_clean)
test_data = arrays_creater(test_clean, x_list, output_window, [1,0,0,0,0,0,0])

double_final = [[],[]]
for array in test_data:
        double_final[0].append(array[0])
        double_final[1].append(array[1])

double_final[0] = numpy.expand_dims(numpy.array(double_final[0]), axis = 3)
double_final[1] = numpy.array(double_final[1])

results = model.predict(double_final)

#print(test_clean)

first_ele = [i[0] for i in temp_nums]

#with open(os.path.join(r"C:\Users\Zach\Downloads\Text_extract\ADC\Results", (loc + ".p")), "rb") as file_loc:
#    test_labels = pickle.load(file_loc)
#print(test_labels)

#test_labels = conversion(test_labels, parameter_num)
#phrase_locator(test_clean, test_labels, parameter_num, output_window) #here for debug only


for sr_num, single_result in enumerate(results):
    large_index = sr_num * 4
    for par_num, par in enumerate(single_result):
        for res_num, result in enumerate(par):
            if(result > .5):
                index = first_ele.index(large_index + res_num + 4) #need to offset
                print(reversion(par_num), " ", temp_nums[index])
#########DEBUG##################################



