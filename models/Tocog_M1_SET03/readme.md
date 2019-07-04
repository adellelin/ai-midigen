
Train on dataset:

M1-SET03.zip

Training command:

train_crmodel MIDIGEN/music_data/M1-SET03/ MIDIGEN/training_out_M1_SET03/ MIDIGEN/music_data/M1-SET03/encoder.json --hidden_code_size 150 --max_response_length 64 --float_type float32 --validation_ratio 0.05 --gradient_clip 5 --batch_size 0 --learning_rate 1e-2 --keep_prob 1 --seed 2

generate model:
generate MIDIGEN/training_out_M1_SET02C/dataset.p MIDIGEN/training_out_M1_SET02C/inference_builder MIDIGEN/training_out_M1_SET02C/ 4

encoder.json:
{"allowed_pitches": [31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81], "time_resolution": 8, "num_bars": 4, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:Initializing model in MIDIGEN/training_out_M1_SET03/
2019-05-09 01:34:40.720757: W tensorflow/contrib/rnn/kernels/lstm_ops.cc:844] BlockLSTMOp is inefficient when both batch_size and input_size are odd. You are using: batch_size=171, input_size=51
INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.009999999776482582
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 42988.4921875
INFO:CallResponseModel:minimum loss: 42988.4921875
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 42988.4921875 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.0032768005039542913
INFO:CallResponseModel:epoch: 3600
INFO:CallResponseModel:training entropy: 1185.1199951171875
INFO:CallResponseModel:minimum loss: 1185.1199951171875
INFO:CallResponseModel:minimum loss epoch: 3600
INFO:CallResponseModel:New minimum validation loss of 1185.1199951171875 at epoch 3600

Validation tracks:

calls R1_MDY01_SET02_0325.mid
calls R1_MDY01_SET02_0015.mid
calls R1_MDY01_SET02_0209.mid
calls R1_MDY01_SET02_0151.mid
calls R1_MDY01_SET02_0087.mid
calls R1_MDY01_SET02_0045.mid
calls R1_MDY01_SET02_0145.mid
calls R1_MDY01_SET02_0031.mid
calls R1_MDY01_SET02_0337.mid


Dataset features:
Multiply copies of R1, with M1 melodies collected from famous anthems with pitch variations
