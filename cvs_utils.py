#!/usr/bin/python

"""

Functions for accessing local CVS repository

Note:
We don't do too much in the way of error checking, as repoman
should catch most errors.

"""

import os


def get_entries(cvs_dir):
    """Open CVS/Entries, return list"""
    if not os.path.exists(cvs_dir):
        print "No CVS dir"
        return

    entries_file = os.path.join(cvs_dir, "CVS/Entries")

    if not os.path.exists(entries_file):
        print "No CVS/Entries"
        return

    try:
        raw_entries = open(entries_file, "r").readlines()
    except:
        print "!!! File read error %s" % entries_file

    return raw_entries 

def format_entries(raw_entries):
    """Pretty up entries from list of CVS/Entries file"""
    entry_indx = 0
    formatted_entries = []
    for entry in raw_entries:
        #Skip directories
        if entry[0] == "D":
            continue
        entry_indx += 1
        end_pos = entry.find("/", 2)
        formatted_entries.append(entry[1:end_pos])
    return formatted_entries

def get_files(root_dir):
    """Get list of files in dir"""
    if not os.path.exists(root_dir):
        print "!!! %s does not exist." % root_dir
        return -1
    my_files = os.listdir(root_dir)
    return my_files

def __query_non_added(cvs_entries, my_files):
    """Return a list of files not in CVS"""
    non_cvs = []

    for test_file in my_files:
        if test_file == "CVS" or test_file == "files":
            continue
        if test_file not in cvs_entries:
            non_cvs.append(test_file)

    return non_cvs

def get_non_added(cvs_dir):
    """Return a list of files non in CVS"""
    raw = get_entries(cvs_dir)
    cvs_files = format_entries(raw)
    my_files = get_files(cvs_dir)
    return __query_non_added(cvs_files, my_files)

if __name__ == "__main__":
    cvs_dir = "/tmp2/cvs/gentoo-x86/dev-python/wxpython-demo/"
    if os.path.exists(cvs_dir):
        print get_non_added(cvs_dir)
