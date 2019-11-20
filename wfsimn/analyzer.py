import numpy as np


class analyzer():

    def __init__(self, wfs):
        self.wfs = wfs

    def loop(self, adc_thre = 100):

        for wf in wfs:

            # timing_fall_dict = {}
            timing_dict = {}
            times, pmts = np.where(wf > adc_thre)
            for time, pmt in zip(times, pmts):

                # timing_fall_dict[pmt] = time

                if pmt in timing_dict: continue
                timing_dict[pmt] = time


            for pmt, time in timing_dict.items():
                pass


        return 0

