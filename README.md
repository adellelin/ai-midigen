# midigen

## fresh installation

1) install anaconda 2 from https://www.anaconda.com/download/

2) acquire wheel file from github releases

3) create conda environment and install library.
    This command assumes you are on macos - replace the tensorflow
    wheel path on different environments

``` bash
conda create -n midigen-env python=2.7
source activate midigen-env
pip install https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.4.0-py2-none-any.whl
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
installed at

```
~/anaconda/envs/midigen-env/midigen/models
```

To run a crserver with a default model use one of those paths, e.g.

``` bash
source activate midigen-env
crserver ~/anaconda/envs/midigen-env/midigen/models/guitar
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

``` bash
source activate midigen-env
interface http://127.0.0.1:5000/tfgen
```

Open the max panel which should be installed to
```
.../anaconda/envs/midigen-env/midigen/max/midigen.maxpat
```
You may need to select your input source on the panel

Open the ableton project which should be installed to:
```
.../anaconda/envs/midigen-env/midigen/ableton/midigen.als
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
/path/to/midigen/dist/midigen-VERSION-py2-none-any.whl
```

To install the wheel on a target system see
'upgrade installation section above'
