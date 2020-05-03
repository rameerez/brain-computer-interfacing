import pandas as pd
import numpy as np

from scipy.signal import welch


def cat_to_numeric(y):
    '''
    Transforms categorical list into df with numeric classes
    '''
    df = pd.DataFrame({'classes': y}, dtype='category')
    df['classes_numeric'] = df['classes'].cat.codes
    return df


def extract_features(dataset, paradigm, sampling_rate, path):
    '''
    Takes a dataset from moabb and stracts features
    '''

    subjects_all = dataset.subject_list

    k = 0
    for subject in subjects_all:
        print(f'{k}\n')
        X, y, _ = paradigm.get_data(dataset=dataset, subjects=[subject])
        X = np.delete(X, -1, axis = 2)

        # Labels
        y_numeric = cat_to_numeric(y)
        y_numeric.to_csv(f'{path}_y_{k}.csv')

        features = {}
        #Features
        for trial in range(X.shape[0]):
            epoch = X[trial]
            epoch_transformed = np.apply_along_axis(welch, 1, epoch, fs = sampling_rate, nperseg = sampling_rate)
            features[str(trial)] = epoch_transformed[5:35,1].reshape(257*10,)

        pd.DataFrame(features).transpose().to_csv(f'{path}_x_{k}.csv', index = False)


        k += 1
