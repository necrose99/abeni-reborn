from wxPython.wx import *
import os
import string
import sys
import re
import popen2
import shutil
#Abeni:
import options


def RunExtProgram(cmd):
    """Run program and return exit code, output in a list"""
    out = []
    p = popen2.Popen4(cmd , 1)
    inp = p.fromchild
    l = inp.readline()
    while l:
        out.append(l.strip())
        l = inp.readline()
    r = p.wait()
    return r, out

def GetOptions(parent):
    """Global options from apprc file"""
    myOptions = options.Options()
    parent.pref = myOptions.Prefs()

def LoadEbuild(parent, filename, portdir):
    """Load ebuild from filename"""
    filename = string.strip(filename)
    if not os.path.exists(filename):
        parent.write("File not found: " + filename)
        dlg = wxMessageDialog(parent, "The file " + filename + " does not exist",
                              "File not found", wxOK | wxICON_ERROR)
        dlg.ShowModal()
        return
    #Check if ebuild has syntax errors before loading.
    #If there are errors ask if they want to edit it in external editor.
    #Try to load again after exiting external editor.
    os.system("chmod +x %s" % filename)
    cmd = "/bin/bash -n %s" % filename
    r, out = RunExtProgram(cmd)
    os.system("chmod -x %s" % filename)
    if r:
        parent.write("Ebuild syntax is incorrect - /bin/bash found an error. Fix this before trying to load:")
        for l in out:
            parent.write(l)
        msg = "The ebuild has a syntax error. Would you like to edit this in your external editor?"
        dlg = wxMessageDialog(parent, msg,
                'Syntax Error', wxOK | wxCANCEL | wxICON_ERROR)
        val = dlg.ShowModal()
        if val == wxID_OK:
            parent.OnMnuEdit(save=0, filename=filename)
        return
    parent.SetFilename(filename)
    parent.recentList.append(filename)
    vars = {}
    funcs = {}
    defaultVars = ['DESCRIPTION', 'HOMEPAGE', 'SRC_URI', 'LICENSE', 'SLOT'
                    'KEYWORDS', 'IUSE', 'DEPEND', 'S']
    f = open(filename, 'r')

    #Indenting shoud be done with tabs, not spaces
    #badSpaces = re.compile('^ +')
    #Comments should be indented to level of code its refering to.
    #badComments = re.compile('^#+')
    while 1:
        l = f.readline()
        if not l: #End of file
            break
        if l !='\n':
            l = string.strip(l)

        # Read in header, then discard it. We always write clean header.
        if l[0:11] == '# Copyright':
            continue
        if l[0:13] == '# Distributed':
            continue
        if l[0:10] == '# $Header:':
            continue

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
    #TODO: This is dumb. Put them in logical order: pkg_setup, src_unpack, src_compile etc.
    #Add functions in order they were in in ebuild:
    for n in range(len(parent.funcOrder)):
        parent.AddFunc(parent.funcOrder[n], funcs[parent.funcOrder[n]])
    parent.panelMain.stext.SetValue(string.join(parent.statementList, '\n'))
    if parent.pref['log'] != 'bottom':
        parent.LogWindow()
    parent.nb.SetSelection(0)

    # Set titlebar of app to ebuild name
    parent.DoTitle()

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
    f.write('# ' + '$' + 'Header:' + ' $\n\n')

    if parent.CVS:
        varDict = parent.panelMain.GetVars()
        for n in range(len(parent.varOrder)):
            if not parent.isDefault(parent.varOrder[n]):
                f.write(parent.varOrder[n] + '=' + varDict[parent.varOrder[n]][1].GetValue() + '\n')

    #Misc statements
    sta = parent.panelMain.stext.GetValue()
    if sta:
        f.write(sta + '\n')
        f.write('\n')

    #We write the misc variables, then misc statements such as 'inherit cvs'
    #because some eclasses need variables set ahead of time
    #Misc variables
    if not parent.CVS:
        varDict = parent.panelMain.GetVars()
        for n in range(len(parent.varOrder)):
            if not parent.isDefault(parent.varOrder[n]):
                f.write(parent.varOrder[n] + '=' + varDict[parent.varOrder[n]][1].GetValue() + '\n')

    f.write('\n')

    # This would print them in original order imported:
    #for n in range(len(parent.varOrder)):
    #    if parent.isDefault(parent.varOrder[n]):
    #        f.write(parent.varOrder[n] + '=' + varList[parent.varOrder[n]].GetValue() + '\n')

    #Default variables
    my_s = parent.panelMain.S.GetValue().strip()
    # Never write S= ${WORKDIR}/${P} because its the default. Bugzilla #25708
    if my_s != "${WORKDIR}/${P}" and my_s != '"${WORKDIR}/${P}"' and my_s != "'${WORKDIR}/${P}'":
        f.write('S=' + parent.panelMain.S.GetValue() + '\n')
    f.write('DESCRIPTION=' + parent.panelMain.Desc.GetValue() + '\n')
    f.write('HOMEPAGE=' + parent.panelMain.Homepage.GetValue() + '\n')
    f.write('SRC_URI=' + parent.panelMain.URI.GetValue() + '\n')
    f.write('LICENSE=' + parent.panelMain.License.GetValue() + '\n')
    f.write('SLOT=' + parent.panelMain.Slot.GetValue() + '\n')
    f.write('KEYWORDS=' + parent.panelMain.Keywords.GetValue() + '\n')
    f.write('IUSE=' + parent.panelMain.USE.GetValue() + '\n')

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
    #TODO: write in logical order: src_unpack, src_compile etc.
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
    #TODO: CRITICAL Fix this. It doesn't work on first save of new ebuild.
    try:
        parent.ebuildfile.editorCtrl.SetReadOnly(0)
    except:
        pass
    try:
        parent.ebuildfile.editorCtrl.SetText(open(filename, 'r').read())
    except:
        pass
    try:
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

def AddToolbar(parent):
    #Create Toolbar with icons
    # icons are about 28x28
    parent.tb = parent.CreateToolBar(wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
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

    editID = wxNewId()
    editBmp = ('/usr/share/pixmaps/abeni/edit.png')
    parent.tb.AddSimpleTool(editID, wxBitmap(editBmp, wxBITMAP_TYPE_PNG), \
                            "Edit ebuild in external editor")
    EVT_TOOL(parent, editID, parent.OnMnuEdit)


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


    toolQmergeID = wxNewId()
    qmergeBmp = ('/usr/share/pixmaps/abeni/qmerge.png')
    parent.tb.AddSimpleTool(toolQmergeID, wxBitmap(qmergeBmp, wxBITMAP_TYPE_PNG), \
                         "Qmerge this package")
    EVT_TOOL(parent, toolQmergeID, parent.OnToolbarQmerge)

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
                            "Launch xterm in ${S}")
    EVT_TOOL(parent, xtermID, parent.OnToolbarXterm)

    #helpID = wxNewId()
    #helpBmp = ('/usr/share/pixmaps/abeni/help.png')
    #parent.tb.AddSimpleTool(helpID, wxBitmap(helpBmp, wxBITMAP_TYPE_PNG), \
    #                        "Help")
    #EVT_TOOL(parent, helpID, parent.OnMnuHelp)

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
    b.SetValue(True)

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


class CVS:

    """ CVS utilities """

    def __init__(self, parent):
        self.parent = parent
        self.cvsRoot = self.parent.pref['cvsRoot']
        self.cat = self.parent.GetCat()
        self.package = self.parent.panelMain.Package.GetValue()
        self.ebuild = self.parent.panelMain.EbuildFile.GetValue()
        self.userName = self.parent.pref['userName']
        self.cvsDir = self.QueryPath()
        if not os.path.exists(self.cvsDir):
            self.CreateCVSdir()
        try:
            os.chdir(self.cvsDir)
        except:
            self.parent.write("ERROR: Couldn't cd to %s" % self.cvsDir)
        self.cvsEbuild = "%s/%s" % (self.cvsDir, self.ebuild)
        self.FixPerms()

    def QueryPath(self):
        """Return CVS directory of this ebuild"""
        return "%s/%s/%s" % (self.cvsRoot, self.cat, self.package)

    def CreateCVSdir(self):
        """Create CVSroot/cat/package directory"""
        catDir = "%s/%s" % (self.cvsRoot, self.cat)
        if not os.path.exists(catDir):
            os.mkdir(catDir)
        try:
            os.mkdir(self.cvsDir)
            self.parent.write("Created %s" % self.cvsDir)
        except:
            self.parent.write("ERROR: Failed to create %s!" % self.cvsDir)

    def FileExistsInCVS(self):
        if os.path.exists('./%s' % self.ebuild):
            return 1

    def CVSupdate(self):
        """/usr/bin/cvs update"""
        cmd = "/usr/bin/cvs update"
        self.Execute(cmd)
        self.parent.write("(cvs update in this directory: %s)" % self.cvsDir)

    def CopyEbuild(self):
        """Copy ebuild and ${FILES} contents from PORT_OVERLAY to CVSroot/cat/package/"""
        # TODO: Copy all files not added to CVS? Just check for patches/config files we added?
        file = self.parent.GetFilename()
        shutil.copy(file, self.cvsDir)
        self.parent.write("Copied %s to %s" % (file, self.cvsDir))
        self.FixPerms()

    def FixPerms(self):
        if len(os.listdir('./')):
            os.system("chown %s -R %s/*" % (self.userName, self.cvsDir))
        os.system("chown %s -R %s" % (self.userName, self.cvsDir))

    def RepomanScan(self):
        if not self.FileExistsInCVS():
            self.parent.write("WARNING: This ebuild hasn't been copied to CVS directory yet.")
        cmd = "su %s -c '/usr/bin/repoman scan'" % self.userName
        self.Execute(cmd)

    def RepomanCommitPretend(self):
        """repoman commmit pretend"""
        if self.FileExistsInCVS():
            cmd = """su %s -c '/usr/bin/repoman --pretend commit -m "test msg"'""" % self.userName
            self.Execute(cmd)
        else:
            self.parent.write("ERROR: Ebuild isn't in CVS directory yet.")

    def RepomanCommit(self):
        if self.FileExistsInCVS():
            msg = self.GetMsg()
            if msg:
                cmd = """su %s -c '/usr/bin/repoman --pretend commit -m "%s"'""" % (self.userName, msg)
                self.Execute(cmd)
            else:
                self.parent.write("ERROR: I won't commit without a message.")
        else:
            self.parent.write("ERROR: ebuild isn't in CVS directory yet.")


    def GetMsg(self):
        dlg = wxTextEntryDialog(self.parent, 'Enter commit message:', 'Commit message:', '')
        if dlg.ShowModal() == wxID_OK:
            msg = dlg.GetValue()
        dlg.Destroy()
        return msg

    def CreateDigest(self):
        if self.FileExistsInCVS():
            cmd = "PORTDIR_OVERLAY='%s' /usr/sbin/ebuild %s digest" % (self.cvsRoot, self.ebuild)
            self.Execute(cmd)
        else:
            self.parent.write("ERROR: ebuild isn't in CVS directory yet.")

    def AddDir(self):
        if self.FileExistsInCVS():
            os.chdir(os.path.dirname(self.cvsDir))
            cmd = "su rob -c '''/usr/bin/cvs add %s'''" % os.path.basename(self.cvsDir)
            self.Execute(cmd)
        else:
            self.parent.write("ERROR: ebuild isn't in CVS directory yet.")

    def AddEbuild(self):
        """/usr/bin/cvs add ebuild"""
        if self.FileExistsInCVS():
            cmd = "su rob -c /usr/bin/cvs add %s" % self.ebuild
            self.Execute(cmd)
        else:
            self.parent.write("ERROR: ebuild isn't in CVS directory yet.")

    def AddDigest(self):
        """/usr/bin/cvs add digest"""
        if not self.FileExistsInCVS():
            self.parent.write("ERROR: ebuild isn't in CVS directory yet.")
            return
        digest = "digest-%s" % self.ebuild[0:-7]
        if os.path.exists('./files/%s' % digest):
            cmd = "/usr/bin/cvs add files/%s" % digest
            self.Execute(cmd)
        else:
            self.parent.write("ERROR: digest doesn't exist in CVS directory yet.")

    def Execute(self, cmd):
        self.parent.write("Executing: %s" % cmd)
        self.parent.ExecuteInLog(cmd)

    def AddChangelog(self):
        if not self.FileExistsInCVS():
            self.parent.write("ERROR: ebuild isn't in CVS directory yet.")
            return
        if os.path.exists('./ChangeLog'):
            cmd = "/usr/bin/cvs add ChangeLog"
            self.Execute(cmd)
        else:
            self.parent.write("ERROR: ChangeLog doesn't exist in CVS directory")

    def AddMetadata(self):
        if not self.FileExistsInCVS():
            self.parent.write("ERROR: ebuild isn't in CVS directory yet.")
            return
        if os.path.exists('./metadata.xml'):
            cmd = "/usr/bin/cvs add metadata.xml"
            self.Execute(cmd)
        else:
            self.parent.write("ERROR: metadata.xml doesn't exist in CVS directory")


    def Echangelog(self):
        dlg = self.parent.dialogs.EchangelogDialog(self.parent, -1, "echangelog entry", \
                                size=wxSize(350, 200), \
                                style = wxDEFAULT_DIALOG_STYLE \
                                )
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if val == wxID_OK:
            l = dlg.inp.GetValue()
            if l:
                self.parent.ExecuteInLog("/usr/bin/echangelog %s" % l)
        dlg.Destroy()