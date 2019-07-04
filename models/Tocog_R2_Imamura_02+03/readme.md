
Train on dataset:

R2_MTF_Imamura_SET02+03 (Diff Pitches).zip

Dataset features:
combined imamura set 2, set 3- simple and increased pitches for R1 input

Training command:

train_crmodel MIDIGEN/music_data/R2_MTF_Imamura_SET02+03_Dif/ MIDIGEN/training_out_R2_Imamura_SET02+03_Dif/ MIDIGEN/music_data/R2_MTF_Imamura_SET02+03_Dif/encoder.json --hidden_code_size 100 --max_response_length 32 --float_type float32 --validation_ratio 0.05 --gradient_clip 5 --batch_size 0 --learning_rate 1e-2 --keep_prob 1 --seed 1

generate model:
generate MIDIGEN/training_out_R2_Imamura_SET02+03_Dif/dataset.p MIDIGEN/training_out_R2_Imamura_SET02+03_Dif/inference_builder MIDIGEN/training_out_R2_Imamura_SET02+03_Dif/ 2

{"allowed_pitches": [50, 51, 52, 53, 60, 61], "time_resolution": 8, "num_bars": 2, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:Initializing model in MIDIGEN/training_out_R2_Imamura_SET02+03_Dif/
INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.009999999776482582
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 8011.5361328125
INFO:CallResponseModel:minimum loss: 8011.5361328125
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 8011.5361328125 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.002621440449729562
INFO:CallResponseModel:epoch: 6800
INFO:CallResponseModel:training entropy: 282.95843505859375
INFO:CallResponseModel:minimum loss: 282.9023132324219
INFO:CallResponseModel:minimum loss epoch: 6400

Validation tracks:
calls R1_MTFI01_D2_0129_SET02_0003.mid
calls R1_MTFI03_0341_SET03_0337.mid
calls R1_MTFI02_0263_SET03_0259.mid
calls R1_MTFI03_0335_SET03_0331.mid
calls R1_MTFI02_0269_SET03_0265.mid
calls R1_MTFI03_D2_0221_SET02_0093.mid
calls R1_MTFI02_D2_0141_SET02_0013.mid
