# Copyright 1998-2003 Daniel Robbins, Gentoo Technologies, Inc.
# Distributed under the GNU Public License v2
# $Header: /cvsroot/abeni/abeni/Attic/nulloutput.py,v 1.1 2003/07/31 14:40:00 robc Exp $

import os,sys

havecolor=1
dotitles=1

codes={}
codes["reset"]=""
codes["bold"]=""

codes["teal"]=""
codes["turquoise"]=""

codes["fuscia"]=""
codes["purple"]=""

codes["blue"]=""
codes["darkblue"]=""

codes["green"]=""
codes["darkgreen"]=""

codes["yellow"]=""
codes["brown"]=""

codes["red"]=""
codes["darkred"]=""

def xtermTitle(mystr):
    pass
    """
	if havecolor and dotitles and os.environ.has_key("TERM"):
		myt=os.environ["TERM"]
		if myt in ["xterm","Eterm","aterm","rxvt"]:
			sys.stderr.write("\x1b]1;\x07\x1b]2;"+str(mystr)+"\x07")
			sys.stderr.flush()
    """

def xtermTitleReset():
    """
	if havecolor and dotitles and os.environ.has_key("TERM"):
		myt=os.environ["TERM"]
		xtermTitle(os.environ["TERM"])
    """
    pass

def notitles():
	"turn off title setting"
	dotitles=0

def nocolor():
	"turn off colorization"
	havecolor=0
	for x in codes.keys():
		codes[x]=""

def resetColor():
	return codes["reset"]

def ctext(color,text):
	return codes[ctext]+text+codes["reset"]

def bold(text):
	return codes["bold"]+text+codes["reset"]
def white(text):
	return bold(text)

def teal(text):
	return codes["teal"]+text+codes["reset"]
def turquoise(text):
	return codes["turquoise"]+text+codes["reset"]
def darkteal(text):
	return turquoise(text)

def fuscia(text):
	return codes["fuscia"]+text+codes["reset"]
def purple(text):
	return codes["purple"]+text+codes["reset"]

def blue(text):
	return codes["blue"]+text+codes["reset"]
def darkblue(text):
	return codes["darkblue"]+text+codes["reset"]

def green(text):
	return codes["green"]+text+codes["reset"]
def darkgreen(text):
	return codes["darkgreen"]+text+codes["reset"]

def yellow(text):
	return codes["yellow"]+text+codes["reset"]
def brown(text):
	return codes["brown"]+text+codes["reset"]
def darkyellow(text):
	return brown(text)

def red(text):
	return codes["red"]+text+codes["reset"]
def darkred(text):
	return codes["darkred"]+text+codes["reset"]
