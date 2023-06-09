from zipfile import ZipFile
import numpy as np
import pandas as pd
import pyedflib
import json as json

def from_zip_dataset_to_numpy(zp:ZipFile)->np.ndarray:
    """Take a dataset

    Args:
        zp (ZipFile): dataset as a zip object

    Raises:
        ValueError: Not a 1D signal 
        ValueError: One signal cannot be read

    Returns:
        np.ndarray: dataset as a np.ndarray
    """

    #Select filename with the right extention and take out the mac extension
    extension_lst = ['.txt','.csv','.EDF']
    mac_sub_dir = "__MACOSX"
    file_to_check = [filename for filename in zp.namelist() if filename[-4:] in extension_lst ]
    file_to_check = [filename for filename in file_to_check if mac_sub_dir not in filename]
    #sort in alphabetic order
    file_to_check.sort()

    if not file_to_check:
        raise ValueError

    #Extract signals 
    lst =[]
    for filename in file_to_check: 
        try:
            if filename[-4:] == '.EDF': 
                signal = pyedflib.EdfReader(zp.extract(filename)).readSignal(0).reshape(-1)
                lst.append(signal)
            else: 
                signal = pd.read_csv(zp.extract(filename),header=None).values
                if signal.ndim == 2: 
                    signal = signal.reshape(-1)
                    lst.append(signal)
                else:
                    raise ValueError
        except:
            raise ValueError
    
    return np.array(lst, dtype=object)

def from_labels_to_dataframe(file:str)->pd.DataFrame:
    """transform a load txt to a dataframe

    Args:
        file (str): txt or csv file

    Returns:
        pd.DataFrame: labels as pandas dataframe
    """
    df = pd.read_csv(file, header=0)
    return df


