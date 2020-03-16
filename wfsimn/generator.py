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

        self.dt = 2  # Time resolution in ns
        self.strax_length = 110  # waveform length in one record
        self.peak_lbk = 20  # Average pulse bins before peak
        self.peak_lfw = 40  # Average pulse bins after peak
        self.bin_baseline = 40  # nbins of baseline including strax format
        self.nbins_templete_wf = self.peak_lbk + self.peak_lfw  # number of avarage pulse bins
        self.time_window = 100  # ns; event time window in strax format

        self.nv_raw_record_dtype = [
            (('Channel/PMT number', 'channel'), np.int16),  # As tentative, 20000 -- 20199, nV
            (('Time resolution in ns', 'dt'), np.int16),  # 2 (ns) for nV
            (('Start time of the interval (ns since unix epoch)', 'time'), np.int64),
            (('Length of the interval in samples', 'length'), np.int32),  # 110
            (("Integral in ADC x samples", 'area'), np.int32),  # Not implemented yet
            (('Length of pulse to which the record belongs (without zero-padding)', 'pulse_length'), np.int32),  # 330
            (('Fragment number in the pulse', 'record_i'), np.int16),  # 0, 1, 2, ...
            (('Baseline in ADC counts. data = int(baseline) - data_orig', 'baseline'), np.float32), # Not implemented yet
            (('Level of data reduction applied (strax.ReductionLevel enum)', 'reduction_level'), np.uint8),  # 0
            (('Waveform data in ADC counts above baseline', 'data'), np.int16, self.strax_length),  # waveforms
        ]

        self.bins_baseline = 40  # nbins to add in strax format
        self.pulse_height = 57  # mean of 1pe pulse height in ADC
        self.pulse_spread = 26  # std. div of 1pe pulse height in ADC
        self.pulse_baseline_ADC = 15925  # Actural baseline in ADC
        self.pulse_baseline_spread = 3.5  # baseline spread in ADC

        self.event_time_interval = 1.e-6  # Each event will occur in this interval (second)


    def load_data(self, average_pulse_file_name, mc_file_name):

        self.average_pulse = np.load(average_pulse_file_name)

        file = uproot.open(mc_file_name)  # pamn file
        events = file['events']
        self.hit_ids = events.array('pmthitid')  # nveto id 20000--20199
        self.hit_times = events.array('pmthittime')  # unit: second
        self.nentries = len(self.hit_ids)

        self.logger.info('#of events in TTree:'+str(self.nentries))


    def generate_by_mc(self):

        events_records = []
        for i_ev in tqdm(range(self.nentries)):
            event_records = self.generate_1ev_by_mc(i_ev, i_ev*self.event_time_interval)
            events_records.append(event_records)
        return events_records


    def generate_1ev_by_mc(self, eventid=0, time_offset_sec=0.):

        event_records = self.generate(self.hit_ids[eventid], self.hit_times[eventid], time_offset_sec=time_offset_sec)
        return event_records


    def generate(self, pmt_ids, pmt_times, time_offset_sec):

        event_records = []
        for pmtid in range(20000, 20120):  # each PMT
            clusters = self.make_clusters(pmtid, pmt_times, pmt_ids)  # each cluster

            for cluster in clusters:
                if len(cluster)==0: continue

                for i in range(len(cluster)):
                    first_time = cluster[0]
                    cluster = [int((time - first_time) / self.dt) for time in cluster]
                    total_pulse_length = np.ceil((self.bins_baseline + cluster[-1] + self.nbins_templete_wf)/self.strax_length)*self.strax_length
                    wf = np.zeros(int(total_pulse_length))

                    for time in cluster:
                        fac = np.random.normal(self.pulse_height, self.pulse_spread)
                        wf[self.bins_baseline + time:self.bins_baseline + time + self.nbins_templete_wf] += self.average_pulse * fac / self.pulse_height
                    wf = np.random.normal(self.pulse_baseline_ADC, self.pulse_baseline_spread, len(wf)) - wf  # add baseline noise

                    records = []
                    for i in range(np.int(np.ceil(len(wf) / self.strax_length))):
                        data = wf[i * self.strax_length:(i + 1) * self.strax_length]

                        record = np.array((
                            pmtid,  # PMT ID 20000 -- 20199
                            self.dt,  # ns time resolution
                            int(cluster[0]) + time_offset_sec*1.e9,  # start time in ns
                            self.strax_length,  # Length of interval in sample
                            0,  # area (not implemented like a raw record)
                            np.ceil(len(wf)), # Length of pulse to which the record belongs
                            i,  # i_record
                            0,  # baseline (not implemented like a raw record)
                            0,  # 'Level of data reduction applied (strax.ReductionLevel enum)
                            data
                        ), dtype=self.nv_raw_record_dtype)
                        records.append(record)
                    event_records.append(records)

        return event_records




    def make_clusters(self, pmtid, pmt_times, pmt_ids):

        # still represent negative values after subtracting baselines
        ## Make Clusters
        # Input: pmt_times = [500.e-9, 700.e-9, 900.e-9, 1200.e-9, 2000.e-9] ## sec
        # time window 300 ns
        # Output: [[0.5, 0.7, 0.9, 1.2], [2.0]]

        ts = [time * 1.e9 for time, pid in zip(pmt_times, pmt_ids) if pid == pmtid]  # ns

        ts.sort()
        clusters = []
        time_list = []
        first_hit_t = -1
        in_window = False
        for t in ts:
            if first_hit_t != -1 and t - first_hit_t > self.time_window:
                in_window = False
                clusters.append(time_list)
            if in_window == False:  # first hit of clusters
                time_list = []
                time_list.append(t)
                first_hit_t = t
                in_window = True
            else:
                time_list.append(t)
        clusters.append(time_list)

        return clusters



if __name__ == '__main__':

    gen = generator()
    gen.load_data('./data/ave_TEST000012_02242020121353_ch0.npy', './data/mc71_test1.root')
    strax_list = gen.generate_1ev_by_mc(0)

