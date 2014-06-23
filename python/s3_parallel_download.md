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
    2014-06-23 11:45:06,896 - __main__ - DEBUG -  19%   6%  13%   6%   6%  13%  27%
    2014-06-23 11:45:16,896 - __main__ - DEBUG -  52%  26%  26%  26%  39%  26%  68%
    2014-06-23 11:45:26,897 - __main__ - DEBUG -  85%  32%  52%  39%  52%  45% 100%
    2014-06-23 11:45:36,897 - __main__ - DEBUG - 100%  78%  78%  59%  65%  65% 100%
    2014-06-23 11:45:46,897 - __main__ - DEBUG - 100% 100% 100%  78%  91%  91% 100%
    Downloaded: /var/folders/qk/t5991kt11cb2y6qgmzrzm_g00000gp/T/tmpU7pL8I
