from wxPython.wx import *
import urlparse, string, os, keyword
from wxPython.gizmos import *
from wxPython.stc import *

faces = { 'times': 'Times',
        'mono' : 'Courier',
        'helv' : 'Helvetica',
        'other': 'new century schoolbook',
        'size' : 12,
        'size2': 10,
        }

class main(wxPanel):

    """Main panel - contains ebuild info, variables and statements"""

    def __init__(self, parent, sb, pref):
        wxPanel.__init__(self, parent, -1)
        self.pref = pref
        self.parent=parent
        self.sb = sb
        #Custom variables
        self.varDict = {}
        self.vrow = 160
        row = 20
        col = 130
        width = 260
        self.group1_ctrls = []
        text0 = wxStaticText(self, -1, "Package")
        self.Package = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30

        text1 = wxStaticText(self, -1, "Ebuild File")
        self.EbuildFile = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        EVT_TEXT(self, self.EbuildFile.GetId(), self.EvtText)
        EVT_CHAR(self.EbuildFile, self.EvtChar)
        EVT_SET_FOCUS(self.EbuildFile, self.OnSetFocus)
        EVT_KILL_FOCUS(self.EbuildFile, self.OnKillFocus)

        row+=30
        catButID = wxNewId()
        catButton = wxButton(self, catButID, "Category")
        EVT_BUTTON(self, catButID, self.OnCatButton)
        self.Category = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        self.group2_ctrls = []
        text3 = wxStaticText(self, -1, "SRC_URI")
        self.URI = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        text5 = wxStaticText(self, -1, "HOMEPAGE")
        self.Homepage = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        self.Homepage.SetFocus()
        row+=30
        text6 = wxStaticText(self, -1, "DESCRIPTION")
        self.Desc = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        text65 = wxStaticText(self, -1, "S")
        self.S = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        text7 = wxStaticText(self, -1, "IUSE")
        self.USE = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        text8 = wxStaticText(self, -1, "SLOT")
        self.Slot = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        text9 = wxStaticText(self, -1, "KEYWORDS")
        self.Keywords = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        butID = wxNewId()
        button = wxButton(self, butID, "LICENSE          ")
        EVT_BUTTON(self, butID, self.OnLicButton)
        self.License = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))

        self.group1_ctrls.append((text0, self.Package))
        self.group1_ctrls.append((text1, self.EbuildFile))
        self.group1_ctrls.append((catButton, self.Category))
        self.group2_ctrls.append((text3, self.URI))
        self.group2_ctrls.append((text5, self.Homepage))
        self.group2_ctrls.append((text6, self.Desc))
        self.group2_ctrls.append((text65, self.S))
        self.group2_ctrls.append((text7, self.USE))
        self.group2_ctrls.append((text8, self.Slot))
        self.group2_ctrls.append((text9, self.Keywords))
        self.group2_ctrls.append((button, self.License))

        self.group3_ctrls = []
        #self.group3_ctrls.append((text11, text12))

        # Layout controls on panel:
        vs = wxBoxSizer(wxVERTICAL)
        box1_title = wxStaticBox( self, -1, "Ebuild Info")
        box1 = wxStaticBoxSizer( box1_title, wxVERTICAL )
        grid1 = wxFlexGridSizer( 0, 2, 0, 20 )
        for ctrl, text in self.group1_ctrls:
            grid1.AddWindow( ctrl, 0, wxALIGN_LEFT|wxLEFT|wxRIGHT|wxTOP, 5 )
            grid1.AddWindow( text, 0, wxALIGN_LEFT|wxLEFT|wxRIGHT|wxTOP, 5 )

        box1.AddSizer( grid1, 0, wxALIGN_LEFT|wxALL, 5 )
        vs.AddSizer( box1, 1, wxALIGN_LEFT|wxALL, 5 )

        box2_title = wxStaticBox( self, -1, "Default Variables" )
        box2 = wxStaticBoxSizer( box2_title, wxVERTICAL )
        grid2 = wxFlexGridSizer( 0, 2, 0, 0 )
        for ctrl, text in self.group2_ctrls:
            grid2.AddWindow( ctrl, 0, wxALIGN_LEFT|wxLEFT|wxRIGHT|wxTOP, 5 )
            grid2.AddWindow( text, 0, wxALIGN_LEFT|wxLEFT|wxRIGHT|wxTOP, 5 )

        box2.AddSizer( grid2, 0, wxALIGN_LEFT|wxALL, 5 )
        vs.AddSizer( box2, 2, wxALIGN_LEFT|wxALL, 5 )

        #vs2 = wxBoxSizer( wxVERTICAL )
        #box3_title = wxStaticBox( self, -1, "Custom Variables" )
        #box3 = wxStaticBoxSizer( box3_title, wxVERTICAL )
        #self.grid3 = wxFlexGridSizer( 0, 1, 0, 0 )
        #for ctrl, text in self.group3_ctrls:
        #    self.grid3.AddWindow( ctrl, 0, wxALIGN_LEFT|wxLEFT|wxRIGHT|wxTOP, 5 )
        #    self.grid3.AddWindow( text, 0, wxALIGN_LEFT|wxLEFT|wxRIGHT|wxTOP, 5 )

        #box3.AddSizer(self.grid3, 0, wxALIGN_LEFT|wxALL, 5 )
        #vs2.AddSizer(box3, 0, wxALIGN_RIGHT|wxALL, 5 )

        self.SetSizer(vs)
        vs.Fit(self)
        #self.SetSizer(vs2)
        #vs2.Fit(self)
        self.boxs = wxStaticBox( self, -1, "Misc. Statements", wxPoint(400, 5), wxSize(480, 117))
        self.stext = wxTextCtrl(self, -1, "", size=(450, 70), pos=(410,30), style=wxTE_MULTILINE)
        self.stext.SetInsertionPoint(0)
        self.boxv = wxStaticBox( self, -1, "Other Variables", wxPoint(400, 132), wxSize(480, 40))
        #EVT_TEXT(self, stext.GetId(), self.EvtText)


    def EvtText(self, event):
        print('EvtText: %s\n' % event.GetString())

    def EvtChar(self, event):
        print('EvtChar: %d\n' % event.GetKeyCode())
        event.Skip()

    def OnSetFocus(self, evt):
        print "OnSetFocus"
        evt.Skip()

    def OnKillFocus(self, evt):
        print "OnKillFocus"
        evt.Skip()

    def DeleteVars(self):
        self.varDict = {}
        self.vrow = 160

    def AddVar(self, var, val):
        """Add custom variable"""
        t = wxStaticText(self, wxNewId(), var, wxPoint(410, self.vrow))
        v = wxTextCtrl(self, wxNewId(), val, wxPoint(525, self.vrow), wxSize(310, 20))
        self.varDict[var] = [t, v]
        v.SetFocus()
        v.SetInsertionPoint(1)
        self.vrow +=30
        self.boxv.Destroy()
        self.boxv = wxStaticBox( self, -1, "Other Variables", wxPoint(400, 132), wxSize(480, self.vrow -120))

    def AddStatement(self, statement):
        """Add command/statement"""
        txt = self.stext.GetValue()
        if statement == '\n' or statement == '\n\n':
            txt += statement
        else:
            txt += statement + '\n'
        self.stext.SetValue(txt)


    def OnCatButton(self, event):
        """Choose ebuild category"""
        c = open('%s/profiles/categories' % self.parent.portdir).readlines()
        def strp(s): return s.strip()
        c = map(strp, c)
        c = filter(None, c)
        c.sort()
        dlg = wxSingleChoiceDialog(self, 'Category', 'Category:',
                                   c, wxOK|wxCANCEL)
        if dlg.ShowModal() == wxID_OK:
            opt = dlg.GetStringSelection()
            self.Category.SetValue(opt)
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

    def OnLicButton(self, event):
        """Pick a license, any license"""
        from wxPython.lib.dialogs import wxMultipleChoiceDialog
        c = os.listdir('%s/licenses' % self.parent.portdir)
        def strp(s): return s.strip()
        c = map(strp, c)
        c = filter(None, c)
        c.sort()
        dlg = wxMultipleChoiceDialog(self, 'Choose one or more:', 'License', c)
        if dlg.ShowModal() == wxID_OK:
            opt = dlg.GetValueString()
            l = ""
            for s in opt:
                print s
                l = ('%s %s' % (l, s.strip()))
            self.License.SetValue('"%s"' % l.strip())
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

    def GetVars(self):
        """Return dictionary of variable controls"""
        return self.varDict

    def PopulateDefault(self):
        """Set default variables in new ebuild"""
        self.Desc.SetValue('""')
        self.S.SetValue('"${WORKDIR}/${P}"')
        self.USE.SetValue('""')
        self.Keywords.SetValue('"~x86"')
        self.Slot.SetValue('"0"')
        self.Homepage.SetValue('"http://"')
        self.License.SetValue('""')

    def SetURI(self, uri):
        """Set URI"""
        self.URI.SetValue('"%s"' % uri)

    def SetName(self, uri):
        """Set ebuild name"""
        path = urlparse.urlparse(uri)[2]
        path = string.split(path, '/')
        file = path[len(path)-1]
        file = string.replace(file, ".zip", "")
        file = string.replace(file, ".tgz", "")
        file = string.replace(file, ".tar.gz", "")
        file = string.replace(file, ".tar.bz2", "")
        file = string.replace(file, ".tbz2", "")
        self.SetEbuildName(file)

    def SetEbuildName(self, file):
        """Set name of ebuild from filename"""
        self.ebuildName = file + ".ebuild"

    def GetEbuildName(self):
        """Return name of ebuild"""
        return self.EbuildFile.GetValue()

    def SetPackage(self):
        """Set ebuild package name"""
        self.EbuildFile.SetValue(self.ebuildName)
        ebuild = string.split(self.ebuildName, '-')
        self.Package.SetValue(ebuild[0])

    def GetPackage(self):
        return self.Package.GetValue()

class LogWindow(wxFrame):

    def __init__(self, parent):
        wxFrame.__init__(self, parent, -1, "Abeni Log", size=wxSize(900, 300))
        self.parent=parent
        self.panel = LogPanel(self, parent.log)
        EVT_CLOSE(self, self.OnClose)

    def OnClose(self, event):
        self.parent.LogBottom(self.panel.log)
        self.Destroy()

class LogPanel(wxPanel):

    def __init__(self, parent, log):
        wxPanel.__init__(self, parent, -1)
        self.parent = parent
        self.log = log
        self.log.Reparent(self)
        s = wxBoxSizer(wxHORIZONTAL)
        s.Add(self.log, 1, wxEXPAND)
        #s.Fit(self)
        self.SetSizer(s)
        self.SetAutoLayout(True)

"""
class LogWindow(wxPanel):

    def __init__(self, parent, log):
        wxPanel.__init__(self, parent, -1)
        s = wxBoxSizer(wxHORIZONTAL)
        s.Add(log, 1, wxEXPAND)
        self.SetSizer(s)
        self.SetAutoLayout(True)

"""

class depend(wxPanel):

    """This class is for adding DEPEND and RDEPEND info"""

    def __init__(self, parent):
        wxPanel.__init__(self, parent, -1)
        self.elb1 = wxEditableListBox(self, -1, "DEPEND",
                                     (10, 10), (450, 170),)
        self.elb2 = wxEditableListBox(self, -1, "RDEPEND",
                                     (10, 184), (450, 170),)


'''
class depend(wxPanel):

    """This class is for adding DEPEND and RDEPEND info"""

    def __init__(self, parent):
        wxPanel.__init__(self, parent, -1)
        self.txt = wxTextCtrl(self, -1, pos=(10, 184), size=(450, 400), style = wxTE_MULTILINE|wxTE_READONLY|wxHSCROLL)
        self.txt.SetFont(wxFont(12, wxMODERN, wxNORMAL, wxNORMAL, faceName="Lucida Console"))
'''

class changelog(wxPanel):

    """This class is for viewing the Changelog file"""

    #TODO: Switch to generic Editor class
    #Make read-only unless in developer mode.
    # Add option to add ChangeLog template
    def __init__(self, parent):
        wxPanel.__init__(self, parent, -1)
        self.edChangelog = PythonSTC(self, -1)
        s = wxBoxSizer(wxHORIZONTAL)
        s.Add(self.edChangelog, 1, wxEXPAND)
        self.SetSizer(s)
        self.SetAutoLayout(True)
        self.edChangelog.EmptyUndoBuffer()
        self.edChangelog.Colourise(0, -1)
        # line numbers in the margin
        self.edChangelog.SetMarginType(1, wxSTC_MARGIN_NUMBER)
        self.edChangelog.SetMarginWidth(1, 25)

    def Populate(self, filename, portdir):
        """Add Changelog template for new ebuilds"""

        if os.path.exists(filename):
            self.edChangelog.SetText(open(filename).read())
        else:
            filename= '%s/skel.ChangeLog' % portdir
            self.edChangelog.SetText(open(filename).read())


class NewFunction(wxPanel):

    """Add notebook page for new function, using a simple text editor"""

    def __init__(self, parent, statusbar, pref):
        wxPanel.__init__(self, parent, -1)
        self.statusbar = statusbar
        self.pref = pref
        self.parent=parent
        self.edNewFun = PythonSTC(self, -1)
        s = wxBoxSizer(wxHORIZONTAL)
        s.Add(self.edNewFun, 1, wxEXPAND)
        self.SetSizer(s)
        self.SetAutoLayout(True)
        self.edNewFun.EmptyUndoBuffer()
        self.edNewFun.Colourise(0, -1)
        # line numbers in the margin
        self.edNewFun.SetMarginType(1, wxSTC_MARGIN_NUMBER)
        self.edNewFun.SetMarginWidth(1, 25)
        self.edNewFun.SetLexer(wxSTC_LEX_PYTHON)


class Editor(wxPanel):

    """Add notebook page for editor"""

    def __init__(self, parent, statusbar, pref):
        wxPanel.__init__(self, parent, -1)
        self.statusbar = statusbar
        self.pref = pref
        self.parent=parent
        self.editorCtrl = PythonSTC(self, -1)
        s = wxBoxSizer(wxHORIZONTAL)
        s.Add(self.editorCtrl, 1, wxEXPAND)
        self.SetSizer(s)
        self.SetAutoLayout(True)
        self.editorCtrl.EmptyUndoBuffer()
        self.editorCtrl.Colourise(0, -1)
        # line numbers in the margin
        self.editorCtrl.SetMarginType(1, wxSTC_MARGIN_NUMBER)
        self.editorCtrl.SetMarginWidth(1, 25)
        self.editorCtrl.SetLexer(wxSTC_LEX_PYTHON)
        #LEX_MAKEFILE is kinda ok too

#wxStyledTextCtrl::SetLexer
#void SetLexer(wxSTC_LEX lexer)
#
#Sets the lexing language of the document.
#The valid values for lexer are: wxSTC_LEX_BATCH, wxSTC_LEX_CPP, wxSTC_LEX_ERRORLIST,
#wxSTC_LEX_HTML, wxSTC_LEX_LATEX, wxSTC_LEX_MAKEFILE, wxSTC_LEX_NULL, wxSTC_LEX_PERL,
#wxSTC_LEX_PROPERTIES, wxSTC_LEX_PYTHON, wxSTC_LEX_SQL, wxSTC_LEX_VB,
#wxSTC_LEX_XCODE and wxSTC_LEX_XML.

class PythonSTC(wxStyledTextCtrl):
    def __init__(self, parent, ID):
        wxStyledTextCtrl.__init__(self, parent, ID,
                                  style = wxNO_FULL_REPAINT_ON_RESIZE)

        self.CmdKeyAssign(ord('B'), wxSTC_SCMOD_CTRL, wxSTC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('N'), wxSTC_SCMOD_CTRL, wxSTC_CMD_ZOOMOUT)

        gentooKeywords = 'insinto docinto glibc_version ewarn replace-flags env-update filter-flags inherit pkg_postinst pkg_postrm pkg_preinst pkg_setup src_unpack src_install \
        pkg_prerm pkg_nofetch pkg_config unpack src_compile dodir pkg_mv_plugins src_mv_plugins einfo epatch \
        use has_version best_version use_with use_enable doexe exeinto econf emake dodoc dohtml dobin dosym \
        einstall check_KV keepdir die einfo eerror into dohard doinfo doins dolib dolib.a dolib.so doman domo \
        donewins dosbin dosed fowners fperms newbin newdoc newexe newins newlib.a newlib.so newman newsbin pmake \
        prepalldocs prepallinfo prepallman prepall addwrite replace-sparc64-flags edit_makefiles'
        #addwrite is undocumented?
        #self.SetKeyWords(0, " ".join(keyword.kwlist))
        self.SetKeyWords(0, gentooKeywords)
        self.SetProperty("fold", "0")
        self.SetProperty("tab.timmy.whinge.level", "3") # Spaces are bad in Gentoo ebuilds!
        self.SetMargins(0,0)

        self.SetViewWhiteSpace(False)
        #self.SetBufferedDraw(False)

        self.SetEdgeMode(wxSTC_EDGE_BACKGROUND)
        self.SetEdgeColumn(132)

        # Setup a margin to hold fold markers
        #self.SetFoldFlags(16)  ###  WHAT IS THIS VALUE?  WHAT ARE THE OTHER FLAGS?  DOES IT MATTER?
        self.SetMarginType(2, wxSTC_MARGIN_SYMBOL)
        self.SetMarginMask(2, wxSTC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)

        if 0: # simple folder marks, like the old version
            self.MarkerDefine(wxSTC_MARKNUM_FOLDER, wxSTC_MARK_ARROW, "navy", "navy")
            self.MarkerDefine(wxSTC_MARKNUM_FOLDEROPEN, wxSTC_MARK_ARROWDOWN, "navy", "navy")
            # Set these to an invisible mark
            self.MarkerDefine(wxSTC_MARKNUM_FOLDEROPENMID, wxSTC_MARK_BACKGROUND, "white", "black")
            self.MarkerDefine(wxSTC_MARKNUM_FOLDERMIDTAIL, wxSTC_MARK_BACKGROUND, "white", "black")
            self.MarkerDefine(wxSTC_MARKNUM_FOLDERSUB, wxSTC_MARK_BACKGROUND, "white", "black")
            self.MarkerDefine(wxSTC_MARKNUM_FOLDERTAIL, wxSTC_MARK_BACKGROUND, "white", "black")

        else: # more involved "outlining" folder marks
            self.MarkerDefine(wxSTC_MARKNUM_FOLDEREND,     wxSTC_MARK_BOXPLUSCONNECTED,  "white", "black")
            self.MarkerDefine(wxSTC_MARKNUM_FOLDEROPENMID, wxSTC_MARK_BOXMINUSCONNECTED, "white", "black")
            self.MarkerDefine(wxSTC_MARKNUM_FOLDERMIDTAIL, wxSTC_MARK_TCORNER,  "white", "black")
            self.MarkerDefine(wxSTC_MARKNUM_FOLDERTAIL,    wxSTC_MARK_LCORNER,  "white", "black")
            self.MarkerDefine(wxSTC_MARKNUM_FOLDERSUB,     wxSTC_MARK_VLINE,    "white", "black")
            self.MarkerDefine(wxSTC_MARKNUM_FOLDER,        wxSTC_MARK_BOXPLUS,  "white", "black")
            self.MarkerDefine(wxSTC_MARKNUM_FOLDEROPEN,    wxSTC_MARK_BOXMINUS, "white", "black")


        EVT_STC_UPDATEUI(self,    ID, self.OnUpdateUI)
        EVT_STC_MARGINCLICK(self, ID, self.OnMarginClick)


        # Make some styles,  The lexer defines what each style is used for, we
        # just have to define what each style looks like.  This set is adapted from
        # Scintilla sample property files.

        self.StyleClearAll()

        # Global default styles for all languages
        self.StyleSetSpec(wxSTC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(wxSTC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
        self.StyleSetSpec(wxSTC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.StyleSetSpec(wxSTC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(wxSTC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")

        # Python styles
        # White space
        self.StyleSetSpec(wxSTC_P_DEFAULT, "fore:#808080,face:%(helv)s,size:%(size)d" % faces)
        # Comment
        self.StyleSetSpec(wxSTC_P_COMMENTLINE, "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
        # Number
        self.StyleSetSpec(wxSTC_P_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        # String
        self.StyleSetSpec(wxSTC_P_STRING, "fore:#7F007F,bold,face:%(mono)s,size:%(size)d" % faces)
        # Single quoted string
        self.StyleSetSpec(wxSTC_P_CHARACTER, "fore:#7F007F,bold,face:%(times)s,size:%(size)d" % faces)
        # Keyword
        self.StyleSetSpec(wxSTC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
        # Triple quotes
        self.StyleSetSpec(wxSTC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces)
        # Triple double quotes
        self.StyleSetSpec(wxSTC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces)
        # Class name definition
        self.StyleSetSpec(wxSTC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces)
        # Function or method name definition
        self.StyleSetSpec(wxSTC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces)
        # Operators
        self.StyleSetSpec(wxSTC_P_OPERATOR, "bold,size:%(size)d" % faces)
        # Identifiers
        # This is actually what most words will use, since we're faking Python mode (ebuild):
        self.StyleSetSpec(wxSTC_P_IDENTIFIER, "fore:#000000,face:%(mono)s,size:%(size)d" % faces)
        #self.StyleSetSpec(wxSTC_P_IDENTIFIER, "fore:#808080,face:%(helv)s,size:%(size)d" % faces)
        # Comment-blocks
        self.StyleSetSpec(wxSTC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces)

        # End of line where string is not closed
        #Gentoo/bash
        # This gets rid of purple line with multi line variables, but the font is too small now. Grrr.
        #self.StyleSetSpec(wxSTC_P_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)

        self.SetCaretForeground("BLUE")

        EVT_KEY_DOWN(self, self.OnKeyPressed)


    def OnKeyPressed(self, event):
        if self.CallTipActive():
            self.CallTipCancel()
        key = event.KeyCode()
        if key == 32 and event.ControlDown():
            pos = self.GetCurrentPos()
            # Tips
            if event.ShiftDown():
                self.CallTipSetBackground("yellow")
                self.CallTipShow(pos, 'param1, param2')
            # Code completion
            else:
                #lst = []
                #for x in range(50000):
                #    lst.append('%05d' % x)
                #st = " ".join(lst)
                #print len(st)
                #self.AutoCompShow(0, st)

                kw = keyword.kwlist[:]
                kw.append("zzzzzz")
                kw.append("aaaaa")
                kw.append("__init__")
                kw.append("zzaaaaa")
                kw.append("zzbaaaa")
                kw.append("this_is_a_longer_value")
                kw.append("this_is_a_much_much_much_much_much_much_much_longer_value")

                kw.sort()  # Python sorts are case sensitive
                self.AutoCompSetIgnoreCase(False)  # so this needs to match

                self.AutoCompShow(0, " ".join(kw))
        else:
            event.Skip()


    def OnUpdateUI(self, evt):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == wxSTC_P_OPERATOR:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)
            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == wxSTC_P_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
            #pt = self.PointFromPosition(braceOpposite)
            #self.Refresh(True, wxRect(pt.x, pt.y, 5,5))
            #print pt
            #self.Refresh(False)


    def OnMarginClick(self, evt):
        # fold and unfold as needed
        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())
                if self.GetFoldLevel(lineClicked) & wxSTC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.Expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.Expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)


    def FoldAll(self):
        lineCount = self.GetLineCount()
        expanding = True

        # find out if we are folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) & wxSTC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break;

        lineNum = 0
        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & wxSTC_FOLDLEVELHEADERFLAG and \
               (level & wxSTC_FOLDLEVELNUMBERMASK) == wxSTC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(lineNum, True)
                    lineNum = self.Expand(lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, False)
                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)

            lineNum = lineNum + 1



    def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
        lastChild = self.GetLastChild(line, level)
        line = line + 1
        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & wxSTC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)
                    line = self.Expand(line, doExpand, force, visLevels-1)

                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, True, force, visLevels-1)
                    else:
                        line = self.Expand(line, False, force, visLevels-1)
            else:
                line = line + 1;

        return line

