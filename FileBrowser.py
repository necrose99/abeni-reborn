"""

Most of this code was taken from ftpcube by
Michael Gilfix <mgilfix@eecs.tufts.edu>
but was also modified for Abeni by
Rob Cakebread <pythonhead@gentoo.org>

Copyright (C) 2002 Michael Gilfix


"""

import os
import re
import time

import wx

import file_utils
import icons.folder
import icons.link
import icons.file
import PermsDialog
import options

class AbstractFileWindow(wx.Panel):

    UNSORTED = 0
    SORT_BY_NAME = 1
    SORT_BY_SIZE = 2
    SORT_BY_DATE = 3
    idLIST = wx.NewId()
    hidden_re = re.compile("^\..*")

    def __init__(self, parent, headers):
        wx.Panel.__init__(self, parent, -1)

        self.list = wx.ListCtrl(self, self.idLIST, 
                                style=wx.LC_SINGLE_SEL | wx.LC_REPORT | wx.SUNKEN_BORDER)
        for i, name in zip(range (len(headers)), headers):
            self.list.InsertColumn(i, name)

        self.image_list = wx.ImageList(15, 17)
        self.folder_index = self.image_list.Add(icons.folder.getBitmap())
        self.link_index = self.image_list.Add(icons.link.getBitmap())
        self.file_index = self.image_list.Add(icons.file.getBitmap())
        self.list.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)

        # Set instance variables
        self.sorted = self.SORT_BY_NAME
        self.directories_first = 1
        self.dir = None

        # Set up the interactivity
        wx.EVT_LEFT_DCLICK(self.list, self.onDoubleClick)
        wx.EVT_RIGHT_DOWN(self.list, self.onRightClick)

    def selectBitmapIndex(self, flags):
        if not flags:
            return self.folder_index
        else:
            if flags[0] == 'l':
                return self.link_index
            elif flags[0] in  'd ':
                return self.folder_index
            else:
                return self.file_index

    def setDir(self, dir):
        self.dir = dir

    def getDir(self):
        return self.dir

    def onDoubleClick(self, event):
        raise NotImplementedError

    def onRightClick(self, event):
        raise NotImplementedError

    def updateListing(self, dir):
        raise NotImplementedError

    def unsorted(self, event=None):
        self.sorted = self.UNSORTED
        self.directories_first = 0
        self.updateListing('.')

    def sortByName(self, event=None):
        self.sorted = self.SORT_BY_NAME
        self.directories_first = 1
        self.updateListing('.')

    def clearList(self):
        if self.list:
            self.list.Freeze()
            self.list.DeleteAllItems()
            self.list.Thaw()

    def sortList(self, sequence):
        raise NotImplementedError

    def performSort(self, sequence):
        if self.sorted == self.SORT_BY_NAME:
            sequence.sort(lambda x, y: cmp(x[0], y[0]))
        elif self.sorted == self.SORT_BY_SIZE:
            sequence.sort(lambda x, y: cmp(long(x[4]), long(y[4])))
        elif self.sorted == self.SORT_BY_DATE:
            # Convert the times beforehand for speed
            try:
                converted = [(i, time.strptime(i[2], "%b %d %H:%M")) for i in sequence ]
            except Exception:
                return sequence
            converted.sort(lambda x, y: cmp(x[1], y[1]))
            sequence = [ i[0] for i in converted ]
        return sequence

    def getFileSize(self, file):
        index = self.list.FindItem(-1, file)
        return file_utils.get_column_text(self.list, index, 2)

class MyBrowser(AbstractFileWindow):

    """Generic file browser used in main Abeni window"""

    idPOPUP_UPLOAD  = wx.NewId()
    idPOPUP_RENAME  = wx.NewId()
    idPOPUP_DELETE  = wx.NewId()
    idPOPUP_CREATE  = wx.NewId()
    idPOPUP_CHMOD   = wx.NewId()
    idPOPUP_REFRESH = wx.NewId()

    time_re = re.compile('[A-Za-z]+\s+([A-Za-z]+\s+\d+\s+\d+:\d+):(\d+)\s+\d+')

    def __init__(self, parent):
        if __debug__:
            pass

        self.headers = [ "Filename", "Size", "Date", "Perms" ]
        AbstractFileWindow.__init__(self, parent, self.headers)

        # Set the headings sizes accordingly
        for i in range(len(self.headers)):
            self.list.SetColumnWidth(i, 100)
        # Explicitly make the filenames column bigger
        self.list.SetColumnWidth(0, 260)

    def populate(self, my_dir):
        if os.path.exists(my_dir):
            self.setDir(my_dir)
            self.last_listing = None
            self.updateListing(self.getDir())

    def onDoubleClick(self, event):
        item = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        if item != -1:
            selected = file_utils.get_column_text(self.list, item, 0)
            self.updateListing(selected)

    def onRightClick(self, event):
        menu = self.makePopupMenu()
        self.PopupMenu(menu, wx.Point(event.m_x, event.m_y))

    def makePopupMenu(self):
        # Create the popup menu
        menu = wx.Menu()
        menu.Append(self.idPOPUP_DELETE, "Delete Selected Files")
        menu.AppendSeparator()
        menu.Append(self.idPOPUP_CHMOD, "Change Permissions")
        menu.Append(self.idPOPUP_REFRESH, "Refresh Listing")
        menu.AppendSeparator()
        wx.EVT_MENU(self, self.idPOPUP_DELETE, self.onDelete)
        wx.EVT_MENU(self, self.idPOPUP_CHMOD, self.onChmod)
        wx.EVT_MENU(self, self.idPOPUP_REFRESH, self.onRefresh)
        return menu

    def getFilename(self):
        """Return full path to selected files"""
        selected = file_utils.get_selected(self.list)
        file = file_utils.get_column_text(self.list, selected[0], 0)
        return os.path.join(self.getDir(), file)

    def onDelete(self, event):
        """Delete selected files"""
        selected = file_utils.get_selected(self.list)
        for item in selected:
            file = file_utils.get_column_text(self.list, item, 0)
            type = self.last_listing[self.list.GetItemData(item)][3]
            path = os.path.join(self.getDir(), file)
            if type[0] in '-lf':
                try:
                    os.remove(path)
                except OSError, strerror:
                    print "Error removing file: %s" % strerror
            else:
                try:
                    os.rmdir(path)
                except OSError, strerror:
                    print "Error removing directory: %s" % strerror
            self.list.SetItemState(item, 0, wx.LIST_STATE_SELECTED)
        self.updateListing(self.getDir())

    def onChmod(self, event):
        selected = file_utils.get_selected(self.list)
        for item in selected:
            file = file_utils.get_column_text(self.list, item, 0)
            path = os.path.join(self.getDir(), file)
            try:
                info = os.stat(path)
                perm = info[0] # st_mode
            except OSError, strerror:
                print "Error obtaining permissions for %(f)s: %(err)s" % \
                        { 'f' : file, 'err' : strerror }
                continue

            chmod_win = PermsDialog.ChmodWindow(self, file, perm)
            ret = chmod_win.ShowModal()
            if ret == wx.ID_OK:
                new_perm = chmod_win.getPermissions()
                try:
                    os.chmod(path, new_perm)
                except OSError, strerror:
                    print "Error setting permissions for %(f)s: %(err)s" % \
                            { 'f' : file, 'err' : strerror }
        if selected:
            self.updateListing(self.getDir())

    def onRefresh(self, event):
        self.updateListing('.')

    def updateListing(self, dir):
        dir = os.path.normpath(dir)
        # Construct our new path
        if dir == '..':
            self.setDir(os.path.dirname(self.getDir()))
        elif dir != '.':
            newpath = os.path.join(self.getDir(), dir)
            if os.path.isdir(newpath):
                self.setDir(newpath)
            #else:
            #    print "Invalid directory: " + newpath

        # Get the new listing
        self.last_listing = self.readDir(self.getDir())

        # Now change the list to reflect the new listing. Notice that
        # we pause the visuals so it doesn't look funny
        self.list.Freeze()
        self.clearList()
        if self.sorted:
            parent_entry = self.last_listing.pop(0)
            self.last_listing = self.sortList(self.last_listing)
            # Make sure parent entry is first
            self.last_listing.insert(0, parent_entry)
        for i in range(len(self.last_listing)):
            item = self.last_listing[i]
            img_index = self.selectBitmapIndex(item[3])
            self.list.InsertImageStringItem(i, item[0], img_index)
            self.list.SetStringItem(i, 1, item[1])
            self.list.SetStringItem(i, 2, item[2])
            self.list.SetStringItem(i, 3, item[3])
            self.list.SetItemData(i, i)
        self.list.Thaw()

    def readDir(self, dir):
        #print dir
        try:
            files = os.listdir(dir)
        except OSError, strerror:
            print strerror
            return

        files = [ i for i in files if not self.hidden_re.match(i) ]

        # Add the special file ".."
        files.insert(0, '..')

        listitems = [ ]
        for f in files:
            # Attempt to retrieve the file info and modification times
            try:
                # lstat is preferrable for systems that support it
                (st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size,
                 st_atime, st_mtime, st_ctime) = os.lstat(os.path.join(dir, f))
            except OSError, strerror:
                # Set the size and mtime to 0 then and carry on if we can't stat
                # the file for some reason but know it's there
                print strerror
                st_size = 0
                st_mtime = 0

            # Beautify the size string
            size = file_utils.beautify_size(st_size)

            # Beautify the time
            match = self.time_re.match(time.ctime(st_mtime))
            mtime = match.group(1)

            # Set the appropriate file type and determine the mode
            mode = self.convertPermToStr(st_mode)
            if os.path.islink(os.path.join(self.getDir(), f)):
                mode = "l" + mode
            elif os.path.isdir(os.path.join(self.getDir(), f)):
                mode = "d" + mode
            else:
                mode = "-" + mode

            listitems.append((f, size, mtime, mode, str(st_size)))

        return listitems

    def convertPermToStr(self, perm):
        flags = [ '-' ] * 9
        if perm &(4 << 6):
            flags[0] = 'r'
        if perm &(2 << 6):
            flags[1] = 'w'
        if perm &(1 << 6):
            flags[2] = 'x'
        if perm &(4 << 3):
            flags[3] = 'r'
        if perm &(2 << 3):
            flags[4] = 'w'
        if perm &(1 << 3):
            flags[5] = 'x'
        if perm & 4:
            flags[6] = 'r'
        if perm & 2:
            flags[7] = 'w'
        if perm & 1:
            flags[8] = 'x'
        return ''.join(flags)

    def sortList(self, list):
        if self.directories_first:
            dirs = [ i for i in list if i[3][0] == 'd' ]
            links = [ i for i in list if i[3][0] == 'l' ]
            files = [ i for i in list if i[3][0] in '-f' ]

            list = [ ]
            list.extend(self.performSort(dirs))
            list.extend(self.performSort(links))
            list.extend(self.performSort(files))
        else:
            list = self.performSort(list)
        return list

class CvsBrowser(AbstractFileWindow):

    """file browser used in repoman console"""

    idPOPUP_DIGEST  = wx.NewId()
    idPOPUP_DELETE  = wx.NewId()
    idPOPUP_ADD  = wx.NewId()
    idPOPUP_REFRESH = wx.NewId()
    idPOPUP_EDIT = wx.NewId()

    time_re = re.compile('[A-Za-z]+\s+([A-Za-z]+\s+\d+\s+\d+:\d+):(\d+)\s+\d+')

    def __init__(self, parent):
        if __debug__:
            pass

        self.headers = [ "Filename", "Size", "Date", "Perms" ]
        AbstractFileWindow.__init__(self, parent, self.headers)

        # Set the headings sizes accordingly
        for i in range(len(self.headers)):
            self.list.SetColumnWidth(i, 100)
        # make column width adjust to longest filenames 
        self.list.SetColumnWidth(0, 200)

    def populate(self, my_dir):
        if os.path.exists(my_dir):
            self.setDir(my_dir)
            self.last_listing = None
            self.updateListing(self.getDir())

    def onDoubleClick(self, event):
        item = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        if item != -1:
            selected = file_utils.get_column_text(self.list, item, 0)
            self.updateListing(selected)

    def onRightClick(self, event):
        menu = self.makePopupMenu()
        self.PopupMenu(menu, wx.Point(event.m_x, event.m_y))

    def setColor(self, filename, color):
        """Find filename in list, color it"""
        index = self.list.FindItem(-1, filename)
        item = self.list.GetItem(index)
        item.SetTextColour(color)
        self.list.SetItem(item)

    def makePopupMenu(self):
        # Create the popup menu
        menu = wx.Menu()
        menu.Append(self.idPOPUP_DELETE, "rm and cvs remove")
        menu.Append(self.idPOPUP_ADD, "cvs add")
        menu.Append(self.idPOPUP_DIGEST, "create digest")
        menu.Append(self.idPOPUP_REFRESH, "Refresh Listing")
        menu.Append(self.idPOPUP_EDIT, "edit file in external editor")
        wx.EVT_MENU(self, self.idPOPUP_DELETE, self.onDelete)
        wx.EVT_MENU(self, self.idPOPUP_REFRESH, self.onRefresh)
        wx.EVT_MENU(self, self.idPOPUP_ADD, self.onAdd)
        wx.EVT_MENU(self, self.idPOPUP_DIGEST, self.onDigest)
        wx.EVT_MENU(self, self.idPOPUP_EDIT, self.onEdit)
        return menu

    def onEdit(self, event):
        """Open selected file in external editor"""
        parent = self.GetParent()
        parent.EditFile()

    def onAdd(self, event):
        """cvs add selected file"""
        parent = self.GetParent()
        parent.OnCvsAdd(-1)

    def onDigest(self, event):
        """Create digest for selected ebuild"""
        parent = self.GetParent()
        parent.OnDigest(-1)

    def getFilename(self):
        """Return full path to selected files"""
        selected = file_utils.get_selected(self.list)
        file = file_utils.get_column_text(self.list, selected[0], 0)
        return os.path.join(self.getDir(), file)

    def onDelete(self, event):
        """Delete selected files"""
        parent = self.GetParent()
        selected = file_utils.get_selected(self.list)
        for item in selected:
            file = file_utils.get_column_text(self.list, item, 0)
            type = self.last_listing[self.list.GetItemData(item)][3]
            path = os.path.join(self.getDir(), file)
            if type[0] in '-lf':
                try:
                    os.remove(path)
                    parent.CvsRemove()
                except OSError, strerror:
                    print "Error removing file: %s" % strerror
            else:
                try:
                    os.rmdir(path)
                    parent.CvsRemove()
                except OSError, strerror:
                    print "Error removing directory: %s" % strerror
            self.list.SetItemState(item, 0, wx.LIST_STATE_SELECTED)
        self.updateListing(self.getDir())
        parent = self.GetParent()

    def onChmod(self, event):
        selected = file_utils.get_selected(self.list)
        for item in selected:
            file = file_utils.get_column_text(self.list, item, 0)
            path = os.path.join(self.getDir(), file)
            try:
                info = os.stat(path)
                perm = info[0] # st_mode
            except OSError, strerror:
                print "Error obtaining permissions for %(f)s: %(err)s" % \
                        { 'f' : file, 'err' : strerror }
                continue

            chmod_win = PermsDialog.ChmodWindow(self, file, perm)
            ret = chmod_win.ShowModal()
            if ret == wx.ID_OK:
                new_perm = chmod_win.getPermissions()
                try:
                    os.chmod(path, new_perm)
                except OSError, strerror:
                    print "Error setting permissions for %(f)s: %(err)s" % \
                            { 'f' : file, 'err' : strerror }
        if selected:
            self.updateListing(self.getDir())

    #def onChange(self, event):
    #    local_browser = browser.LocalBrowser(self, self.getDir())
    #    ret = local_browser.ShowModal()
    #    if ret == wx.ID_OK:
    #        dir = local_browser.getDirectory()
    #        if dir:
    #            self.updateListing(dir)

    def onRefresh(self, event):
        self.updateListing('.')

    def updateListing(self, dir):
        dir = os.path.normpath(dir)
        if not os.path.isdir(dir):
            return
        # Construct our new path
        if dir == '..':
            self.setDir(os.path.dirname(self.getDir()))
        elif dir != '.':
            newpath = os.path.join(self.getDir(), dir)
            if os.path.isdir(newpath):
                self.setDir(newpath)

        # Get the new listing
        self.last_listing = self.readDir(self.getDir())

        # Now change the list to reflect the new listing. Notice that
        # we pause the visuals so it doesn't look funny
        self.list.Freeze()
        self.clearList()
        if self.sorted:
            parent_entry = self.last_listing.pop(0)
            self.last_listing = self.sortList(self.last_listing)
            # Make sure parent entry is first
            self.last_listing.insert(0, parent_entry)
        for i in range(len(self.last_listing)):
            item = self.last_listing[i]
            img_index = self.selectBitmapIndex(item[3])
            self.list.InsertImageStringItem(i, item[0], img_index)
            self.list.SetStringItem(i, 1, item[1])
            self.list.SetStringItem(i, 2, item[2])
            self.list.SetStringItem(i, 3, item[3])
            self.list.SetItemData(i, i)
        self.list.Thaw()
        parent = self.GetParent()
        parent.MarkNonCvs()

    def readDir(self, dir):
        #print dir
        try:
            files = os.listdir(dir)
        except OSError, strerror:
            print strerror
            return

        files = [ i for i in files if not self.hidden_re.match(i) ]

        # Add the special file ".."
        files.insert(0, '..')

        listitems = [ ]
        for f in files:
            # Attempt to retrieve the file info and modification times
            try:
                # lstat is preferrable for systems that support it
                (st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size,
                 st_atime, st_mtime, st_ctime) = os.lstat(os.path.join(dir, f))
            except OSError, strerror:
                # Set the size and mtime to 0 then and carry on if we can't stat
                # the file for some reason but know it's there
                print strerror
                st_size = 0
                st_mtime = 0

            # Beautify the size string
            size = file_utils.beautify_size(st_size)

            # Beautify the time
            match = self.time_re.match(time.ctime(st_mtime))
            mtime = match.group(1)

            # Set the appropriate file type and determine the mode
            mode = self.convertPermToStr(st_mode)
            if os.path.islink(os.path.join(self.getDir(), f)):
                mode = "l" + mode
            elif os.path.isdir(os.path.join(self.getDir(), f)):
                mode = "d" + mode
            else:
                mode = "-" + mode

            listitems.append((f, size, mtime, mode, str(st_size)))

        return listitems

    def convertPermToStr(self, perm):
        flags = [ '-' ] * 9
        if perm &(4 << 6):
            flags[0] = 'r'
        if perm &(2 << 6):
            flags[1] = 'w'
        if perm &(1 << 6):
            flags[2] = 'x'
        if perm &(4 << 3):
            flags[3] = 'r'
        if perm &(2 << 3):
            flags[4] = 'w'
        if perm &(1 << 3):
            flags[5] = 'x'
        if perm & 4:
            flags[6] = 'r'
        if perm & 2:
            flags[7] = 'w'
        if perm & 1:
            flags[8] = 'x'
        return ''.join(flags)

    def sortList(self, list):
        if self.directories_first:
            dirs = [ i for i in list if i[3][0] == 'd' ]
            links = [ i for i in list if i[3][0] == 'l' ]
            files = [ i for i in list if i[3][0] in '-f' ]

            list = [ ]
            list.extend(self.performSort(dirs))
            list.extend(self.performSort(links))
            list.extend(self.performSort(files))
        else:
            list = self.performSort(list)
        return list

