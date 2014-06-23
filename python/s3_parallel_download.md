Summary
-------

A parallel S3 *downloader* using greenlets (gevent).


Usage
-----

Use it as a module or run it as a command. It'll determine whether to do a 
standard download or multipart upload based on filesize (if larger than 30M). 
The default chunk-size is 20M.

Progress will be written to the log. By default, this will be displayed to the 
console if run as a command.


Examples
--------

This upload was performed with a 130M file.

    $ python s3_parallel_upload.py (access key) (secret key) (bucket name) (key name) (file-path)
    ...
    2014-06-23 11:31:47,981 - __main__ - DEBUG -   0%   6%  13%   6%   6%  13%  27%
    2014-06-23 11:31:57,981 - __main__ - DEBUG -  13%  13%  32%  19%  26%  19%  40%
    2014-06-23 11:32:07,982 - __main__ - DEBUG -  26%  26%  65%  39%  39%  52%  81%
    2014-06-23 11:32:17,982 - __main__ - DEBUG -  39%  52%  85%  65%  45%  65% 100%
    2014-06-23 11:32:27,982 - __main__ - DEBUG -  59%  72% 100%  85%  65%  85% 100%
    2014-06-23 11:32:37,983 - __main__ - DEBUG -  72% 100% 100% 100%  85% 100% 100%
    2014-06-23 11:32:47,983 - __main__ - DEBUG -  85% 100% 100% 100% 100% 100% 100%
