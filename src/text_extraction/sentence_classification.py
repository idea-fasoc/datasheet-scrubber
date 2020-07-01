from supervised_classifier_ngram import supervised_classifier_ngram
import os


def sentence_classification(training_folder, testing_folder):
    feedback = 0  # 0 when nothing needs to change; 1 when bad is wrongly classified
    prob_subparagraph = "None"  # problem subparagraph: bad subparagraph wrongly classified as perfect
    prob_col = 2
    # label sentences as perfect and bad, training set in two folders
    perfect_label = 'perfect'
    bad_label = 'bad'
    perfect_path = [os.path.join(training_folder, 'perfect'), perfect_label]
    bad_path = [os.path.join(training_folder, 'bad'), bad_label]
    SOURCES = [perfect_path, bad_path]
    # define the directory with subparagraphs
    sentence_classification_result = []
    for subparagraph in os.listdir(testing_folder):
        subparagraph = os.path.join(testing_folder, subparagraph)
        classifier_result = supervised_classifier_ngram(SOURCES, subparagraph)
        sentence_classification_result = sentence_classification_result + classifier_result
    return sentence_classification_result
