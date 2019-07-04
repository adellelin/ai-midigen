
Train on dataset:

M1-SET01.zip

Training command:

train_crmodel MIDIGEN/music_data/M1-SET01/ MIDIGEN/training_out_M1_SET01C/ MIDIGEN/music_data/M1-SET01/encoder.json --hidden_code_size 150 --max_response_length 64 --float_type float32 --validation_ratio 0.05 --gradient_clip 5 --batch_size 0 --learning_rate 1e-3 --keep_prob 1 --seed 1

generate model:
generate MIDIGEN/training_out_M1_SET01/dataset.p MIDIGEN/training_out_M1_SET01/inference_builder MIDIGEN/training_out_M1_SET01/ 4

encoder.json:
{"allowed_pitches": [31, 32, 34, 36, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 74, 75, 76, 77, 78, 79, 80], "time_resolution": 8, "num_bars": 4, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:Initializing model in MIDIGEN/training_out_M1_SET01C/
INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.0010000000474974513
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 10100.75390625
INFO:CallResponseModel:minimum loss: 10100.75390625
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 10100.75390625 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.00026214405079372227
INFO:CallResponseModel:epoch: 15400
INFO:CallResponseModel:training entropy: 92.12205505371094
INFO:CallResponseModel:minimum loss: 92.12205505371094
INFO:CallResponseModel:minimum loss epoch: 15400
INFO:CallResponseModel:New minimum validation loss of 92.12205505371094 at epoch 15400

Validation tracks:
calls R1_MDY01_009_0017.mid
calls R1_MDY01_016_0031.mid
calls R1_MDY01_041_0081.mid

Dataset features:
Concatenated R1 2 bar tunes, with M1 melodies collected from famous anthems
