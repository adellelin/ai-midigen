
Train on dataset:

M1-SET02.zip

Training command:

train_crmodel MIDIGEN/music_data/M1-SET02/ MIDIGEN/training_out_M1_SET02C/ MIDIGEN/music_data/M1-SET02/encoder.json --hidden_code_size 150 --max_response_length 64 --float_type float32 --validation_ratio 0.05 --gradient_clip 5 --batch_size 0 --learning_rate 1e-2 --keep_prob 1 --seed 1

generate model:
generate MIDIGEN/training_out_M1_SET02C/dataset.p MIDIGEN/training_out_M1_SET02C/inference_builder MIDIGEN/training_out_M1_SET02C/ 4

encoder.json:
{"allowed_pitches": [31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81], "time_resolution": 8, "num_bars": 4, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:Initializing model in MIDIGEN/training_out_M1_SET02C/
INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.009999999776482582
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 10587.740234375
INFO:CallResponseModel:minimum loss: 10587.740234375
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 10587.740234375 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.0032768005039542913
INFO:CallResponseModel:epoch: 1800
INFO:CallResponseModel:training entropy: 0.017790958285331726
INFO:CallResponseModel:minimum loss: 0.017790958285331726
INFO:CallResponseModel:minimum loss epoch: 1800
INFO:CallResponseModel:New minimum validation loss of 0.017790958285331726 at epoch 1800

Validation tracks:

calls R1_MDY01_SET02_0025.mid
calls R1_MDY01_SET02_0087.mid
calls R1_MDY01_SET02_0075.mid

Dataset features:
Concatenated R1 2 bar tunes and each input transposed up a step, with M1 melodies collected from famous anthems
