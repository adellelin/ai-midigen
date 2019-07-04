
Train on dataset:

R2_MTF_SET04.zip

Dataset features:
combined imamura and kevin's R2, Imamura up to track 0248

Training command:

train_crmodel MIDIGEN/music_data/R2_MTF_SET04/ MIDIGEN/training_out_R2_MTF_SET04/ MIDIGEN/music_data/R2_MTF_SET04/encoder.json --hidden_code_size 150 --max_response_length 32 --float_type float32 --validation_ratio 0.10 --gradient_clip 5 --batch_size 0 --learning_rate 1e-2 --keep_prob 1 --seed 1

generate model:
generate MIDIGEN/music_data/R2_MTF_SET04/ MIDIGEN/training_out_R2_MTF_SET04/dataset.p MIDIGEN/training_out_R2_MTF_SET04/inference_builder MIDIGEN/training_out_R2_MTF_SET04/output 2

{"allowed_pitches": [50, 51, 52, 53, 54, 55, 60, 61], "time_resolution": 8, "num_bars": 2, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:Initializing model in MIDIGEN/training_out_R2_MTF_SET04/
INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.009999999776482582
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 16104.810546875
INFO:CallResponseModel:minimum loss: 16104.810546875
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 16104.810546875 at epoch 0

manually stop training:

INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.009999999776482582
INFO:CallResponseModel:epoch: 3700
INFO:CallResponseModel:training entropy: 1131.697265625
INFO:CallResponseModel:minimum loss: 1131.697265625
INFO:CallResponseModel:minimum loss epoch: 3700
INFO:CallResponseModel:New minimum validation loss of 1131.697265625 at epoch 3700

Validation tracks:

validation call R1_MTFI02_0283_SET03_0279.mid
validation call R1_MTFI03_0327_SET03_0199.mid
validation call R1_MTFI03_0337_SET03_0209.mid
validation call R1_MTFI03_0335_SET03_0455.mid
validation call R1_MTFI03_0325_SET03_0197.mid
validation call R1_MTFI03_0373_SET03_0369.mid
validation call R1_MTFI03_0329_SET03_0325.mid
validation call R1_MTFI02_D2_0141_SET02_0013.mid
validation call R1_MTFI02_0263_SET03_0259.mid
validation call R1_MTFI03_0351_SET03_0223.mid
validation call R1_MTFI02_0267_SET03_0139.mid
validation call R1_MTFI03_0321_SET03_0317.mid
validation call R1_MTFI02_0297_SET03_0293.mid
validation call R1_MTFI03_0367_SET03_0487.mid
validation call R1_MTFI03_0317_SET03_0437.mid
validation call R1_MTFI03_0327_SET03_0447.mid
validation call R1_MTFI03_0359_SET03_0479.mid
validation call R1_MTFI02_0303_SET03_0175.mid
validation call R1_MTFI03_0321_SET03_0193.mid
validation call R1_MTFI03_0367_SET03_0363.mid
validation call R1_MTFI03_0323_SET03_0319.mid
validation call R1_MTFI02_0297_SET03_0417.mid
validation call R1_MTFI03_0325_SET03_0321.mid
validation call R1_MTFI03_D2_0229_SET02_0101.mid
validation call R1_MTFI02_0275_SET03_0147.mid
