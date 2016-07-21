#!/usr/bin/env python3.4

# TODO(dustin): Requires `tabulate`.

import sys
import os
import csv
import argparse
import tabulate

def _get_args():
    p = argparse.ArgumentParser()
    
    p.add_argument(
        '-d', '--delimiter', 
        help="Delimiter")
    
    p.add_argument(
        '-q', '--quote', 
        help="Quote character")
    
    p.add_argument(
        '-r', '--rows', 
        action="store_true",
        help="Row-oriented format")
    
    p.add_argument(
        '-H', '--headings', 
        help="Comma-separated list of heading names")
    
    p.add_argument(
        '-e', '--encapsulate-values', 
        action="store_true",
        help="Put square brackets around values (only in row-oriented format)")
    
    args = p.parse_args()
    return args

def _main():
    args = _get_args()

    if sys.stdin.isatty() is True:
        print("Please feed data into STDIN.")
        sys.exit(1)

    if args.headings is None:
        headings_raw = sys.stdin.readline()
    else:
        headings_raw = args.headings

    headings = [s.strip() for s in headings_raw.rstrip().split(',')]
    max_size = max([len(s) for s in headings])

    kwargs = {}
    
    if args.delimiter is not None:
        kwargs['delimiter'] = args.delimiter

    if args.quote is not None:
        kwargs['quotechar'] = args.quote

    dr = csv.reader(sys.stdin, *kwargs)
    records = list(dr)

    if args.rows is True:
        if args.encapsulate_values is True:
            format_string = '{:' + str(max_size) + '}: [{}]'
        else:
            format_string = '{:' + str(max_size) + '}: {}'

        for i, record in enumerate(records):
            print("#{}".format(i + 1))
            print('')

            data = dict(zip(headings, record))
            for heading in headings:
                print(format_string.format(heading, data[heading].strip()))

            print('')
    else:
        print(tabulate.tabulate(records, headers=headings))

if __name__ == '__main__':
    _main()
