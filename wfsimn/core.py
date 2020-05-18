import os, sys
import pkg_resources
import logging
import numpy as np
import pickle
from tqdm import tqdm
import wfsimn

class manager:
    """
    """

    def __init__(self):

        self.logger = logging.getLogger(__name__)
        self.logger.info('Manager Initialize Ver. 2.0.0 - trial 0')

        # Parameters
        self.__data_path = pkg_resources.resource_filename('wfsimn', 'data/')

        self.average_pulse_file_name = self.__data_path + 'ave_TEST000012_02242020121353_ch0.npy'
        self.mc_file_name = self.__data_path + 'mc_neutron_10000evt_Sort.root'
        self.qe_table = self.__data_path + 'R5912QE.dat'

    def generate_by_mc(self):
        self.gen = wfsimn.generator()
        self.gen.load_data(self.average_pulse_file_name, self.mc_file_name)

        self.events_records = []
        # print('Generating pulse...')
        self.events_records = self.gen.generate_by_mc()
        return

    def generate_dark(self, dark_rate_hz=2000, generate_sec=1.e-3):

        self.gen = wfsimn.generator()
        self.gen.load_data(self.average_pulse_file_name, self.mc_file_name, self.qe_table)
        ## mc read is dummy

        total_dark = int(120 * dark_rate_hz * generate_sec)
        ids = np.random.randint(20000, 20120, total_dark)
        times = np.sort(np.random.rand(total_dark) * generate_sec)

        self.events_records = []
        event_records = self.gen.generate(ids, times, 0)
        self.events_records.append(event_records)
        return


    def save_pickle(self, filename='wfs.dat'):
        self.logger.info('Save '+filename)
        with open(filename, 'wb') as file:
            pickle.dump(self.events_records, file)
        return

    def load_pickle(self, filename='wfs.dat'):
        self.logger.info('Load '+filename)
        with open(filename, 'rb') as file:
            self.events_records = pickle.load(file)
        return

    def generator(self):
        gen = wfsimn.generator()
        gen.load_data(self.average_pulse_file_name, self.mc_file_name)
        return gen

    def event_visualizer(self, eventid=0):
        vis = wfsimn.visualizer(self.events_records[eventid])
        return vis


    def flatten_events_records(self, events_records=None):
        if events_records is None:
            events_records = self.events_records

        i = 0
        while i < len(events_records):
            while type(events_records[i]) != np.ndarray:
                if not events_records[i]:
                    events_records.pop(i)
                    i -= 1
                    break
                else:
                    events_records[i:i + 1] = events_records[i]
            i += 1
        return events_records


if __name__ == '__main__':

    logging.basicConfig(level='DEBUG')

    #mc_name = 'mc71_test1'
    man = manager()
    man.generate_by_mc()

