
# coding: utf-8

# In[20]:


#script to make one big track and save file names and measure index
#concat function shamelessly borrowed from Pickett's endoder (Thanks Matt!)

from mido import Message, MidiFile, MidiTrack
import numpy as np
import pretty_midi as pm
import csv
import glob
#import midi



def concat(midis, min_len=None):
    """
    Concatenate notes in time from  a list of pretty midi objects
    :param midis: an iterable of midis
    :param min_len: the minimum length of each segment
    :return: a pretty_midi midi object
    """
    midi = pm.PrettyMIDI()
    prev_end_time = 0.0
    new_insts = {}

    for cur_midi in midis:
        cur_end_time = 0.0
        for inst in cur_midi.instruments:
            if inst.program not in new_insts.keys():
                new_insts[inst.program] = pm.Instrument(program=inst.program)
            for note in inst.notes:
                new_note = pm.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=note.start + prev_end_time,
                    end=note.end + prev_end_time)

                new_insts[inst.program].notes.append(new_note)
                cur_end_time = max(cur_end_time, new_note.end)

        if min_len is None:
            prev_end_time = cur_end_time
        else:
            prev_end_time = max(cur_end_time, prev_end_time + min_len)

    for new_inst in new_insts.values():
        midi.instruments.append(new_inst)

    return midi




full_set = pm.PrettyMIDI()
cr_midis = []
int_variable = 1.0

with open("Bass_Rock_test.csv", "wb") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for f in glob.glob('Bass_Rock/*.mid'):       
        m= pm.PrettyMIDI(f)
        #for i, track in enumerate(m.tracks):    
        cr_midis.append(m)   
        
        m_name= MidiFile(f)
        temp_list = []
        temp_list.append(int_variable)
        temp_list.append(f)


        #pattern = midi.read_midifile(f)
        #highest_tick = 0
        #for track in pattern:
        #    for tick in track:
        #        highest_tick +=1
                    
        temp_list.append(m.get_end_time())

        writer.writerow(temp_list)
        
        #divide time by 2 because each measure is 2 seconds --> this givies us approx index to measure
        int_variable+= m.get_end_time()/2
        del temp_list[:]
                        
midi_full = concat(cr_midis)
midi_full.write('bass_rock.mid')

