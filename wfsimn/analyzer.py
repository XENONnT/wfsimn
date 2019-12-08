import logging
import numpy as np
from tqdm import tqdm
import wfsimn

class analyzer():

    def __init__(self, wfs):
        self.logger = logging.getLogger(__name__)
        self.wfs = wfs

    def loop(self, adc_thre=40, gate_time_ns=200):

        hit_numbers = []

        for wf in tqdm(self.wfs, leave=False):

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

    def loop_event_delta_time(self, threshold=0.1):

        delta_times = []

        for wf in tqdm(self.wfs, leave=False):

            pulse = np.sum(wf, axis=1)
            peak_ADC = pulse.max()
            peak_timebin = pulse.argmax()
            under_threshold_indexs = np.where(pulse < peak_ADC * threshold)[0]
            try:
                #delta_timebin_lbk = peak_timebin - under_threshold_indexs[under_threshold_indexs < peak_timebin].max()
                delta_timebin_lfw = under_threshold_indexs[under_threshold_indexs > peak_timebin].min() - peak_timebin
            except ValueError:
                continue

            delta_times.append(delta_timebin_lfw * 2)

        return delta_times


if __name__ == '__main__':

    logging.basicConfig(level='DEBUG')

    man = wfsimn.manager()
    mc_name = 'mc51'
    batchid = 1
    man.mc_file_name = '/Users/mzks/xenon/mc/nv/' + mc_name + '/output' + str(batchid).zfill(4) + '_Sort.root'
    man.load_pickle('/Users/mzks/xenon/wfsimn/notebooks/wf_files/' + mc_name + '_' + str(batchid).zfill(4) + '.pkl')

    ana = man.analyzer()
    delta_times = ana.loop_event_delta_time()

