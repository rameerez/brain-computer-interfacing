#!/usr/bin/env python3

''' 
Model for common spatial pattern (CSP) feature calculation and classification for EEG data
'''

import numpy as np
import time
from sklearn.svm import LinearSVC, SVC
from sklearn.model_selection import KFold

# import self defined functions 
from csp import generate_projection,generate_eye,extract_feature
from get_data import get_data
from filters import load_filterbank 

__author__ = "Michael Hersche and Tino Rellstab"
__email__ = "herschmi@ethz.ch,tinor@ethz.ch"

class CSP_Model:

	def __init__(self):
		self.crossvalidation = False
		self.data_path 	= 'dataset/'
		self.svm_kernel	= 'linear' #'sigmoid'#'linear' # 'sigmoid', 'rbf', 'poly'
		self.svm_c 	= 0.1 # 0.05 for linear, 20 for rbf, poly: 0.1
		self.useCSP = True
		self.NO_splits = 5 # number of folds in cross validation 
		self.fs = 250. # sampling frequency 
		self.NO_channels = 22 # number of EEG channels 
		self.NO_subjects = 9
		self.NO_csp = 24 # Total number of CSP feature per band and timewindow
		self.bw = np.array([2,4,8,16,32]) # bandwidth of filtered signals 
		# self.bw = np.array([1,2,4,8,16,32])
		self.ftype = 'butter' # 'fir', 'butter'
		self.forder= 2 # 4
		self.filter_bank = load_filterbank(self.bw,self.fs,order=self.forder,max_freq=40,ftype = self.ftype) # get filterbank coeffs  
		time_windows_flt = np.array([
		 						[2.5,3.5],
		 						[3,4],
		 						[3.5,4.5],
		 						[4,5],
		 						[4.5,5.5],
		 						[5,6],
		 						[2.5,4.5],
		 						[3,5],
		 						[3.5,5.5],
		 						[4,6],
		 						[2.5,6]])*self.fs # time windows in [s] x fs for using as a feature

		# time_windows_flt = np.array([
		#						[2.5,3.5],
		#						[3,4],
		#						[4,5],
		#						[5,6],
		#						[2.5,4.5],
		#						[4,6],
		#						[2.5,6]])*self.fs # time windows in [s] x fs for using as a feature
		self.time_windows = time_windows_flt.astype(int)
		# restrict time windows and frequency bands 
		# self.time_windows = self.time_windows[10] # use only largest timewindow
		# self.filter_bank = self.filter_bank[18:27] # use only 4Hz bands 
		
		self.NO_bands = self.filter_bank.shape[0]
		self.NO_time_windows = int(self.time_windows.size/2)
		self.NO_features = self.NO_csp*self.NO_bands*self.NO_time_windows
		self.train_time = 0
		self.train_trials = 0
		self.eval_time = 0
		self.eval_trials = 0
		
	def run_csp(self):

		################################ Training ############################################################################
		start_train = time.time()
		# 1. Apply CSP to bands to get spatial filter 
		if self.useCSP: 
			w = generate_projection(self.train_data,self.train_label, self.NO_csp,self.filter_bank,self.time_windows)
		else: 
			w = generate_eye(self.train_data,self.train_label,self.filter_bank,self.time_windows)


		# 2. Extract features for training 
		feature_mat = extract_feature(self.train_data,w,self.filter_bank,self.time_windows)

		# 3. Stage Train SVM Model 
		# 2. Train SVM Model 
		if self.svm_kernel == 'linear' : 
			clf = LinearSVC(C = self.svm_c, intercept_scaling=1, loss='hinge', max_iter=1000,multi_class='ovr', penalty='l2', random_state=1, tol=0.00001)
		else:
			clf = SVC(self.svm_c,self.svm_kernel, degree=10, gamma='auto', coef0=0.0, tol=0.001, cache_size=10000, max_iter=-1, decision_function_shape='ovr')
		clf.fit(feature_mat,self.train_label) 
		
		end_train = time.time()
		self.train_time += end_train-start_train
		self.train_trials += len(self.train_label)

		################################# Evaluation ###################################################
		start_eval = time.time()
		eval_feature_mat = extract_feature(self.eval_data,w,self.filter_bank,self.time_windows)

		success_rate = clf.score(eval_feature_mat,self.eval_label)

		end_eval = time.time()
		
		#print("Time for one Evaluation " + str((end_eval-start_eval)/len(self.eval_label)) )

		self.eval_time += end_eval-start_eval
		self.eval_trials += len(self.eval_label)


		return success_rate 


	def load_data(self):		
			if self.crossvalidation:
				data,label = get_data(self.subject,True,self.data_path)
				kf = KFold(n_splits=self.NO_splits)
				split = 0 
				for train_index, test_index in kf.split(data):
					if self.split == split:
						self.train_data = data[train_index]
						self.train_label = label[train_index]
						self.eval_data = data[test_index]
						self.eval_label = label[test_index]
					split += 1
			else:
				self.train_data,self.train_label = get_data(self.subject,True,self.data_path)
				self.eval_data,self.eval_label = get_data(self.subject,False,self.data_path)





def main():


	model = CSP_Model()

	print("Number of used features: "+ str(model.NO_features))

	# success rate sum over all subjects 
	success_tot_sum = 0

	if model.crossvalidation:
		print("Cross validation run")
	else: 
		print("Test data set")
	start = time.time()

	# Go through all subjects 
	for model.subject in range(1,model.NO_subjects+1):

		#print("Subject" + str(model.subject)+":")
		

		if model.crossvalidation:
			success_sub_sum = 0 

			for model.split in range(model.NO_splits):
				model.load_data()
				success_sub_sum += model.run_csp()
				print(success_sub_sum/(model.split+1))
			# average over all splits 
			success_rate = success_sub_sum/model.NO_splits

		else: 
			# load Eval data 
			model.load_data()
			success_rate = model.run_csp()

		print(success_rate)
		success_tot_sum += success_rate 


	# Average success rate over all subjects 
	print("Average success rate: " + str(success_tot_sum/model.NO_subjects))

	print("Training average time: " +  str(model.train_time/model.NO_subjects))
	print("Evaluation average time: " +  str(model.eval_time/model.NO_subjects))

	end = time.time()	

	print("Time elapsed [s] " + str(end - start))

if __name__ == '__main__':
	main()
