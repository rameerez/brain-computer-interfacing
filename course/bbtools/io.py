"""
Contains tools for processing Bitbrain files into MNE objects
"""

import mne
import pandas as pd
import numpy as np

def read_csv(eeg_csv, channels, sfreq = 256, montage = 'standard_1020', useless_cols = ['timestamp', 'sequence', 'battery', 'flags']):
  df = pd.read_csv(eeg_csv)
  df_mne = df.drop(useless_cols, axis=1)

  # Transpose the matrix because MNE expects it like that
  data_mne = df_mne.to_numpy().transpose()

  # Scale the data
  # data_mne = data_mne / 1000000

  # Create MNE Raw's Info object
  info_mne = mne.create_info(
      #ch_names=list(df_mne.columns),
      ch_names=channels,
      ch_types='eeg',
      sfreq=sfreq)

  bbt_raw = mne.io.RawArray(data_mne, info_mne)
  ten_twenty_montage = mne.channels.make_standard_montage(montage)

  raw = bbt_raw.copy().set_montage(ten_twenty_montage)
  return raw