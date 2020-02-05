#!/usr/bin/env python3

'''	Functions used for bandpass filtering and freuquency band generation'''

import numpy as np
from scipy import signal 
from scipy.signal import butter, sosfilt, sosfreqz


__author__ = "Michael Hersche and Tino Rellstab"
__email__ = "herschmi@ethz.ch,tinor@ethz.ch"

# def bandpass_filter(signal_in,f_band_nom):
# 	'''	Filter N channels with fir filter of order 101

# 	Keyword arguments:
# 	signal_in -- numpy array of size [NO_channels, NO_samples]
# 	f_band_nom -- normalized frequency band [freq_start, freq_end]

# 	Return:	filtered signal 
# 	'''
# 	numtabs = 101
# 	h = signal.firwin(numtabs,f_band_nom,pass_zero=False)
# 	NO_channels ,NO_samples = signal_in.shape 
# 	sig_filt = np.zeros((NO_channels ,NO_samples))

# 	for channel in range(0,NO_channels):
# 		sig_filt[channel] = signal.convolve(signal_in[channel,:],h,mode='same') # signal has same size as signal_in (centered)

# 	return sig_filt

def bandpass_filter(signal_in,f_band_nom): 


	'''	Filter N channels with fir filter of order 101

	Keyword arguments:
	signal_in -- numpy array of size [NO_channels, NO_samples]
	f_band_nom -- normalized frequency band [freq_start, freq_end]

	Return:	filtered signal 
	'''
	order = 4
	sos = butter(order, f_band_nom, analog=False, btype='band', output='sos')
	sig_filt = sosfilt(sos, signal_in)

	return sig_filt

def load_bands(bandwidth,f_s,max_freq = 40):
	'''	Filter N channels with fir filter of order 101

	Keyword arguments:
	bandwith -- numpy array containing bandwiths ex. [2,4,8,16,32]
	f_s -- sampling frequency

	Return:	numpy array of normalized frequency bands
	'''
	f_bands = np.zeros((99,2)).astype(float)
	
	band_counter = 0
	for bw in bandwidth:
		startfreq = 4
		while (startfreq + bw <= max_freq): 
			f_bands[band_counter] = [startfreq, startfreq + bw]
			
			if bw ==1: # do 1Hz steps
				startfreq = startfreq +1
			elif bw == 2: # do 2Hz steps
				startfreq = startfreq +2 
			else : # do 4 Hz steps if Bandwidths >= 4Hz
				startfreq = startfreq +4

			band_counter += 1 

	# convert array to normalized frequency 
	f_bands_nom = 2*f_bands[:band_counter]/f_s
	return f_bands_nom


def load_filterbank(bandwidth,fs, order = 4, max_freq = 40,ftype = 'butter'): 
	'''	Calculate Filters bank with Butterworth filter  

	Keyword arguments:
	bandwith -- numpy array containing bandwiths ex. [2,4,8,16,32]
	f_s -- sampling frequency

	Return:	numpy array containing filters coefficients dimesnions 'butter': [N_bands,order,6] 'fir': [N_bands,order]
	'''
	
	f_band_nom = load_bands(bandwidth,fs,max_freq) # get normalized bands 
	n_bands = f_band_nom.shape[0]
	
	if ftype == 'butter': 
		filter_bank = np.zeros((n_bands,order,6))
	elif ftype == 'fir':
		filter_bank = np.zeros((n_bands,order))



	for band_idx in range(n_bands):
		if ftype == 'butter': 
			filter_bank[band_idx] = butter(order, f_band_nom[band_idx], analog=False, btype='band', output='sos')
		elif ftype == 'fir':
			
			
			filter_bank[band_idx] = signal.firwin(order,f_band_nom[band_idx],pass_zero=False)
	return filter_bank

def butter_fir_filter(signal_in,filter_coeff):

	if filter_coeff.ndim == 2: # butter worth 
		return sosfilt(filter_coeff, signal_in)
	elif filter_coeff.ndim ==1: # fir filter 
		
		NO_channels ,NO_samples = signal_in.shape 
		sig_filt = np.zeros((NO_channels ,NO_samples))

		for channel in range(0,NO_channels):
			sig_filt[channel] = signal.convolve(signal_in[channel,:],filter_coeff,mode='same') # signal has same size as signal_in (centered)
		
		return sig_filt
		

def butter_bandpass(lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        sos = butter(order, [low, high], analog=False, btype='band', output='sos')
        return sos

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
        sos = butter_bandpass(lowcut, highcut, fs, order=order)
        y = sosfilt(sos, data)
        return y



