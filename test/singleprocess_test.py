from time import sleep
import numpy as np
import os

import allogger

import logging
logging.basicConfig(level=logging.INFO)

def main():
    allogger.basic_configure(logdir='/tmp/allogger/singleprocess', default_outputs=['tensorboard'], hdf_writer_params=dict(
        min_time_diff_btw_disc_writes=10, precision=2,
    ), debug=True, default_path_exists='ask')
    allogger.utils.report_env(to_stdout=True)
    logger = allogger.get_logger(scope='main')

    start = 0
    if os.path.exists('/tmp/allogger/singleprocess/checkpoint.npy'):
        start, step_per_key = np.load('/tmp/allogger/singleprocess/checkpoint.npy', allow_pickle=True)
        allogger.get_logger('root').step_per_key = allogger.get_logger('root').manager.dict(step_per_key)
        print(f'Resuming from step {start}')

    for step in range(start, start+10):
        logger.log(step, 'value')
        logger.info(f'We are in step {step}')

    logger.log(np.random.rand(1, 5, 5), 'blub')
    logger.log(np.random.rand(1, 5, 5), 'blub')

    logger.log(np.random.rand(10), 'array', data_type='array')
    logger.log(np.random.rand(10), 'array', data_type='array')

    np.save(os.path.join(allogger.get_logger('root').logdir, 'checkpoint'), (step+1, dict(allogger.get_logger('root').step_per_key)))

    allogger.close()

if __name__ == '__main__':
    main()