### Rock_Bass_4bar


### Blues_Guitar_2bar


### run commands for Script

crserver ~/anaconda/envs/midigen-env/midigen/models/guitar --port=6000
interface http://127.0.0.1:6000/tfgen /guitar/sound.mid --tempo=226

crserver ~/anaconda/envs/midigen-env/midigen/models/bass --port=5000
interface http://127.0.0.1:5000/tfgen /Path/To/Bass/Response/midifile/Bass_response.mid  --in_port='AI_Bass_In' --out_port='AI_Bass_Out' --log_midi_files --tempo=226
