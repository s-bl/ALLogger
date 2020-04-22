from time import sleep
import numpy as np
import os

import allogger

def main():
    allogger.basic_configure('/tmp/allogger/singleprocess', ['tensorboard'])
    logger = allogger.get_logger(scope='main')

    start = 0
    if os.path.exists('/tmp/allogger/singleprocess/checkpoint.npy'):
        start, step_per_key = np.load('/tmp/allogger/singleprocess/checkpoint.npy', allow_pickle=True)
        allogger.get_logger('root').step_per_key = allogger.get_logger('root').manager.dict(step_per_key)
        print(f'Resuming from step {start}')

    for step in range(start, start+10):
        logger.log(step, 'value')
        sleep(np.random.uniform(1, 5))

    np.save(os.path.join(allogger.get_logger('root').logdir, 'checkpoint'), (step+1, dict(allogger.get_logger('root').step_per_key)))

    allogger.close()

if __name__ == '__main__':
    main()