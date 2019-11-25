import pkg_resources
import logging
import numpy as np
from scipy import fftpack
import pandas as pd
from tqdm import tqdm
import uproot
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(context='notebook', style='whitegrid', palette='bright')


class generator():

    def __init__(self, seed=0):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Generator Initialize')
        np.random.seed(seed)
        self.__data_path = pkg_resources.resource_filename('wfsimn', 'data/')

    def load_data(self, average_pulse_file_name, mc_file_name):

        self.average_pulse = np.load(average_pulse_file_name)

        file = uproot.open(mc_file_name)  # nSorted file
        events = file['events/events']
        self.hit_ids = events.array('pmthitid')  # nveto id 20000--20199
        self.hit_times = events.array('pmthittime') * 1.e9 # unit: ns
        self.nentries = len(self.hit_ids)

        self.logger.info('#of events in TTree:'+str(self.nentries))

    def generate_by_mc(self):

        wfs = []
        # print('Generating pulse...')
        for i_ev in tqdm(range(self.nentries)):
            wf = self.generate_1ev_by_mc(i_ev)
            wfs.append(wf)
        return wfs

    def generate_1ev_by_mc(self, eventid=0):

        min_timing = 9999999999.
        for (id, time) in zip(self.hit_ids[eventid], self.hit_times[eventid]):
            if (not 20000 <= id < 20120): continue
            if (min_timing > time): min_timing = time
        hit_time_test = self.hit_times[eventid] - min_timing

        wf = self.generate(self.hit_ids[eventid], hit_time_test)

        return wf

    def generate(self, pmt_ids, pmt_times):
        # pmt_ids (20000--20119)
        # pmt_times (ns)
        self.__num_gen_tbins = 500  # bins bin/2ns
        self.__num_spe_tbins = 50  # tbins bin/2ns
        self.__num_pmts = 120  # total number of nVeto PMTs

        self.__simulated_pulse = np.zeros((self.__num_gen_tbins, self.__num_pmts))

        # 1. Add dark rate
        dark_ids, dark_times = self.add_dark()
        pmt_ids = np.append(pmt_ids, dark_ids)
        pmt_times = np.append(pmt_times, dark_times)

        for (pmt_id, pmt_time) in zip(pmt_ids, pmt_times):

            if not 20000 <= pmt_id < 20120: continue
            pmt_id = pmt_id - 20000

            # 1. About timing
            # 1.1 Transit Time Spread - tentative value from SWT
            pmt_time = pmt_time + np.random.normal(0, 3.0/2.354820) # 3 ns FWHM as tentative
            # 1.2 Transit Time - Not considered (No data from SWT)
            # 1.3 After pulse - Not considered yet (conservatively)

            # 2. Add Pulses
            # 2.1 SPE Spread
            gain_spread_factor = np.random.normal(1, 0.3)  # 30%, very tentative value estimatd from SWT

            # 2.2 Add Pulse
            tbin = int(pmt_time / 2)
            active_bin = self.__num_gen_tbins - tbin

            if 0 < active_bin <= self.__num_spe_tbins:
                self.__simulated_pulse[tbin:tbin + active_bin, pmt_id] += self.average_pulse[0:active_bin] * gain_spread_factor
            elif self.__num_spe_tbins < active_bin <= self.__num_gen_tbins:
                active_bin = self.__num_spe_tbins
                self.__simulated_pulse[tbin:tbin + active_bin, pmt_id] += self.average_pulse[0:active_bin] * gain_spread_factor
            elif self.__num_gen_tbins < active_bin:
                active_bin -= 500
                self.__simulated_pulse[0:active_bin, pmt_id] += self.average_pulse[-1*active_bin:] * gain_spread_factor
            elif active_bin < 0:
                continue

        # 3. Add noise (very, very tentative from SWT)
        self.__simulated_pulse += np.random.normal(loc=0., scale=6.58, size=(self.__num_gen_tbins,self.__num_pmts))
        # 6.58 is tentative value from SWT 10 bit digitizer

        # 4. floorized
        self.__simulated_pulse = np.floor(self.__simulated_pulse).astype(np.int16)

        return self.__simulated_pulse


    def add_dark(self):
        dark_rate = 2200. # Hz
        num_of_darks = np.random.poisson(dark_rate * 1000.e-9, 120)
        pmt_ids, pmt_times = [], []
        for i_pmt, num_of_dark in enumerate(num_of_darks):
            if num_of_dark == 0: continue
            for i in range(num_of_dark):
                pmt_ids.append(i_pmt)
                pmt_times.append(np.random.randint(0, 1000))

        dark_ids = np.array(pmt_ids, dtype='uint8') + 20000
        dark_times = np.array(pmt_times, dtype='uint8')
        return dark_ids, dark_times

    def add_dark_faster(self):
        num_of_darks = np.random.poisson(2.2e3 * 1000.e-9 * 120)
        dark_ids = np.random.randint(0, 120, num_of_darks).astype('uint8') + 20000
        dark_times = np.random.randint(0, 1000, num_of_darks)
        return dark_ids, dark_times



if __name__ == '__main__':
    pass
