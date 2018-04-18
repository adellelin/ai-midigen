import sys
import os
from os.path import abspath, join
import traceback
import json
from flask import Flask, request, make_response
import numpy as np
import pretty_midi
from midigen.encode import MelodyEncoder, concat
from midigen.package import logger, version


def main():

    data_dir = abspath('test_midi')
    encoder = MelodyEncoder(
        [55, 58, 60, 63, 65, 66, 67, 70, 72, 75, 77, 78, 79, 82, 84],
        8, 2, 2)
    filecount = 1

    def error_response(e):
        logger.exception(e)
        e_type, e_value, e_traceback = sys.exc_info()
        e_traceback = traceback.format_tb(e_traceback)

        e_dict = {'error_type': str(e_type),
                  'error_value': str(e_value),
                  'error_traceback': ''.join(e_traceback)}
        j = json.dumps(e_dict, ensure_ascii=False).encode('utf8')
        response = make_response(j)
        response.headers['content-type'] = 'application/json; charset=utf-8'
        return response

    for fileList in os.listdir(data_dir):
        if fileList.endswith('.mid'):
            midi_track = data_dir+'/'+fileList
            print("track", midi_track)
            try:
                call_midi = pretty_midi.PrettyMIDI(midi_track)
            except EOFError as err:
                return error_response(err)

            try:
                call_encoded = encoder.encode_ohc(call_midi).reshape((1, encoder.num_time_steps, encoder.num_symbols))

            except IndexError as err:
                return error_response(err)

            print("encoded call", np.amax(call_encoded, axis=2))
            output_vel_symbols = np.amax(call_encoded, axis=2).reshape(encoder.num_time_steps) * 127
            # float to int
            output_vel_symbols = np.int8(output_vel_symbols)
            print("output_vel_symbols", output_vel_symbols)
            output_symbols = np.argmax(call_encoded, axis=2).reshape(encoder.num_time_steps)
            response_midi = encoder.decode(output_symbols, output_vel_symbols)

            #write to midi track
            response_midi.write('test_midi/results/decoded_w_vel'+str(filecount)+'.mid')
            filecount += 1


if __name__ == '__main__':
    main()
