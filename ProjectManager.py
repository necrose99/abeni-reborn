from portage import config
from wxPython.wx import *
from wxPython.grid import *
import popen2, gadfly, os, string

env = config().environ()
portdir_overlay = env['PORTDIR_OVERLAY'].split(" ")[0]
portdir = env['PORTDIR']


#---------------------------------------------------------------------------

class CustomDataTable(wxPyGridTableBase):
    """
    """

    def __init__(self):
        wxPyGridTableBase.__init__(self)
        loc = os.path.expanduser('~/.abeni/bugz')
        if not os.path.exists("%s/EBUILDS.grl" % loc):
            print "Creating project database and tables..."
            self.createDB()
            print "Database created."
        else:
            self.ConnectDB()

        self.colLabels = ['Package', 'Bugz Nbr', 'Bugzilla Status', 'Bugzilla Rsltn',
                          'Mine', 'In Portage', ' Abeni Status ']
        self.dataTypes = [wxGRID_VALUE_STRING,
                          wxGRID_VALUE_STRING,
                          wxGRID_VALUE_CHOICE + ':,UNCONFIRMED,NEW,ASSIGNED,REOPENED,RESOLVED,VERIFIED,CLOSED',
                          wxGRID_VALUE_CHOICE + ':,FIXED,INVALID,WONTFIX,LATER,REMIND,DUPLICATE,WORKSFORME',
                          wxGRID_VALUE_BOOL,
                          wxGRID_VALUE_BOOL,
                          wxGRID_VALUE_CHOICE + ':,FIXED,WONTFIX,LATER,OBSOLETE,TESTING,REMIND,SUBMITTED',
                          ]

        #self.data = [
        #    [ "app-admin/abeni-0.0.6", 11010,'ASSIGNED', '', 1, 0,'SUBMITTED'],
        #    [ "app-games/flowbie-0.1", 31011, "NEW", '', 0, 0, 0],
        #    [ "media-sound/boobs-1.0", 21012, "RESOLVED", "FIXED", 'all', 0, 1, 'SUBMITTED']
        #    ]

        self.data = []
        ebuilds = self.GetEbuilds()
        ebuilds.sort()
        for e in ebuilds:
            portage = self.checkOverlay(e)
            status = ""
            res = ""
            mine = 0
            abenistatus = ''
            e = e.replace(portdir_overlay, "")
            e = e[1:-8]
            catpack = e.split("/")
            cat = catpack[0]
            p = catpack[2]
            e = "%s/%s" % (cat, p)
            self.cursor.execute("SELECT p, package, cat, bug, bzstatus, bzresolution, \
                                notes, mine, abenistatus FROM ebuilds WHERE p='%s'" % p)
            mydata = self.cursor.fetchall()
            bug = ''
            if mydata:
                p, package, cat, bug, bzstatus, bzresolution, notes, mine, abenistatus = mydata[0]
                if bzstatus:
                    status = bzstatus
                if bzresolution:
                    res = bzresolution
            my = [e, bug, status, res, mine, portage, abenistatus]
            self.data.append(my)

    def ConnectDB(self):
        loc = os.path.expanduser('~/.abeni/bugz')
        self.connection = gadfly.gadfly("bugzDB", loc)
        self.cursor = self.connection.cursor()

    def UpdateRow(self, p, row, col):
        """Reload data in row,c with data found by p"""
        #We need to reconnect the DB because another process updated it
        self.ConnectDB()
        self.cursor.execute("SELECT p, package, cat, bug, bzstatus, bzresolution, \
                            notes, mine, abenistatus FROM ebuilds WHERE p='%s'" % p)
        mydata = self.cursor.fetchall()
        p, package, cat, bug, bzstatus, bzresolution, notes, mine, abenistatus = mydata[0]
        self.SetValue(row, 1, mydata[0][3])
        self.SetValue(row, 2, mydata[0][4])
        self.SetValue(row, 3, mydata[0][5])
        self.SetValue(row, 4, mydata[0][7])
        self.SetValue(row, 6, mydata[0][8])

        #'Package', 'Bugz Nbr', 'Bugzilla Status', 'Bugzilla Rsltn',
        #                  'Mine', 'In Portage', ' Abeni Status ']

    def checkOverlay(self, n):
        o = n.replace(portdir_overlay, portdir).strip()
        if os.path.exists(o):
            return 1

    def createDB(self):
        self.connection = gadfly.gadfly()
        loc = os.path.expanduser('~/.abeni/bugz')
        self.connection.startup("bugzDB", loc)
        self.cursor = self.connection.cursor()
        cmd = "create table ebuilds (\
           p VARCHAR, \
           package VARCHAR, \
           cat VARCHAR, \
           bug VARCHAR, \
           bzstatus VARCHAR, \
           bzresolution VARCHAR, \
           notes VARCHAR, \
           mine INTEGER, \
           abenistatus VARCHAR \
           )"
        self.cursor.execute(cmd)
        self.connection.commit()

    def GetEbuilds(self):
        ebuilds = []
        cmd = "find %s -name '*.ebuild'" % portdir_overlay
        a = popen2.Popen4(cmd, 1)
        inp = a.fromchild
        pid = a.pid
        l = inp.readline()
        while l:
            ebuilds.append(l)
            l = inp.readline()
        return ebuilds

    #--------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return len(self.data) + 1

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return true

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        try:
            self.data[row][col] = value
        except IndexError:
            # add a new row
            self.data.append([''] * self.GetNumberCols())
            self.SetValue(row, col, value)

            # tell the grid we've added a row
            msg = wxGridTableMessage(self,                             # The table
                                     wxGRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                                     1)                                # how many

            self.GetView().ProcessTableMessage(msg)


    def splitCSVLine(self, line):
        """Splits a CSV-formatted line into a list."""
        import string
        list = []
        position = 0
        fieldStart = 0
        while 1:
            if position >= len(line):
                # This only happens when we have a trailing comma
                list.append('')
                return list
            if line[position] == '"':
                field = ""
                position = position + 1
                while 1:
                    end = string.find(line, '"', position)
                    if end == -1:
                        # This indicates a badly-formed CSV file, but
                        # we'll accept it anyway.
                        field = line[position:]
                        position = len(line)
                        break
                    if end + 1 < len(line) and line[end + 1] == '"':
                        field = "%s%s" % (field, line[position:end + 1])
                        position = end + 2
                    else:
                        field = "%s%s" % (field, line[position:end])
                        position = end + 2
                        break
            else:
                end = string.find(line, ",", position)
                if end == -1:
                    list.append(line[position:end])
                    return list
                field = line[position:end]
                position = end + 1
            list.append(field)
        return list

    def OnBugzFetchButton(self, lines):
        """Update Bugzilla status/resoltn"""
        rs = self.GetNumberRows()
        cs = self.GetNumberCols()
        bugz = []
        for l in lines:
            bugz.append(self.splitCSVLine(l))
        for row in range(rs-1):
            d = self.GetValue(row, 1)
            if d:
                for b in bugz:
                    if b[0] == d:
                        print "Checking...", d, b[5], b[6]
                        self.SetValue(row, 2, b[5])
                        self.SetValue(row, 3, b[6])
        print "Done updating"

    def OnSaveButton(self):
        rs = self.GetNumberRows()
        cs = self.GetNumberCols()
        for row in range(rs-1):
            l = []
            for col in range(cs):
                d = self.GetValue(row,col)
                l.append(d)
            self.UpdateDB(l)
        self.connection.commit()

    def PtoPackage(self, p):
        """Given P, return package name"""
        parts = p.split("-")
        n = len(parts)
        if n == 2:
            pn = parts[0]
        else:
            if parts[n-1][0] == "r":
                pn = parts[:-2]
            else:
                pn = parts[:-1]
            pn = string.join(pn, "-")
        return pn

    def UpdateDB(self, l):
        p = l[0].split("/")[1]
        cat = l[0].split("/")[0]
        bug = l[1]
        bzstatus = l[2]
        bzresolution = l[3]
        mine = l[4]
        abenistatus = l[6]
        package = self.PtoPackage(p)
        notes = ''
        self.cursor.execute("SELECT p FROM ebuilds WHERE p='%s'" % p)
        exists = self.cursor.fetchall()
        if exists:
            #print "Updated", p, bug, bzstatus, bzresolution, mine
            self.cursor.execute("UPDATE ebuilds SET bug='%s', bzstatus='%s',  \
                                bzresolution='%s', mine=%i, abenistatus='%s' WHERE p='%s'" \
                                % (bug, bzstatus, bzresolution, mine, abenistatus, p))
        elif bug =='' and bzstatus =='' and bzresolution == '' and mine == 0 and abenistatus == '':
            pass
        else:
            #print "INSERT", p, cat, bug, bzstatus, bzresolution, mine
            self.cursor.execute("INSERT INTO ebuilds(p, package, cat, bug, bzstatus, \
                    bzresolution, notes, mine, abenistatus) \
                    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s',%i, '%s')" \
                    % (p, package, cat, bug, bzstatus, bzresolution, notes, mine, abenistatus)\
                    )

    #--------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.colLabels[col]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # nativly by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.dataTypes[col]

    # editor and renderer.  This allows you to enforce some type-safety
    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[col].split(':')[0]
        if typeName == colType:
            return true
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)

#---------------------------------------------------------------------------

class CustTableGrid(wxGrid):
    def __init__(self, parent):
        wxGrid.__init__(self, parent, -1)

        self.table = CustomDataTable()

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(self.table, true)

        self.SetRowLabelSize(0)
        self.SetMargins(0,0)
        self.AutoSizeColumns(False)

        EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)
        #EVT_GRID_SELECT_CELL(self, self.OnCellSelect)
        # I do this because I don't like the default behaviour of not starting the
        # cell editor on double clicks, but only a second click.

    def GetCur(self):
        """ Return row, col of cursor"""
        r = self.GetGridCursorRow()
        c = self.GetGridCursorCol()
        return r, c

    def GetP(self):
        return self.p

    def GetCat(self):
        return self.cat

    def GetPackage(self):
        return self.package

    def PtoPackage(self, p):
        """Given P, return package name"""
        parts = p.split("-")
        n = len(parts)
        if n == 2:
            pn = parts[0]
        else:
            if parts[n-1][0] == "r":
                pn = parts[:-2]
            else:
                pn = parts[:-1]
            pn = string.join(pn, "-")
        return pn

    def OnEditInfo(self):
        r, c = self.GetCur()
        if c !=0:
            #You must select a cell with cat/package
            return
        self.table.connection = None
        from dialogs import BugzillaDialog
        catpack = self.GetCellValue(r, c)
        self.p = catpack.split("/")[1]
        self.cat = catpack.split("/")[1]
        self.package = self.PtoPackage(self.p)
        dlg = BugzillaDialog(self)
        dlg.CenterOnScreen()
        v = dlg.ShowModal()
        if v == wxID_OK:
            res = dlg.SaveInfo()
            self.table.UpdateRow(self.p, r, c)
        dlg.Destroy()

    def OnCellSelect(self, evt):
        evt.Skip()

    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

    def OnBugzFetchButton(self, l):
        self.table.OnBugzFetchButton(l)

    def OnDelButton(self):
        self.table.OnDelButton()

    def OnSaveButton(self):
        self.SaveEditControlValue()
        self.table.OnSaveButton()

#---------------------------------------------------------------------------

class MyFrame(wxFrame):
    def __init__(self, parent):
        wxFrame.__init__(self, parent, -1, "Abeni Ebuild Project Manager", size=(800,480))
        EVT_CLOSE(self,self.OnClose)
        self.parent = parent
        p = wxPanel(self, -1, style=0)
        self.grid = CustTableGrid(p)
        b1 = wxButton(p, -1, "Save")
        EVT_BUTTON(self, b1.GetId(), self.OnSaveButton)
        b2 = wxButton(p, -1, "Edit Info")
        EVT_BUTTON(self, b2.GetId(), self.OnEditButton)
        #b3 = wxButton(p, -1, "Delete")
        #EVT_BUTTON(self, b3.GetId(), self.OnDelButton)
        b4 = wxButton(p, -1, "Get Bugzilla Stats")
        EVT_BUTTON(self, b4.GetId(), self.OnBugzFetchButton)
        b5 = wxButton(p, -1, "Cancel")
        EVT_BUTTON(self, b5.GetId(), self.OnCancelButton)
        #b6 = wxButton(p, -1, "Query/Find Bug#")
        #EVT_BUTTON(self, b6.GetId(), self.OnQueryButton)

        bs = wxBoxSizer(wxVERTICAL)
        buts = wxBoxSizer(wxHORIZONTAL)
        buts.Add(b1)
        buts.Add((6,6)) # Gap between buttons
        buts.Add(b2)
        buts.Add((6,6))
        #buts.Add(b3)
        #buts.Add((6,6))
        buts.Add(b4)
        buts.Add((6,6))
        buts.Add(b5)
        #buts.Add((60,6))
        #buts.Add(b6)
        bs.Add(self.grid, 2, wxGROW|wxALL, 5)
        bs.Add(buts,0, wxEXPAND|wxALL, 10)
        p.SetSizer(bs)

    def OnClose(self, evt):
        self.CloseMe()

    def CloseMe(self):
        self.Destroy()

    def OnQueryButton(self, evt):
        pass
        #t = self.QueryCtrl.GetValue()

    def OnSaveButton(self, evt):
        wxSafeYield()
        self.grid.OnSaveButton()

    def OnDelButton(self, evt):
        self.grid.OnDelButton()

    def OnEditButton(self, evt):
        self.grid.OnEditInfo()

    def OnCancelButton(self, evt):
        self.CloseMe()

    def OnBugzFetchButton(self, evt):
        import urllib, options
        myOptions = options.Options()
        pref = myOptions.Prefs()
        print "Fetching Info from bugs.gentoo.org..."
        wxSafeYield()
        e = pref['email']
        if not e:
            print "No email address specified"
            return
        uname = e.split("@")[0]
        host = e.split("@")[1]
        email = uname+"%40"+host
        print email
        #"http://bugs.gentoo.org/buglist.cgi?query_format=&short_desc_type=allwordssubstr&short_desc=&long_desc_type=substring&long_desc=&bug_file_loc_type=allwordssubstr&bug_file_loc=&keywords_type=allwords&keywords=&bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&bug_status=RESOLVED&bug_status=VERIFIED&bug_status=CLOSED&emailassigned_to1=1&emailreporter1=1&emailqa_contact1=1&emailcc1=1&emaillongdesc1=1&emailtype1=exact&email1=robc%40myrealbox.com&emailtype2=substring&email2=&bugidtype=include&bug_id=&votes=&changedin=&chfieldfrom=&chfieldto=Now&chfieldvalue=&field0-0-0=noop&type0-0-0=noop&value0-0-0=&ctype=csv"
        addr1="http://bugs.gentoo.org/buglist.cgi?query_format=&short_desc_type=allwordssubstr&"
        addr2="short_desc=&long_desc_type=substring&long_desc=&bug_file_loc_type=allwordssubstr&bug_file_loc=&"
        addr3="keywords_type=allwords&keywords=&bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_"
        addr4="status=REOPENED&bug_status=RESOLVED&bug_status=VERIFIED&bug_status=CLOSED&emailassigned_to1=1&"
        addr5="emailreporter1=1&emailqa_contact1=1&emailcc1=1&emaillongdesc1=1&emailtype1=exact&email1="
        addr6="%s&emailtype2=substring&email2=&bugidtype=include&bug_id=&votes=&changedin=" % email
        addr7="&chfieldfrom=&chfieldto=Now&chfieldvalue=&field0-0-0=noop&type0-0-0=noop&value0-0-0=&ctype=csv"
        addr="%s%s%s%s%s%s%s" % (addr1, addr2, addr3, addr4, addr5, addr6, addr7)
        f = urllib.urlopen(addr)
        lines = f.readlines()
        self.grid.OnBugzFetchButton(lines)

#---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    app = wxPySimpleApp()
    frame = MyFrame(None)
    frame.Show(true)
    app.MainLoop()


#---------------------------------------------------------------------------
