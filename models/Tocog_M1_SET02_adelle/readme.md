
Train on dataset:

M1-SET02.zip

Training command:

train_crmodel MIDIGEN/music_data/M1-SET02_adelle/ MIDIGEN/training_out_M1_SET02_adelle/ MIDIGEN/music_data/M1-SET02_adelle/encoder.json --hidden_code_size 150 --max_response_length 64 --float_type float32 --validation_ratio 0.05 --gradient_clip 5 --batch_size 0 --learning_rate 1e-3 --keep_prob 1 --seed 2

generate model:
generate MIDIGEN/training_out_M1_SET02_adelle/dataset.p MIDIGEN/training_out_M1_SET02_adelle/inference_builder MIDIGEN/training_out_M1_SET02_adelle/ 4

encoder.json:
{"allowed_pitches": [31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81], "time_resolution": 8, "num_bars": 4, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.0010000000474974513
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 10545.693359375
INFO:CallResponseModel:minimum loss: 10545.693359375
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 10545.693359375 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.0005497559905052185
INFO:CallResponseModel:epoch: 8700
INFO:CallResponseModel:training entropy: 0.0008424518164247274
INFO:CallResponseModel:minimum loss: 0.0008424518164247274
INFO:CallResponseModel:minimum loss epoch: 8700
INFO:CallResponseModel:New minimum validation loss of 0.0008424518164247274 at epoch 8700

Validation tracks:

calls M1_KD_0017.mid
calls M1_KD_0031.mid
calls M1_KD_0081.mid

Dataset features:
Used the set of melodies as input and output, response (46-90 become 1-45, 2-44 become 47-89) with M1 melodies collected from famous anthems
