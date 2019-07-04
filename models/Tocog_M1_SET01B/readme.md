
Train on dataset:

M1-SET01.zip

Training command:

train_crmodel MIDIGEN/music_data/M1-SET01/ MIDIGEN/training_out_M1_SET01/ MIDIGEN/music_data/M1-SET01/encoder.json --hidden_code_size 100 --max_response_length 64 --float_type float32 --validation_ratio 0.05 --gradient_clip 5 --batch_size 0 --learning_rate 1e-2 --keep_prob 1 --seed 1

generate model:
generate MIDIGEN/training_out_M1_SET01/dataset.p MIDIGEN/training_out_M1_SET01/inference_builder MIDIGEN/training_out_M1_SET01/ 4

encoder.json:
{"allowed_pitches": [31, 32, 34, 36, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 74, 75, 76, 77, 78, 79, 80], "time_resolution": 8, "num_bars": 4, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:Initializing model in MIDIGEN/training_out_M1_SET01B/
INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.009999999776482582
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 10161.84765625
INFO:CallResponseModel:minimum loss: 10161.84765625
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 10161.84765625 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.0013421776238828897
INFO:CallResponseModel:epoch: 5500
INFO:CallResponseModel:training entropy: 87.9716796875
INFO:CallResponseModel:minimum loss: 87.9716796875
INFO:CallResponseModel:minimum loss epoch: 5500
INFO:CallResponseModel:New minimum validation loss of 87.9716796875 at epoch 5500


Validation tracks:
calls R1_MDY01_013_0025.mid
calls R1_MDY01_044_0087.mid
calls R1_MDY01_038_0075.mid


Dataset features:
Concatenated R1 2 bar tunes, with M1 melodies collected from famous anthems
