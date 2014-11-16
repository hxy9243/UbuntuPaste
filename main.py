#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Main script, parse args and send request
#
# Author: Kevin Hu


import os
import sys
import yaml
import glob
from optparse import OptionParser

from urlrequest import RequestURL


# parse argument
def parseargs():
    """
    parse argument, and return config
    param: list of argv except executable name
    return: config table containing
        typename -t
        open browser -b
    """
    usage = "Usage: <up> [OPTION]... FILENAME..."
    parser = OptionParser(usage = usage)

    # Add typename option
    parser.add_option("-t", "--type",
                      dest="type", help="specify type of target file")

    # Add open browser option
    parser.add_option("-b", "--browser",
                      action="store_true", dest="browser",
                      help="open response url in browser")

    return parser


# Find type of the file
def findtype(filename, suffix_match):
    """
    param: filename
    return: type string
    """
    if (filename.lower().startswith("makefile")):
        return "make"

    if (filename.lower() == "cmakelist.txt"):
        return "cmake"

    fs = filename.split(".")
    if len(fs) == 1:
        return "text"

    suffix = (fs[-1]).lower()

    if suffix not in suffix_match.keys():
        return "text"

    return suffix_match[suffix]


# The main function
def main():
    """
    The main function
    """
    # read options and args
    parser = parseargs()
    (options, args) = parser.parse_args()
    if (args == []):
        parser.print_help()
        exit()

    filetype = None
    if options.type:
        filetype = options.type

    # open and read in all files
    config = yaml.load(open('config.yml'))
    totalsize = 0
    allfiles = []
    MAX_SIZE = int( config['TOTALSIZE'] )
    for f in args:
        for g in glob.iglob(f):
            try:
                allfiles.append( open(g, "r").read() )
                totalsize += os.stat(g).st_size

                # protector for file size
                if totalsize > MAX_SIZE:
                    print("Over size limit, please send one at a time")
                    exit()

                # protector for different file type
                if not filetype:
                    filetype = findtype(g, config["SUFFIX"])

            except Exception as e:
                print(e)
                print("Error opening file")
        # protector if overall size too large

    print(allfiles)
    print(filetype)
    print(totalsize)

    # send the request
    content = {"poster": os.environ["USER"],
               "syntax": filetype,
               "content": ('\n' * 8).join(allfiles)}

    print content

    req = RequestURL(content)
    resp = req.send()

    print(resp.url)

    

# run main function
main()