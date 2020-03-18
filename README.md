# wfsimn
XENON nVeto waveform generator

### Input files
1. average pulse shape
2. MC (ryu1kup/pamn) data


### Output file
Strax friendly numpy structured arrays.


## Install
```
git clone https://github.com/mzks/wfsimn.git
cd wfsimn
make
```

## Usage
See `notebooks/usage.ipynb`


## Develop
Main logic is written at `generate()` in `wfsimn/core.py`.
