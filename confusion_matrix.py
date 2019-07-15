import numpy as np
import supervised_classifier_ngram
from supervised_classifier_ngram import supervised_classifier_ngram

#def confusionMatrix(y_true, y_pred, class_num = 15):
def confusionMatrix(y_true, y_pred, class_num = 13):
    """
    y_true represents the array of real classes ("targets" array in the implement
    of the training part of classifier function); y_pred represents the
    "predictions" array returned by the classifiers.
    """
    conf_matrix = np.zeros((class_num, class_num))
    true = []
    prediction = []
    """
    Labeling ADC, PLL, DCDC, CDC, Temperature_Sensor, SRAM, LDO as class 0-6
    respectively; if we need to add Opamp as a class as well, simply add one
    elif in the first two loops (and turn default class_num into 8).
    """
    for t in y_true:
        if t == 'ADC':
            true.append(0)
        elif t == 'PLL':
            true.append(1)
        elif t == 'DCDC':
            true.append(2)
        elif t == 'CDC':
            true.append(3)
        elif t == 'Temperature_Sensor':
            true.append(4)
        elif t == 'SRAM':
            true.append(5)
        elif t == 'LDO':
            true.append(6)
        elif t == 'BDRT':
            true.append(7)
        elif t == 'counters':
            true.append(8)
        #elif t == 'DAC':
         #   true.append(9)
        #elif t == 'Delay_Line':
         #   true.append(10)
        #elif t == 'DSP':
         #   true.append(11)
        #elif t == 'IO':
         #   true.append(12)
        #elif t == 'Opamp':
         #   true.append(13)
        #elif t == 'Digital_Potentiometers':
         #   true.append(14)
        elif t == 'DSP':
            true.append(9)
        elif t == 'IO':
            true.append(10)
        elif t == 'Opamp':
            true.append(11)
        elif t == 'Digital_Potentiometers':
            true.append(12)
    for p in y_pred:
        if p == 'ADC':
            prediction.append(0)
        elif p == 'PLL':
            prediction.append(1)
        elif p == 'DCDC':
            prediction.append(2)
        elif p == 'CDC':
            prediction.append(3)
        elif p == 'Temperature_Sensor':
            prediction.append(4)
        elif p == 'SRAM':
            prediction.append(5)
        elif p == 'LDO':
            prediction.append(6)
        elif p == 'BDRT':
            prediction.append(7)
        elif p == 'counters':
            prediction.append(8)
        #elif p == 'DAC':
         #   prediction.append(9)
        #elif p == 'Delay_Line':
        #    prediction.append(10)
        #elif p == 'DSP':
         #   prediction.append(11)
        #elif p == 'IO':
         #   prediction.append(12)
        #elif p == 'Opamp':
         #   prediction.append(13)
        #elif p == 'Digital_Potentiometers':
         #   prediction.append(14)
        elif p == 'DSP':
            prediction.append(9)
        elif p == 'IO':
            prediction.append(10)
        elif p == 'Opamp':
            prediction.append(11)
        elif p == 'Digital_Potentiometers':
            prediction.append(12)
    for t,p in zip(true, prediction):
        conf_matrix[t][p] += 1
    return conf_matrix

#def performance(y_true, y_pred, class_num = 15, metric = 'accuracy'):
def performance(y_true, y_pred, class_num = 13, metric = 'accuracy'):
    score = 0
    data_size = len(y_true)
    conf_matrix = confusionMatrix_multi(y_true, y_pred, class_num)
    for i in range(class_num):
        score += conf_matrix[i][i]
    score /= data_size
    return score
