import json
import numpy as np
import pretty_midi as pm
from scipy.ndimage import convolve1d
from midigen.package import logger


class MelodyEncoder(object):
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
        self.decoder_lut = {v: k for k, v in self.encoder_lut.iteritems()}
        self.num_pitches = len(self.allowed_pitches)
        self.num_symbols = self.num_pitches + 2
        self.num_time_steps = self.time_resolution * self.total_time
        self.sixteeth_time = self.bar_time / 16.0

    def __dict__(self):
        return dict({
            u'allowed_pitches': self.allowed_pitches,
            u'time_resolution': self.time_resolution,
            u'num_bars': self.num_bars,
            u'bar_time': self.bar_time})

    def to_json(self):
        return json.dumps(self.__dict__())

    @staticmethod
    def from_json(s):
        return MelodyEncoder(**dict(json.loads(s)))

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
                logger.warn('ignoring unsupported pitch = ' + str(note.pitch))
                continue
            if note.start > self.total_time:
                logger.warn('ignoring late note at = ' + str(note.start))
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

        return encoding

    def encode_ohc(self, midi, instrument_index=0):
        """
        Encode a pretty midi object into a one hot code sequence
        :param midi a pretty_midi midi object
        :param instrument_index index of the instrument to encode
        :return a numpy encoding array containing one hot codes
        """
        symbols = self.encode(midi, instrument_index)
        ohcs = np.zeros((self.num_time_steps, self.num_symbols), dtype=np.float32)

        # TODO: naive approach. make this more efficient?
        for step_n in range(self.num_time_steps):
            ohcs[step_n, symbols[step_n]] = 1.0

        return ohcs

    def decode(self, encoding,
               program=pm.instrument_name_to_program('Acoustic Grand Piano')):
        """
        Decode a symbol sequence into a pretty midi object

        :param encoding: the encoded numpy array
        :param program: pretty_midi instrument program
        :return: a pretty_midi midi object
        """

        midi = pm.PrettyMIDI()
        inst = pm.Instrument(program=program)

        start_time = None
        cur_key = None
        key_on = False
        for elem_n, elem in enumerate(encoding):
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
            stop_time = float(len(encoding))/self.time_resolution
            inst.notes.append(
                pm.Note(velocity=self.default_velocity,
                        pitch=self.decoder_lut[cur_key],
                        start=start_time, end=stop_time))
        midi.instruments.append(inst)
        return midi


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
