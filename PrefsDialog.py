#!/usr/bin/env python
# generated by wxGlade 0.3.3 on Sat Jul 24 10:49:02 2004


import wx
import string

from options import *

class MyDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.notebook = wx.Notebook(self, -1, style=0)
        self.notebook_pane_6 = wx.Panel(self.notebook, -1)
        self.noteboo_pane_emerge = wx.Panel(self.notebook, -1)
        self.noteboo_pane_dev = wx.Panel(self.notebook, -1)
        self.noteboo_pane_editor = wx.Panel(self.notebook, -1)
        self.noteboo_pane_general = wx.Panel(self.notebook, -1)
        self.notebook_ext_apps = wx.Panel(self.notebook, -1)
        self.sizer_editor_staticbox = wx.StaticBox(self.notebook_ext_apps, -1, "Editor")
        self.sizer_browser_staticbox = wx.StaticBox(self.notebook_ext_apps, -1, "Web browser")
        self.sizer_diff_staticbox = wx.StaticBox(self.notebook_ext_apps, -1, "Graphical diff")
        self.sizer_9_staticbox = wx.StaticBox(self.noteboo_pane_general, -1, "Logging")
        self.sizer_12_staticbox = wx.StaticBox(self.noteboo_pane_editor, -1, "Font")
        self.sizer_cvs_staticbox = wx.StaticBox(self.noteboo_pane_dev, -1, "CVS")
        self.sizer_4_staticbox = wx.StaticBox(self.notebook_pane_6, -1, "Choose a database backend for your Notes/Bugzilla")
        self.sizer_xterm_staticbox = wx.StaticBox(self.notebook_ext_apps, -1, "xterm")
        self.text_ctrl_xterm = wx.TextCtrl(self.notebook_ext_apps, -1, "")
        self.label_xterm_copy = wx.StaticText(self.notebook_ext_apps, -1, "Standard xterm is recommended\n(Konsole will open new sessions)")
        self.text_ctrl_editor = wx.TextCtrl(self.notebook_ext_apps, -1, "")
        self.label_editor = wx.StaticText(self.notebook_ext_apps, -1, "External editor.\nIf using gvim use the -f option.")
        self.text_ctrl_browser = wx.TextCtrl(self.notebook_ext_apps, -1, "")
        self.label_browser = wx.StaticText(self.notebook_ext_apps, -1, "Used for help system and\nchecking HOMEPAGE variable.")
        self.text_ctrl_diff = wx.TextCtrl(self.notebook_ext_apps, -1, "")
        self.label_diff = wx.StaticText(self.notebook_ext_apps, -1, "GUI diff program.\ngtkdiff, kompare etc.")
        self.checkbox_strip_header = wx.CheckBox(self.noteboo_pane_general, -1, "Auto-strip CVS header on save")
        self.checkbox_clear_log_window = wx.CheckBox(self.noteboo_pane_general, -1, "Clear log window on new or loading ebuild")
        self.checkbox_check_syntax = wx.CheckBox(self.noteboo_pane_general, -1, "Check syntax when saving")
        self.checkbox_external_control = wx.CheckBox(self.noteboo_pane_general, -1, "Allow control from vim or gvim")
        self.checkbox_logfile = wx.CheckBox(self.noteboo_pane_general, -1, "Log output to file")
        self.text_ctrl_logfile = wx.TextCtrl(self.noteboo_pane_general, -1, "")
        self.button_font = wx.Button(self.noteboo_pane_editor, -1, "Font")
        self.text_ctrl_font = wx.TextCtrl(self.noteboo_pane_editor, -1, "", style=wx.TE_READONLY)
        self.checkbox_highlight = wx.CheckBox(self.noteboo_pane_editor, -1, "Sourcecode highlighting (color)")
        self.checkbox_gentoo_highlighting = wx.CheckBox(self.noteboo_pane_editor, -1, "Highlight Gentoo keywords/functions/variables")
        self.checkbox_whitespace = wx.CheckBox(self.noteboo_pane_editor, -1, "Show whitespace")
        self.label_tabsize = wx.StaticText(self.noteboo_pane_editor, -1, "Spaces per tab char:")
        self.text_ctrl_1 = wx.TextCtrl(self.noteboo_pane_editor, -1, "4")
        self.label_cvs_root = wx.StaticText(self.noteboo_pane_dev, -1, "Enter directory for CVS root (e.g. ~/gentoo-x86)")
        self.text_ctrl_cvs_root = wx.TextCtrl(self.noteboo_pane_dev, -1, "")
        self.label_cvs_warn = wx.StaticText(self.noteboo_pane_dev, -1, "Only applies to official Gentoo developers")
        self.label_USE = wx.StaticText(self.noteboo_pane_emerge, -1, "USE=")
        self.text_ctrl_USE = wx.TextCtrl(self.noteboo_pane_emerge, -1, "")
        self.label_FEATURES = wx.StaticText(self.noteboo_pane_emerge, -1, "FEATURES=")
        self.text_ctrl_FEATURES = wx.TextCtrl(self.noteboo_pane_emerge, -1, "noauto")
        self.radio_box_database = wx.RadioBox(self.notebook_pane_6, -1, "Database", choices=["None", "SQLite", "PostgreSQL", "Firebird", "MySQL"], majorDimension=1, style=wx.RA_SPECIFY_COLS)
        self.label_msg = wx.StaticText(self.notebook_pane_6, -1, "Notes tab disabled if None selected")
        self.label_user = wx.StaticText(self.notebook_pane_6, -1, "user:")
        self.text_ctrl_user = wx.TextCtrl(self.notebook_pane_6, -1, "")
        self.label_host = wx.StaticText(self.notebook_pane_6, -1, "host:")
        self.text_ctrl_host = wx.TextCtrl(self.notebook_pane_6, -1, "localhost")
        self.button_save = wx.Button(self, wx.ID_OK, "")
        self.button_cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        self.SetTitle("Preferences")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("/usr/share/pixmaps/abeni/abeni_logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.Hide()
        self.checkbox_external_control.Enable(False)
        self.label_cvs_warn.SetForegroundColour(wx.Colour(255, 0, 0))
        self.radio_box_database.SetSelection(0)
        self.label_msg.SetForegroundColour(wx.Colour(0, 0, 255))
        self.label_user.Enable(False)
        self.text_ctrl_user.Enable(False)
        self.label_host.Enable(False)
        self.text_ctrl_host.Enable(False)
        self.button_save.SetDefault()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_14 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_15 = wx.BoxSizer(wx.VERTICAL)
        sizer_16 = wx.BoxSizer(wx.VERTICAL)
        sizer_18 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_13 = wx.BoxSizer(wx.VERTICAL)
        sizer_cvs = wx.StaticBoxSizer(self.sizer_cvs_staticbox, wx.VERTICAL)
        sizer_11 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12 = wx.StaticBoxSizer(self.sizer_12_staticbox, wx.HORIZONTAL)
        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        sizer_9 = wx.StaticBoxSizer(self.sizer_9_staticbox, wx.VERTICAL)
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_ext_apps = wx.GridSizer(2, 2, 10, 10)
        sizer_diff = wx.StaticBoxSizer(self.sizer_diff_staticbox, wx.VERTICAL)
        sizer_browser = wx.StaticBoxSizer(self.sizer_browser_staticbox, wx.VERTICAL)
        sizer_editor = wx.StaticBoxSizer(self.sizer_editor_staticbox, wx.VERTICAL)
        sizer_xterm = wx.StaticBoxSizer(self.sizer_xterm_staticbox, wx.VERTICAL)
        sizer_xterm.Add(self.text_ctrl_xterm, 0, wx.ALL|wx.EXPAND, 4)
        sizer_xterm.Add(self.label_xterm_copy, 0, 0, 0)
        grid_sizer_ext_apps.Add(sizer_xterm, 0, wx.ALL|wx.EXPAND, 4)
        sizer_editor.Add(self.text_ctrl_editor, 0, wx.ALL|wx.EXPAND, 4)
        sizer_editor.Add(self.label_editor, 0, 0, 12)
        grid_sizer_ext_apps.Add(sizer_editor, 0, wx.ALL|wx.EXPAND, 4)
        sizer_browser.Add(self.text_ctrl_browser, 0, wx.ALL|wx.EXPAND, 4)
        sizer_browser.Add(self.label_browser, 0, 0, 0)
        grid_sizer_ext_apps.Add(sizer_browser, 0, wx.ALL|wx.EXPAND, 4)
        sizer_diff.Add(self.text_ctrl_diff, 0, wx.ALL|wx.EXPAND, 4)
        sizer_diff.Add(self.label_diff, 0, 0, 0)
        grid_sizer_ext_apps.Add(sizer_diff, 1, wx.ALL|wx.EXPAND, 4)
        self.notebook_ext_apps.SetAutoLayout(True)
        self.notebook_ext_apps.SetSizer(grid_sizer_ext_apps)
        grid_sizer_ext_apps.Fit(self.notebook_ext_apps)
        grid_sizer_ext_apps.SetSizeHints(self.notebook_ext_apps)
        sizer_8.Add(self.checkbox_strip_header, 0, wx.ALL, 8)
        sizer_8.Add(self.checkbox_clear_log_window, 0, wx.ALL, 8)
        sizer_8.Add(self.checkbox_check_syntax, 0, wx.ALL, 8)
        sizer_8.Add(self.checkbox_external_control, 0, wx.ALL, 8)
        sizer_10.Add(self.checkbox_logfile, 0, wx.ALL, 8)
        sizer_10.Add(self.text_ctrl_logfile, 1, wx.ALL, 8)
        sizer_9.Add(sizer_10, 1, wx.EXPAND, 0)
        sizer_8.Add(sizer_9, 0, wx.EXPAND, 0)
        self.noteboo_pane_general.SetAutoLayout(True)
        self.noteboo_pane_general.SetSizer(sizer_8)
        sizer_8.Fit(self.noteboo_pane_general)
        sizer_8.SetSizeHints(self.noteboo_pane_general)
        sizer_12.Add(self.button_font, 0, wx.ALL, 8)
        sizer_12.Add(self.text_ctrl_font, 1, wx.ALL, 8)
        sizer_11.Add(sizer_12, 0, wx.ALL|wx.EXPAND, 12)
        sizer_11.Add(self.checkbox_highlight, 0, wx.ALL|wx.EXPAND, 12)
        sizer_11.Add(self.checkbox_gentoo_highlighting, 0, wx.ALL|wx.EXPAND, 12)
        sizer_11.Add(self.checkbox_whitespace, 0, wx.ALL|wx.EXPAND, 12)
        sizer_3.Add(self.label_tabsize, 0, wx.LEFT|wx.RIGHT, 12)
        sizer_3.Add(self.text_ctrl_1, 0, 0, 0)
        sizer_11.Add(sizer_3, 1, wx.EXPAND, 0)
        self.noteboo_pane_editor.SetAutoLayout(True)
        self.noteboo_pane_editor.SetSizer(sizer_11)
        sizer_11.Fit(self.noteboo_pane_editor)
        sizer_11.SetSizeHints(self.noteboo_pane_editor)
        sizer_cvs.Add(self.label_cvs_root, 0, wx.LEFT|wx.TOP|wx.EXPAND, 12)
        sizer_cvs.Add(self.text_ctrl_cvs_root, 0, wx.ALL|wx.EXPAND, 12)
        sizer_13.Add(sizer_cvs, 0, wx.ALL|wx.EXPAND, 20)
        sizer_13.Add(self.label_cvs_warn, 0, wx.LEFT|wx.FIXED_MINSIZE, 16)
        self.noteboo_pane_dev.SetAutoLayout(True)
        self.noteboo_pane_dev.SetSizer(sizer_13)
        sizer_13.Fit(self.noteboo_pane_dev)
        sizer_13.SetSizeHints(self.noteboo_pane_dev)
        sizer_17.Add(self.label_USE, 0, wx.ALL, 12)
        sizer_17.Add(self.text_ctrl_USE, 1, wx.ALL, 12)
        sizer_16.Add(sizer_17, 0, wx.EXPAND, 0)
        sizer_18.Add(self.label_FEATURES, 0, wx.ALL, 12)
        sizer_18.Add(self.text_ctrl_FEATURES, 1, wx.ALL, 12)
        sizer_16.Add(sizer_18, 0, wx.EXPAND, 0)
        self.noteboo_pane_emerge.SetAutoLayout(True)
        self.noteboo_pane_emerge.SetSizer(sizer_16)
        sizer_16.Fit(self.noteboo_pane_emerge)
        sizer_16.SetSizeHints(self.noteboo_pane_emerge)
        sizer_14.Add(self.radio_box_database, 0, wx.ALL|wx.FIXED_MINSIZE, 12)
        sizer_15.Add((60, 60), 0, wx.FIXED_MINSIZE, 0)
        sizer_15.Add(self.label_msg, 0, wx.LEFT|wx.FIXED_MINSIZE, 20)
        sizer_14.Add(sizer_15, 1, wx.EXPAND, 0)
        sizer_4.Add(sizer_14, 1, wx.EXPAND, 0)
        sizer_6.Add(self.label_user, 0, wx.TOP|wx.FIXED_MINSIZE, 12)
        sizer_6.Add(self.text_ctrl_user, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.FIXED_MINSIZE, 10)
        sizer_5.Add(sizer_6, 0, wx.EXPAND, 0)
        sizer_7.Add(self.label_host, 0, wx.TOP|wx.FIXED_MINSIZE, 12)
        sizer_7.Add(self.text_ctrl_host, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.FIXED_MINSIZE, 10)
        sizer_5.Add(sizer_7, 1, wx.EXPAND, 0)
        sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)
        self.notebook_pane_6.SetAutoLayout(True)
        self.notebook_pane_6.SetSizer(sizer_4)
        sizer_4.Fit(self.notebook_pane_6)
        sizer_4.SetSizeHints(self.notebook_pane_6)
        self.notebook.AddPage(self.notebook_ext_apps, "External apps")
        self.notebook.AddPage(self.noteboo_pane_general, "General")
        self.notebook.AddPage(self.noteboo_pane_editor, "Editor")
        self.notebook.AddPage(self.noteboo_pane_dev, "CVS")
        self.notebook.AddPage(self.noteboo_pane_emerge, "Emerge")
        self.notebook.AddPage(self.notebook_pane_6, "Database")
        sizer_1.Add(wx.NotebookSizer(self.notebook), 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.button_save, 0, wx.LEFT, 20)
        sizer_2.Add(self.button_cancel, 0, wx.LEFT, 20)
        sizer_1.Add(sizer_2, 0, wx.ALL|wx.EXPAND, 12)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()
        # end wxGlade

        self.checkbox_highlight.Disable()
        self.checkbox_gentoo_highlighting.Disable()

        myOptions = Options()
        p = myOptions.Prefs()

        #ext apps
        self.text_ctrl_browser.SetValue(p['browser'])
        self.text_ctrl_xterm.SetValue(p['xterm'])
        self.text_ctrl_diff.SetValue(p['diff'])
        self.text_ctrl_editor.SetValue(p['editor'])

        #General
        self.checkbox_strip_header.SetValue(int(p['stripHeader']))
        self.checkbox_clear_log_window.SetValue(int(p['clearLog']))
        self.checkbox_check_syntax.SetValue(int(p['checkSyntax']))
        self.checkbox_external_control.SetValue(int(p['externalControl']))
        self.checkbox_logfile.SetValue(int(p['logfile']))
        self.text_ctrl_logfile.SetValue(p['logFilename'])

        #Editor
        self.text_ctrl_font.SetValue(p['font'])
        self.checkbox_highlight.SetValue(int(p['highlighting']))
        self.checkbox_gentoo_highlighting.SetValue(int(p['gentooHighlight']))
        self.checkbox_whitespace.SetValue(int(p['show_whitespace']))
        #spaces per tab
        #TODO: change in wxlade
        try:
            self.text_ctrl_1.SetValue(p['tabsize'])
        except:
            self.text_ctrl_1.SetValue('4')
        #gen devs
        self.text_ctrl_cvs_root.SetValue(p['cvsRoot'])

        #portage 
        self.text_ctrl_USE.SetValue(p['use'])
        self.text_ctrl_FEATURES.SetValue(p['features'])

        self.radio_box_database.SetSelection(p['db'])
        wx.EVT_BUTTON(self, self.button_font.GetId(), self.OnFont)
        self.Bind(wx.EVT_RADIOBOX, self.on_radio_db, self.radio_box_database)
        self.on_radio_db()

    def on_radio_db(self, evt=None):
        """select database"""
        if self.radio_box_database.GetSelection() == 0:
            self.enable_userhost(False)
            self.label_msg.SetLabel("Notes tab is disabled if None selected")
        if self.radio_box_database.GetSelection() == 1:
            self.enable_userhost(False)
            self.label_msg.SetLabel("Requires dev-python/pysqlite\nThis is the recommended database.")
        if self.radio_box_database.GetSelection() == 2:
            self.enable_userhost(True)
            self.label_msg.SetLabel("Requires dev-python/psycopg\nThis database is untested.")
        if self.radio_box_database.GetSelection() == 3:
            self.enable_userhost(True)
            self.label_msg.SetLabel("Requires dev-python/kinterbasdb\nThis database is untested.")
        if self.radio_box_database.GetSelection() == 4:
            self.enable_userhost(True)
            self.label_msg.SetLabel("Requires dev-python/mysql-python\nThis database is untested.")

    def enable_userhost(self, val):
        """Enable host and user text boxes"""         
        self.label_user.Enable(val)
        self.text_ctrl_user.Enable(val)
        self.label_host.Enable(val)
        self.text_ctrl_host.Enable(val)

    def OnFont(self, evt):
        """select font"""
        data = wx.FontData()
        face,size=self.text_ctrl_font.GetValue().split(',')
        size=eval(size)
        font=wx.Font(size,wx.DEFAULT,wx.NORMAL,wx.NORMAL,0,face)
        data.SetInitialFont(font)
        dialog=wx.FontDialog(self,data)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                data = dialog.GetFontData()
                font = data.GetChosenFont()
                colour = data.GetColour()
                self.text_ctrl_font.SetValue('%s,%s'%(font.GetFaceName(),font.GetPointSize()))
        finally:
            dialog.Destroy()

 

# end of class MyDialog


