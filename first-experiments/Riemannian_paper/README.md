# Fast and Accurate Multiclass Inference for MI-BCIs Using Large Multiscale Temporal and Spectral Features

This is the code of an accepted conference paper submitted to EUSIPCO 2018. The preprint is available on this arXiv [link](https://arxiv.org/abs/1806.06823). If you are using this code please cite our paper. 

## Getting Started

First, download the source code.
Then, download the dataset "Four class motor imagery (001-2014)" of the [BCI competition IV-2a](http://bnci-horizon-2020.eu/database/data-sets). Put all files of the dataset (A01T.mat-A09E.mat) into a subfolder within the project called 'dataset' or change self.data_path in main_csp and main_riemannian. 

### Prerequisites

- python3
- numpy
- sklearn
- pyriemann
- scipy

The packages can be installed easily with conda and the _config.yml file: 
```
$ conda env create -f _config.yml -n msenv
$ source activate msenv 
```

### Recreate results

For the recreation of the CSP results run main_csp.py. 
Change self.svm_kernel for testing different kernels:
- self.svm_kernel='linear'  -> self.svm_c = 0.05
- self.svm_kernel='rbf'     -> self.svm_c = 20
- self.svm_kernel='poly'    -> self.svm_c = 0.1

```
$ python3 main_csp.py
```
For the recreation of the Riemannian results run main_riemannian.py. 
Change self.svm_kernel for testing different kernels:
- self.svm_kernel='linear'  -> self.svm_c = 0.1
- self.svm_kernel='rbf'     -> self.svm_c = 20

Change self.riem_opt for testing different means:
- self.riem_opt = "Riemann"
- self.riem_opt = "Riemann_Euclid" 
- self.riem_opt = "Whitened_Euclid"
- self.riem_opt = "No_Adaptation"

```
$ python3 main_riemannian.py
```

## Authors

* **Michael Hersche** - *Initial work* - [MHersche](https://github.com/MHersche)
* **Tino Rellstab** - *Initial work* - [tinorellstab](https://github.com/tinorellstab)
