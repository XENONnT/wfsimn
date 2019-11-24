import numpy as np
from tqdm import tqdm

class analyzer():

    def __init__(self, wfs):
        self.wfs = wfs

    def loop(self, adc_thre=40, gate_time_ns=200):

        hit_numbers = []

        for wf in tqdm(self.wfs):

            # timing_fall_dict = {}
            timing_dict = {}
            timebins, pmtids = np.where(wf > adc_thre)

            # sum_pulse = np.sum(wf, axis=1)
            for timebin, pmtid in zip(timebins, pmtids):

                # timing_fall_dict[pmt] = time

                if pmtid in timing_dict: continue
                timing_dict[pmtid] = timebin

            initial_timebin = min(timing_dict.values(), default=0)
            hit_pmts = [pmtid for pmtid, timebin in timing_dict.items() if timebin < initial_timebin + gate_time_ns / 2]

            hit_numbers.append(len(hit_pmts))

        return hit_numbers

