![Bitbrain x Saturdays.AI](/assets/bitbrain-x-ai-saturdays-madrid.png)

# AI6's Brain-Computer Interfacing Research & Study Group

![Saturdays.AI](https://img.shields.io/badge/status-active-brightgreen)
![GitHub contributors](https://img.shields.io/github/contributors/rameerez/brain-computer-interfacing)
![GitHub](https://img.shields.io/github/license/rameerez/brain-computer-interfacing)


[Saturdays.AI](https://saturdays.ai) is a global initiative to democratize access to Artificial Intelligence education at the quality and rigour of the world’s best universities, in the form of 14-week bootcamps.

We've partnered with [Bitbrain](https://bitbrain.com), a leading world-class neurotechnology company, to explore projects at the intersection of Brain-Computer Interfacing (BCI) and Artificial Intelligence (AI).

![Part of the Saturdays.AI's BCI EEG team](/assets/saturdays-ai-bitbrain-bci-eeg-team.JPG)

## The bootcamp course `/course`

As part of this collaboration and within the context of Saturdays.AI, our main goal is to create an introductory Brain-Computer Interfacing bootcamp to be done over the course of 14 weeks.

We ourselves will be the first students and beta users of this course, which, if successful, will be exported to the rest of the cities in the [Saturdays.AI](https://saturdays.ai) network as a new specialization path together with the usual Machine Learning, Deep Learning and Reinforcement Learning specialization paths.

The course will propose a number of readings and resources to read through the week and will introduce a related code-based challenge to solve during the hands-on team meeting on Saturdays.


![Javi Rameerez wearing a Bitbrain's 16-ch EEG BCI headset](/assets/javi-rameerez-eeg-bci-headset.jpg)

## The end goal

One of our goals is to finish the bootcamp with enough knowledge to move objects "with our minds". Technically, we will gather EEG brainwaves using a Bitbrain 16-channel headset (as seen in the picture) and we will create machine learning models to create classifiers capable of predicting the required actions to move motor-enabled objects such as electric wheelchairs or RC cars.

Our initial experiments exploring approaches to achieve this can be found in `/first-experiments`.

![Javi Rameerez BCI EEG brainwaves](/assets/javi-rameerez-bci-eeg-brainwaves.JPG)

## Data Collection

![](/assets/eeg-10-20-location.png)

We're using a [Bitbrain EEG headset](https://www.bitbrain.com/neurotechnology-products/semi-dry-eeg/versatile-eeg) (semi-dry electrodes).

All electrodes were placed following the 10-20 system.

Four electrodes related to motor imagery were placed along the primary motor cortex area (`C1`, `C2`, `C3` and `C4`)

`Fp1`, `Fp2`, `Fp3` and `Fp4` were used to record blinking artifacts.


`P7`, `01`, `02` and `P8` were also used.


## How to get started

// TODO Bitbrain's Python wrapper `py-bbt-sdk-1.4.5-win64` probably needs to be located within `/vendor`, but can't probably be distributed and uploaded to the repo due to copyright issues. Bitbrain's SDK only works in Windows environments.

## How to contribute

To understand the project, read through the Jupyter notebooks in order. We're trying to keep them well documented and self-explainable.

PRs are welcome.

If you make contributions to a notebook, feel free to add yourself as one of the authors at the top of said notebook.

Adding Markdown cells to the notebooks to explain unclear things is always a plus, so feel free to add any necessary documentation.

Help is most likely specially needed with data science / artificial intelligence engineering at the most recent notebook. We try to keep this work updated so the last notebook will most likely reflect the current state of the project and where we're currently stuck at.

Please contact us with any questions!
