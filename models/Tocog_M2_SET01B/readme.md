
Train on dataset:

M2-KD-SET01.zip

Dataset features:
Multiply copies of R1, with new M1 melodies created by Kevin

Training command:

train_crmodel MIDIGEN/music_data/M2-KD-SET01/ MIDIGEN/training_out_M2_SET01B/ MIDIGEN/music_data/M2-KD-SET01/encoder.json --hidden_code_size 250 --max_response_length 64 --float_type float32 --validation_ratio 0.05 --gradient_clip 5 --batch_size 0 --learning_rate 1e-2 --keep_prob 1 --seed 1

generate model:
generate MIDIGEN/music_data/M2-KD-SET01/ MIDIGEN/training_out_M2_SET01B/dataset.p MIDIGEN/training_out_M2_SET01B/inference_builder MIDIGEN/training_out_M2_SET01B/Output/ 4

encoder.json:
{"allowed_pitches": [31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81], "time_resolution": 8, "num_bars": 4, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:Initializing model in MIDIGEN/training_out_M2_SET01B/
2019-05-13 04:20:10.508346: W tensorflow/contrib/rnn/kernels/lstm_ops.cc:844] BlockLSTMOp is inefficient when both batch_size and input_size are odd. You are using: batch_size=45, input_size=55
INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.009999999776482582
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 11539.728515625
INFO:CallResponseModel:minimum loss: 11539.728515625
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 11539.728515625 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.005120000336319208
INFO:CallResponseModel:epoch: 1900
INFO:CallResponseModel:training entropy: 0.008826456032693386
INFO:CallResponseModel:minimum loss: 0.008826456032693386
INFO:CallResponseModel:minimum loss epoch: 1900
INFO:CallResponseModel:New minimum validation loss of 0.008826456032693386 at epoch 1900

Validation tracks:

validation call R1_MDY01_SET02_0023.mid
validation call R1_MDY01_SET02_0019.mid
validation call R1_MDY01_SET02_0017.mid
validation call R1_MDY01_SET02_0025.mid
validation call R1_MDY01_SET02_0087.mid
validation call R1_MDY01_SET02_0075.mid
