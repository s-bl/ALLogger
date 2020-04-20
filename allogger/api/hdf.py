from pandas import HDFStore, read_hdf

def list_keys(file):
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

def read_from_key(file, key):
    return read_hdf(file, key)