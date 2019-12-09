
import numpy as np
import pandas as pd
import os
import pickle

np.random.seed(42)

def epoch(data, samples_epoch, samples_overlap=0):
    """Extract epochs from a time series.
    Given a 2D array of the shape [n_samples, n_channels]
    Creates a 3D array of the shape [wlength_samples, n_channels, n_epochs]
    Args:
        data (numpy.ndarray or list of lists): data [n_samples, n_channels]
        samples_epoch (int): window length in samples
        samples_overlap (int): Overlap between windows in samples
    Returns:
        (numpy.ndarray): epoched data of shape
    """

    if isinstance(data, list):
        data = np.array(data)

    n_samples, n_channels = data.shape

    samples_shift = samples_epoch - samples_overlap

    n_epochs =  int(np.floor((n_samples - samples_epoch) / float(samples_shift)) + 1)

    # Markers indicate where the epoch starts, and the epoch contains samples_epoch rows
    markers = np.asarray(range(0, n_epochs + 1)) * samples_shift
    markers = markers.astype(int)

    # Divide data in epochs
    epochs = np.zeros((samples_epoch, n_channels, n_epochs))

    for i in range(0, n_epochs):
        epochs[:, :, i] = data[markers[i]:markers[i] + samples_epoch, :]

    return epochs

starting_time = [23.36,13.31,13.90,12.28,11.02,12.93,8.05,7.89,7.72,12.45,9.06,10.17,5.95,7.15,12.15,11.45,6.91,9.34]
dir = './dataset_our/'

def array_preparaing(starting_time, dir):
    dirs = sorted([dir+f for f in os.listdir(dir)])
    files = sorted([dir+'/'+file for dir in dirs for file in os.listdir(dir) if file == 'EEG.csv'])
    starting_time = starting_time
    class_number = 3
    samples = len(starting_time)*class_number
    channels = 16
    samples_per_second = 256
    seconds_per_training_label = 10
    samples_per_training_label = seconds_per_training_label * samples_per_second
    epochs_final = np.zeros((samples,channels,samples_per_training_label))
    class_final = np.empty(samples)
    
    counter_i = 1
    
    for file,starting_seconds in zip(files,starting_time):
    
        print(file,' Staring_seconds: ',starting_seconds)
        df = pd.read_csv(file)
    
        starting_sample = int(starting_seconds * samples_per_second)
    

        first_label_start = starting_sample
        second_label_start = starting_sample + samples_per_training_label
        third_label_start = second_label_start + samples_per_training_label
        third_label_end = third_label_start + samples_per_training_label
    
        for i, row in df.iterrows():
            if first_label_start <= i <= second_label_start:
                df.at[i, 'label'] = "left"
                df.at[i, 'label_code'] = 1
            elif second_label_start <= i <= third_label_start:
                df.at[i, 'label'] = "right"
                df.at[i, 'label_code'] = 2
            elif third_label_start <= i <= third_label_end:
                df.at[i, 'label'] = "rest"
                df.at[i, 'label_code'] = 0
            else:
                df.at[i, 'label'] = "none"
                df.at[i, 'label_code'] = -1
    
    
    
        print(type(df))
        df.to_pickle("./dataset_our/dataframes/full_df/labelled-raw-eeg_"+str(counter_i)+".pkl")
    
        df = df.loc[df['label'] != 'none']  # Eliminamos las lecturas que no pertenecen a ninguna clase
    
        print('df ',counter_i)
        print(' ')
        print("Left: ",len(df.loc[df['label'] == "left"]))
        print('Right: ',len(df.loc[df['label'] == "right"]))
        print('Rest: ',len(df.loc[df['label'] == "rest"]))
        print(len(df))
    
    
        df.reset_index( inplace=True )
        df = df.drop([0])  # Quitamos el primer registro para que cada clase todos tenga 2560 lecturas
        df.reset_index(inplace=True)

        df = df.drop(columns=(['timestamp', 'sequence', 'battery', 'flags', 'index', 'level_0']), axis=1)
    
        print('df ',counter_i)
        print(' ')
        print("Left: ",len(df.loc[df['label'] == "left"]))
        print('Right: ',len(df.loc[df['label'] == "right"]))
        print('Rest: ',len(df.loc[df['label'] == "rest"]))
    
        #Guardamos las labels como np array
        df_labels = df[df.columns[-2:]]
        np.save("./dataset_our/dataframes/labels/labels_"+str(counter_i), df_labels.to_numpy())
        class_final[(counter_i-1)*class_number:(counter_i*class_number)] = np.array([1.,2.,0.])
        np.save("./dataset_our/dataframes/labels/labels_final", class_final)
    
        # Guardamos los 16 canales  como np array
        df_allchannels = df.drop(columns=(['label', 'label_code']), axis=1)
        print(df_allchannels.head())
        np.save("./dataset_our/dataframes/16_channels/16_channels_"+str(counter_i), df_allchannels.to_numpy())
    
        #Calculamos el epochs
        epochs = epoch(df_allchannels.to_numpy(), 3)
        print('epochs_',counter_i,': ',epochs.shape)
        np.save("./dataset_our/dataframes/epochs_16ch/epochs_16ch_"+str(counter_i), epochs)
        epochs_final[((counter_i-1)*class_number):counter_i*class_number,0:channels,0:samples_per_training_label] = epochs
        np.save( "./dataset_our/dataframes/epochs_16ch/epochs_final", epochs_final)



        counter_i += 1

    return print(epochs_final.shape)







array_preparaing(starting_time, dir)



