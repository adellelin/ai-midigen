from os.path import abspath, split, join, expanduser
from io import BytesIO
import requests
import json
import base64
import pretty_midi as pm

# TODO: make these parameters arguments and possibly launch a crserver as a secondary process
# TODO: for now just manually launch a crserver with the --verbose_response flag to run this test
crserver_url = 'http://127.0.0.1:5000/tfgen'
this_dir = split(abspath(__file__))[0]
test_file = join(this_dir, 'test_midi', '2Bar_120BPM_SET3_01.mid')
output_dir = expanduser('~')

midi = pm.PrettyMIDI(test_file)
call_io = BytesIO()
midi.write(call_io)
a = call_io.getvalue()
r = requests.post(
    url=crserver_url,
    data=a,
    headers={'Content-Type': 'application/octet-stream'})

if r.headers['content-type'] == 'application/json; charset=utf-8':
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


