from multiprocessing import Process
from time import sleep
import numpy as np

import allogger

def worker_process(id):
    logger = allogger.get_logger(f'process_{id}')

    for i in range(10):
        logger.log(i, 'value')
        sleep(np.random.uniform(1, 5))

    allogger.close()

def main():
    allogger.basic_configure('/tmp/allogger/multiprocessing', ['tensorboard'])
    logger = allogger.get_logger('main')

    workers = []
    for i in range(10):
        worker = Process(target=worker_process,
                                         args=(i,))
        workers.append(worker)
        worker.start()
    for w in workers:
        w.join()

    allogger.close()

if __name__ == '__main__':
    main()