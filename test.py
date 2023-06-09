import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pathlib import Path
import pyedflib

DATA_PATH = Path('/Volumes/Ultra Touch/Data/mice_cholinesterase/physostigmine')
SEG_PATH = Path('/Volumes/Ultra Touch/MOUSE/mouse_list.csv')

SAMPFREQ = 2000
DOWN_SAMPFREQ = 500
PROMINENCE = 0.03
WLEN = 2
MIN_CYCLE = 0.1
MAX_CYCLE = 0.3 
TRAINING_SIZE = 30 
INTERVAL = 60 
N_IN_CLUSTER = 5
N_OUT_CLUSTER = 5 
IN_D = 0.2
OUT_D =0.2
N_ITER = 10
MAX_WARPING = 0.06
QUNATILE = 0.95
NJOBS =1
VERBOSE= True

fct = lambda x: (np.array([int(t) for t in x.split(':')]) @ np.array([3600,60,1]).reshape(-1,1))[0]*SAMPFREQ

df = pd.read_csv(SEG_PATH, delimiter=';',index_col=0).reset_index(drop=True)
df = df.dropna()
df['before_start'] =  df['before_start'].apply(fct)
df['before_end'] =  df['before_end'].apply(fct)
df['after_start'] =  df['after_start'].apply(fct)
df['after_end'] =  df['after_end'].apply(fct)

def get_data(path): 
    f = pyedflib.EdfReader(str(path))
    sig = -f.readSignal(1)
    return sig.astype('float')

lst = []
for line in df.values:
    data = get_data(DATA_PATH/line[0])
    data1 = data[line[4]:line[5]]
    lst.append(data1)
    data2 = data[line[2]:line[3]]
    lst.append(data2)

arr = np.array(lst,dtype=object)

from tools.pipeline import Pipeline
pipe = Pipeline(SAMPFREQ,PROMINENCE,WLEN,MIN_CYCLE,MAX_CYCLE,TRAINING_SIZE,INTERVAL,N_IN_CLUSTER,IN_D,N_OUT_CLUSTER,OUT_D,DOWN_SAMPFREQ,MAX_WARPING,N_ITER,QUNATILE,NJOBS,VERBOSE)
pipe.fit(arr)

for pred in pipe.predictions_: 
    print(pred.shape)