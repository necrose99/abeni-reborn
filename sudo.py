#!/usr/bin/python

""" 
sudo.py

    execute args with sudo
    This will allow us to log all sudo stuff easier

"""

import sys
import commands

__revision__ = "$Id: sudo.py,v 1.3 2004/12/26 03:24:57 robc Exp $"

def cmd(args):
    """Execute command via sudo"""
    (status, output) = commands.getstatusoutput("/usr/bin/sudo %s" % args)
    return (status, output)

if __name__ == "__main__":
    """Main"""
    if len(sys.argv) < 2:
        sys.exit()
    args = ' '.join(sys.argv[1:])

