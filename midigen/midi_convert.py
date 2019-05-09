#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import argparse
import pretty_midi

def process_midi(mod_folder, file, shift):
    filename = file.replace('.mid', '')
    midi_data = pretty_midi.PrettyMIDI(args.folder+file)
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            note.pitch += shift
    #midi_data.write(mod_folder+filename+'_'+str(shift)+'.mid')
    midi_data.write(mod_folder + filename + '.mid')

parser = argparse.ArgumentParser(description='Pass your midi file name in.')
parser.add_argument('-f', '--folder', type=str)
parser.add_argument('-s', '--shift', type=int, default=5)
args = parser.parse_args()

mod_folder = args.folder+'mod'+str(args.shift)+'/'
if(os.path.isdir(mod_folder) == False):
    os.mkdir(mod_folder)
for file in os.listdir(args.folder):
    if(file.endswith('.mid')):
        process_midi(mod_folder, file, args.shift)
