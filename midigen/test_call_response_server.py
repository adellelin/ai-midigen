from os.path import abspath, split, join, expanduser
import os
from io import BytesIO
import requests
import json
import base64
import pretty_midi as pm

# TODO: make these parameters arguments and possibly launch a crserver as a secondary process
# TODO: for now just manually launch a crserver with the --verbose_response flag to run this test
crserver_url = 'http://127.0.0.1:5000/tfgen'
this_dir = split(abspath(__file__))[0]
#test_file = join(this_dir, 'test', 'full_call_61.mid') # full_call_8.mid, full_call_12.mid, full_call_37.mid, full_call_43.mid
#output_dir = expanduser('~')
output_dir = '/Users/adelleli/Documents/Git/ai-midigen/midigen/M3_SET01_valid_response/'
# name of the folder containing calls
directory = join(this_dir, 'M3_SET01_valid_original_call')
output_fname_prefix = 'M3_01_'
print(directory)

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

for root, dirs, files in os.walk(directory):
    print(root, dirs, files, directory)
    for i, file in enumerate(files):
        full_fname = join(directory, file)
        print(full_fname)
        if '.DS_Store' in full_fname:
            continue
        midi = pm.PrettyMIDI(full_fname)

        call_io = BytesIO()
        # validate the call
        midi.write(call_io)
        #midi.write(join(output_dir, full_fname))
        a = call_io.getvalue()
        try:
            r = requests.post(
                url=crserver_url,
                data=a,
                headers={'Content-Type': 'application/octet-stream'})
        except IOError as e:
            print(e)

        print(r.headers['content-type'])
        print(r)

        if r.headers['content-type'] == 'application/octet-stream':
            response_io = BytesIO(r.content)
            response_midi = pm.PrettyMIDI(response_io)
            output_fname = output_fname_prefix + str(i*2)+'.mid'
            #response_midi.write(join(output_dir, 'imamura_06B.mid'))
            print("output_midi", output_fname)
            response_midi.write(join(output_dir, output_fname))

        elif r.headers['content-type'] == 'application/json; charset=utf-8':
            response_dict = json.loads(r.content, encoding='utf-8')
            response_midi_bytes = base64.b64decode(response_dict['midi'])
            response_midi = pm.PrettyMIDI(BytesIO(response_midi_bytes))
            response_out_dist = response_dict['output_distribution']
            response_midi.write(join(output_dir, 'test_crserver_out.midi'))

        else:
            raise ValueError()


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



