from pandas import HDFStore, read_hdf, concat
from glob import glob
import os

def list_keys(path):
    file = sorted(glob(os.path.join(path, '*.h5')))[0]
    with HDFStore(file) as hdf:
        keys = hdf.keys()

        scalars = [k for k in keys if k.startswith('/scalar')]
        histograms = [k for k in keys if k.startswith('/histrogram')]
        images = [k for k in keys if k.startswith('/images')]

        print('Scalars:')
        print('\t' + '\n\t'.join(scalars))
        print('Histograms')
        print('\t' + '\n\t'.join(histograms))
        print('Images')
        print('\t' + '\n\t'.join(images))

def read_from_key(path, key):
    datas = []
    for file in sorted(glob(os.path.join(path, '*.h5'))):
        data = read_hdf(file, key)
        print(f'Extracting {key} from {file}, index {data.index[0]} to {data.index[-1]}')
        datas.append(data)
    return concat(datas)