
# coding: utf-8

# In[6]:


#script to make test encoder
#concat function shamelessly borrowed from Pickett's endoder (Thanks Matt!)
#Note concat function has issues so we are outputting individual midi
#files as well into another folder to do a 1:1 comparison

from mido import Message, MidiFile, MidiTrack
import numpy as np

import pretty_midi as pm
import csv
import glob
from scipy.ndimage import convolve1d
from abc import ABC, abstractmethod
#import midi
import logging
from os.path import basename

_LOGGER = logging.getLogger('midigen-encoder')


def encoder_from_dict(the_dict):
    type_name = the_dict['encoder_type']
    pruned = copy.deepcopy(the_dict)
    del pruned['encoder_type']
    return getattr(sys.modules[__name__], type_name)(**pruned)


class Encoder(ABC):
    encoding_channels = NotImplemented  # type: int

    @abstractmethod
    def encode(self, midi, instrument_index):
        """
        Encode a pretty midi object into an encoding
        :param midi a pretty_midi midi object
        :param instrument_index index of the instrument to encode
        :return the numpy encoding array
        """
        pass

    @abstractmethod
    def decode(self, encoding, program):
        """
        Decode an encoding into a pretty midi object
        :param encoding: the encoded numpy array
        :param program: pretty_midi instrument program
        :return: a pretty_midi midi object
        """
        pass



class MelodyEncoder(Encoder):
    def __init__(self, allowed_pitches, time_resolution, num_bars, bar_time):

        # set properties
        self.allowed_pitches = allowed_pitches
        self.time_resolution = time_resolution
        self.num_bars = num_bars
        self.bar_time = bar_time

        # define constants
        self.hold_note = 0
        self.no_note = 1
        self.default_velocity = 100

        # evaluate dependent properties
        self.total_time = num_bars * bar_time
        self.encoder_lut = {k: v + 2 for v, k in enumerate(allowed_pitches)}
        self.decoder_lut = {v: k for k, v in self.encoder_lut.items()}
        self.num_pitches = len(self.allowed_pitches)
        self.num_symbols = self.num_pitches + 2
        self.num_time_steps = self.time_resolution * self.total_time
        self.sixteeth_time = self.bar_time / 16.0
        self.encoding_channels = self.num_symbols

    def __dict__(self):
        return dict({
            u'allowed_pitches': self.allowed_pitches,
            u'time_resolution': self.time_resolution,
            u'num_bars': self.num_bars,
            u'bar_time': self.bar_time})

    def encode(self, midi, instrument_index=0):
        """
        Encode a pretty midi object into a symbol sequence
        :param midi a pretty_midi midi object
        :param instrument_index index of the instrument to encode
        :return a numpy encoding array containing symbols
        """
        inst = midi.instruments[instrument_index]
        assert not inst.is_drum

        us = 10
        steps_per_s = us*self.time_resolution
        map_steps = int(self.total_time*steps_per_s)
        note_map = np.zeros((self.num_symbols, map_steps))

        for note in inst.notes:
            if note.pitch not in self.allowed_pitches:
                _LOGGER.warn('ignoring unsupported pitch = ' + str(note.pitch))
                continue
            if note.start > self.total_time:
                _LOGGER.warn('ignoring late note at = ' + str(note.start))
                continue
            symbol_n = self.encoder_lut[note.pitch]
            start_n = int(note.start*steps_per_s)
            end_n = min(int(note.end*steps_per_s), map_steps - 1)

            note_map[symbol_n, start_n:end_n] = 1

        ave_width = us // 2 + 1
        ave = np.ones(ave_width)/float(ave_width)
        note_map = convolve1d(note_map, ave, axis=1)
        accum = np.zeros(self.num_symbols)
        symbols = np.empty(map_steps)
        for step_n in range(map_steps):
            if np.sum(note_map[:, step_n]) == 0:
                accum *= 0
                symbols[step_n] = self.no_note
            else:
                accum *= note_map[:, step_n] > 0
                accum += note_map[:, step_n]
                symbols[step_n] = np.argmax(accum)
        encoding = np.ones(self.num_time_steps, dtype=np.uint8)
        encoding[:] = symbols[::us]
        held_key = None
        for step_n, cur_key in enumerate(encoding):
            if cur_key > 1 and cur_key == held_key:
                encoding[step_n] = self.hold_note
            held_key = cur_key

        ohcs = np.zeros((self.num_time_steps, self.num_symbols), dtype=np.float32)
        for step_n in range(self.num_time_steps):
            ohcs[step_n, encoding[step_n]] = 1.0

        return ohcs

    def decode(self, probability,
               program=pm.instrument_name_to_program('Acoustic Grand Piano')):
        """
        Decode a symbol probability sequence into a pretty midi object
        :param probability: the probability sequence numpy array
        :param program: pretty_midi instrument program
        :return: a pretty_midi midi object
        """

        symbols = np.argmax(probability, axis=1)
        midi = pm.PrettyMIDI()
        inst = pm.Instrument(program=program)

        start_time = None
        cur_key = None
        key_on = False
        for elem_n, elem in enumerate(symbols):
            # start note
            if not key_on and elem > self.no_note:
                key_on = True
                cur_key = elem
                start_time = float(elem_n)/self.time_resolution

            # hold no note
            elif not key_on and elem == self.no_note:
                pass

            # hold no note
            elif not key_on and elem == self.hold_note:
                pass

            # hold note
            elif key_on and elem == self.hold_note:
                pass

            # stop note
            elif key_on and elem == self.no_note:
                stop_time = float(elem_n)/self.time_resolution
                inst.notes.append(
                    pm.Note(velocity=self.default_velocity,
                            pitch=self.decoder_lut[cur_key],
                            start=start_time, end=stop_time))

                key_on = False
                cur_key = None
                start_time = None
            # stop note and start new note
            elif key_on and elem > self.no_note:
                stop_time = float(elem_n)/self.time_resolution
                inst.notes.append(
                    pm.Note(velocity=self.default_velocity,
                            pitch=self.decoder_lut[cur_key],
                            start=start_time, end=stop_time))

                key_on = True
                cur_key = elem
                start_time = stop_time
        if key_on:
            stop_time = float(len(symbols))/self.time_resolution
            inst.notes.append(
                pm.Note(velocity=self.default_velocity,
                        pitch=self.decoder_lut[cur_key],
                        start=start_time, end=stop_time))
        midi.instruments.append(inst)
        return midi



#def build_dataset(self, data_dir):
        #_LOGGER.debug(f'building dataset from {data_dir}')

        #np.random.seed(self.seed)

#        calls = []
#        responses = []

#        for dirName, subdirList, fileList in walk(data_dir):
#            cur_cr = {}
            #for fname in fileList:
            #    if fname.endswith('.mid') and not fname[0] == '.':
            #        try:
            #            num = int(fname.replace('.mid', '').replace(' ', '_').split('_')[-1])
            #        except ValueError:
            #            _LOGGER.warning(f'file name does not end with integer {fname}')
            #            continue

            #        full_path = join(dirName, fname)
            #        try:
 #                       midi = pm.PrettyMIDI(full_path)
  #                      assert len(midi.instruments[0].notes) > 3
   #                     cur_cr[num] = self.encoder.encode(midi, instrument_index=0)
            #        except (AssertionError, IOError, KeyError):
            #            _LOGGER.warning(f'Could not add midi file {join(dirName, fname)}.')

   #         for k in cur_cr.keys():
    #            if k % 2 == 1:
            #        try:
     #                   cur_call = cur_cr[k]
      #                  cur_response = cur_cr[k + 1]
       #                 responses.append(cur_response)
        #                calls.append(cur_call)
          #          except KeyError:
          #              _LOGGER.warning(f'Could not add index {k} from {dirName} because '
          #                              f'it does not have a valid call/response.')

#        _LOGGER.debug(f'building dataset from {data_dir}')

   #     call_len = calls[0].shape[0]
    #    for call, response in zip(calls, responses):
     #       assert call.shape[0] == call_len
      #      assert response.shape[0] == call_len

  #      num_examples = len(calls)
       # num_training_examples = int(num_examples*(1.0-self.validation_ratio))
       # indices = np.arange(num_examples, dtype=np.int32)
       # np.random.shuffle(indices)

   #     dataset = {
    #        'calls': np.stack(calls),
     #       'responses': np.stack(responses),
     #       'training_indices': indices[:num_training_examples],
      #      'validation_indices': indices[num_training_examples:]
       # }

    #    return dataset



    
    
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
cr_names = []
int_variable = 1.0

with open("guitar_Rock_Encoded.csv", "w") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for f in glob.glob('CTX_EGTR_clean_nadine/*.mid'):       
        m= pm.PrettyMIDI(f)
        #for i, track in enumerate(m.tracks):  
        
        #Cool = MelodyEncoder(allowed_pitches=[15, 17, 19, 20, 22, 24, 26, 27, 29, 31, 32, 34, 36, 38, 39, 41, 43, 44, 46, 48, 51, 53, 55, 56, 58, 63, 100], time_resolution=16, num_bars=4, bar_time=2)
        Cool = MelodyEncoder(allowed_pitches= [42, 43, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56, 57, 58, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 74, 75, 76, 77, 78, 79, 80, 81, 82, 84, 85, 86, 87], time_resolution=8, num_bars=4, bar_time=2)
        m_encode = Cool.encode(midi=m, instrument_index=0)
        m_decode = Cool.decode(m_encode, pm.instrument_name_to_program('Acoustic Grand Piano'))
        cr_midis.append(m_decode)   
        cr_names.append(basename(f))
        m_name= MidiFile(f)
        
       # m_decode.write('Bass_Rock_Encoded/'+str(m_name))
        
        temp_list = []
        temp_list.append(str(int_variable))
        temp_list.append(f)

                    
        temp_list.append(m.get_end_time())

        writer.writerow(temp_list)
        int_variable+= m.get_end_time()/2
        del temp_list[:]
        
i = 0
for cur_midi in cr_midis:
    cur_midi.write('Guitar_Rock_Encoded_Fix/'+cr_names[i])
    i+=1
                        
midi_full = concat(cr_midis)
midi_full.write('Guitar_rock_encoded_fix.mid')

