#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Based on votl_maketags.pl
#   Copyright (C) 2001-2003, 2011 by Steve Litt (slitt@troubleshooters.com)
#   This script is
#   Copyright (C) 2015 Matěj Cepl <mcepl@cepl.eu>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, see <http://www.gnu.org/licenses/>.
from __future__ import print_function, unicode_literals

import argparse
import os.path
import re


TAGFILENAME = os.path.expanduser("~/.vim/vimoutliner/vo_tags.tag")
TAGFILENAME_fh = None

TAG_RE = re.compile(r'''
^\s*(?P<tagname>_tag_\S+).*
    \n # and on the next line
    ^\s*(?P<filename>.*)
''', re.VERBOSE | re.MULTILINE)

# HashRef containing a map from a filename to its tag names
# { filename => { tagname => filename } }
files_to_tags = {}
# list of all the files left to process
process_queue = []

def append_tags_to_tagfile(tags):
    global TAGFILENAME_fh
    for tag in tags:
        print("{0}\t{1}\t:1".format(tag, tags[tag]), file=TAGFILENAME_fh)

def process_file(filename):
    f = os.path.abspath(filename)
    f_contents = open(f, 'r').read()
    f_tags = {}

    for match in TAG_RE.finditer(f_contents):
        f_tags[match.group('tagname')] = \
            match.group('filename')

    return f_tags

def create_and_process(filename):
    global files_to_tags, process_queue
    filename = os.path.abspath(filename)

    if filename in files_to_tags:
        return

    basedir = os.path.dirname(filename)

    if not os.path.exists(filename):
        os.makedirs(basedir)
        open(filename, 'w')
        files_to_tags[filename] = {}
    else:
        results = process_file(filename)
        for tag in results:
            results[tag] = os.path.abspath(os.path.join(basedir, results[tag]))
        process_queue.extend(results.values())

        append_tags_to_tagfile(results)

        # let's store all the tags (useful for debugging)
        files_to_tags[filename] = results


def sort_and_dedupe_tagfile():
    global TAGFILENAME
    sorted_set = sorted(set(open(TAGFILENAME, 'r').readlines()))
    with open(TAGFILENAME, 'w') as tagfile:
        tagfile.writelines(sorted_set)

def main():
    global TAGFILENAME_fh, TAGFILENAME, process_queue
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs="+",
                        help='directories with data')
    args = parser.parse_args()
    process_queue = args.files

    TAGFILENAME_fh = open(TAGFILENAME, 'a')

    for otl_file in process_queue:
        create_and_process(otl_file)

    TAGFILENAME_fh.close()
    sort_and_dedupe_tagfile()


if __name__ == '__main__':
    main()
