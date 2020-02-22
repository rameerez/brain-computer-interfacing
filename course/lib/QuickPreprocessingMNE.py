import mne
import pandas as pd
import numpy as np

def Bitbrain_to_raw(path, channels_list, sampling_rate):
    '''Loading Bitbrain's .CSV EEG into a mne.io.raw object'''
    
    df = pd.read_csv(path)
    df_mne = df.drop(['timestamp', 'sequence', 'battery', 'flags'], axis=1)

    '''Transpose'''
    data_mne = df_mne.to_numpy().transpose()

    '''Scale'''
    data_mne = data_mne / 1000000

    '''Raw info'''
    channels = channels_list
    info_mne = mne.create_info(ch_names=channels,ch_types='eeg',sfreq = sampling_rate)

    bbt_raw = mne.io.RawArray(data_mne, info_mne)
    ten_twenty_montage = mne.channels.make_standard_montage('standard_1020')

    '''Final Raw object'''
    raw_1020 = bbt_raw.copy().set_montage(ten_twenty_montage)
    
    return raw_1020

def high_low_filter_notches(raw, fmin = 0.5, fmax = 100, fnotch = 50.):
    '''Apply High/low filters and notch filters to raw data:
	- raw [mne.io.raw object]: raw data
	- fmin [float]: high pass filter
	- fmax [float]: low pass filter
	'''
    fig = raw.plot_psd(fmin = 0, fmax = fmax + 100, average=False, tmin = 0, tmax = 250)
    
    raw.filter(l_freq = fmin, h_freq = fmax, method = 'iir')
    powerEEG = raw.plot_psd(fmin = 0, fmax = 200, average=False, tmin = 0, tmax = 250)
    timeEEG = raw.plot(start = 0., duration = 250., scalings=0.5e-3, remove_dc=True)
   
    raw.notch_filter(fnotch, fir_design='firwin')
    powerEEG = raw.plot_psd(fmin = 0, fmax = 200, average=False, tmin = 0, tmax = 250)
    timeEEG = raw.plot(start = 0., duration = 250., scalings=0.5e-3, remove_dc=True)
    
    return raw

def interpolate_bat_electrodes(raw, bad_channels_list):
    
    raw.info['bads'] = bad_channels_list
    
    print('Bad electrodes: ', raw.info['bads'])
    raw.interpolate_bads(reset_bads=False)
    
    return raw

def epochs_around_false_events(raw, event_duration= 1., criteria = 1.3e-4, eventid = 333):
    
    events = mne.make_fixed_length_events(raw, id = eventid, duration = event_duration)
    
    reject_criteria = dict(eeg = criteria)

    epochs = mne.Epochs(raw, events, event_id = 333, tmin=-0.2, tmax=0.5,
                        reject=reject_criteria, preload=True)

    fig = epochs.plot(scalings=0.5e-4, block=True)
    
    epochs.plot_image()
    
    return epochs
