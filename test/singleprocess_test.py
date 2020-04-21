from time import sleep
import numpy as np

import allogger

def main():
    allogger.basic_configure('/tmp/allogger/multiprocessing', ['tensorboard'])
    logger = allogger.get_logger(scope='main')

    for i in range(10):
        logger.log(i, 'value')
        sleep(np.random.uniform(1, 5))

    allogger.close()

if __name__ == '__main__':
    main()