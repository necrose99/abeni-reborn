#!/usr/bin/python

import sys
import commands


""" sudo module 

    execute args with sudo
    This will allow us to log all sudo stuff easier


"""

def cmd(args):
    (status, output) = commands.getstatusoutput("/usr/bin/sudo %s" % args)
    return (status, output)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit()
    args = ' '.join(sys.argv[1:])
