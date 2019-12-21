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

        file = uproot.open(mc_file_name)  # pamn file
        events = file['events']
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

        strax_readable_list = self.generate(self.hit_ids[eventid], self.hit_times[eventid])
        return strax_readable_list

    def generate(self, pmt_ids, pmt_times):


        # pmt_ids (20000--20119)
        # pmt_times (ns)
        self.__num_gen_tbins = 40  # bins bin/2ns
        self.__num_spe_tbins = 50  # tbins bin/2ns
        gen_pls_bins = int(50 + self.__num_gen_tbins + self.__num_spe_tbins)

        nv_dtype = [
            (('Channel/PMT number', 'channel'), np.int16),
            (('Time resolution in ns', 'dt'), np.int16),
            (('Start time of the interval (ns since unix epoch)', 'time'), np.int64), # Don't try to make O(second) long intervals!
            (('Length of the interval in samples', 'length'), np.int32),
            (("Integral in ADC x samples", 'area'), np.int32),
            (('Length of pulse to which the record belongs (without zero-padding)', 'pulse_length'), np.int32),
            (('Fragment number in the pulse', 'record_i'), np.int16),
            (('Baseline in ADC counts. data = int(baseline) - data_orig', 'baseline'), np.float32),
            (('Level of data reduction applied (strax.ReductionLevel enum)', 'reduction_level'), np.uint8),
            # Note this is defined as a SIGNED integer, so we can
            # still represent negative values after subtracting baselines
            (('Waveform data in ADC counts above baseline', 'data'), np.int16, gen_pls_bins),
        ]

        strax_readable_list = []

        for pmtid in range(20000, 20120):
            #print('pmtid', pmtid)
            clusters = self.make_clusters(pmtid, pmt_times, pmt_ids)
            #print(clusters)
            for cluster in clusters:

                if len(cluster) == 0: continue
                pulse = np.zeros(gen_pls_bins)
                for time in cluster:
                    gain_spread_factor = np.random.normal(1, 0.3)  # 30%, very tentative value estimatd from SWT
                    pulse[50-15+int((time - cluster[0]) / 2) : 50-15+int((time - cluster[0]) / 2) + self.__num_spe_tbins] \
                        += self.average_pulse * gain_spread_factor

                # 3. Add noise (very, very tentative from SWT)
                pulse += np.random.normal(loc=0., scale=6.58, size=(gen_pls_bins))
                # 6.58 is tentative value from SWT 10 bit digitizer

                # 4. floorized
                pulse = np.floor(pulse).astype(np.int16)

                # 5. calc baseline
                baseline = int(pulse[0:50].mean())
                pulse = pulse - baseline
                integral = pulse.sum()

                record = np.array((
                    pmtid,
                    2,
                    int(cluster[0]), # TODO: Should refer TPC timing
                    gen_pls_bins, # Length of interval in sample
                    integral,
                    gen_pls_bins, # Length of pulse to which the record belongs
                    0,
                    baseline,
                    0, #'Level of data reduction applied (strax.ReductionLevel enum)
                    pulse
                ), dtype=nv_dtype )

                strax_readable_list.append(record)
                #print(pulse)

        return strax_readable_list

    def make_clusters(self, pmtid, pmt_times, pmt_ids):
        ## Make Clusters
        ts = [time for time, pid in zip(pmt_times, pmt_ids) if pid == pmtid and 0 < time < 1.e9]  # ns
        ts.sort()
        clusters = []
        time_list = []
        first_hit_t = -1
        in_window = False
        time_window = self.__num_gen_tbins * 2  # ns
        for t in ts:
            if first_hit_t != -1 and t - first_hit_t > time_window:
                in_window = False
                clusters.append(time_list)
            if in_window == False:  # init hit of clusters
                time_list = []
                time_list.append(t)
                first_hit_t = t
                in_window = True
            else:
                time_list.append(t)
        clusters.append(time_list)
        # clusters : hit time list in the one group list in one PMT
        return clusters



if __name__ == '__main__':

    gen = generator()
    gen.load_data('./data/average_pulse_v2.npy', './data/mc51s4_short.root')

    #gen.generate_1ev_by_mc(1327)

    #gen.generate_by_mc()

