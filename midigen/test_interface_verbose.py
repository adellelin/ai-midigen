from os.path import abspath, split, join, expanduser
from io import BytesIO
import requests
import json
import base64
import pretty_midi as pm
import logging
import mido
import numpy as np
import sys

import argparse
import time
import random

from pythonosc import osc_message_builder
from pythonosc import osc_bundle_builder
from pythonosc import udp_client


# TODO: make these parameters arguments and possibly launch a crserver as a secondary process
# TODO: for now just manually launch a crserver with the --verbose_response flag to run this test
crserver_url = 'http://127.0.0.1:7000/tfgen'
this_dir = split(abspath(__file__))[0]
test_file = join(this_dir, 'test_midi', '2Bar_120BPM_SET3_01.mid')
output_dir = expanduser('~')

midi = pm.PrettyMIDI(test_file)
call_io = BytesIO()
midi.write(call_io)
a = call_io.getvalue()


class PostToServer:
    def __init__(self):
        print("self")

    def write_output_midi(self, response_io):
        response_midi = mido.MidiFile(file=response_io)
        response_midi.type = 0
        response_path = 'response' + '05' + '.mid'
        with open(response_path, mode='wb') as f:
            response_io.seek(0)
            f.write(response_io.getvalue())

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default="127.0.0.1",
                            help="The ip of the OSC server")
        parser.add_argument("--port", type=int, default=5007,
                            help="The port the OSC server is listening on")
        args = parser.parse_args()

        client = udp_client.SimpleUDPClient(args.ip, args.port)

        try:
            r = requests.post(
                url=crserver_url,
                data=a,
                headers={'Content-Type': 'application/octet-stream'})

            return_type=['application/json; charset=utf-8','application/octet-stream']

        except requests.ConnectionError:
            logging.error("cr server not found")
            sys.exit(-1)
        try:
            assert r.headers['content-type'] in return_type
            if r.headers['content-type'] == 'application/octet-stream':
                response_io = BytesIO(r.content)
                try:
                    self.write_output_midi(response_io)
                except IOError as e:
                    logging.warning("error")

            else:
                print("probability and midi", r.headers['content-type'])

                response_dict = json.loads(r.content, encoding='utf-8')
                response_midi_bytes = base64.b64decode(response_dict['midi'])
                response_io = BytesIO(response_midi_bytes)
                response_out_dist = response_dict['output_distribution']
                response_out_np_dist = np.array(response_out_dist)
                print("output shape", response_out_np_dist.shape)
                out_symbols = np.argmax(response_out_np_dist, axis=1)
                print("note symbols", out_symbols.shape, out_symbols)
                out_symbols = out_symbols.tolist()
                client.send_message("/output_symbols/", out_symbols)
                client.send_message("/animation/seq", 1)  # trigger rnn animation

                try:
                    self.write_output_midi(response_io)
                    response_out_np_dist = np.array(response_out_dist, dtype=float)
                    #set up osc bundle
                    bundle = osc_bundle_builder.OscBundleBuilder(
                        osc_bundle_builder.IMMEDIATELY)
                    test_array = []
                    for index in range(len(response_out_np_dist)):
                        sub_array = []
                        msg = osc_message_builder.OscMessageBuilder(address="/probdist/" + str(index))
                        for x in np.nditer(response_out_np_dist[index]):
                            msg.add_arg(float(x))
                            sub_array.append(float(x))
                        bundle.add_content(msg.build())
                        test_array.append(sub_array)
                        #print("array", index, sub_array)
                    bundle = bundle.build()
                    client.send(bundle)
                    try:
                        assert test_array[index] == response_out_dist[index]
                    except AssertionError:
                        logging.warning("arrays don't match")

                except IOError as e:
                    logging.warning("error")


        except AssertionError:
            logging.warning("header %s type not found", "r.headers['content-type']")



if __name__ == "__main__":
    PostToServer().main()




'''
if r.headers['content-type'] == 'application/json; charset=utf-8':
    response_dict = json.loads(r.content, encoding='utf-8')
    response_midi_bytes = base64.b64decode(response_dict['midi'])
    response_midi = pm.PrettyMIDI(BytesIO(response_midi_bytes))
    response_out_dist = response_dict['output_distribution']
    response_midi.write(join(output_dir, 'test_crserver_out.midi'))
else:
    raise ValueError()
'''

#print("dist", len(response_out_dist), len(response_out_dist[0]))

# TODO: run crserver as subprocess? could use example from:
#  https://stackoverflow.com/questions/16071866/non-blocking-subprocess-call
# async def do_subprocess():
#     print('Subprocess sleeping')
#     proc = await asyncio.create_subprocess_exec('crserver', model_path)
#     returncode = await proc.wait()
#     print('Subprocess done sleeping.  Return code = %d' % returncode)
#
#
# async def sleep_report(number):
#     for i in range(number + 1):
#         print('Slept for %d seconds' % i)
#         await asyncio.sleep(1)
#
# loop = asyncio.get_event_loop()
#
# tasks = [
#     asyncio.ensure_future(do_subprocess()),
#     asyncio.ensure_future(sleep_report(5)),
# ]
#
# loop.run_until_complete(asyncio.gather(*tasks))
# loop.close()



