
Train on dataset:

R2_MTF_Imamura SET02.zip

Training command:

train_crmodel MIDIGEN/music_data/R2_MTF_Imamura_SET02/ MIDIGEN/training_out_R2_Imamura_02/ MIDIGEN/music_data/R2_MTF_Imamura_SET02/encoder.json --hidden_code_size 100 --max_response_length 32 --float_type float32 --batch_size 141 --validation_ratio 0.05 --gradient_clip 5 --learning_rate 1e-2 --keep_prob 1 --seed 1

generate model:
generate MIDIGEN/training_out_R2_Imamura_02/dataset.p MIDIGEN/training_out_R2_Imamura_02/inference_builder MIDIGEN/training_out_R2_Imamura_02/ 2

{"allowed_pitches": [50, 51, 60, 61], "time_resolution": 8, "num_bars": 2, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.10000000149011612
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 5803.2197265625
INFO:CallResponseModel:minimum loss: 5803.2197265625
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 5803.2197265625 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.0008589937351644039
INFO:CallResponseModel:epoch: 9100
INFO:CallResponseModel:training entropy: 6.226404666900635
INFO:CallResponseModel:minimum loss: 6.226404666900635
INFO:CallResponseModel:minimum loss epoch: 9100
INFO:CallResponseModel:New minimum validation loss of 6.226404666900635 at epoch 9100
