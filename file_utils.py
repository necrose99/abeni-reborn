"""Contains help functions for file browser tabs"""

import wx

def beautify_size(size):
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
	item = list.GetItem(index, col)
	return item.GetText()

def get_selected(list):
	selected = [ ]
	item = -1
	while 1:
		item = list.GetNextItem(item, wx.LIST_NEXT_ALL,
		                               wx.LIST_STATE_SELECTED)
		if item == -1:
			break
		selected.append(item)
	return selected
