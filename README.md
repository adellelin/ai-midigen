# midigen

## fresh installation

1) install miniconda 3

if installing on Ubuntu you need ALSA and JACK libraries installed:

```
sudo apt-get install libasound2-dev libjack-dev
```

2) acquire wheel file from github releases

3) create conda environment and install library

``` bash
conda create -n midigen-env python=3.6 tensorflow==1.8
    or pip3 install --upgrade https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.8.0-py3-none-any.whl
source activate midigen-env
pip install /path/to/wheel.whl
```

## upgrade installation

1) acquire new wheel file

2) uninstall and re-install new wheel

``` bash
source activate midigen-env
pip uninstall midigen
pip install /path/to/wheel.whl
```


## Usage

### crserver
Start a call-reponse server for generating responses
``` bash
source activate midigen-env
crserver /path/to/model
```

When installing from a released wheel file, some default models should be
installed into the environment. Depending on how the environment is configured, the
path to the models should looks something like:

```
~/miniconda3/envs/midigen-env/midigen/models
```

To run a crserver with a default model use one of those paths, e.g.

``` bash
source activate midigen-env
crserver ~/miniconda3/envs/midigen-env/midigen/models/guitar
```

Interact directly with the crserver by POSTing the contents of a midi file,
the reply will be the contents of a new response midi file. This can be
done with curl as follows:
``` bash
curl --data-binary "@example_call.mid" http://localhost:5000/tfgen > ~/example_response.mid
```


### interface
To do live generation, start an interface which interacts with max.
The URL argument is the one the crserver is set up to listen at

``` 
source activate midigen-env
interface http://127.0.0.1:5000/tfgen
```

Open the max panel which should be installed to
```
.../miniconda3/envs/midigen-env/midigen/max/midigen.maxpat
```
You may need to select your input source on the panel

Open the ableton project which should be installed to:
```
.../miniconda3/envs/midigen-env/midigen/ableton/midigen.als
```



### training
To generate a model of your own data, start a training and watch it for a long time.

create a directory for the trained model and checkpoint files : **TRAINING_OUT**

pull all your data or our dataset into a reasonable place : **TRAINING_DATA/BASS**

create a encoder.json (or use one for our \models) for all the training parameters: **TRAINING_DATA/BASS/encoder.json**

```
{"allowed_pitches": [27, 29, 31, 32, 34, 36, 38, 39, 41, 43, 44, 46, 48, 51, 53, 55, 56, 58, 63, 72, 74, 68, 60, 62, 54, 65, 79, 75, 54, 67, 64, 69, 70, 79], "time_resolution": 8, "num_bars": 4, "bar_time": 2, "encoder_type": "MelodyEncoder"}
```


kick-off a training like so, if you've used the paths above:


```
train_crmodel TRAINING_DATA/BASS/  TRAINING_OUT/ TRAINING_DATA/BASS/encoder.json --hidden_code_size 50 --max_response_length 64 --float_type float32 --batch_size 247 --validation_ratio 0.05 --gradient_clip 5 --learning_rate 1e-3 --keep_prob 1 --seed 1
```

#### tensorboard
To view tensorboard graphs, run the following command and point to the training_out folder:

```
tensorboard --logdir=path/to/TRAINING_OUT/
```

Then go to ```localhost:6006``` in a web browser

### generate


there is a process for generating early results during training. the generate scripts points to your **TRAINING_OUT** .  you'll need to ctrl-c out of your train_crmodel. this will trigger some checkout files and a put the best model into **TRAINING_OUT/inference_builder**

```
generate TRAINING_OUT/dataset.p TRAINING_OUT/inference_builder TRAINING_OUT
```





### Release process

 - merge changes into master
 - update the version number in package.py!!!!!!
 - push changes to origin
 - tag the release under github 'releases' tab and build/upload distribution wheel

#### building distribution wheel
```
source activate midigen-env
cd /path/to/midigen
python setup.py bdist_wheel
```

The wheel file should be output to:

```
/path/to/midigen/dist/midigen-VERSION-py3-none-any.whl
```

To install the wheel on a target system see
'upgrade installation section above'

## Docker

### building docker container

```
cd /path/to/ai-midigen
docker build -f docker/cpu/Dockerfile . -t midigen
```

### using docker container

#### running a training job

```
docker run -it --rm\
    -v $HOME"/ai_music:/shared" \
    -e ASUSER=`id -u` \
    midigen \
    'train_crmodel \
        /shared/data/4bar_bass_rock \
        /shared/training/4bar_bass_6 \
        /shared/data/4bar_bass_rock/encoder.json \
        --hidden_code_size 50 \
        --max_response_length 64 \
        --float_type float32 \
        --batch_size 490 \
        --validation_ratio 0.05 \
        --gradient_clip 5 \
        --learning_rate 1e-3 \
        --keep_prob 1 \
        --seed 1'
```

#### running tensorboard

```
docker run -it -v /path/to/logdir:/shared -p 6006:6006 midigen tensorboard --logdir /shared --host 0.0.0.0
```

then navigate to localhost:6006 with a browser on the host
