
Train on dataset:

M2-KD-SET01.zip

Dataset features:
Multiply copies of R1, with new M1 melodies created by Kevin

Training command:

train_crmodel MIDIGEN/music_data/M2-KD-SET01/ MIDIGEN/training_out_M2_SET01/ MIDIGEN/music_data/M2-KD-SET01/encoder.json --hidden_code_size 150 --max_response_length 64 --float_type float32 --validation_ratio 0.05 --gradient_clip 5 --batch_size 0 --learning_rate 1e-2 --keep_prob 1 --seed 1

generate model:
generate MIDIGEN/music_data/M2-KD-SET01/ MIDIGEN/training_out_M2_SET01/dataset.p MIDIGEN/training_out_M2_SET01/inference_builder MIDIGEN/training_out_M2_SET01/ 4

encoder.json:
{"allowed_pitches": [31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81], "time_resolution": 8, "num_bars": 4, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:Initializing model in MIDIGEN/training_out_M2_SET01/
INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.009999999776482582
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 12226.84765625
INFO:CallResponseModel:minimum loss: 12226.84765625
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 12226.84765625 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.002621440449729562
INFO:CallResponseModel:epoch: 3200
INFO:CallResponseModel:training entropy: 0.0026588416658341885
INFO:CallResponseModel:minimum loss: 0.0026588416658341885
INFO:CallResponseModel:minimum loss epoch: 3200
INFO:CallResponseModel:New minimum validation loss of 0.0026588416658341885 at epoch 3200

Validation tracks:

validation call R1_MDY01_SET02_0025.mid
validation call R1_MDY01_SET02_0087.mid
validation call R1_MDY01_SET02_0075.mid
