from pandas import HDFStore, read_hdf, concat
from glob import glob
import os
import numpy as np
from ast import literal_eval

def list_keys(path):
    file = sorted(glob(os.path.join(path, '*.h5')))[0]
    with HDFStore(file) as hdf:
        keys = hdf.keys()

        scalars = [k for k in keys if k.startswith('/scalar')]
        histograms = [k for k in keys if k.startswith('/histrogram')]
        images = [k for k in keys if k.startswith('/image')]
        arrays = [k for k in keys if k.startswith('/array')]

        print('Scalars:')
        print('\t' + '\n\t'.join(scalars))
        print('Histograms:')
        print('\t' + '\n\t'.join(histograms))
        print('Images:')
        print('\t' + '\n\t'.join(images))
        print('Arrays:')
        print('\t' + '\n\t'.join(arrays))

def read_from_key(path, key):
    datas = []

    for file in sorted(glob(os.path.join(path, '*.h5'))):
        data = read_hdf(file, key)
        print(f'Extracting {key} from {file}, index {data.index[0]} to {data.index[-1]}')
        datas.append(data)

    datas = concat(datas)

    if key.startswith('/image') or key.startswith('/array'):
        datas['value'] = datas['value'].apply(lambda x: np.asarray(literal_eval(x)))

    return datas