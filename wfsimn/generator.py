import pkg_resources
import logging
import numpy as np
from scipy import fftpack
import pandas as pd
from tqdm import tqdm
import uproot
import matplotlib.pyplot as plt
import strax
import wfsimn


class generator():

    def __init__(self, seed=0):

        self.logger = logging.getLogger(__name__)
        self.logger.info('Generator Initialize')
        np.random.seed(seed)
        self.__data_path = pkg_resources.resource_filename('wfsimn', 'data/')

        # Strax record parameters
        self.dt = 2  # Time resolution in ns
        self.record_length = 110  # waveform length in one record
        self.peak_lbk = 20  # Average pulse bins before peak
        self.peak_lfw = 40  # Average pulse bins after peak
        self.bin_baseline = 40  # nbins of baseline including strax format
        self.nbins_templete_wf = self.peak_lbk + self.peak_lfw  # number of avarage pulse bins
        self.time_window = 100  # ns; event time window in strax format

        self.nv_raw_record_dtype = strax.raw_record_dtype(self.record_length)

        # Pulse parameters
        self.pulse_height = 57  # mean of 1pe pulse height in ADC
        self.pulse_spread = 26  # std. div of 1pe pulse height in ADC
        self.pulse_baseline_ADC = 15925  # Actural baseline in ADC
        self.pulse_baseline_spread = 3.5  # baseline spread in ADC

        self.event_time_interval = 1.e-6  # Each event will occur in this interval (second)

        self.preprocessor = wfsimn.preprocessor()


    def load_data(self, average_pulse_file_name, mc_file_name, qe_table):

        self.average_pulse = np.load(average_pulse_file_name)

        self.preprocessor.set_input(mc_file_name) # nSort file(s)
        self.preprocessor.set_qe_table(qe_table)
        self.hit_ids, self.hit_times = self.preprocessor.load_nsorted()
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


    def generate(self, pmt_ids, pmt_times, time_offset_sec=0.):

        event_records = []
        for pmtid in range(20000, 20120):  # each PMT
            clusters = self.make_clusters(pmtid, pmt_times, pmt_ids)  # each cluster

            for cluster in clusters:
                if len(cluster)==0: continue

                for i in range(len(cluster)):
                    first_time = cluster[0]  # ns
                    cluster = [int((time - first_time) / self.dt) for time in cluster]  # bins
                    actual_pulse_length = self.bin_baseline + cluster[-1] + self.nbins_templete_wf
                    total_pulse_length = np.ceil((actual_pulse_length)/self.record_length)*self.record_length
                    wf = np.zeros(int(total_pulse_length))

                    for time in cluster:
                        fac = np.random.normal(self.pulse_height, self.pulse_spread)
                        wf[self.bin_baseline + time:self.bin_baseline + time + self.nbins_templete_wf] += self.average_pulse * fac / self.pulse_height
                    wf = np.random.normal(self.pulse_baseline_ADC, self.pulse_baseline_spread, len(wf)) - wf  # add baseline noise

                    records = []
                    for i in range(np.int(np.ceil(len(wf) / self.record_length))):
                        data = wf[i * self.record_length:(i + 1) * self.record_length]

                        record = np.array((
                            int(first_time) + time_offset_sec*1.e9,  # start time in ns
                            self.record_length,  # Length of interval in sample
                            self.dt,  # ns time resolution
                            pmtid - 20000 + 2000,  # PMT ID 2000 -- 2199
                            np.ceil(len(wf)), # Length of pulse to which the record belongs
                            i,  # i_record
                            np.mean(data[0:self.bin_baseline]),  # baseline
                            data
                        ), dtype=self.nv_raw_record_dtype)
                        records.append(record)
                    event_records.append(records)

        return event_records




    def make_clusters(self, pmtid, pmt_times, pmt_ids):

        # still represent negative values after subtracting baselines
        ## Make Clusters
        # Input: pmt_times = [500.e-9, 700.e-9, 900.e-9, 1200.e-9, 2000.e-9] ## sec
        # time window 200 ns
        # Output: [[500, 700, 900], [1200], [2000]]

        ts = [time * 1.e9 for time, pid in zip(pmt_times, pmt_ids) if pid == pmtid]  # ns

        ts.sort()
        clusters = []
        time_list = []
        last_hit_t = -1
        in_window = False
        for t in ts:

            if last_hit_t != -1 and t - last_hit_t > self.time_window:
                in_window = False
                clusters.append(time_list)
            if in_window == False:  # first hit of clusters
                time_list = []
                time_list.append(t)
                last_hit_t = t
                in_window = True
            else:
                time_list.append(t)
                last_hit_t = t
        clusters.append(time_list)

        return clusters



if __name__ == '__main__':

    gen = generator()
    gen.load_data('./data/ave_TEST000012_02242020121353_ch0.npy', './data/mc_neutron_10000evt_Sort.root', './data/average_nv_qe1.txt')
    strax_list = gen.generate_1ev_by_mc(1)

