#!/usr/bin/env python
#
# { ssld-extract.py }
# Copyright (C) 2012 Alex Kozadaev [akozadaev at yahoo com]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.#

import sys, signal

# TODO: I am new to python so I reckon the code needs optimisation and refactoring
#=============================================================
conf = { 'ports': set(), 'conns': set() }
version = '0.11'

#=============================================================
def parse(infile):
    needclose = False
    inside = False

    if infile == '-':
        fh = sys.stdin
    else:
        try:
            fh = open(infile, 'r')
        except IOError:
            die("cannot open file {0}".format(infile))
        needclose = True

    # main logic here
    for line in fh: 
        if line[:3] == 'New':
            try:
                port = line[ line.index('(')+1 : line.index(')') ]
                conn = line[ line.index('#')+1 : line.index(':') ]
            except ValueError:
                warn("cannot parse connection record")
                next

            if ((conn.isdigit() and int(conn) in conf['conns']) or 
                (port.isdigit() and int(port) in conf['ports'])):
                print line,
                conf['conns'].add(int(conn))
                inside = True
        elif line[0].isspace():
            if inside: print line,
        elif line[0].isdigit():
            try:
                val = line[: line.index(' ') ]
            except ValueError:
                warn("cannot parse connection number")
                inside = False
                next

            if val.isdigit() and (int(val) in conf['conns']):
                print line,
                inside = True
            else:
                inside = False

    if needclose:
        fh.close()

#=============================================================
def readargs():
    infile = None
    if (len(sys.argv) == 1): usage()
    program = sys.argv.pop(0)
    for val in sys.argv:
            if val == '-p':
                newval = sys.argv.pop(1)
                readvalues(newval, 'ports')
            elif val == '-n':
                newval = sys.argv.pop(1)
                readvalues(newval, 'conns')
            elif val == '-h':
                usage()
                exit()
            elif val == '-':
                infile = '-'
            elif val[0] == '-':
                die("bad argument {}".format(val))
            else:
                infile = val
    if infile == None:
        die("no source given")
    return infile

#=============================================================
def readvalues(values, cfgset):
    for p in values.split(','):
        if (p.isdigit()):
            conf[cfgset].add(int(p))
        else:
            die("Invalid format {}".format(p))

#=============================================================
def usage():
    print """ssld-extract (python-edition) v{} Alex Kozadaev(C)

    ssld-extact [-n x,y | -p n,m] [ssldump filename | - to read from pipe]

    Extract one or more connections from a SSL dump file.

        Usage:
            -n    comma separated list of connection numbers (no spaces allowed)
            -p    comma separated list of client port numbers (no spaces allowed)
            -h    this text

    Firstly python version was as twise as slower then the perl version. But after refactoring I 
    managed  to make it even faster. I tested both versions by parsing 173 megabyte ssldump file
    and python was ~0.7sec faster this time.
""".format(version)
    exit()

#=============================================================
def die(msg):
    print "ERROR: {}".format(msg)
    exit(1)

#=============================================================
def warn(msg):
    print "WARN: {}".format(msg)

def handler(signum, frame):
    print "\nexiting..."
    exit(1)

#==[ main ]===================================================
if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    parse(readargs())

# vim: set tabstop=4 softtabstop=4 shiftwidth=4 smarttab ai expandtab