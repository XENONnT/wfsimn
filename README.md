# wfsimn
XENON nVeto waveform generator

### Input files
1. average pulse shape
2. MC (ryu1kup/pamn) data


### Output file
Strax friendly numpy structured arrays.


## Install
```
pip install git+https://github.com/XENONnT/wfsimn.git
```

## Usage
Clone this repository and see `notebooks/usage_examples.ipynb`.


## Develop
Main logic is written at `generate()` in `wfsimn/core.py`.
