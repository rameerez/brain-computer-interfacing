#!/usr/bin/env python3

'''	Functions used for common spatial patterns'''

import numpy as np 
from scipy.special import binom
import pyriemann.utils.mean as rie_mean
from filters import butter_fir_filter
from eig import gevd

__author__ = "Michael Hersche and Tino Rellstab"
__email__ = "herschmi@ethz.ch,tinor@ethz.ch"

def csp_one_one(cov_matrix,NO_csp,NO_classes):
	'''	
	calculate spatial filter for class all pairs of classes 

	Keyword arguments:
	cov_matrix -- numpy array of size [NO_channels, NO_channels]
	NO_csp -- number of spatial filters (24)

	Return:	spatial filter numpy array of size [22,NO_csp] 
	'''
	N, _ = cov_matrix[0].shape 
	n_comb = binom(NO_classes,2)

	NO_filtpairs = int(NO_csp/(n_comb*2))
	
	w = np.zeros((N,NO_csp))
	
	kk = 0 # internal counter 
	for cc1 in range(0,NO_classes):
		for cc2 in range(cc1+1,NO_classes):
			w[:,NO_filtpairs*2*(kk):NO_filtpairs*2*(kk+1)] = gevd(cov_matrix[cc1], cov_matrix[cc2],NO_filtpairs)
			kk +=1		
	return w 

def generate_projection(data,class_vec,NO_csp,filter_bank,time_windows,NO_classes=4): 
	'''	generate spatial filters for every timewindow and frequancy band

	Keyword arguments:
	data -- numpy array of size [NO_trials,channels,time_samples]
	class_vec -- containing the class labels, numpy array of size [NO_trials]
	NO_csp -- number of spatial filters (24)
	filter_bank -- numpy array containing butter sos filter coeffitions dim  [NO_bands,order,6]
	time_windows -- numpy array [[start_time1,end_time1],...,[start_timeN,end_timeN]] 

	Return:	spatial filter numpy array of size [NO_timewindows,NO_freqbands,22,NO_csp] 
	'''
	time_windows = time_windows.reshape((-1,2))
	NO_bands = filter_bank.shape[0]
	NO_time_windows = len(time_windows[:,0])
	NO_channels = len(data[0,:,0])
	NO_trials = class_vec.size

	# Initialize spatial filter: 
	w = np.zeros((NO_time_windows,NO_bands,NO_channels,NO_csp))
		
	# iterate through all time windows 
	for t_wind in range(0,NO_time_windows):
		# get start and end point of current time window 
		t_start = time_windows[t_wind,0]
		t_end = time_windows[t_wind,1]

		# iterate through all frequency bandwids 
		for subband in range(0,NO_bands): 

			cov = np.zeros((NO_classes,NO_trials, NO_channels,NO_channels)) # sum of covariance depending on the class
			cov_avg = np.zeros((NO_classes,NO_channels,NO_channels))
			cov_cntr = np.zeros(NO_classes).astype(int) # counter of class occurence 
					
			#go through all trials and estimate covariance matrix of every class 
			for trial in range(0,NO_trials):
				#frequency band of every channel
				data_filter = butter_fir_filter(data[trial,:,t_start:t_end], filter_bank[subband])
				cur_class_idx = int(class_vec[trial]-1)

				# caclulate current covariance matrix 
				cov[cur_class_idx,cov_cntr[cur_class_idx],:,:] = np.dot(data_filter,np.transpose(data_filter))

				# update covariance matrix and class counter 
				cov_cntr[cur_class_idx] += 1

			# calculate average of covariance matrix 
			for clas in range(0,NO_classes):
				cov_avg[clas,:,:] = rie_mean.mean_covariance(cov[clas,:cov_cntr[clas],:,:], metric = 'euclid')
			w[t_wind,subband,:,:] = csp_one_one(cov_avg,NO_csp,NO_classes) 
	return w


def generate_eye(data,class_vec,filter_bank,time_windows): 
	'''	generate unity spatial filters for every timewindow and frequancy band

	Keyword arguments:
	data -- numpy array of size [NO_trials,channels,time_samples]
	class_vec -- containing the class labels, numpy array of size [NO_trials]
	filter_bank -- numpy array containing butter sos filter coeffitions dim  [NO_bands,order,6]
	time_windows -- numpy array [[start_time1,end_time1],...,[start_timeN,end_timeN]] 

	Return:	spatial unity filter numpy array of size [NO_timewindows,NO_freqbands,22,NO_csp] 
	'''
	time_windows = time_windows.reshape((-1,2))
	NO_bands = filter_bank.shape[0]
	NO_time_windows = len(time_windows[:,0])
	NO_channels = len(data[0,:,0])
	NO_trials = class_vec.size

	# Initialize spatial filter: 
	w = np.zeros((NO_time_windows,NO_bands,NO_channels,NO_channels))
	for t_wind in range(NO_time_windows):
		for band in range(NO_bands):
			w[t_wind,band] = np.eye(NO_channels)
	return w

def extract_feature(data,w,filter_bank,time_windows):
	'''	calculate features using the precalculated spatial filters

	Keyword arguments:
	data -- numpy array of size [NO_trials,channels,time_samples]
	w -- spatial filters, numpy array of size [NO_timewindows,NO_freqbands,22,NO_csp]
	filter_bank -- numpy array containing butter sos filter coeffitions dim  [NO_bands,order,6]
	time_windows -- numpy array [[start_time1,end_time1],...,[start_timeN,end_timeN]] 

	Return:	features, numpy array of size [NO_trials,(NO_csp*NO_bands*NO_time_windows)] 
	'''
	NO_csp = len(w[0,0,0,:])
	time_windows = time_windows.reshape((-1,2))
	NO_time_windows = int(time_windows.size/2)
	NO_bands = filter_bank.shape[0]
	NO_trials = len(data[:,0,0])
	NO_features = NO_csp*NO_bands*NO_time_windows
	
	feature_mat = np.zeros((NO_trials, NO_time_windows,NO_bands,NO_csp))
	
	# initialize feature vector 
	feat = np.zeros((NO_time_windows,NO_bands,NO_csp))

	# go through all trials 
	for trial in range(0,NO_trials):	

		# iterate through all time windows 
		for t_wind in range(0,NO_time_windows):
			# get start and end point of current time window 
			t_start = time_windows[t_wind,0]
			t_end = time_windows[t_wind,1]

			for subband in range(0,NO_bands):
				#Apply spatial Filter to data 
				cur_data_s = np.dot(np.transpose(w[t_wind,subband]),data[trial,:,t_start:t_end])
				
				#frequency filtering  
				cur_data_f_s = butter_fir_filter(cur_data_s,filter_bank[subband])

				# calculate variance of all channels 
				feat[t_wind,subband] = np.var(cur_data_f_s,axis=1)
	
			# calculate log10 of normalized feature vector 
		
		
		for subband in range(0,NO_bands):
			feat[:,subband] = np.log10(feat[:,subband])#/np.sum(feat[:,subband]))

		# store feature in list 	
		feature_mat[trial,:,:,:] = feat	
	return np.reshape(feature_mat,(NO_trials,-1)) #