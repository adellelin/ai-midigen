Train on dataset:

CTX_EGTR_clean_nadine

Training command:

train_crmodel --hidden_code_size 10 --max_response_length 64
--batch_size 40 --float_type float64 --validation_ratio 0.05
--gradient_clip 5 --learning_rate 1e-3 --keep_prob 1.0 --seed 1
~/music_data/4_bar_rock_sets_guitar/CTX_EGTR_clean_nadine/
/media/mdpicket/FCF6AC0BF6ABC3EC/training_out/ai_music/rock_guitar_4/
~/music_data/4_bar_rock_sets_guitar/encoder.json

encoder contents:

{"allowed_pitches": [42, 43, 46, 47, 48, 49, 51, 53, 54, 55, 56, 57,
58, 60, 62, 63, 65, 66, 67, 68, 69, 70, 72, 74, 75, 77, 78, 79,
81, 82, 84, 85, 86, 87],
"time_resolution": 8, "num_bars": 4,
"bar_time": 2, "encoder_type": "MelodyEncoder"}

manually stop training at 417300 epochs