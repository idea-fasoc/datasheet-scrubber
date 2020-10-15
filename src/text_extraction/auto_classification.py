from Address import Address
from single_layer_classification import page_classification, paragraph_classification, subparagraph_classification, sentence_classification
from os.path import isdir
import os
import shutil


def auto_classification(training_list, testing_list):
    [page_train, para_train, subpara_train, sentence_train] = training_list
    [page_test, para_test, subpara_test, sentence_test] = testing_list
    print("start page classification:")
    page_classification_result = page_classification(page_train, page_test)
    has_perfect = False
    for page, pred in page_classification_result:
        if pred == 'perfect':
            has_perfect = True
            copy_src = os.path.join("All_paragraph_folders/ADC", page)
            copy_dst = os.path.join(para_test, page)
            if isdir(copy_src):
                shutil.copytree(copy_src, copy_dst)
                print("Correctly classified page: {}".format(page))
            else:
                print("Wrongly classified page: {}".format(page))
    if not has_perfect:
        print('no perfect page in this testing group')
        exit(0)
    print("start paragraph classification:")
    paragraph_classification_result = paragraph_classification(para_train, para_test)
    for result_list in paragraph_classification_result:
        has_perfect = False
        for paragraph, pred in result_list:
            if pred == 'perfect':
                has_perfect = True
                copy_src = os.path.join("All_subparagraph_folders/ADC", paragraph)
                copy_dst = os.path.join(subpara_test, paragraph)
                shutil.copytree(copy_src, copy_dst)
        if not has_perfect:
            for paragraph, pred in result_list:
                if pred == 'good':
                    copy_src = os.path.join("All_subparagraph_folders/ADC", paragraph)
                    copy_dst = os.path.join(subpara_test, paragraph)
                    shutil.copytree(copy_src, copy_dst)
    print("start subparagraph classification:")
    subparagraph_classification_result = subparagraph_classification(subpara_train, subpara_test)
    for subparagraph, pred in subparagraph_classification_result:
        if pred == 'perfect':
            copy_src = os.path.join("All_sentence_folders/ADC", subparagraph)
            copy_dst = os.path.join(sentence_test, subparagraph)
            if isdir(copy_src):
                shutil.copytree(copy_src, copy_dst)
                print("Correctly classified subparagraph: {}".format(subparagraph))
            else:
                print("Wrongly classified subparagraph: {}".format(subparagraph))
    print("start sentence classification:")
    sentence_classification_result = sentence_classification(sentence_train, sentence_test)
    return sentence_classification_result
