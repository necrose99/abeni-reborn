from wxPython.wx import *
import os, string, sys, re
import options

def GetOptions(parent):
    """Global options from apprc file"""
    myOptions = options.Options()
    parent.pref = myOptions.Prefs()

def LoadEbuild(parent, filename, __version__, portdir):
    filename = string.strip(filename)
    parent.SetFilename(filename)
    parent.recentList.append(filename)
    vars = {}
    funcs = {}
    statements = []
    defaultVars = ['DESCRIPTION', 'HOMEPAGE', 'SRC_URI', 'LICENSE', 'SLOT'
                    'KEYWORDS', 'IUSE', 'DEPEND', 'S']
    f = open(filename, 'r')
    # Read in header, then discard it. We always write clean header.
    # This may change for developer version in future.
    f.readline()
    f.readline()
    f.readline()

    #Indenting shoud be done with tabs, not spaces
    badSpaces = re.compile('^ +')
    #Comments should be indented to level of code its refering to.
    badComments = re.compile('^#+')
    while 1:
        l = f.readline()
        if not l: #End of file
            break
        if l !='\n':
            l = string.strip(l)

        # Variables always start a line with all caps and has an =
        varTest = re.search('^[A-Z]+.*= ?', l)

        # Match any of these:
        #  mine() {
        #  mine () {   # I hate when people use this one.
        #  my_func() {
        #  my_func () {
        #  Any above with { on separate line
        funcTest = re.search('^[a-zA-Z]*(_[a-zA-Z]*)?(_[a-zA-Z]*)? ?\(\)', l)

        if varTest:
            s = string.split(l, "=")
            if len(s) > 2:  # RDEPEND = ">=foolib2"   (has two equal signs)
                s[1] = s[1] + "=" + s[2] + "\n"
            #Multi-line variables
            if l.count('"') == 1:
                v = s[1] + '\n'
                while 1:
                    l = f.readline()
                    v += l
                    if l.count('"') == 1:
                        #print s[0], v
                        s[1] = v.replace('\t', '')
                        s[1] = s[1].replace('\n\n', '\n')
                        break
            vars[s[0]] = s[1]
            parent.varOrder.append(s[0])
            continue

        if funcTest:
            tempf = []
            fname = string.replace(l, "{", "")
            tempf.append(l + "\n")
            while 1:
                l = f.readline()
                #This needs more testing.
                #replace spaces with tabs
                #if parent.pref['autoTabs'] == 'yes':
                #    l = badSpaces.sub('\t', l)
                #    l = badComments.sub('\t#', l)
                tempf.append(l)
                if l[0] == "}":
                    s = ""
                    for ls in tempf:
                        s += ls
                    funcs[fname] = s
                    parent.funcOrder.append(fname)
                    break
            continue
        # Command like 'inherit cvs' or a comment
        if re.search('^([a-z]|#|\[)', l):
            parent.statementList.append(l)

    f.close()

    '''
    print parent.statementList
    t = string.join(parent.statementList, '\n')
    print t
    dups = re.compile(r"""\n\n\n""", re.DOTALL)
    t = dups.sub('\n', t)
    print t
    parent.statementList= string.split(t, '\n')
    print parent.statementList
    '''
    s = string.split(filename, "/")
    parent.ebuild_file = s[len(s)-1]
    package = s[len(s)-2]
    category = s[len(s)-3]
    defaultVars = {}
    otherVars = {}
    defaultVars, otherVars = parent.SeparateVars(vars)
    defaultVars['package'] = package
    defaultVars['ebuild_file'] = parent.ebuild_file
    defaultVars['category'] = category

    #If S isn't set it equals
    if defaultVars['S'] == '':
        defaultVars['S'] = '${WORKDIR}/${P}'

    #You must set IUSE, even if you don't use it.
    if defaultVars['IUSE'] == '':
        defaultVars['IUSE'] = '""'
    parent.editing = 1
    parent.AddPages()
    parent.PopulateForms(defaultVars)
    clog = string.replace(filename, parent.ebuild_file, '') + 'ChangeLog'
    parent.ebuildDir = string.replace(filename, parent.ebuild_file, '')
    parent.panelChangelog.Populate(clog, portdir)

    # Add original ebuild file:
    parent.AddEditor('Output', open(filename, 'r').read())
    #Add custom variables to Main panel

    #This was un-ordered:
    #for v in otherVars:
    #    parent.AddNewVar(v, otherVars[v])

    # Put them in panel in the order they were in the ebuild
    for n in range(len(parent.varOrder)):
        for v in otherVars:
            if v == parent.varOrder[n]:
                parent.AddNewVar(v, otherVars[v])
    if parent.CheckUnpacked():
        parent.ViewEnvironment()
        parent.ViewConfigure()
        parent.ViewMakefile()
        parent.ViewSetuppy()
    #Add functions in order they were in in ebuild:
    for n in range(len(parent.funcOrder)):
        parent.AddFunc(parent.funcOrder[n], funcs[parent.funcOrder[n]])
    parent.panelMain.stext.SetValue(string.join(parent.statementList, '\n'))
    if parent.pref['log'] == 'bottom':
        parent.nb.SetSelection(0)
    else:
        parent.LogTab()
        parent.nb.SetSelection(1)

    # Set titlebar of app to ebuild name
    parent.SetTitle(parent.ebuild_file + " | Abeni " + __version__)

def WriteEbuild(parent, temp=0):
    """Format data into fields and output to ebuild file"""
    categoryDir = parent.GetCategory()
    if not os.path.exists(categoryDir):
        os.mkdir(categoryDir)
    parent.ebuildDir = os.path.join (categoryDir, parent.panelMain.Package.GetValue())
    if not os.path.exists(parent.ebuildDir):
        os.mkdir(parent.ebuildDir)
    filename = os.path.join(parent.ebuildDir, parent.panelMain.EbuildFile.GetValue())
    parent.SetFilename(filename)
    parent.filehistory.AddFileToHistory(filename.strip())
    f = open(filename, 'w')
    f.write('# Copyright 1999-2003 Gentoo Technologies, Inc.\n')
    f.write('# Distributed under the terms of the GNU General Public License v2\n')
    # Heh. CVS fills this line in, have to trick it with:
    f.write('# ' + '$' + 'Header:' + ' $\n')

    #Misc statements
    f.write('\n')
    t = parent.panelMain.stext.GetValue()
    if t:
        f.write(t + '\n')
        f.write('\n')

    #Misc variables
    varDict = parent.panelMain.GetVars()
    for n in range(len(parent.varOrder)):
        if not parent.isDefault(parent.varOrder[n]):
            f.write(parent.varOrder[n] + '=' + varDict[parent.varOrder[n]][1].GetValue() + '\n')

    #TODO: Write these in the order they were imported? Or keep like in skel.ebuild?
    # This would print them in original order imported:
    #for n in range(len(parent.varOrder)):
    #    if parent.isDefault(parent.varOrder[n]):
    #        f.write(parent.varOrder[n] + '=' + varList[parent.varOrder[n]].GetValue() + '\n')

    #Default variables
    f.write('S=' + parent.panelMain.S.GetValue() + '\n')
    f.write('DESCRIPTION=' + parent.panelMain.Desc.GetValue() + '\n')
    f.write('HOMEPAGE=' + parent.panelMain.Homepage.GetValue() + '\n')
    f.write('SRC_URI=' + parent.panelMain.URI.GetValue() + '\n')
    f.write('LICENSE=' + parent.panelMain.License.GetValue() + '\n')
    f.write('SLOT=' + parent.panelMain.Slot.GetValue() + '\n')
    f.write('KEYWORDS=' + parent.panelMain.Keywords.GetValue() + '\n')
    f.write('IUSE=' + parent.panelMain.USE.GetValue() + '\n')

    #f.write(parent.panelDepend.txt.GetText())

    dlist = parent.panelDepend.elb1.GetStrings()
    depFirst = 1 # Do we write DEPEND or RDEPEND first?
    d = 'DEPEND="'
    for ds in dlist:
        if ds == '${RDEPEND}':
            depFirst = 0
        if d == 'DEPEND="':
            d += ds + "\n"
        else:
            d += '\t' + ds + "\n"
    d = string.strip(d)
    d += '"'
    if d == 'DEPEND=""':
        d = ''
        f.write('\n')
    rdlist = parent.panelDepend.elb2.GetStrings()
    rd = 'RDEPEND="'
    for ds in rdlist:
        if rd == 'RDEPEND="':
            rd += ds + "\n"
        else:
            rd += "\t" + ds + "\n"
    rd = string.strip(rd)
    rd += '"'
    if rd == 'RDEPEND=""':
        rd = ''
    if depFirst:
        if d:
            f.write(d + '\n')
        if rd:
            f.write(rd + '\n')
    else:
        if rd and d:
            f.write(rd + '\n')
            f.write(d + '\n')
    f.write('\n')

    #Write functions:
    for fun in parent.funcList:
        ftext = fun.edNewFun.GetText()
        f.write(ftext + '\n')
    f.close()

    # Mark functions as saved
    for fns in parent.funcList:
        fns.edNewFun.SetSavePoint()

    changelog = os.path.join(parent.ebuildDir, 'ChangeLog')
    f = open(changelog, 'w')
    f.write(parent.panelChangelog.edChangelog.GetText())
    f.close()
    parent.recentList.append(filename)
    parent.sb.SetStatusText("Saved", 0)
    #parent.write("Saved %s" % filename)
    #parent.SetTitle("%s | %s" % (parent.panelMain.EbuildFile.GetValue(), parent.__version__))
    #TODO: CRITICAL Fix this. It doesn't work on first save of new ebuild.
    try:
        parent.ebuildfile.editorCtrl.SetReadOnly(0)
        parent.ebuildfile.editorCtrl.SetText(open(filename, 'r').read())
        parent.ebuildfile.editorCtrl.SetReadOnly(1)
    except:
        pass

def getDefaultVars(parent):
    """Gather default variables from Main form"""
    defaultVars = {}
    defaultVars['package'] = parent.panelMain.Package.GetValue()
    defaultVars['ebuild_file'] = parent.panelMain.EbuildFile.GetValue()
    defaultVars['DESCRIPTION'] = parent.panelMain.Desc.GetValue()
    defaultVars['HOMEPAGE'] = parent.panelMain.Homepage.GetValue()
    defaultVars['SRC_URI'] = parent.panelMain.URI.GetValue()
    defaultVars['LICENSE'] = parent.panelMain.License.GetValue()
    defaultVars['SLOT'] = parent.panelMain.Slot.GetValue()
    defaultVars['KEYWORDS'] = parent.panelMain.Keywords.GetValue()
    defaultVars['S'] = parent.panelMain.S.GetValue()
    defaultVars['IUSE'] = parent.panelMain.USE.GetValue()
    defaultVars['DEPEND'] = parent.panelDepend.elb1.GetStrings()
    defaultVars['RDEPEND'] = parent.panelDepend.elb2.GetStrings()
    if defaultVars.has_key('S'):
        pass
    else:
        defaultVars['S'] = "S=${WORKDIR}/${P}"
    defaultVars['changelog'] = parent.panelChangelog.edChangelog.GetText()
    return defaultVars

def EclassGames(parent):
    """Add games.eclass stuff"""

    parent.AddCommand("inherit games")

    src_compile = "src_compile() {\n" + \
    "\tegamesconf\n" + \
    "\temake\n" + \
    "}"
    parent.AddFunc("src_compile", (src_compile))

    src_install = "src_install() {\n" + \
    "\tmake DESTDIR=${D} install || die\n" + \
    "\tprepgamesdirs\n" + \
    "}"
    parent.AddFunc("src_install", (src_install))


def EclassDistutils(parent):
    """Add Python distutils-related variables, inherit etc."""
    # You don't need src_install() with distutils because it gets called automatically.
    # We add it in case they want to add anything to it.

    src_install = "src_install() {\n" + \
    "\tdistutils_src_install\n" + \
    "}"
    parent.AddCommand("inherit distutils")
    parent.AddFunc("src_install", (src_install))

def EclassCVS(parent):
    """Add CVS-related variables, inherit etc."""
    src_compile = "src_compile() {\n" + \
    "\texport WANT_AUTOCONF_2_5=1\n" + \
    "\tsh autogen.sh\n" + \
    "\teconf || die 'configure failed'\n" + \
    "\temake || die 'parallel make failed'\n" + \
    "}"

    src_install = "src_install() {\n" + \
    "\teinstall || die 'make install failed'\n" + \
    "}"

    parent.AddNewVar("ECVS_SERVER", "")
    parent.AddNewVar("ECVS_MODULE", "")
    parent.AddNewVar("ECVS_TOD_DIR", "$DIST/")
    parent.AddNewVar("S", "${WORKDIR}/${PN/-cvs/}")
    parent.AddCommand("inherit cvs")
    parent.AddFunc("src_compile", (src_compile))
    parent.AddFunc("src_install", (src_install))

def AddMenu(parent):
    #Create menus, setup keyboard accelerators
    # File
    parent.menu = menu_file = wxMenu()
    mnuNewID=wxNewId()
    menu_file.Append(mnuNewID, "&New ebuild")
    EVT_MENU(parent, mnuNewID, parent.OnMnuNew)
    mnuLoadID=wxNewId()
    menu_file.Append(mnuLoadID, "&Load ebuild")
    EVT_MENU(parent, mnuLoadID, parent.OnMnuLoad)
    mnuSaveID=wxNewId()
    menu_file.Append(mnuSaveID, "&Save ebuild")
    EVT_MENU(parent, mnuSaveID, parent.OnMnuSave)
    mnuExitID=wxNewId()
    menu_file.Append(mnuExitID, "E&xit\tAlt-X")
    EVT_MENU(parent, mnuExitID, parent.OnMnuExit)
    menubar = wxMenuBar()
    menubar.Append(menu_file, "&File")
    EVT_MENU_RANGE(parent, wxID_FILE1, wxID_FILE9, parent.OnFileHistory)
    parent.filehistory = wxFileHistory()
    parent.filehistory.UseMenu(parent.menu)

    # Variable
    menu_variable = wxMenu()
    mnuNewVariableID = wxNewId()
    menu_variable.Append(mnuNewVariableID, "&New Variable\tF2", "New Variable")
    EVT_MENU(parent, mnuNewVariableID, parent.OnMnuNewVariable)
    mnuDelVariableID = wxNewId()
    menu_variable.Append(mnuDelVariableID, "&Delete Variable")
    EVT_MENU(parent, mnuDelVariableID, parent.OnMnuDelVariable)
    menubar.Append(menu_variable, "&Variable")
    # Function
    menu_function = wxMenu()
    mnuNewFunctionID = wxNewId()
    menu_function.Append(mnuNewFunctionID, "&New Function\tF3", "New Function")
    EVT_MENU(parent, mnuNewFunctionID, parent.OnMnuNewFunction)
    mnuDelFunctionID = wxNewId()
    menu_function.Append(mnuDelFunctionID, "&Delete Function")
    EVT_MENU(parent, mnuDelFunctionID, parent.OnMnuDelFunction)
    menubar.Append(menu_function, "Functio&n")
    # Eclass
    menu_eclass = wxMenu()

    mnuGamesID = wxNewId()
    menu_eclass.Append(mnuGamesID, "games")
    EVT_MENU(parent, mnuGamesID, parent.OnMnuEclassGames)

    mnuCVSID = wxNewId()
    menu_eclass.Append(mnuCVSID, "cvs")
    EVT_MENU(parent, mnuCVSID, parent.OnMnuEclassCVS)

    mnuDistutilsID = wxNewId()
    menu_eclass.Append(mnuDistutilsID, "distutils")
    EVT_MENU(parent, mnuDistutilsID, parent.OnMnuEclassDistutils)

    menubar.Append(menu_eclass, "E&class")
    # Tools
    menu_tools = wxMenu()
    mnuEbuildID = wxNewId()
    menu_tools.Append(mnuEbuildID, "Run &ebuild <this ebuild> <command>\tf4")
    EVT_MENU(parent, mnuEbuildID, parent.OnMnuEbuild)
    mnuEmergeID = wxNewId()
    menu_tools.Append(mnuEmergeID, "Run e&merge <args> <this ebuild>\tf5")
    EVT_MENU(parent, mnuEmergeID, parent.OnMnuEmerge)
    mnuLintoolID = wxNewId()
    menu_tools.Append(mnuLintoolID, "Run &Lintool on this ebuild")
    EVT_MENU(parent, mnuLintoolID, parent.OnMnuLintool)
    mnuRepomanID = wxNewId()
    menu_tools.Append(mnuRepomanID, "Run &Repoman on this ebuild")
    EVT_MENU(parent, mnuRepomanID, parent.OnMnuRepoman)
    mnuDigestID = wxNewId()
    menu_tools.Append(mnuDigestID, "&Create Digest")
    EVT_MENU(parent, mnuDigestID, parent.OnMnuCreateDigest)
    mnuDiffCreateID = wxNewId()
    menu_tools.Append(mnuDiffCreateID, "Create diff &file")
    EVT_MENU(parent, mnuDiffCreateID, parent.OnMnuDiffCreate)

    mnuClearLogID = wxNewId()
    menu_tools.Append(mnuClearLogID, "Clear log &window\tf11")
    EVT_MENU(parent, mnuClearLogID, parent.OnMnuClearLog)

    menubar.Append(menu_tools, "&Tools")
    # View
    menu_view = wxMenu()
    mnuViewID = wxNewId()
    menu_view.Append(mnuViewID, "en&vironment")
    EVT_MENU(parent, mnuViewID, parent.OnMnuViewEnvironment)
    mnuViewConfigureID = wxNewId()
    menu_view.Append(mnuViewConfigureID, "configure")
    EVT_MENU(parent, mnuViewConfigureID, parent.OnMnuViewConfigure)
    mnuViewMakefileID = wxNewId()
    menu_view.Append(mnuViewMakefileID, "Makefile")
    EVT_MENU(parent, mnuViewMakefileID, parent.OnMnuViewMakefile)
    mnuViewSetuppyID = wxNewId()
    menu_view.Append(mnuViewSetuppyID, "setup.py")
    EVT_MENU(parent, mnuViewSetuppyID, parent.OnMnuViewSetuppy)
    mnuDiffID = wxNewId()
    menu_view.Append(mnuDiffID, "&diff")
    EVT_MENU(parent, mnuDiffID, parent.OnMnuDiff)
    mnuEditID = wxNewId()
    menu_view.Append(mnuEditID, "This ebuild in e&xternal editor\tf7")
    EVT_MENU(parent, mnuEditID, parent.OnMnuEdit)
    #mnuExploreWorkdirID = wxNewId()
    #menu_view.Append(mnuExploreWorkdirID, "File browser in ${WORKDIR}")
    #EVT_MENU(parent, mnuExploreWorkdirID, parent.ExploreWorkdir)
    menubar.Append(menu_view, "Vie&w")
    # Options
    menu_options = wxMenu()
    mnuPrefID = wxNewId()
    menu_options.Append(mnuPrefID, "&Global Preferences")
    EVT_MENU(parent, mnuPrefID, parent.OnMnuPref)
    menu_options.AppendSeparator()
    mnuLogBottomID = wxNewId()
    menu_options.Append(mnuLogBottomID, "Log at &bottom\tf9", "", wxITEM_RADIO)
    EVT_MENU(parent, mnuLogBottomID, parent.OnMnuLogBottom)
    mnuLogTabID = wxNewId()
    menu_options.Append(mnuLogTabID, "Log in separate &tab\tf10", "", wxITEM_RADIO)
    EVT_MENU(parent, mnuLogTabID, parent.OnMnuLogTab)
    menu_options.AppendSeparator()

    menubar.Append(menu_options, "&Options")
    # Help
    menu_help = wxMenu()
    mnuHelpID = wxNewId()
    mnuHelpRefID = wxNewId()
    mnuAboutID = wxNewId()
    menu_help.Append(mnuHelpID,"&Contents\tF1")
    EVT_MENU(parent, mnuHelpID, parent.OnMnuHelp)
    menu_help.Append(mnuHelpRefID,"&Ebuild Quick Reference")
    EVT_MENU(parent, mnuHelpRefID, parent.OnMnuHelpRef)
    menu_help.Append(mnuAboutID,"&About")
    EVT_MENU(parent, mnuAboutID, parent.OnMnuAbout)
    menubar.Append(menu_help,"&Help")
    parent.SetMenuBar(menubar)

def AddToolbar(parent):
    #Create Toolbar with icons
    # icons are about 28x28
    parent.tb = parent.CreateToolBar(wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT) #wxTB_3DBUTTONS
    #parent.tb.SetToolSeparation(10)
    newID = wxNewId()
    newBmp = ('/usr/share/pixmaps/abeni/new.png')
    parent.tb.AddSimpleTool(newID, wxBitmap(newBmp, wxBITMAP_TYPE_PNG), \
                            "Create new ebuild")
    EVT_TOOL(parent, newID, parent.OnMnuNew)

    openID = wxNewId()
    openBmp = ('/usr/share/pixmaps/abeni/open.png')
    parent.tb.AddSimpleTool(openID, wxBitmap(openBmp, wxBITMAP_TYPE_PNG), \
                            "Open ebuild")
    EVT_TOOL(parent, openID, parent.OnMnuLoad)
    saveID = wxNewId()
    saveBmp = ('/usr/share/pixmaps/abeni/save.png')
    parent.tb.AddSimpleTool(saveID, wxBitmap(saveBmp, wxBITMAP_TYPE_PNG), \
                            "Save ebuild")
    EVT_TOOL(parent, saveID, parent.OnMnuSave)
    parent.tb.AddSeparator()
    newVarID = wxNewId()
    newVarBmp = ('/usr/share/pixmaps/abeni/x.png')
    parent.tb.AddSimpleTool(newVarID, wxBitmap(newVarBmp, wxBITMAP_TYPE_PNG), \
                            "New Variable")
    EVT_TOOL(parent, newVarID, parent.OnMnuNewVariable)
    newFunID = wxNewId()
    newFunBmp = ('/usr/share/pixmaps/abeni/fx.png')
    parent.tb.AddSimpleTool(newFunID, wxBitmap(newFunBmp, wxBITMAP_TYPE_PNG), \
                            "New Function")
    EVT_TOOL(parent, newFunID, parent.OnMnuNewFunction)
    parent.tb.AddSeparator()

    toolDigestID = wxNewId()
    digestBmp = ('/usr/share/pixmaps/abeni/digest.png')
    parent.tb.AddSimpleTool(toolDigestID, wxBitmap(digestBmp, wxBITMAP_TYPE_PNG), \
                         "Create digest for this ebuild")
    EVT_TOOL(parent, toolDigestID, parent.OnMnuCreateDigest)
    toolUnpackID = wxNewId()
    unpackBmp = ('/usr/share/pixmaps/abeni/unpack.png')
    parent.tb.AddSimpleTool(toolUnpackID, wxBitmap(unpackBmp, wxBITMAP_TYPE_PNG), \
                         "Unpack this package")
    EVT_TOOL(parent, toolUnpackID, parent.OnToolbarUnpack)

    toolCompileID = wxNewId()
    compileBmp = ('/usr/share/pixmaps/abeni/compile.png')
    parent.tb.AddSimpleTool(toolCompileID, wxBitmap(compileBmp, wxBITMAP_TYPE_PNG), \
                         "Compile this package")
    EVT_TOOL(parent, toolCompileID, parent.OnToolbarCompile)

    toolInstallID = wxNewId()
    installBmp = ('/usr/share/pixmaps/abeni/install.png')
    parent.tb.AddSimpleTool(toolInstallID, wxBitmap(installBmp, wxBITMAP_TYPE_PNG), \
                         "Install this package")
    EVT_TOOL(parent, toolInstallID, parent.OnToolbarInstall)

    parent.tb.AddSeparator()
    toolEbuildID = wxNewId()
    ebuildBmp = ('/usr/share/pixmaps/abeni/ebuild.png')
    parent.tb.AddSimpleTool(toolEbuildID, wxBitmap(ebuildBmp, wxBITMAP_TYPE_PNG), \
                         "ebuild (this ebuild) <command>")
    EVT_TOOL(parent, toolEbuildID, parent.OnMnuEbuild)

    toolEmergeID = wxNewId()
    emergeBmp = ('/usr/share/pixmaps/abeni/emerge.png')
    parent.tb.AddSimpleTool(toolEmergeID, wxBitmap(emergeBmp, wxBITMAP_TYPE_PNG), \
                         "emerge <opts> (this ebuild)")
    EVT_TOOL(parent, toolEmergeID, parent.OnMnuEmerge)

    parent.tb.AddSeparator()

    #lintoolID = wxNewId()
    #lintoolBmp = ('/usr/share/pixmaps/abeni/lintool.png')
    #parent.tb.AddSimpleTool(lintoolID, wxBitmap(lintoolBmp, wxBITMAP_TYPE_PNG), \
    #                     "Lintool - check syntax of ebuild")
    #EVT_TOOL(parent, lintoolID, parent.OnMnuLintool)

    xtermID = wxNewId()
    xtermBmp = ('/usr/share/pixmaps/abeni/xterm.png')
    parent.tb.AddSimpleTool(xtermID, wxBitmap(xtermBmp, wxBITMAP_TYPE_PNG), \
                            "Launch xterm in ../${WORKDIR}")
    EVT_TOOL(parent, xtermID, parent.OnToolbarXterm)

    helpID = wxNewId()
    helpBmp = ('/usr/share/pixmaps/abeni/help.png')
    parent.tb.AddSimpleTool(helpID, wxBitmap(helpBmp, wxBITMAP_TYPE_PNG), \
                            "Help")
    EVT_TOOL(parent, helpID, parent.OnMnuHelp)
    #Load recent ebuilds to File menu
    for ebuild in parent.recentList:
        parent.filehistory.AddFileToHistory(ebuild.strip())

    parent.tb.AddSeparator()
    parent.noautoID = wxNewId()
    b = wxToggleButton(parent.tb, parent.noautoID, "noauto")
    EVT_TOGGLEBUTTON(parent, parent.noautoID, parent.OnNoAuto)
    parent.tb.AddControl(b)

    parent.tb.AddSeparator()
    parent.toolStopID = wxNewId()
    stopBmp = ('/usr/share/pixmaps/abeni/stop.png')
    parent.stop = parent.tb.AddSimpleTool(parent.toolStopID, wxBitmap(stopBmp, wxBITMAP_TYPE_PNG), \
                         "Stop command running")
    EVT_TOOL(parent, parent.toolStopID, parent.KillProc)
    parent.tb.EnableTool(parent.toolStopID, False)

    parent.tb.Realize()
    #parent.timer = None
    parent.OnNoAuto(-1)

def DelVariable(parent):
    varDict = parent.panelMain.GetVars()
    l = varDict.keys()
    dlg = wxSingleChoiceDialog(parent, 'Choose variable to DELETE:', 'Delete Variable',
                        l, wxOK|wxCANCEL)
    if dlg.ShowModal() == wxID_OK:
        f = dlg.GetStringSelection()
        for key in varDict.keys():
            if key == f:
                varDict[key][0].Destroy()
                varDict[key][1].Destroy()
                break
        del varDict[key]
        n = 0
        for l in parent.varOrder:
            if l == key:
                break
            n+=1
        del parent.varOrder[n]
        # This part deletes then redraws all variables.
        # If I can do this with wxSizers, get rid of this mess:
        tmpDict = {}
        for l in varDict.keys():
            tmpDict[l] = [varDict[l][1].GetValue()]
            varDict[l][0].Destroy()
            varDict[l][1].Destroy()
        parent.panelMain.DeleteVars()
        for k in tmpDict.keys():
            parent.panelMain.AddVar(k, tmpDict[k][0])
    dlg.Destroy()
