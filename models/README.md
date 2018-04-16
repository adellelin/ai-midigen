### guitar_4

- 8 Hz trained with L2 regularization
- Trained on sets 1,2,3,4

### bass_1

- 8 Hz bass, no regularization
- Trained on bass set 1

### bass_2

- 8 Hz bass, with regularization
- Trained on bass set 1 with augmentation


### run commands for Script

crserver ~/anaconda/envs/midigen-env/midigen/models/guitar --port=6000
interface http://127.0.0.1:6000/tfgen /guitar/sound.mid --tempo=226

crserver ~/anaconda/envs/midigen-env/midigen/models/bass --port=5000
interface http://127.0.0.1:5000/tfgen /Path/To/Bass/Response/midifile/Bass_response.mid  --in_port='AI_Bass_In' --out_port='AI_Bass_Out' --log_midi_files --tempo=226
