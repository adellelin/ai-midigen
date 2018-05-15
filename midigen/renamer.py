# Import the os module, for the os.walk function
import os
from os.path import abspath, join

data_dir = abspath('SD_04_Hard Rock_KD_SET 01')
count = 1

for dirName, subdirList, fileList in os.walk(data_dir):
    prev_encoding = None
    cur_cr = {}
    for fname in fileList:
        if fname.endswith('.mid'):
            name = (fname.split('_')[5])
            name = fname[:fname.index(name)]
            newname = name +str(count).zfill(2) +'.mid'
            count +=1
            #print(newname)
            full_path = join(dirName, fname)
            os.rename(full_path, join(dirName, newname))
