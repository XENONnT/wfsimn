#!/usr/bin/env python3
# coding: utf-8

import argparse
import wfsimn


parser = argparse.ArgumentParser(description='Waveform generator')
parser.add_argument('-d', '--dirname', default='/dali/lgrandi/mzks/mc/', help='MC directory')
parser.add_argument('-n', '--mcname', default='mc51', help='MC directory name')
parser.add_argument('-i', '--id', default=1, type=int, help='Batch ID')

args = parser.parse_args()

man = wfsimn.manager()
man.mc_file_name = args.dirname + args.mcname + '/workdir/output' + str(args.id).zfill(4) + '_Sort.root'
print(man.mc_file_name)

gen = man.generator()
man.wfs = gen.generate_by_mc()
pkl_filename = args.dirname + args.mcname + '/workdir/output' + str(args.id).zfill(4) + '_Sort.pkl'
man.load_pickle(pkl_filename)

