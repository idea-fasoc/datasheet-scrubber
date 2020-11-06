from Address import Address
import pdf_cropper_for_extraction
from auto_classification import auto_classification
from os.path import join as p_join
from os.path import isdir
from os import mkdir, listdir, remove
from shutil import rmtree, copytree, copyfile


path_extracted = Address(1).split("\n")
base_dir = path_extracted[0]
auto_dir = p_join(base_dir, 'auto_generated')
if isdir(auto_dir):
    rmtree(auto_dir)
mkdir(auto_dir)
subject = 'ADC'
# input location of the basic training sets
page_classes = 'All_pages_text_twoclasses'
para_classes = 'All_paragraphs_text'
subpara_classes = 'All_subparagraph_text'
sentence_classes = 'All_sentences_text'
page_total = 'All_trained_datasheets'
para_total = 'All_paragraph_folders'
subpara_total = 'All_subparagraph_folders'
sentence_total = 'All_sentence_folders'
# input the folders you want to use:
page_train = 'page_training'
page_test = 'page_testing'
para_train = 'paragraph_training'
para_test = 'paragraph_testing'
subpara_train = 'subparagraph_training'
subpara_test = 'subparagraph_testing'
sentence_train = 'sentence_training'
sentence_test = 'sentence_testing'
tmp = 'tmp'

# input the testing set size used in cross validation:
k = 3

# build basic data
page_perfect = p_join(p_join(p_join(base_dir, page_classes), subject), 'perfect')
page_bad = p_join(p_join(p_join(base_dir, page_classes), subject), 'bad')
para_perfect = p_join(p_join(p_join(base_dir, para_classes), subject), 'perfect')
para_good = p_join(p_join(p_join(base_dir, para_classes), subject), 'good')
para_bad = p_join(p_join(p_join(base_dir, para_classes), subject), 'bad')
subpara_perfect = p_join(p_join(p_join(base_dir, subpara_classes), subject), 'perfect')
subpara_bad = p_join(p_join(p_join(base_dir, subpara_classes), subject), 'bad')
sentence_perfect = p_join(p_join(p_join(base_dir, sentence_classes), subject), 'perfect')
sentence_bad = p_join(p_join(p_join(base_dir, sentence_classes), subject), 'bad')
tmp = p_join(base_dir, tmp)
if isdir(tmp):
    rmtree(tmp)
perfect_page = [page.split('.txt')[0] for page in listdir(page_perfect)]
perfect_page = [page.split('.txt')[0] for page in listdir(page_bad)]
perfect_paragraph = [paragraph.split('.txt')[0] for paragraph in listdir(para_perfect)]
good_paragraph = [paragraph.split('.txt')[0] for paragraph in listdir(para_good)]
bad_paragraph = [paragraph.split('.txt')[0] for paragraph in listdir(para_bad)]
perfect_subparagraph = [subparagraph.split('.txt')[0] for subparagraph in listdir(subpara_perfect)]
bad_subparagraph = [subparagraph.split('.txt')[0] for subparagraph in listdir(subpara_bad)]
perfect_sentence = [[sentence.split('.txt')[0] for sentence in listdir(p_join(base_dir, 'zzz', folder))]
                    for folder in listdir(p_join(base_dir, 'zzz'))]
perfect_all_sentence = [sentence.split('.txt')[0] for sentence in listdir(sentence_perfect)]
# bad_sentence = [sentence.split('.txt')[0] for sentence in listdir(sentence_bad)]

# folder path
page_total = p_join(p_join(base_dir, page_total), subject)
para_total = p_join(p_join(base_dir, para_total), subject)
subpara_total = p_join(p_join(base_dir, subpara_total), subject)
sentence_total = p_join(p_join(base_dir, sentence_total), subject)
# training / testing path
page_train = p_join(auto_dir, page_train)
para_train = p_join(auto_dir, para_train)
subpara_train = p_join(auto_dir, subpara_train)
sentence_train = p_join(auto_dir, sentence_train)
page_test = p_join(auto_dir, page_test)
para_test = p_join(auto_dir, para_test)
subpara_test = p_join(auto_dir, subpara_test)
sentence_test = p_join(auto_dir, sentence_test)

"""simple classification"""
# if isdir(para_test):
#     rmtree(para_test)
# mkdir(para_test)
# if isdir(subpara_test):
#     rmtree(subpara_test)
# mkdir(subpara_test)
# if isdir(sentence_test):
#     rmtree(sentence_test)
# mkdir(sentence_test)
#
# result = auto_classification([page_train, para_train, subpara_train, sentence_train],
#                              [page_test, para_test, subpara_test, sentence_test])
# print(result)

"""cross validation"""
datasheet_list = []
for datasheet in listdir(page_total):
    datasheet_list.append(datasheet)
n = 0
accuracy = 0
wrong = 0
while k*n < len(datasheet_list):
    print(n)
    # prepare training and testing set folders
    for directory in [page_train, para_train, subpara_train, sentence_train, page_test, para_test, subpara_test, sentence_test]:
        if isdir(directory):
            rmtree(directory)
    for directory in [page_test, para_test, subpara_test, sentence_test]:
        mkdir(directory)
    # pick page folder for page testing
    testing_datasheet = [datasheet_list[k*n+i] for i in range(min(k, len(datasheet_list) - k*n))]
    # testing_folder = [paragraph_folder_list[k*n+i] for i in range(min(k, len(paragraph_folder_list) - k*n))]
    # copy the datasheets for testing
    for datasheet in testing_datasheet:
        copy_src = p_join(page_total, datasheet)
        copy_dir = p_join(page_test, datasheet)
        copyfile(copy_src, copy_dir)
    mkdir(tmp)
    pdf_cropper_for_extraction.pdf_cropper_multiple(page_test, tmp)
    testing_page = []
    for folder in listdir(tmp):
        folder = p_join(tmp, folder)
        testing_page = testing_page + [page for page in listdir(folder)]
    rmtree(tmp)
    # copy the paragraphs for testing
    testing_paragraph = []
    for page in testing_page:
        page = page.split('.pdf')[0]
        testing_paragraph_folder = p_join(para_total, page)
        if isdir(testing_paragraph_folder):
            testing_paragraph = testing_paragraph + [paragraph for paragraph in listdir(testing_paragraph_folder)]
    testing_subparagraph = []
    for paragraph in testing_paragraph:
        paragraph = paragraph.split('.txt')[0]
        testing_subparagraph_folder = p_join(subpara_total, paragraph)
        if isdir(testing_subparagraph_folder):
            testing_subparagraph = testing_subparagraph + \
                                   [subparagraph for subparagraph in listdir(testing_subparagraph_folder)]
    testing_sentence = []
    for subparagraph in testing_subparagraph:
        subparagraph = subparagraph.split('.txt')[0]
        testing_sentence_folder = p_join(sentence_total, subparagraph)
        if isdir(testing_sentence_folder):
            testing_sentence = testing_sentence + [sentence for sentence in listdir(testing_sentence_folder)]
    # copy total training set first
    copytree(p_join(p_join(base_dir, page_classes), subject), page_train)
    copytree(p_join(p_join(base_dir, para_classes), subject), para_train)
    copytree(p_join(p_join(base_dir, subpara_classes), subject), subpara_train)
    copytree(p_join(p_join(base_dir, sentence_classes), subject), sentence_train)
    # delete labels on testing files
    for folder in listdir(page_train):
        folder = p_join(page_train, folder)
        for test_file in listdir(folder):
            if test_file in testing_page:
                remove(p_join(folder, test_file))
    for folder in listdir(para_train):
        folder = p_join(para_train, folder)
        for test_file in listdir(folder):
            if test_file in testing_paragraph:
                remove(p_join(folder, test_file))
    for folder in listdir(subpara_train):
        folder = p_join(subpara_train, folder)
        for test_file in listdir(folder):
            if test_file in testing_subparagraph:
                remove(p_join(folder, test_file))
    for folder in listdir(sentence_train):
        folder = p_join(sentence_train,folder)
        for test_file in listdir(folder):
            if test_file in testing_sentence:
                remove(p_join(folder, test_file))
    result = auto_classification([page_train, para_train, subpara_train, sentence_train],
                                 [page_test, para_test, subpara_test, sentence_test])
    pred_perfect = [sentence for sentence, pred in result if pred == 'perfect']
    print(pred_perfect)
    for sentence_list in perfect_sentence:
        for sentence in sentence_list:
            if sentence in pred_perfect:
                accuracy += 1
                break
    for pred_sentence in pred_perfect:
        if pred_sentence not in perfect_all_sentence:
            wrong += 1
    n += 1
accuracy /= len(perfect_sentence)
print("Accuracy: extracted perfect sentences/real perfect sentences = ", accuracy)



