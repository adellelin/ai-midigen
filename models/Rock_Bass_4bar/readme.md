Use data sets:
Rock_Bass_4bar_Dataset.zip in latest release


train_crmodel ~/music_data/4_bar_rock_sets_bass /media/mdpicket/FCF6AC0BF6ABC3EC/training_out/ai_music/4bar_rock_bass_5/ ~/music_data/4_bar_rock_sets_bass/encoder.json --hidden_code_size 50 --max_response_length 64 --float_type float32 --batch_size 490 --validation_ratio 0.05 --gradient_clip 5 --learning_rate 1e-3 --keep_prob 1 --seed 1

Trained for 266k epochs

Notes:

sourced originally from kevin doucette:
TYR_BASS_ROCK_KD_SET01
TYR_BASS_ROCK_KD_SET02
TYR_BASS_ROCK_KD_SET03

