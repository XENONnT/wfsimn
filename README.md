# wfsimn
XENON nVeto waveform generator (prototype)

### Input files
1. average pulse shape
2. MC nSorted data

### Output file
List of waveforms in each events.
As a default, waveform is ndarray (500,120). (500 timebin (each 2ns) * 120 PMTs of nVeto)


## Install
```
git clone https://github.com/mzks/wfsimn.git
cd wfsimn
make
```

## Usage
See `notebooks/simple_sample.ipynb`

## Develop
Main logic is written at `generate()` in `wfsimn/core.py`.
User-friendly source should be developed.
I also would like to prepare a document as soon as possible.
