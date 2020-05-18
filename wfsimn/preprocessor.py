import os
from tqdm import tqdm
import numpy as np
import pandas as pd
import uproot


class preprocessor:
    """
    nSort files preprocessor for wfsimn
    """
    def __init__(self, inputfiles=None, qe_table=None):
        self.set_input(inputfiles)
        self.qe_table = qe_table
        self.pmthitid = None
        self.pmthittime = None
        self.pmthitenergy = None

    def set_input(self, inputfiles):
        """
        set input files to self.input
        support multiple input files or a text file listing them
        """

        if inputfiles is None:
            pass
        elif type(inputfiles) == str and inputfiles.split('.')[-1] == 'txt':
            inputfiles = [root.replace('\n', '') for root in open(inputfiles)]
        elif type(inputfiles) == str and inputfiles.split('.')[-1] == 'root':
            inputfiles = [inputfiles]
        self.input = inputfiles

    def add_input(self, inputfiles):
        """
        add input files to self.input
        """

        if type(inputfiles) == str and inputfiles.split('.')[-1] == 'txt':
            inputfiles = [root.replace('\n', '') for root in open(inputfiles)]
        elif type(inputfiles) == str and inputfiles.split('.')[-1] == 'root':
            inputfiles = [inputfiles]
        self.input = self.input + inputfiles

    def set_qe_table(self, qe_table):
        self.qe_table = qe_table

    def _to_ndarray(self, pmthitid, pmthittime, pmthitenergy, filling=-1):
        """
        convert pmthitid, pmthittime and pmthitenergy opened by uproot to ndarray
        note: not to be used from outside
        """

        maxlen = 0
        for i in range(len(pmthitid)):
            if maxlen < len(pmthitid[i]):
                maxlen = len(pmthitid[i])

        pmthitid_ = np.zeros((len(pmthitid), maxlen))
        pmthittime_ = np.zeros((len(pmthitid), maxlen))
        pmthitenergy_ = np.zeros((len(pmthitid), maxlen))
        for idx, (i, t, e) in enumerate(zip(pmthitid, pmthittime, pmthitenergy)):
            fill = np.full(maxlen - len(i), filling)
            pmthitid_[idx] = np.concatenate((i, fill))
            pmthittime_[idx] = np.concatenate((t, fill))
            pmthitenergy_[idx] = np.concatenate((e, fill))

        return pmthitid_, pmthittime_, pmthitenergy_

    def _apply_qe(self, pmthitid, pmthittime, pmthitenergy):
        """
        apply QE correction to pmthitid, pmthittime and pmthitenergy
        note: not to be used from outside
        """

        nv_pmt_wl, nv_pmt_qe = np.loadtxt(self.qe_table, unpack=True)
        wavelength = 1239.84 / pmthitenergy

        mask = np.full_like(pmthitenergy, False)
        for i in range(len(nv_pmt_wl) - 1):
            idx = np.where((pmthitid >= 20000) & (nv_pmt_wl[i] <= wavelength) & (wavelength < nv_pmt_wl[i+1]))
            prob = np.random.rand(*mask[idx].shape)
            mask[idx] = 0.01 * ((nv_pmt_qe[i+1] - nv_pmt_qe[i]) / (nv_pmt_wl[i+1] - nv_pmt_wl[i]) * (wavelength[idx] - nv_pmt_wl[i]) + nv_pmt_qe[i]) > prob

        mask = mask.astype(np.bool)
        nentries = len(mask)
        pmthitid_ = [pmthitid[i, mask[i]] for i in range(nentries)]
        pmthittime_ = [pmthittime[i, mask[i]] for i in range(nentries)]
        return pmthitid_, pmthittime_

    def load_nsorted(self):
        """
        get pmthit branches with QE correction applied
        """

        assert self.input is not None, 'nSort files are not specified. Call preprocessor.set_input(inputfiles).'
        assert self.qe_table is not None, 'QE table is not specified. Call preprocessor.set_qe_table(qe_table).'
        assert os.path.exists(self.qe_table), 'Specified QE table is not found. Please set correct path with preprocessor.set_qe_table(qe_table).'

        pmthitids = []
        pmthittimes = []
        with tqdm(self.input, desc='load nsorted') as pbar:
            for i, f in enumerate(pbar):
                pbar.set_postfix(input=f.split('/')[-1])
                events = uproot.open(f)['events/events']
                tree = events.arrays(['pmthitid', 'pmthittime', 'pmthitenergy'])

                pmthitid, pmthittime, pmthitenergy = tree[b'pmthitid'], tree[b'pmthittime'], tree[b'pmthitenergy']
                pmthitid, pmthittime, pmthitenergy = self._to_ndarray(pmthitid, pmthittime, pmthitenergy)
                pmthitid, pmthittime = self._apply_qe(pmthitid, pmthittime, pmthitenergy)

                pmthitids += pmthitid
                pmthittimes += pmthittime

        self.pmthitid = pmthitids
        self.pmthittime = pmthittimes
        return self.pmthitid, self.pmthittime


if __name__ == '__main__':
    inputfiles = 'input_mc201.txt'
    qe_table = '/home/ryuichi/pypamn/data/R5912QE.dat'
    preprocessor = preprocessor(inputfiles, qe_table)
    pmthitid, pmthittime = preprocessor.load_nsorted()
