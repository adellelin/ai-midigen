Use data sets:
TYR_BASS_ROCK_KD_SET01
TYR_BASS_ROCK_KD_SET02
TYR_BASS_ROCK_KD_SET03

train_crmodel ~/music_data/4_bar_rock_sets_bass /media/mdpicket/FCF6AC0BF6ABC3EC/training_out/ai_music/4bar_rock_bass_5/
~/music_data/4_bar_rock_sets_bass/encoder.json --hidden_code_size 50 --max_response_length 64 --float_type float32
--batch_size 490 --validation_ratio 0.05 --gradient_clip 5 --learning_rate 1e-3 --keep_prob 1 --seed 1

encoder contents:
{"allowed_pitches": [27, 29, 31, 32, 34, 36, 38, 39, 41, 43, 44, 46, 48, 51, 53, 55, 56, 58, 63, 72, 74, 68, 60, 62, 54, 65, 79, 75, 54, 67, 64, 69, 70, 79],
"time_resolution": 8, "num_bars": 4, "bar_time": 2, "encoder_type": "MelodyEncoder"}

Tried training with a 16 Hz encoder - lots of empty responses