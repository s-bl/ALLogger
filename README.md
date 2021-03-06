# ALLogger

## Description

## Usage

Initialize root logger at the beginning of your script

```
import allogger

alloger.basic_configure(logdir=logdir, default_outputs=list_of_valid_outputs)
```

Valid outputs can be listed with

`allogger.vallid_outputs`

Create a new logger (or retriev an already existing logger) with

```
allogger.get_logger(scope='main')
```

If `logdir` is passed to `get_logger` a separate logdir gets created for this particular logger.
Arguments not passed to `get_logger` get inherited from the parent logger, where the hierarchy is specified by a dot separated list of scopes.
The `root` logger is the root node of that hierarchy. For instance, the logger created above has scope `root.main`.

Close the logger at the end of your script with

```
allogger.close()
```

to ensure that all data is written to disc.

If you use `tensorboard` as default output, data is also written to a `.h5` file for faster loading during postprocessing.
This behaviour can be suppressed by passing

```
tensorboard_writer_params={'use_hdf_hook': False}
```

to `basic_configure` or `get_logger`.

To log data use

```
logger.log(value, key)
```

### Logfile and console output

To log messages to a logfile (located in ``logdir``) use

```
logger.info(message)
```

To also print the massage to the console, use

```
logger.info(message)
```

### Filtering

In principle, you can spam your code with `logger.log(...)` statements and afterwards use a filtering mechanism based on regex to only log
what you actually care about. To do that, e.g. pass

```
hdf_writer_params={'filter': '.*loss.*'}
```

to `basic_configure` or `get_logger`.

### Log environment state

To log the environment state (hostname, user, git meta data) use

```
allogger.utils.report_env()
```

## API for reading the data

### HDF

To list all keys present in a `.h5` file, use

```
allogger.api.hdf.list_keys(hdf_log_directory)
```

To load a particular key from a `.h5` file, use

```
allogger.api.hdf.read_from_key(hdf_log_directory, key)
```

## Multiprocessing

See `test/multiprocessing_test.py`.

Make sure that each subprocess that creates a logger with a custom logdir calls

```
allogger.close()
```

to ensure that all data of every subprocess is written to disc.

## Custom writers

Custom writers can be implemented in writers. Contributions are welcome.

## Changelog

0.2.4 -> 0.2.5

- Reimplemented hdfwriter

0.2.3 -> 0.2.4

- Enable/Disable logger globally

0.2.2 -> 0.2.3

- Report logdir in utils.report_env
- Set precision in hdf writer for image and array data
- Warn user about large file sizes if storing arrays or images

0.2.1 -> 0.2.2

- Handle existing logdir

0.2.0 -> 0.2.1

- Added debug flag
- Implemented logging of arbitrary shaped arrays to hdf file

0.1.0 -> 0.2.0

- Implemented logging of images. Images need to be in the CHW format.
- Changed filename from hostname_timestamp to timestamp_hostname for correct ordering
- Automatic concatenation of multiple event files

## Todo

- Implement more writers (csv, etc.)