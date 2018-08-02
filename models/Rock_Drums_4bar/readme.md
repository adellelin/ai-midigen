
Train on dataset:

Rock_Drum_4bar_Dataset.zip


Training command:

train_crmodel TRAINING_DATA/  TRAINING_OUT_100/ TRAINING_DATA/encoder.json --hidden_code_size 100 --max_response_length 64 --float_type float32 --batch_size 1757 --validation_ratio 0.05 --gradient_clip 5 --learning_rate 1e-2 --keep_prob 1 --seed 1

TRAINING_DATA/encoder.json
{"allowed_pitches": [24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48], "time_resolution": 8, "num_bars": 4, "bar_time": 2, "encoder_type": "MelodyEncoder"}

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.0005120000569149852
INFO:CallResponseModel:epoch: 47600
INFO:CallResponseModel:training entropy: 1495.04248046875
INFO:CallResponseModel:minimum loss: 1331.6669921875
INFO:CallResponseModel:minimum loss epoch: 46600


Datasets:
