
Train on dataset:

M3_KD_SET01.zip

Dataset features:
combined imamura and kevin's R1, with new melody M3 from kevin

Training command:

train_crmodel MIDIGEN/music_data/M3-KD-SET01/ MIDIGEN/training_out_M3_SET01/ MIDIGEN/music_data/M3-KD-SET01/encoder.json --hidden_code_size 150 --max_response_length 32 --float_type float32 --validation_ratio 0.10 --gradient_clip 5 --batch_size 0 --learning_rate 1e-2 --keep_prob 1 --seed 1

generate model:
generate MIDIGEN/music_data/M3-KD-SET01/ MIDIGEN/training_out_M3_SET01/dataset.p MIDIGEN/training_out_M3_SET01/inference_builder MIDIGEN/training_out_M3_SET01/output 2

{"allowed_pitches": [65, 67, 69, 70, 72, 50, 51, 52, 53, 54, 55, 60], "time_resolution": 8, "num_bars": 4, "bar_time": 2, "encoder_type": "MelodyEncoder"}

started:

INFO:CallResponseModel:Initializing model in MIDIGEN/training_out_M3_SET01/
FIRST EPOCH
2019-07-03 10:56:45.569895: W tensorflow/contrib/rnn/kernels/lstm_ops.cc:844] BlockLSTMOp is inefficient when both batch_size and input_size are odd. You are using: batch_size=333, input_size=15
INFO:CallResponseModel:+++++++++++++++++
INFO:CallResponseModel:learning_rate: 0.009999999776482582
INFO:CallResponseModel:epoch: 0
INFO:CallResponseModel:training entropy: 56862.53515625
INFO:CallResponseModel:minimum loss: 56862.53515625
INFO:CallResponseModel:minimum loss epoch: 0
INFO:CallResponseModel:New minimum validation loss of 56862.53515625 at epoch 0

manually stop training:

INFO:CallResponseModel:epoch: 5400
INFO:CallResponseModel:training entropy: 2091.9912109375
INFO:CallResponseModel:minimum loss: 2091.582275390625
INFO:CallResponseModel:minimum loss epoch: 5000

Validation tracks:
validation call R2_MTF01-SET07_0723.mid
validation call R1_MTFI02_SET02_0031.mid
validation call R1_MTFI02_SET03_0423.mid
validation call R1_MTFI02_SET03_0411.mid
validation call R2_MTF01-SET07_0697.mid
validation call R1_MTFI03_SET03_0369.mid
validation call R2_MTF01-SET05_0529.mid
validation call R1_MTFI03_SET03_0355.mid
validation call R2_MTF01-SET06_0633.mid
validation call R1_MTFI01_SET02_0003.mid
validation call R2_MTF01-SET06_0627.mid
validation call R1_MTFI02_SET02_0015.mid
validation call R2_MTF01-SET06_0635.mid
validation call R2_MTF01-SET07_0639.mid
validation call R1_MTFI01_SET03_0129.mid
validation call R1_MTFI03_SET02_0091.mid
validation call R1_MTFI02_SET03_0283.mid
validation call R1_MTFI03_SET03_0483.mid
validation call R1_MTFI03_SET03_0367.mid
validation call R1_MTFI02_SET03_0177.mid
validation call R1_MTFI02_SET03_0141.mid
validation call R1_MTFI03_SET02_0121.mid
validation call R2_MTF01-SET05_0505.mid
validation call R2_MTF01-SET05_0509.mid
validation call R2_MTF01-SET06_0553.mid
validation call R1_MTFI03_SET03_0229.mid
validation call R2_MTF01-SET06_0563.mid
validation call R1_MTFI03_SET03_0475.mid
validation call R1_MTFI02_SET03_0183.mid
validation call R1_MTFI03_SET02_0067.mid
validation call R1_MTFI03_SET02_0097.mid
validation call R2_MTF01-SET07_0671.mid
validation call R1_MTFI03_SET02_0075.mid
validation call R1_MTFI03_SET03_0343.mid
validation call R2_MTF01-SET05_0511.mid
validation call R1_MTFI02_SET03_0185.mid
validation call R1_MTFI03_SET03_0471.mid
validation call R1_MTFI02_SET02_0045.mid
