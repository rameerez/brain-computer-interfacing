import pandas as pd
import numpy as np
import mne
from scipy.signal import welch
import glob

# Importar los datos 
def cat_to_numeric(y):
    #Convert to pandas
    df = pd.DataFrame({'classes':y}, dtype='category')
    df['classes_numeric'] = df['classes'].cat.codes
    return df

def get_raw(dataset, paradigm, n_channels, sfreq, path):
    '''
    Takes a dataset from moabb datasets and creates 3 dictionaries with subject number as keys and X matrix, y labels and metadata
    as dictionary values respectively.
    X: Original 3D data matrix (num_cases, n_channels, lectures) is reshaped to 2D matrix (len(num_cases)*len(lectures),len(n_channels))
    y: This array corresponds with the class for each case. It has num_cases length.
    metadata: Describes each subject
    '''
    
    subjects_all = dataset.subject_list
    channels = [str(a) for a in range(n_channels)]
    

    X_all_subjects = {}
    y_all_subjects = {}
    metadata_all_subjects = {}
    
    for subject in subjects_all:
        
        X, y, metadata = paradigm.get_data(dataset=dataset, subjects=[subject])
        X = np.delete(X, -1,axis = 2)
        X_2d = X.reshape(n_channels,(X.shape[0]*X.shape[2]))
        data_mne = X_2d
        data_mne = data_mne / 1000000      
                        
        info_mne = mne.create_info(
            ch_names=channels,
            ch_types='eeg',
            sfreq=sfreq)
        
        raw = mne.io.RawArray(data_mne, info_mne)
        #ten_twenty_montage = mne.channels.make_standard_montage('standard_1020')
        #raw_1020 = raw.copy().set_montage(ten_twenty_montage)

        X_all_subjects.update({str(subject):raw})
        y_all_subjects.update({str(subject):y})
        metadata_all_subjects.update({str(subject):metadata})
    
    for k,v  in X_all_subjects.items():
        v.save(f'{path}_X_{k}.fif', overwrite=True)
        
    for k,v  in y_all_subjects.items():
        y = cat_to_numeric(v)
        y.to_csv(f'{path}_y_{k}.csv')
        
    return X_all_subjects, y_all_subjects, metadata_all_subjects       


# Preprocesado

def dir_to_raw(dir_path):
    '''Function for loading .fif data from a directory and creating a mne.io raw objects, storing them on a dict'''

    raw_dict = {}
    files = glob.glob(dir_path)

    print(files)  

    i = 0

    for file in files:
		
        raw_dict[str(i)] = mne.io.read_raw_fif(file, preload=True)
        i += 1
    return (raw_dict)


def filters(raw, fmin=0.5, fmax=100., notch=50., sampling_rate=512, fir_design='firwin'):
    '''Apply high/low-pass and notch filters:

        === Args ===
        * raw - mne Raw object: object to apply filters on
        * fmin, fmax - float: bandpass frequencies
        * notch - float: powerline (AC current) frequecy
        * ny_freq - float: Nyquist frequency. Half of the sampling rate
        * fir_design: str: Notch filter type. See mne doc for more details
        * sampling_rate - int, float: sampling rate of the measured data

        === Returns ===
        * raw_c - mne Raw object: Processed Raw copy
        '''
    raw_c = raw.copy()
    raw_c.filter(l_freq = fmin, h_freq = fmax)
    raw_c.notch_filter(np.arange(notch, sampling_rate / 2, notch), fir_design=fir_design)
    return raw_c


def make_epochs(raw, tmin=0.0, duration=5, id_name=333, sampling_rate=512):
    '''Epoch data based on regular known events:

        === Args ===
        * raw - mne Raw object: object to epoch
        * tmin, (duration) - float: time in seconds as the origin (duration) of the epoch since the event
        * id - int: id name for the events
        * sampling_rate - int, float: sampling rate of the measured data
        === Returns ===
        * events - array: time ticks of the events
        * epochs - mne Epochs object: Epoched data
        * raw_c - mne Raw object: Processed Raw copy
        '''

    raw_c = raw.copy()
    events = mne.make_fixed_length_events(raw_c, id=id_name, duration=duration - 1 / sampling_rate)
    # Reject trials
    epochs = mne.Epochs(raw_c, events, event_id=id_name, tmin=tmin, tmax=tmin + duration,
                        preload=True, baseline=None, verbose=True, reject=None)

    return events, epochs, raw_c


def plot_epochs(raw, events, epochs):
    raw.plot(events=events)


# Features


def convert_to_freq_domain(df, epoch='0', n_channels=15, sampling_rate=512):
    '''Use Welch's method to obtain the Power Spectral Density (PSD):

        === Args ===
        * df - pandas DataFrame: df with the time series data for one epoch, with channels as columns and entries as rows
        * epoch - string: epoch to perform the operation to
        * n_channels - int: number of total channels
        * sampling_rate - int, float: sampling rate of the measured data
        === Returns ===
        * df - pandas DataFrame: df with channels as columns and rows as frequencies
        '''

    psd = {}
    freq = {}
    data_epoch = df.loc[epoch][df.columns[2:n_channels + 2]].to_numpy()
    for i in range(data_epoch.shape[1]):
        freq[str(i)], psd[str(i)] = welch(data_epoch[:, i], fs=sampling_rate, nfft=4 * sampling_rate)

    df = pd.DataFrame(psd)
    df['Frequencies'] = freq['0']
    return df


def compute_average(df, fmin=7, fmax=14):
    '''Extract the feature of each channel as mean the value of the PSD for one epoch:

        === Args ===
        * df - pandas DataFrame: df with the PSD, with channels as columns and frequencies as rows
        * fmin, fmax - float, int: min and max frequencies of the selected band
        === Returns ===
        * df - pandas Series: one column with the features of each channel
        '''

    df_sel = df[(df.Frequencies >= fmin) & (df.Frequencies <= fmax)].copy()
    df_sel.drop('Frequencies', inplace=True, axis=1)
    means = df_sel.apply(np.mean, axis=0, result_type='expand')
    return means

def compute_csp(df):
    return df


# Pipelines

def prep_pipeline(raw, **kwargs):
    '''Returns events (mne), epochs (pandas df) and raw_epochs (mne)'''
    raw_filtered = filters(raw, **kwargs)
    events, epochs, raw_epochs = make_epochs(raw_filtered, **kwargs)

    return events, epochs.to_data_frame(index=['epoch']), raw_epochs


def feature_pipeline(df, **kwargs):
    '''Extract features from epochs from prep_pipeline()'''
    features_df = {}
    for epoch in pd.unique(df.index):
        psd_df = convert_to_freq_domain(df, epoch=epoch, **kwargs)
        csp_df = compute_csp(psd_df)  #Falta implementar
        features_df[epoch] = compute_average(csp_df, **kwargs)
    return pd.DataFrame(features_df).transpose()

