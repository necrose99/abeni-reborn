"""Contains help functions for file browser tabs"""


# Most of this code was taken from ftpcube by
# Michael Gilfix <mgilfix@eecs.tufts.edu>
# but was also modified for Abeni by
# Rob Cakebread <pythonhead@gentoo.org>
# Copyright (C) 2002 Michael Gilfix


import wx

def beautify_size(size):
	"""Change raw length to g/m/kbytes"""
	if size / 1073741824:
		return ("%(sz)0.2f Gbytes") %{ 'sz' : (float(size) / 1073741824.0) }
	elif size / 1048576:
		return ("%(sz)0.2f Mbytes") %{ 'sz' : (float(size) / 1048576.0) }
	elif size / 1024:
		return ("%(sz)0.2f KBytes") %{ 'sz' : (float(size) / 1024.0) }
	else:
		return ("%(sz)s Bytes") %{ 'sz' : size }
	return None

def get_column_text(list, index, col):
	"""Return text for given column index"""
	item = list.GetItem(index, col)
	return item.GetText()

def get_selected(list):
	"""Return all selected items"""
	selected = [ ]
	item = -1
	while 1:
		item = list.GetNextItem(item, wx.LIST_NEXT_ALL,
		                               wx.LIST_STATE_SELECTED)
		if item == -1:
			break
		selected.append(item)
	return selected
