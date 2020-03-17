#!/usr/bin/env python3

'''	general eigenvalue decomposition'''
import numpy as np
from scipy import linalg

__author__ = "Michael Hersche and Tino Rellstab"
__email__ = "herschmi@ethz.ch,tinor@ethz.ch"

def gevd(x1,x2,no_pairs):
	'''Solve generalized eigenvalue decomposition
	
	Keyword arguments:
	x1 -- numpy array of size [NO_channels, NO_samples]
	x2 -- numpy array of size [NO_channels, NO_samples]
	no_pairs -- number of pairs of eigenvectors to be returned 

	Return:	numpy array of 2*No_pairs eigenvectors 
	'''
	ev,vr= linalg.eig(x1,x2,right=True) 
	evAbs = np.abs(ev)
	sort_indices = np.argsort(evAbs)
	chosen_indices = np.zeros(2*no_pairs).astype(int)
	chosen_indices[0:no_pairs] = sort_indices[0:no_pairs]
	chosen_indices[no_pairs:2*no_pairs] = sort_indices[-no_pairs:]
	
	w = vr[:,chosen_indices] # ignore nan entries 
	return w