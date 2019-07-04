
Train on dataset:

SD_04_Hard Rock_KD_SET 03_TOCOG.zip

Training command:

train_crmodel TRAINING_DATA/ training_out_drums_2bar_4/ TRAINING_DATA/encoder.json --hidden_code_size 100 --max_response_length 32 --float_type float32 --batch_size 298 --validation_ratio 0.05 --gradient_clip 5 --learning_rate 1e-2 --keep_prob 1 --seed 1

TRAINING_DATA/encoder.json
{"allowed_pitches": [24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 57, 58, 59, 60, 62, 64, 66, 68, 76, 77, 78, 79, 80], "time_resolution": 8, "num_bars": 2, "bar_time": 2, "encoder_type": "MelodyEncoder"}

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.00800000037997961
INFO:CallResponseModel:epoch: 7700
INFO:CallResponseModel:training entropy: 672.0377197265625
INFO:CallResponseModel:minimum loss: 671.9406127929688
INFO:CallResponseModel:minimum loss epoch: 4300
