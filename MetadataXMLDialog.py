#!/usr/bin/env python
# generated by wxGlade 0.3.3 on Wed Aug 25 17:22:14 2004

import os, popen2, string

import wx

class MyDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_1 = wx.StaticText(self, -1, "Enter name of herd:")
        self.text_ctrl_herd = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER)
        self.button_herd = wx.Button(self, -1, "Add")
        self.list_box_herds = wx.ListBox(self, -1, choices=[])
        self.button_remove_herd = wx.Button(self, -1, "Remove herd")
        self.text_ctrl_long_desc = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.label_email = wx.StaticText(self, -1, "Email address of maintainer")
        self.text_ctrl_email = wx.TextCtrl(self, -1, "")
        self.label_name = wx.StaticText(self, -1, "Full name of maintainer (optional)")
        self.text_ctrl_name = wx.TextCtrl(self, -1, "")
        self.label_desc = wx.StaticText(self, -1, "Description of maintainership")
        self.text_ctrl_desc = wx.TextCtrl(self, -1, "")
        self.button_remove_maintainer = wx.Button(self, -1, "Clear All")
        self.button_add_maintainer = wx.Button(self, -1, "Add")
        self.tree_ctrl_1 = wx.TreeCtrl(self, -1, style=wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.stc = GentooSTC(self, -1)
        self.button_save = wx.Button(self, wx.ID_OK, "Save")
        self.button_cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.button_preview = wx.Button(self, -1, "Preview")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        self.SetTitle("metadata.xml")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Maintainer"), wx.VERTICAL)
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Herds"), wx.VERTICAL)
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Long Description"), wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(self.label_1, 0, wx.TOP, 12)
        sizer_5.Add(self.text_ctrl_herd, 1, 0, 0)
        sizer_5.Add(self.button_herd, 0, 0, 0)
        sizer_4.Add(sizer_5, 0, wx.ALL|wx.EXPAND, 6)
        sizer_3.Add(sizer_4, 0, wx.EXPAND, 0)
        sizer_3.Add(self.list_box_herds, 1, wx.ALL|wx.EXPAND, 6)
        sizer_3.Add(self.button_remove_herd, 0, wx.ALL, 12)
        sizer_11.Add(self.text_ctrl_long_desc, 1, wx.ALL|wx.EXPAND, 6)
        sizer_10.Add(sizer_11, 1, wx.EXPAND, 0)
        sizer_3.Add(sizer_10, 0, wx.EXPAND, 0)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        sizer_7.Add(self.label_email, 0, wx.TOP, 12)
        sizer_7.Add(self.text_ctrl_email, 0, wx.ALL|wx.EXPAND, 4)
        sizer_7.Add(self.label_name, 0, wx.TOP, 4)
        sizer_7.Add(self.text_ctrl_name, 0, wx.ALL|wx.EXPAND, 6)
        sizer_7.Add(self.label_desc, 0, wx.TOP, 4)
        sizer_7.Add(self.text_ctrl_desc, 0, wx.ALL|wx.EXPAND, 6)
        sizer_8.Add(self.button_remove_maintainer, 0, wx.ALL, 8)
        sizer_8.Add(self.button_add_maintainer, 0, wx.ALL, 8)
        sizer_7.Add(sizer_8, 0, wx.EXPAND, 0)
        sizer_6.Add(sizer_7, 1, wx.EXPAND, 0)
        sizer_6.Add(self.tree_ctrl_1, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_6, 1, wx.EXPAND, 0)
        sizer_2.Add(self.stc, 2, wx.ALL|wx.EXPAND, 6)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        sizer_9.Add(self.button_save, 0, wx.ALL, 20)
        sizer_9.Add(self.button_cancel, 0, wx.ALL, 20)
        sizer_9.Add(self.button_preview, 0, wx.ALL, 20)
        sizer_1.Add(sizer_9, 0, wx.EXPAND, 0)
        self.SetAutoLayout(1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()
        # end wxGlade

        if os.environ.has_key("ECHANGELOG_USER"):
            e = os.environ["ECHANGELOG_USER"]
            my_email = e[e.find("<") +1:e.find(">")]
            my_name = e[0:e.find("<")-1]
            self.text_ctrl_email.SetValue(my_email)
            self.text_ctrl_name.SetValue(my_name)

        self.root = self.tree_ctrl_1.AddRoot("Maintainer info:")
        self.maint = {}
        wx.EVT_BUTTON(self, self.button_herd.GetId(), self.AddHerd)
        wx.EVT_BUTTON(self, self.button_remove_herd.GetId(), self.RemoveHerd)
        wx.EVT_BUTTON(self, self.button_preview.GetId(), self.Preview)
        wx.EVT_BUTTON(self, self.button_add_maintainer.GetId(), self.AddMaintainer)
        wx.EVT_BUTTON(self, self.button_remove_maintainer.GetId(), self.RemoveMaintainer)
        wx.EVT_TEXT_ENTER(self, self.list_box_herds.GetId(), self.AddHerd)

    def SetStyleSTC(self):
        self.stc.Colourise(0, -1)
        self.stc.SetMarginType(1, wx.STC_MARGIN_NUMBER)
        self.stc.SetMarginWidth(1, 10)
        myKeywords = 'herd, email, name, description, longdescription'
        self.stc.SetKeyWords(0, myKeywords)
        my_face, my_size = ["Courier", "12"]
        my_size = string.atoi(my_size)
        faces = { 'mono' : my_face,
            'size' : my_size,
            'size2': 10,
            }

        self.stc.StyleSetSpec(wx.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
    
        self.stc.StyleSetSpec(wx.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(mono)s,size:%(size2)d" % faces)
        self.stc.StyleSetSpec(wx.STC_STYLE_CONTROLCHAR, "face:%(mono)s" % faces)
        self.stc.StyleSetSpec(wx.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
        self.stc.StyleSetSpec(wx.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")
        self.stc.StyleSetSpec(wx.STC_P_DEFAULT, "fore:#808080,face:%(mono)s,size:%(size)d" % faces)
        self.stc.StyleSetSpec(wx.STC_P_COMMENTLINE, "fore:#007F00,face:%(mono)s,size:%(size)d" % faces)
        self.stc.StyleSetSpec(wx.STC_P_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        self.stc.StyleSetSpec(wx.STC_P_STRING, "fore:#7F007F,bold,face:%(mono)s,size:%(size)d" % faces)
        self.stc.StyleSetSpec(wx.STC_P_CHARACTER, "fore:#7F007F,bold,face:%(mono)s,size:%(size)d" % faces)
        self.stc.StyleSetSpec(wx.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
        self.stc.StyleSetSpec(wx.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces)
        self.stc.StyleSetSpec(wx.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces)
        self.stc.StyleSetSpec(wx.STC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces)
        self.stc.StyleSetSpec(wx.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces)
        self.stc.StyleSetSpec(wx.STC_P_OPERATOR, "bold,size:%(size)d" % faces)
        self.stc.StyleSetSpec(wx.STC_P_IDENTIFIER,"face:%(mono)s,size:%(size)d" % faces) 
        self.stc.StyleSetSpec(wx.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces)
        self.stc.StyleSetSpec(wx.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,eol,size:%(size)d" % faces)

    def AddMaintainer(self, evt):
        email = self.text_ctrl_email.GetValue()
        if email:
            name = self.text_ctrl_name.GetValue()
            desc = self.text_ctrl_desc.GetValue()
            main = self.tree_ctrl_1.AppendItem(self.root, email)
            self.maint[email] = [name, desc]
            if name:
                self.tree_ctrl_1.AppendItem(main, name)
            if  desc:
                self.tree_ctrl_1.AppendItem(main, desc)
            self.tree_ctrl_1.Expand(self.root)
            self.tree_ctrl_1.Expand(main)
            self.text_ctrl_email.SetValue("")
            self.text_ctrl_name.SetValue("")
            self.text_ctrl_desc.SetValue("")
        else:
            #TODO popup dialog "Need email"
            pass

    def RemoveMaintainer(self, evt):
        """Nuke entire maintainer tree"""
        self.maint = {}
        self.tree_ctrl_1.DeleteAllItems()
        self.root = self.tree_ctrl_1.AddRoot("Maintainer info:")

    def AddHerd(self, evt):
        """Get herd from txt ctrl and add it to list"""
        evt.Skip()
        herd = self.text_ctrl_herd.GetValue()
        self.list_box_herds.Append(herd)
        self.text_ctrl_herd.SetValue('')
        self.text_ctrl_herd.SetFocus()

    def RemoveHerd(self, evt):
        """Delete herd from listbox"""
        try:
            self.list_box_herds.Delete(self.list_box_herds.GetSelection())
        except:
            #nothing selected
            pass

    def GetLongDesc(self):
        """Returns long description"""
        return self.text_ctrl_long_desc.GetValue()

    def GetHerds(self):
        """Return herds"""
        n = self.list_box_herds.GetCount()
        if not n:
            return None

        s = []
        for i in range(n):
            s.append(self.list_box_herds.GetString(i))
        return s

    def print_item(self, child):
        print self.tree_ctrl_1.GetItemText(child)

    def traverse(self, traverseroot, function, cookie=0):
        """ recursivly walk maintainer tree control """
        # step in subtree if there are items or ...
        if self.tree_ctrl_1.ItemHasChildren(traverseroot):
            firstchild, cookie = self.tree_ctrl_1.GetFirstChild(traverseroot, cookie)
            print "ITEM"
            function(firstchild)
            self.traverse(firstchild, function, cookie)

        # ... loop siblings
        child = self.tree_ctrl_1.GetNextSibling(traverseroot)
        if child:
            print "CHILD"
            function(child)
            self.traverse(child, function, cookie) 

    def Preview(self, evt):        
        """Show wx.STC control with output from metagen"""
        #self.traverse(self.root, self.print_item)
        self.stc.SetReadOnly(0)
        herds = self.GetHerds()
        if not herds:
            herds = ["no-herd"]
        #email = self.GetEmails()
        #names = self.GetNames()
        #descs = self.GetDescs()
        long = self.GetLongDesc()
        #my_xml = open("metadata.xml", "r").read()
        cmd = "metagen -Q -H %s" % ",".join(herds)
        
        keys = self.maint.keys()
        names = []
        descs = []
        emails = []
        for e in keys:
            emails.append(e)
            if self.maint[e][0]:
                names.append('"%s"' % self.maint[e][0])
            if self.maint[e][1]:
                descs.append('"%s"' % self.maint[e][1])
        print names   
        if emails:
            cmd += " -e %s" % ",".join(keys) 
        if names:
            cmd += " -n %s" % ",".join(names) 
        if descs:
            cmd += " -d %s" % ",".join(descs) 
        if long:
            cmd += " -l '%s'" % long
        print cmd
        a = popen2.Popen4(cmd , 1)
        inp = a.fromchild
        my_xml = inp.read()
        self.stc.SetText(my_xml)
        self.stc.SetReadOnly(1)

# end of class MyDialog

class GentooSTC(wx.StyledTextCtrl):

    """Main editor widget"""

    def __init__(self, parent, ID):
        wx.StyledTextCtrl.__init__(self, parent, ID,
                                  style = wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        #Increase text size
        self.CmdKeyAssign(ord('B'), wx.STC_SCMOD_CTRL, wx.STC_CMD_ZOOMIN)
        #Decrease text size
        self.CmdKeyAssign(ord('N'), wx.STC_SCMOD_CTRL, wx.STC_CMD_ZOOMOUT)
        self.Colourise(0, -1)
        # line numbers in the margin
        self.SetMarginType(1, wx.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 10)
        # No bash lexer. Maybe there is a better than Python?
        self.SetLexer(wx.STC_LEX_XML)
        #self.SetLexer(wx.STC_LEX_AUTOMATIC)

        #gentooKeywords = ''
        #self.SetKeyWords(0, gentooKeywords)
        self.SetProperty("fold", "0")
        # Leading spaces are bad in Gentoo ebuilds!
        #self.SetProperty("tab.timmy.whinge.level", "3") 
        self.SetMargins(0,0)
        self.SetUseTabs(1)
        self.SetTabWidth(4)
        self.SetBufferedDraw(False)

        self.SetEdgeMode(wx.STC_EDGE_BACKGROUND)
        self.SetEdgeColumn(80)

        self.SetMarginWidth(2, 10)

        self.SetCaretForeground("BLUE")
        self.SetMyStyle()

    def SetMyStyle(self):
        my_face, my_size = ["Courier", "12"]
        my_size = string.atoi(my_size)
        faces = { 'mono' : my_face,
            'size' : my_size,
            'size2': 10,
            }

        self.StyleClearAll()

        self.StyleSetSpec(wx.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
        #self.StyleSetSpec(wx.STC_STYLE_DEFAULT, 'fore:#000000,back:#FFFFFF,face:Courier,size:12')
    
        self.StyleSetSpec(wx.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(mono)s,size:%(size2)d" % faces)
        self.StyleSetSpec(wx.STC_STYLE_CONTROLCHAR, "face:%(mono)s" % faces)
        self.StyleSetSpec(wx.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(wx.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")
        self.StyleSetSpec(wx.STC_P_DEFAULT, "fore:#808080,face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(wx.STC_P_COMMENTLINE, "fore:#007F00,face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(wx.STC_P_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        self.StyleSetSpec(wx.STC_P_STRING, "fore:#7F007F,bold,face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(wx.STC_P_CHARACTER, "fore:#7F007F,bold,face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(wx.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
        self.StyleSetSpec(wx.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces)
        self.StyleSetSpec(wx.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces)
        self.StyleSetSpec(wx.STC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces)
        self.StyleSetSpec(wx.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces)
        self.StyleSetSpec(wx.STC_P_OPERATOR, "bold,size:%(size)d" % faces)
        self.StyleSetSpec(wx.STC_P_IDENTIFIER,"face:%(mono)s,size:%(size)d" % faces) 
        self.StyleSetSpec(wx.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces)
        self.StyleSetSpec(wx.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,eol,size:%(size)d" % faces)


class MyApp(wx.App):

    """ Main wx.Python app class """

    def OnInit(self):
        """Set up the main frame"""
        frame=MyDialog(None,-1, 'my xml.data')
        frame.Show(true)
        #self.SetTopWindow(self.frame)
        return true


app=MyApp(0)
app.MainLoop()

