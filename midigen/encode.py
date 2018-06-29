import copy
import sys
import numpy as np
from abc import ABC, abstractmethod
import logging
import pretty_midi as pm
from scipy.ndimage import convolve1d
from midigen.package import logger


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


class PolyEncoder(Encoder):
    def __init__(self, allowed_pitches, sample_frequency, press_threshold, hold_threshold, max_len):
        self.allowed_pitches = allowed_pitches
        self.num_pitches = len(allowed_pitches)
        self.sample_frequency = sample_frequency
        self.press_threshold = press_threshold
        self.hold_threshold = hold_threshold
        self.max_len = max_len

        self.velocity_scale = 1.0/127.0
        self.velocity_offset = 1
        self.hold_offset = 2
        self.chans_per_pitch = 3
        self.encoding_channels = self.chans_per_pitch*self.num_pitches
        self.pitch_to_index = {p: n for n, p in enumerate(allowed_pitches)}
        self.index_to_pitch = {n: p for p, n in self.pitch_to_index.items()}

    def __dict__(self):
        return dict({
            u'allowed_pitches': self.allowed_pitches,
            u'sample_frequency': self.sample_frequency,
            u'press_threshold': self.press_threshold,
            u'hold_threshold': self.hold_threshold,
            u'max_len': self.max_len})

    def encode(self, midi, instrument_index):
        inst = midi.instruments[instrument_index]
        assert not inst.is_drum
        end_time = min(inst.notes[-1].end, self.max_len)
        total_samples = int(end_time*self.sample_frequency + 1)
        encoding = np.zeros((total_samples, self.encoding_channels))

        for note in inst.notes:
            if note.pitch not in self.allowed_pitches:
                _LOGGER.warning(f'Ignoring disallowed pitch: {note.pitch}')
                continue

            start_sample = int(np.ceil(note.start*self.sample_frequency))
            end_sample = int(np.floor(note.end*self.sample_frequency))
            pitch_index = self.pitch_to_index[note.pitch]
            encoding[start_sample, pitch_index*self.chans_per_pitch] = 1.0
            encoding[start_sample, pitch_index*self.chans_per_pitch + self.velocity_offset] = \
                note.velocity*self.velocity_scale

            # set hold channel
            if end_sample > start_sample:
                encoding[start_sample + 1:end_sample + 1, pitch_index*self.chans_per_pitch + self.hold_offset] = 1.0

        return encoding

    def decode(self, encoding, program):

        midi = pm.PrettyMIDI()
        inst = pm.Instrument(program=program)

        key_state = np.zeros(self.num_pitches, dtype=np.uint8)
        start_sample = np.zeros(self.num_pitches, dtype=np.uint32)
        velocity_state = np.zeros(self.num_pitches, dtype=np.uint8)
        hold_count = np.zeros(self.num_pitches, dtype=np.uint32)

        def press_key(pitch_index, velocity, sample_index):
            key_state[pitch_index] = 1
            velocity_state[pitch_index] = velocity
            hold_count[pitch_n] = 0
            start_sample[pitch_n] = sample_index

        def release_key(pitch_index):
            start_time = start_sample[pitch_index]/self.sample_frequency
            end_time = start_time + (1+hold_count[pitch_n])/self.sample_frequency
            inst.notes.append(
                pm.Note(velocity=velocity_state[pitch_index],
                        pitch=self.index_to_pitch[pitch_index],
                        start=start_time,
                        end=end_time))
            key_state[pitch_index] = 0
            velocity_state[pitch_index] = 0
            hold_count[pitch_n] = 0
            start_sample[pitch_n] = 0

        for sample_n in range(encoding.shape[0]):
            for pitch_n in range(self.num_pitches):

                # key is pressed
                if encoding[sample_n, self.chans_per_pitch*pitch_n] > self.press_threshold:
                    # key was previously being held, release key
                    if key_state[pitch_n] == 1:
                        release_key(pitch_n)

                    # start new press
                    vel_n = self.chans_per_pitch * pitch_n + self.velocity_offset
                    vel = encoding[sample_n, vel_n]/self.velocity_scale
                    press_key(pitch_n, vel, sample_n)

                # key is held
                elif encoding[sample_n, self.chans_per_pitch*pitch_n+self.hold_offset] > self.hold_threshold and \
                        key_state[pitch_n] == 1:
                    hold_count[pitch_n] += 1

                # key is released
                elif key_state[pitch_n] == 1:
                    release_key(pitch_n)

                # no activity on key
                else:
                    pass

        # release all keys held at the end
        for pitch_n in range(self.num_pitches):
            if key_state[pitch_n] == 1:
                release_key(pitch_n)

        midi.instruments.append(inst)
        return midi


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

        us = 10  # us is the up-sampling factor
        steps_per_s = us*self.time_resolution
        map_steps = int(self.total_time*steps_per_s)
        note_map = np.zeros((self.num_symbols, map_steps))

        # go through all notes, filters out notes that aren't within the allowed pitches
        for note in inst.notes:
            if note.pitch not in self.allowed_pitches:
                logger.warn('ignoring unsupported pitch = ' + str(note.pitch))
                continue
            if note.start > self.total_time:
                logger.warn('ignoring late note at = ' + str(note.start))
                continue
            symbol_n = self.encoder_lut[note.pitch]
            start_n = int(note.start*steps_per_s)
            end_n = min(int(note.end*steps_per_s), map_steps - 1)

            note_map[symbol_n, start_n:end_n] = 1

        # Encodes notes according to specified time resolution,
        # Note choice when multiple notes - keep the longest held note
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
        # downsample to resolution
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
