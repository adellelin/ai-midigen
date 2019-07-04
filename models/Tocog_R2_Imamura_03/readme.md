
Train on dataset:

R2_MTF_Imamura_SET03-Simple.zip

Training command:

train_crmodel MIDIGEN/music_data/R2_MTF_Imamura_SET03-Simple/ MIDIGEN/training_out_Imamura_03-Simple/ MIDIGEN/music_data/R2_MTF_Imamura_SET03-Simple/encoder.json --hidden_code_size 100 --max_response_length 32 --float_type float32 --batch_size 141 --validation_ratio 0.05 --gradient_clip 5 --learning_rate 1e-3 --keep_prob 1 --seed 1

generate model:
generate MIDIGEN/training_out_Imamura_03-Simple/dataset.p MIDIGEN/training_out_Imamura_03-Simple/inference_builder MIDIGEN/training_out_Imamura_03-Simple/ 2

{"allowed_pitches": [50, 51, 60, 61], "time_resolution": 8, "num_bars": 2, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.0010000000474974513
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 3276.7666015625
INFO:CallResponseModel:minimum loss: 3276.7666015625
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 3276.7666015625 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.000640000042039901
INFO:CallResponseModel:epoch: 7200
INFO:CallResponseModel:training entropy: 106.90530395507812
INFO:CallResponseModel:minimum loss: 106.90530395507812
INFO:CallResponseModel:minimum loss epoch: 7200
INFO:CallResponseModel:New minimum validation loss of 106.90530395507812 at epoch 7200

Validation tracks:
calls R1_MTFI02_0271.mid
calls R1_MTFI02_0279.mid
calls R1_MTFI03_0341.mid
calls R1_MTFI03_0329.mid
