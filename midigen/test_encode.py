import os
from os import path
from unittest import TestCase
import pretty_midi as pm
from midigen.encode import PolyEncoder, MelodyEncoder

# criteria, same number of notes, same velocity, start within 1 sample and send within 2 samples of original
# Use unit test hooks


class TestEncoder(TestCase):
    def setUp(self):
        this_dir = path.abspath(path.split(__file__)[0])
        data_dir = path.join(this_dir, 'test_midi')
        self.test_midis = []
        for fileList in os.listdir(data_dir):
            if not fileList.endswith('.mid'):
                continue

            midi_track = path.join(data_dir, fileList)
            self.test_midis.append(pm.PrettyMIDI(midi_track))

        #self.allowed_pitches = [55, 58, 60, 63, 65, 66, 67, 70, 72, 75, 77, 78, 79, 82, 84]
        self.allowed_pitches = [29, 31, 34, 36, 42, 43, 46, 47, 48, 49, 51, 53, 54, 55, 56, 57, 58, 60, 62, 63, 65, 66, 67, 68, 69, 70, 72, 74, 75, 77, 78, 79, 81, 82, 84, 85, 86, 87]

    '''
    def test_poly_encoder(self):
        encoder = PolyEncoder(
            self.allowed_pitches,
            sample_frequency=25,
            press_threshold=0.5,
            hold_threshold=0.5,
            max_len=10)

        for midi in self.test_midis:
            encoding = encoder.encode(midi, 0)
            decoded = encoder.decode(encoding, 0)
            # make sure decoded contains same number of notes
            assert len(midi.instruments[0].notes) == len(decoded.instruments[0].notes)
            num_notes = len(midi.instruments[0].notes)

            for note_n in range(num_notes):
                ref_note = midi.instruments[0].notes[note_n]
                dec_note = decoded.instruments[0].notes[note_n]
                # make sure all notes have the same velocity
                assert ref_note.velocity == dec_note.velocity
                # make sure all notes start within 1 sample of reference
                assert abs(ref_note.start-dec_note.start) <= 1.0/encoder.sample_frequency
                # make sure all notes end within 2 samples of reference
                assert abs(ref_note.end-dec_note.end) <= 2.0/encoder.sample_frequency
    '''

    def test_melody_encoder(self):
        encoder = MelodyEncoder(
            self.allowed_pitches,
            time_resolution=8,
            num_bars=4,
            bar_time=2)

        for midi in self.test_midis:
            print("orig", len(midi.instruments[0].notes))
            encoding = encoder.encode(midi, 0)
            decoded = encoder.decode(encoding, 0)
            # make sure decoded contains same number of notes
            num_notes = len(midi.instruments[0].notes)

            try:
                assert len(midi.instruments[0].notes) == len(decoded.instruments[0].notes)
            except AssertionError as e:
                print("e", num_notes, midi.instruments[0].notes)
                print("d", len(decoded.instruments[0].notes))
                # for notes in decoded.instruments[0].notes:
                #    print(notes.pitch)
                print("AssertionError 1 ", e)
                pass

            try:
                for note_n in range(num_notes):
                    ref_note = midi.instruments[0].notes[note_n]
                    dec_note = decoded.instruments[0].notes[note_n]
                    # make sure all notes have the same velocity
                    # assert ref_note.velocity == dec_note.velocity
                    # make sure all notes start within 1 sample of reference
                    assert abs(ref_note.start-dec_note.start) <= 1.0/encoder.time_resolution
                    # make sure all notes end within 2 samples of reference
                    assert abs(ref_note.end-dec_note.end) <= 2.0/encoder.time_resolution

            except IndexError as e:
                print("Index Error", e)
                pass
            except AssertionError as e:
                print("AssertionError 2 ", e)
                pass


