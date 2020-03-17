__docformat__ = "restructuredtext"

# Let users know if they're missing any of our hard dependencies
hard_dependencies = ("numpy", "pandas", "mne")
missing_dependencies = []

for dependency in hard_dependencies:
  try:
    __import__(dependency)
  except ImportError as e:
    missing_dependencies.append(f"{dependency}: {e}")

if missing_dependencies:
  raise ImportError(
    "Unable to import required dependencies:\n" + "\n".join(missing_dependencies)
  )
del hard_dependencies, dependency, missing_dependencies


from bbtools.io import *
from bbtools.mne import *


# module level doc-string
__doc__ = """
bbtools - a library to manage and wrangle Bitbrain devices' EEG data
====================================================================
**bbtools** is a Python package providing tools to handle and transform EEG data generated from Bitbrain devices with ease. It's useful to transform raw capture data (typically in `csv` format) to more standard formats in the BCI industry, such as `MNE` objects.

Main Features
-------------
  - Transform `csv` EEG capture data into an MNE `raw` object
"""