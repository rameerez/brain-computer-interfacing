#!/usr/bin/env python3

'''	Loads the dataset 2a of the BCI Competition IV
available on http://bnci-horizon-2020.eu/database/data-sets
'''

import numpy as np
import scipy.io as sio

__author__ = "Michael Hersche and Tino Rellstab"
__email__ = "herschmi@ethz.ch,tinor@ethz.ch"

def get_data(subject,training,PATH):
    '''

    Loads the dataset 2a of the BCI Competition IV
    available on http://bnci-horizon-2020.eu/database/data-sets

    Keyword arguments:
    subject -- number of subject in [1, .. ,9]
    training -- if True, load training data
                if False, load testing data

    Return:	data_return 	numpy matrix 	size = NO_valid_trial x 22 x 1750
            class_return 	numpy matrix 	size = NO_valid_trial
    '''
    '''
    NO_channels = 22 # ->22
    NO_tests =  6*48
    Window_Length =  7*250 #->7*250
    

    class_return = np.zeros(NO_tests)
    data_return = np.zeros((NO_tests,NO_channels,Window_Length))

    NO_valid_trial = 0
    if training:
        a = sio.loadmat(PATH+'A0'+str(subject)+'T.mat')
    else:
        a = sio.loadmat(PATH+'A0'+str(subject)+'E.mat')
    a_data = a['data']
    for ii in range(0,a_data.size):
        a_data1 = a_data[0,ii]
        a_data2=[a_data1[0,0]]
        a_data3=a_data2[0]
        a_X 		= a_data3[0]
        a_trial 	= a_data3[1]
        a_y 		= a_data3[2]
        a_fs 		= a_data3[3]
        a_classes 	= a_data3[4]
        a_artifacts = a_data3[5]
        a_gender 	= a_data3[6]
        a_age 		= a_data3[7]
        for trial in range(0,a_trial.size):
            if(a_artifacts[trial]==0):
                data_return[NO_valid_trial,:,:] = np.transpose(a_X[int(a_trial[trial]):(int(a_trial[trial])+Window_Length),:22])
                class_return[NO_valid_trial] = int(a_y[trial])
                NO_valid_trial +=1

    return data_return[0:NO_valid_trial,:,:], class_return[0:NO_valid_trial]
                

    '''

    if training:

        class_return = np.load('./dataset_our/dataframes/labels/labels_final.npy')
        data_return = np.load('./dataset_our/dataframes/epochs_16ch/epochs_final.npy')

        data_return = data_return[:,4:15,:]

        from sklearn.utils import shuffle

        class_return, data_return = shuffle(class_return, data_return, random_state = 27 )
    #else:
       # class_return = np.load('./class_return.npy')
       # data_return = np.load('./df_shuffled_epoched_x9.npy')

    return data_return, class_return

