# Copyright (c) 2013, Edd Barrett <edd@openbsd.org> <vext01@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import argparse

VERSION=0.1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--initdb", action='store_true',
            help="initialise the database")
    parser.add_argument("-s", "--subset", action='store_true',
            help="compute a subset")
    parser.add_argument("-i", "--include", nargs='*',
            help="include package in subset")
    parser.add_argument("-x", "--exclude", nargs='*',
            help="exclude package in subset")
    parser.add_argument("--version", action='store_true',
            help="show version")

    args = parser.parse_args()

    # No two of these should be enabled at once
    primary_tasks = [args.subset, args.version, args.initdb]
    chosen_tasks = [ x for x in primary_tasks if x ]

    if len(chosen_tasks) != 1:
        parser.error("please select a single primary task.\n  one of: --initdb, --subset, --version")

    if args.subset:
        import subset
        subset.compute_subset(args.include, args.exclude)
    elif args.initdb:
        import tlpdbparser
        tlpdbparser.initdb()
    elif args.version:
        print("TeXScythe Version %s" % (VERSION))
    else:
        assert False # should not happen
