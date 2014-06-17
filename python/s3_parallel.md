Summary
-------

A parallel S3 uploader using greenlets (gevent).


Usage
-----

Use it as a module or run it as a command. It'll determine whether to do a 
standard upload or multipart upload based on filesize (if larger than 30M). The
default chunk-size is 20M (it must be at least 5M for S3).

Progress will be written to the log. By default, this will be displayed to the 
console if run as a command.


Examples
--------

This upload was performed with a 130M file.

    $ python s3_parallel.py (access key) (secret key) (bucket name) (file-path)
    2014-06-17 10:16:48,458 - __main__ - DEBUG -   0%    0%    0%    0%    0%    0%    0% 
    2014-06-17 10:16:58,459 - __main__ - DEBUG -   3%    3%    2%    2%    2%    1%    7% 
    2014-06-17 10:17:08,460 - __main__ - DEBUG -   6%    5%    5%    4%    5%    4%   14% 
    2014-06-17 10:17:18,461 - __main__ - DEBUG -  10%    7%    8%    8%    7%    6%   18% 
    2014-06-17 10:17:28,461 - __main__ - DEBUG -  16%   10%   13%   11%   10%    8%   26% 
    2014-06-17 10:17:38,462 - __main__ - DEBUG -  21%   14%   20%   15%   14%   12%   35% 
    2014-06-17 10:17:48,462 - __main__ - DEBUG -  26%   17%   27%   19%   19%   15%   48% 
    2014-06-17 10:17:58,463 - __main__ - DEBUG -  32%   20%   33%   24%   24%   18%   59% 
    2014-06-17 10:18:08,463 - __main__ - DEBUG -  37%   24%   39%   29%   28%   22%   70% 
    2014-06-17 10:18:18,464 - __main__ - DEBUG -  43%   28%   44%   34%   32%   26%   82% 
    2014-06-17 10:18:28,464 - __main__ - DEBUG -  48%   31%   50%   39%   36%   31%   91% 
    2014-06-17 10:18:38,465 - __main__ - DEBUG -  52%   35%   55%   44%   43%   36%  100% 
    2014-06-17 10:18:48,465 - __main__ - DEBUG -  60%   39%   63%   47%   47%   40%  100% 
    2014-06-17 10:18:58,466 - __main__ - DEBUG -  68%   44%   69%   53%   53%   45%  100% 
    2014-06-17 10:19:08,466 - __main__ - DEBUG -  77%   49%   75%   58%   57%   49%  100% 
    2014-06-17 10:19:18,467 - __main__ - DEBUG -  83%   54%   84%   65%   62%   52%  100% 
    2014-06-17 10:19:28,467 - __main__ - DEBUG -  88%   58%   90%   71%   69%   58%  100% 
    2014-06-17 10:19:38,468 - __main__ - DEBUG -  96%   61%   96%   77%   74%   63%  100% 
    2014-06-17 10:19:48,468 - __main__ - DEBUG - 100%   67%  100%   83%   83%   70%  100% 
    2014-06-17 10:19:58,469 - __main__ - DEBUG - 100%   73%  100%   93%   93%   76%  100% 
    2014-06-17 10:20:08,469 - __main__ - DEBUG - 100%   83%  100%  100%  100%   86%  100% 
    2014-06-17 10:20:18,470 - __main__ - DEBUG - 100%   95%  100%  100%  100%  100%  100% 
