"""
Wrapper on top of some MNE utilities
"""

import mne

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