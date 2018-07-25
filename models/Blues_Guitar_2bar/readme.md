
Train on dataset:

Blues_Guitar_2bar_Dataset.zip


Training command:

train_crmodel --hidden_code_size 50 --max_response_length 32 --batch_size 40 --float_type float64 --validation_ratio 0.05 --gradient_clip 5 --learning_rate 1e-3 --keep_prob 1.0 --seed 1 /TRAINING_DATA/JAZZ_GUITAR/ /TRAINING_OUT/ /TRAINING_DATA/JAZZ_GUITAR/encoder.json


manually stop training at 660300 epochs


Notes:

“2 Bar C&R - Set 3 112117”, “2Bar_120BPM_SET2_Exports”, “2 Bar C&R - Set 4 113017 Guitar” 