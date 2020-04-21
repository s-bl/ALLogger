from multiprocessing import Process, current_process
from time import sleep
import numpy as np

import allogger

def worker_process(id):
    if id % 2 == 0:
        logger = allogger.get_logger(f'worker')
    else:
        logger = allogger.get_logger(scope=f'worker', logdir=f'/tmp/allogger/multiprocessing/{current_process().name}')

    for i in range(10):
        logger.log(i, 'value')
        sleep(np.random.uniform(1, 5))

    if id % 2 != 0:
        allogger.close()

def main():
    allogger.basic_configure('/tmp/allogger/multiprocessing', ['tensorboard'])
    logger = allogger.get_logger('main')

    for i in range(10):
        logger.log(i, 'value')
        sleep(np.random.uniform(1, 5))

    workers = []
    for i in range(20):
        worker = Process(target=worker_process,
                                         args=(i,))
        workers.append(worker)
        worker.start()
    for w in workers:
        w.join()

    allogger.close()

if __name__ == '__main__':
    main()