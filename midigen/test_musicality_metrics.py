import os
from os import path
from os.path import join
from unittest import TestCase
import pretty_midi as pm

# criteria, same number of notes, same velocity, start within 1 sample and send within 2 samples of original
# Use unit test hooks


class TestEncoder(TestCase):
    def setUp(self):
        this_dir = path.abspath(path.split(__file__)[0])
        self.data_dir = path.join(this_dir, 'test_midi')
        self.test_midis_calls = []
        self.test_midis_responses = []
        cur_cr = {}
        cur_name = {}

        for fname in os.listdir(self.data_dir):
            full_path = join(self.data_dir, fname)

            if fname.endswith('.mid') and not fname[0] == '.':

                try:
                    num = int(fname.replace('.mid', '').replace(' ', '_').split('_')[-1])
                except ValueError:
                    print(f'file name does not end with integer {fname}')
                    continue

                try:
                    midi = pm.PrettyMIDI(full_path)

                    assert len(midi.instruments[0].notes) > 3
                    cur_cr[num] = midi
                    cur_name[num] = full_path
                except (AssertionError, IOError, KeyError):
                    print(f'Could not add midi file {full_path}.')

        for k in cur_cr.keys():
            if k % 2 == 1:
                try:
                    cur_call = (cur_name[k], cur_cr[k])
                    cur_response = (cur_name[k + 1], cur_cr[k + 1])
                    self.test_midis_calls.append(cur_call)
                    self.test_midis_responses.append(cur_response)
                except KeyError:
                    print(f'Could not add index {k} from {cur_name[k]} because it does not have a valid call/response.')

    def test_musicality_counts(self):

        for i in range(len(self.test_midis_calls)):
            call_name, call = self.test_midis_calls[i]
            response_name, response = self.test_midis_responses[i]
            call_count = len(call.instruments[0].notes)
            response_count = len(response.instruments[0].notes)
            print('call/response differ by ', abs(call_count - response_count))

            print('DEBUG: \ncall:', call_name, ':', call_count, '\nresp:', response_name, ':', response_count)

            for note in call.instruments[0].notes:
                print('DEBUG: call:', call_name, ':', note)


