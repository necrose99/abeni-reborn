import wx

def beautifySize (size):
	if size / 1073741824:
		return ("%(sz)0.2f Gbytes") %{ 'sz' : (float (size) / 1073741824.0) }
	elif size / 1048576:
		return ("%(sz)0.2f Mbytes") %{ 'sz' : (float (size) / 1048576.0) }
	elif size / 1024:
		return ("%(sz)0.2f KBytes") %{ 'sz' : (float (size) / 1024.0) }
	else:
		return ("%(sz)s Bytes") %{ 'sz' : size }
	return None

def AddLineSeparator (toolbar, height):
	space = wx.StaticText (toolbar, -1, "")
	space.SetSize ((3, -1))
	toolbar.AddControl (space)
	line = wx.StaticLine (toolbar, -1, style=wx.LI_VERTICAL)
	line.SetSize ((-1, height))
	toolbar.AddControl (line)
	space = wx.StaticText (toolbar, -1, "")
	space.SetSize ((4, -1))
	toolbar.AddControl (space)

def getColumnText (list, index, col):
	item = list.GetItem (index, col)
	return item.GetText ()

def getSelected (list):
	selected = [ ]
	item = -1
	while 1:
		item = list.GetNextItem (item, wx.LIST_NEXT_ALL,
		                               wx.LIST_STATE_SELECTED)
		if item == -1:
			break
		selected.append (item)
	return selected

def setListColumnAlignment (list, col, align):
	item_info = list.GetColumn (col)
	item_info.SetAlign (align)
	list.SetColumn (col, item_info)

def colorToTuple (color):
	return (color.Red (), color.Green (), color.Blue ())
