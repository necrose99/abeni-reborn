
import wx

import __version__
import options
import utils

class GentooSTC(wx.stc.StyledTextCtrl):

    """Main editor widget"""

    def __init__(self, parent, frame, toolbar, toolbarId):
        self.frame = frame
        self.toolbar = toolbar
        self.toolbarId = toolbarId
        wx.stc.StyledTextCtrl.__init__(self, parent, -1,
                                  style = wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        #Increase text size
        self.CmdKeyAssign(ord('B'), wx.stc.STC_SCMOD_CTRL, wx.stc.STC_CMD_ZOOMIN)
        #Decrease text size
        self.CmdKeyAssign(ord('N'), wx.stc.STC_SCMOD_CTRL, wx.stc.STC_CMD_ZOOMOUT)
        self.Colourise(0, -1)
        # line numbers in the margin
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 25)
        # No bash lexer. Maybe there is a better than Python?
        self.SetLexer(wx.stc.STC_LEX_PYTHON)
        #self.SetLexer(wx.stc.STC_LEX_AUTOMATIC)

        gentooKeywords = 'jumpin eastereggs abeni FILESDIR WORKDIR PV P PN PVR D S DESCRIPTION HOMEPAGE SRC_URI LICENSE SLOT KEYWORDS IUSE DEPEND RDEPEND insinto docinto glibc_version ewarn replace-flags env-update filter-flags inherit pkg_postinst pkg_postrm pkg_preinst pkg_setup src_unpack src_install pkg_prerm pkg_nofetch pkg_config unpack src_compile dodir pkg_mv_plugins src_mv_plugins einfo epatch use has_version best_version use_with use_enable doexe exeinto econf emake dodoc dohtml dobin dosym einstall check_KV keepdir die einfo eerror into dohard doinfo doins dolib dolib.a dolib.so doman domo donewins dosbin dosed fowners fperms newbin newdoc newexe newins newlib.a newlib.so newman newsbin pmake prepalldocs prepallinfo prepallman prepall addwrite replace-sparc64-flags edit_makefiles'
        self.SetKeyWords(0, gentooKeywords)
        self.SetProperty("fold", "0")
        # Leading spaces are bad in Gentoo ebuilds!
        self.SetProperty("tab.timmy.whinge.level", "3") 
        self.SetMargins(0,0)
        self.SetUseTabs(1)
        self.SetBufferedDraw(False)

        #self.SetEdgeMode(wx.stc.STC_EDGE_BACKGROUND)
        self.SetEdgeMode(wx.stc.STC_EDGE_LINE)
        self.SetEdgeColumn(80)

        self.SetMarginWidth(2, 12)

        self.SetCaretForeground("BLUE")
        self.SetMyStyle()
        wx.stc.EVT_STC_SAVEPOINTLEFT(self, -1, self.OnSaveChange)
        wx.stc.EVT_STC_SAVEPOINTREACHED(self, -1, self.OnSaveChange)

    def SetMyStyle(self):
        try:
            my_face, my_size = options.Options().Prefs()['font'].split(",")
        except:
            my_face = "Courier"
            my_size = "12"
        my_size = int(my_size)
        faces = { 'mono' : my_face,
            'size' : my_size,
            'size2': 10,
            }

        self.SetViewWhiteSpace(int(options.Options().Prefs()['show_whitespace']))
        self.SetTabWidth(int(options.Options().Prefs()['tabsize']))
        self.StyleClearAll()
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(mono)s,size:%(size2)d" % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, "face:%(mono)s" % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")
        self.StyleSetSpec(wx.stc.STC_P_DEFAULT, "fore:#808080,face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_P_COMMENTLINE, "fore:#007F00,face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_P_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_P_STRING, "fore:#7F007F,bold,face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_P_CHARACTER, "fore:#7F007F,bold,face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_P_OPERATOR, "bold,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_P_IDENTIFIER,"face:%(mono)s,size:%(size)d" % faces) 
        self.StyleSetSpec(wx.stc.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,eol,size:%(size)d" % faces)

    def DoTitle(self, tab=True):
        """Set application's titlebar"""
        if self.GetModify():
            title = "*%s  - Abeni %s" % (utils.get_p(self.frame),
                                         __version__.version)
            self.frame.SetTitle(title)
            self.toolbar.EnableTool(self.toolbarId, True)
            if tab:
                self.SetTabModified(True)

        else:
            self.frame.SetTitle(utils.get_p(self.frame) + " - Abeni " + __version__.version)
            self.toolbar.EnableTool(self.toolbarId, False)
            if tab:
                self.SetTabModified(False)

    def SetTabModified(self, modified): 
        page = self.frame.ed_shown
        if modified:
            tab = self.frame.notebook_editor.GetPageText(page)
            self.frame.notebook_editor.SetPageText(page, "* %s" % tab)
        else:
            tab = self.frame.notebook_editor.GetPageText(page)
            tab = tab.replace("* ", "")
            self.frame.notebook_editor.SetPageText(page, tab)

    def OnSaveChange(self, evt):
        ''' Set application's titlebar '''
        self.DoTitle()
 
