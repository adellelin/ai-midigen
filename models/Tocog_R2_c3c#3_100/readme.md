
Train on dataset:

R2_MTF01_C3C#3.zip

Training command:

train_crmodel MIDIGEN/music_data/R2_MTF01_C3C#3/ MIDIGEN/training_out_MTF01_C3C#3/ MIDIGEN/music_data/R2_MTF01_C3C#3/encoder.json --hidden_code_size 100 --max_response_length 32 --float_type float32 --batch_size 141 --validation_ratio 0.05 --gradient_clip 5 --learning_rate 1e-2 --keep_prob 1 --seed 1

generate model:
generate MIDIGEN/training_out_MTF01_C3C#3/dataset.p MIDIGEN/training_out_MTF01_C3C#3/inference_builder MIDIGEN/training_out_MTF01_C3C#3/ 2

{"allowed_pitches": [60, 61], "time_resolution": 8, "num_bars": 2, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.009999999776482582
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 10385.9990234375
INFO:CallResponseModel:minimum loss: 10385.9990234375
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 10385.9990234375 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.006400000303983688
INFO:CallResponseModel:epoch: 5300
INFO:CallResponseModel:training entropy: 1896.8935546875
INFO:CallResponseModel:minimum loss: 1896.8935546875
INFO:CallResponseModel:minimum loss epoch: 5300
INFO:CallResponseModel:New minimum validation loss of 1896.8935546875 at epoch 5300

validation tracks:
calls R2_MTF01-1_C3_03_0885.mid
calls R2_MTF01-1_C3_06_1151.mid
calls R2_MTF01-1_C3_03_1001.mid
calls R2_MTF01-1_C3_05_1031.mid
calls R2_MTF01-1_C3_06_1127.mid
calls R2_MTF01-1_C3_03_0901.mid
calls R2_MTF01-1_C3_03_1009.mid
calls R2_MTF01-1_C3_06_1149.mid
calls R2_MTF01-1_C3_03_1017.mid
calls R2_MTF01-1_C3_03_0887.mid
calls R2_MTF01-1_C3_05_1023.mid
calls R2_MTF01-1_C3_07_1213.mid
calls R2_MTF01-1_C3_02_0817.mid
