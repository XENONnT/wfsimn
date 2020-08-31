import os, sys
import pkg_resources
import logging
import numpy as np
import pickle
from tqdm import tqdm
import wfsimn

import logging
import uproot
import nestpy

import numpy as np
import pandas as pd

import strax
from straxen.common import get_resource
from straxen import get_to_pe
import wfsim
from immutabledict import immutabledict


export, __all__ = strax.exporter()
__all__ += ['raw_records_nv_dtype']

raw_records_nv_dtype = strax.raw_record_dtype(110)

log = logging.getLogger('SimulationNvCore')

@strax.takes_config(
    strax.Option('seed',default=False, track=True,
                 help="Option for setting the seed of the random number"),
)
class WfsimN(strax.Plugin):

    provides = (
        'raw_records_nv'
    )
    #data_kind = immutabledict(zip(provides, provides))
    depends_on = tuple()
    rechunk_on_save = False
    parallel = False
    last_chunk_time = -999999999999999
    input_timeout = 3600 # as an hour


    def setup(self):

        self.man = wfsimn.manager()
        self.man.generate_by_mc()
        self.wfs = self.man.flatten_events_records(self.man.events_records)
        #self.wfs = strax.sort_by_time(self.wfs)
        self.sim_iter = iter(self.wfs)


    def infer_dtype(self):

        dtype = strax.raw_record_dtype()
        return dtype


    def is_ready(self, chunk_i):
        """Overwritten to mimic online input plugin.
        Returns False to check source finished;
        Returns True to get next chunk.
        """
        if 'ready' not in self.__dict__: self.ready = False
        self.ready ^= True # Flip
        return self.ready


    #def source_finished(self):
        #"""Return whether all instructions has been used."""
        #return self.sim.source_finished()


    def compute(self, chunk_i):
        try:
            result = next(self.sim_iter)
        except StopIteration:
            raise RuntimeError("Bug in chunk count computation")
        #r = strax.raw_to_records(np.array(self.wfs))
        #del self.wfs
        #return r

        return {'raw_records_nv': result}



