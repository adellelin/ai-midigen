import os
from setuptools import setup, find_packages
from midigen import version

# find model files in the models directory
model_files = {}
ignored = ['.DS_Store']
for root, dirnames, filenames in os.walk('models'):
    dest = 'midigen/' + root
    for filename in filenames:
        if filename not in ignored:
            if dest not in model_files.keys():
                model_files[dest] = [os.path.join(root, filename)]
            else:
                model_files[dest].append(os.path.join(root, filename))
data_files = [
    ('midigen/Responses', ['Responses/Bass_response.mid', 'Responses/Guitar_response.mid']),
    ('midigen/max', ['max/midigen.maxpat', 'max/AI_Visualizer.maxpat', 'max/background_max.png', 'max/ella_max.png', 'max/line_max.png', 'max/line_v_max.png', 'max/miles_Max.png', 'max/movidius_max.png', 'max/disklavier_max.png']),
    ('midigen/ableton', ['ableton/midigen.als', 'ableton/SyncCallAndResponse.amxd', 'ableton/AI_Bassist_Touch_New_Flourish.amxd',
        'ableton/AI_Guitar_Touch_New_Flourish.amxd', 'ableton/Song_Sync_Touch.amxd', 'ableton/NM-Humanizer-monophonic.amxd', 'ableton/Kev_Touch_New.amxd', 'ableton/Transport.amxd']),
    ('midigen/ableton/Ableton Project Info', ['ableton/Ableton Project Info/Project8_1.cfg'])]
data_files.extend(zip(model_files.keys(), model_files.values()))

setup(
    name='midigen',
    version=version,
    url='https://github.com/adellelin/ai-midigen',
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    install_requires=[
        'pretty_midi', 'flask', 'flask-restful', 'tensorflow==1.5',
        'numpy', 'mido', 'requests', 'appdirs', 'python-rtmidi', 'pykka', 'scipy',
        'json', 'base64', 'math', 'pythonosc'],

    data_files=data_files,

    entry_points={
        'console_scripts': [
            'crserver=midigen.call_response_server:main',
            'interface=midigen.rt_midi_interface:main'],
    },
)
