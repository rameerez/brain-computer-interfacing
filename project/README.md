# Motor Imagery for two-class task classification

We will use motor imagery data for training a machine learning model capable of discerning between two classes. This prediction can be used to potentially move objects with our minds.


## A 30.000ft view of the process

1. Import data
2. Preprocessing *(load -> highpass, lowpass, notch filter -> (csp) -> artifacts -> psd -> make epochs)*
3. Feature extraction *(load epochs -> get mu band -> average mu band -> make feature)*
4. Model training & prediction *(train/test split -> training -> prediction)*


## Data IO (data shapes and formats) for each stage

### 1. Import data
 - **Input**: MOABB
 - **Output**: `.fif` -> `ndarray[15, 160*5*512] -> [channels, readings]`

### 2. Preprocessing *(load -> highpass, lowpass, notch filter -> (csp) -> artifacts -> psd -> make epochs)*
 - **Input**: `.fif` -> `ndarray[15, 160*5*512] -> [channels, readings]`
 - **Output**: `ndarray[15, 512*5, 160]` -> `[channels, epoch_length, n_epochs]`

### 3. Feature extraction *(load epochs -> get mu band -> average mu band -> make feature)*
 - **Input**: `ndarray[15, 512*5, 160]` -> `[channels, epoch_length, n_epochs]`
 - **Output**: `ndarray[15, 160]` -> `[channels, epoch_channel_mu_band_average]`

### 4. Model training & prediction *(train/test split -> training -> prediction)*
 - **Input**: `ndarray[15, 160]` -> `[channels, epoch_channel_mu_band_average]`
 - **Output**: prob. class