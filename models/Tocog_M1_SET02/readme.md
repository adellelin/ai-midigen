
Train on dataset:

M1-SET02.zip

Training command:

train_crmodel MIDIGEN/music_data/M1-SET02/ MIDIGEN/training_out_M1_SET02/ MIDIGEN/music_data/M1-SET02/encoder.json --hidden_code_size 100 --max_response_length 64 --float_type float32 --validation_ratio 0.05 --gradient_clip 5 --batch_size 0 --learning_rate 1e-2 --keep_prob 1 --seed 1

generate model:
generate MIDIGEN/training_out_M1_SET02/dataset.p MIDIGEN/training_out_M1_SET02/inference_builder MIDIGEN/training_out_M1_SET02/ 4

encoder.json:
{"allowed_pitches": [31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81], "time_resolution": 8, "num_bars": 4, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:Initializing model in MIDIGEN/training_out_M1_SET02/
INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.009999999776482582
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 10554.0185546875
INFO:CallResponseModel:minimum loss: 10554.0185546875
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 10554.0185546875 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.0005497559905052185
INFO:CallResponseModel:epoch: 8700
INFO:CallResponseModel:training entropy: 0.0008424518164247274
INFO:CallResponseModel:minimum loss: 0.0008424518164247274
INFO:CallResponseModel:minimum loss epoch: 8700
INFO:CallResponseModel:New minimum validation loss of 0.0008424518164247274 at epoch 8700

Validation tracks:

calls R1_MDY01_SET02_0017.mid
calls R1_MDY01_SET02_0031.mid
calls R1_MDY01_SET02_0081.mid

Dataset features:
Concatenated R1 2 bar tunes and each input transposed up a step, with M1 melodies collected from famous anthems
