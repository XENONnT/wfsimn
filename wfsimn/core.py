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
        self.mc_file_name = self.__data_path + 'mc71_test1.root'

    def generate_by_mc(self):
        self.gen = wfsimn.generator()
        self.gen.load_data(self.average_pulse_file_name, self.mc_file_name)

        self.events_records = []
        # print('Generating pulse...')
        for i_ev in tqdm(range(self.gen.nentries)):
            event_records = self.gen.generate_by_mc(i_ev)
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



if __name__ == '__main__':

    logging.basicConfig(level='DEBUG')

    mc_name = 'mc71_test1'
    man = manager()

    gen = man.generator()
    man.events_records = gen.generate_by_mc()
    man.save_pickle('mc71_test1.pkl')


