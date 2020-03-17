#!/usr/bin/env python3

'''	Functions used for calculating the Riemannian features'''

import numpy as np
from pyriemann.utils import mean,base
import scipy 

from filters import butter_fir_filter
from eig import gevd

__author__ = "Michael Hersche and Tino Rellstab"
__email__ = "herschmi@ethz.ch,tinor@ethz.ch"

class riemannian_multiscale:
	""" Riemannian feature multiscale class 

	Parameters
	----------

	filter_bank : array, shape (n_freq,order,(order))
		Filterbank coefficients: If FIR dim = 2
								If IIR dim = 3
	temp_windows : array, shape (n_temp,2)
		start and end sample of temporal window 

	riem_opt : String {'Riemann', "Riemann_Euclid","Whitened_Euclid","No_Adaptation"}
		Riemannian option 

	rho: float 
		Regularization parameter for covariance calculation 

	vectorized: bool 
		Concatenate all frequency bands and temp window features to one vector

	Attributes
	----------

	Examples
	--------
	
	"""

	def __init__(self,filter_bank,temp_windows,riem_opt = 'Riemann',rho = 0.1,vectorized = True):
		# Frequency bands 
		self.filter_bank = filter_bank
		self.n_freq = filter_bank.shape[0]
		# Temporal windows 
		self.temp_windows = temp_windows
		self.n_temp = temp_windows.shape[0]
		# determine kernel function 
		if riem_opt == 'Whitened_Euclid':
			self.riem_kernel = self.whitened_kernel
		else: 
			self.riem_kernel = self.log_whitened_kernel 
		# determine mean metric 
		if riem_opt == 'Riemann':
			self.mean_metric = 'riemann'
		elif riem_opt == 'Riemann_Euclid' or riem_opt == 'Whitened_Euclid':
			self.mean_metric = 'euclid'
		self.riem_opt = riem_opt 

		# regularization 
		self.rho = rho
		# vectorization (for SVM) 
		self.vectorized = vectorized



	def fit(self,data):
		'''
		Calculate average covariance matrices and return freatures of training data

		Parameters
		----------
		data: array, shape (n_tr_trial,n_channel,n_samples)
			input training time samples 
		
		Return  
		------
		train_feat: array, shape: if vectorized: (n_tr_trial,(n_temp x n_freq x n_riemann)
								  else 			 (n_tr_trial,n_temp , n_freq , n_riemann)
		'''

		n_tr_trial,n_channel,_ = data.shape
		self.n_channel = n_channel
		self.n_riemann = int((n_channel+1)*n_channel/2)

		cov_mat = np.zeros((n_tr_trial,self.n_temp,self.n_freq,n_channel,n_channel))
		
		# calculate training covariance matrices  
		for trial_idx in range(n_tr_trial):	
			
			for temp_idx in range(self.n_temp): 
				t_start,t_end  = self.temp_windows[temp_idx,0] ,self.temp_windows[temp_idx,1]
				n_samples = t_end-t_start
				
				for freq_idx in range(self.n_freq): 
					# filter signal 
					data_filter = butter_fir_filter(data[trial_idx,:,t_start:t_end], self.filter_bank[freq_idx])
					# regularized covariance matrix 
					cov_mat[trial_idx,temp_idx,freq_idx] = 1/(n_samples-1)*np.dot(data_filter,np.transpose(data_filter)) + self.rho/n_samples*np.eye(n_channel)
		

		# calculate mean covariance matrix 
		self.c_ref_invsqrtm = np.zeros((self.n_freq,n_channel,n_channel))

		for freq_idx in range(self.n_freq): 
			
			if self.riem_opt == 'No_Adaptation': 
				self.c_ref_invsqrtm[freq_idx]= np.eye(n_channel)
			else: 
				# Mean covariance matrix over all trials and temp winds per frequency band 
				cov_avg = mean.mean_covariance(cov_mat[:,:,freq_idx].reshape(-1,n_channel,n_channel), metric = self.mean_metric)
				self.c_ref_invsqrtm[freq_idx] = base.invsqrtm(cov_avg)

		# calculate training features 
		train_feat = np.zeros((n_tr_trial,self.n_temp,self.n_freq,self.n_riemann))

		for trial_idx in range(n_tr_trial):	
			for temp_idx in range(self.n_temp): 				
				for freq_idx in range(self.n_freq): 
					
					train_feat[trial_idx,temp_idx,freq_idx] = self.riem_kernel(cov_mat[trial_idx,temp_idx,freq_idx],self.c_ref_invsqrtm[freq_idx])

		if self.vectorized: 
			return train_feat.reshape(n_tr_trial,-1)
		else: 
			return train_feat


	def features(self,data):
		'''
		Generate multiscale Riemannian features 

		Parameters
		----------
		data: array, shape (n_trial,n_channel,n_samples)
			input time samples 
		
		Return  
		------
		feat: array, shape: if vectorized: (n_trial,(n_temp x n_freq x n_riemann)
								  else 			 (n_trial,n_temp , n_freq , n_riemann)
		'''
		n_trial = data.shape[0]

		feat = np.zeros((n_trial,self.n_temp,self.n_freq,self.n_riemann))

		# calculate training covariance matrices  
		for trial_idx in range(n_trial):	
			
			for temp_idx in range(self.n_temp): 
				t_start,t_end  = self.temp_windows[temp_idx,0] ,self.temp_windows[temp_idx,1]
				n_samples = t_end-t_start


				for freq_idx in range(self.n_freq): 
					# filter signal 
					data_filter = butter_fir_filter(data[trial_idx,:,t_start:t_end], self.filter_bank[freq_idx])
					
					# regularized covariance matrix 
					cov_mat = 1/(n_samples-1)*np.dot(data_filter,np.transpose(data_filter)) + self.rho/n_samples*np.eye(self.n_channel)
					# 
					feat[trial_idx,temp_idx,freq_idx] = self.riem_kernel(cov_mat,self.c_ref_invsqrtm[freq_idx])

		if self.vectorized: 
			return feat.reshape(n_trial,-1)
		else: 
			return feat

	def onetrial_feature(self,data):
		'''
		Generate multiscale Riemannian one trial and temp window 

		Parameters
		----------
		data: array, shape (n_channel,n_samples)
			input time samples 
		
		Return  
		------
		feat: array, shape: if vectorized: (n_freq x n_riemann)
								  else 		(n_freq , n_riemann)
		'''
		n_samples = data.shape[1]

		feat = np.zeros((self.n_freq,self.n_riemann))

		for freq_idx in range(self.n_freq): 
					# filter signal 
					data_filter = butter_fir_filter(data, self.filter_bank[freq_idx])
					
					# regularized covariance matrix 
					cov_mat = 1/(n_samples-1)*np.dot(data_filter,np.transpose(data_filter)) + self.rho/n_samples*np.eye(self.n_channel)
					# 
					feat[freq_idx] = self.riem_kernel(cov_mat,self.c_ref_invsqrtm[freq_idx])

		if self.vectorized: 
			return feat.reshape(-1)
		else: 
			return feat


	def half_vectorization(self,mat):
		'''	Calculates half vectorization of a matrix

		Parameters
		----------
		mat: array, shape(n_channel,n_channel)
			Input symmetric matrix 
		
		Output
		----------
		vec: array, shape (n_riemann,)
			Vectorized matrix 
		'''
		_,N = mat.shape 

		NO_elements = ((N+1)*N/2)
		NO_elements = int(NO_elements)
		out_vec = np.zeros(NO_elements)

		# fill diagonal elements with factor one 
		for diag in range(0,N):
			out_vec[diag] = mat[diag,diag]

		sqrt2 = np.sqrt(2)
		idx = N
		for col in range(1,N):
			for row in range(0,col):
				out_vec[idx] = sqrt2*mat[row,col]
				idx +=1
		return out_vec

	def whitened_kernel(self,mat,c_ref_invsqrtm): 
		return self.half_vectorization(np.dot(np.dot(c_ref_invsqrtm,mat),c_ref_invsqrtm)) 

	def log_whitened_kernel(self,mat,c_ref_invsqrtm): 
		return self.half_vectorization(base.logm(np.dot(np.dot(c_ref_invsqrtm,mat),c_ref_invsqrtm))) 
