import os
import string
import sys
import re
import popen2
import shutil

from wxPython.wx import *
from wxPython.lib.dialogs import wxScrolledMessageDialog, wxMultipleChoiceDialog
from portage import config, portdb, db, pkgsplit, catpkgsplit, settings
sys.path.insert(0, "/usr/lib/gentoolkit/pym")
import gentoolkit

import options
import panels
import __version__


modulePath = "/usr/lib/python%s/site-packages/abeni" % sys.version[0:3]

try:
    env = config(clone=settings).environ()
except:
    print "ERROR: Can't read portage configuration from /etc/make.conf"
    sys.exit(1)


defaults = ["SRC_URI", "HOMEPAGE", "DEPEND", "RDEPEND", "DESCRIPTION", \
            "S", "IUSE", "SLOT", "KEYWORDS", "LICENSE"]

distdir = env['DISTDIR']
portdir = env['PORTDIR']
portdir_overlay = env['PORTDIR_OVERLAY'].split(" ")[0]
if portdir_overlay[-1] == "/":
    portdir_overlay = portdir_overlay[:-1]
portage_tmpdir = env['PORTAGE_TMPDIR']

codes={}
codes["bold"]="\x1b[01m"
codes["teal"]="\x1b[36;06m"
codes["turquoise"]="\x1b[36;01m"
codes["fuscia"]="\x1b[35;01m"
codes["purple"]="\x1b[35;06m"
codes["blue"]="\x1b[34;01m"
codes["darkblue"]="\x1b[34;06m"
codes["green"]="\x1b[32;01m"
codes["darkgreen"]="\x1b[32;06m"
codes["yellow"]="\x1b[33;01m"
codes["brown"]="\x1b[33;06m"
codes["red"]="\x1b[31;01m"
codes["darkred"]="\x1b[31;06m"

def ResolveDeps(frame, l):
    new = []
    for p in l:
        p = p.strip()
        if p:
            #curver = frame.versions('^%s$' % p)
            curver = versions(frame, p)
            if curver == None:
                #frame.write("Can't find: %s" % p)
                new.append(p)
            elif curver == "":
                #Multiple names. Be more specific.")
                #Also means isn't installed.
                #frame.write("Not installed, or multiple names like %s" % p)
                new.append(p)
            else:
                write(frame, ">=%s" % curver)
                new.append(">=%s" % curver)
    return new

def search(search_key):
    matches = []
    for package in portdb.cp_all():
        package_parts=package.split("/")
        if re.search(search_key.lower(), package_parts[1].lower()):
            matches.append(package)
    return matches

def versions(frame, query):
    tup = smart_pkgsplit(query)
    if tup[0] and tup[1]:
        matches = [ tup[0] + "/" + tup[1] ]
    elif tup[1]:
        matches = search(tup[1])
    curver = ""
    for package in matches:
        curver = db["/"]["vartree"].dep_bestmatch(package)
        return curver

def smart_pkgsplit(query):
    cat = ''
    pkg = ''
    ver = ''
    rev = ''

    if len(query.split('/')) == 2:
        cat = query.split('/')[0]
        query = query.split('/')[1]

    components = query.split('-')
    name_components = []
    ver_components = []

    # seperate pkg-ver-rev
    for c in components:
        if ver_components:
            ver_components.append(c)
        elif ord(c[0]) > 47 and ord(c[0]) < 58:
            ver_components.append(c)
        else:
            name_components.append(c)
    pkg = '-'.join(name_components)

    # check if there is a revision number
    if len(ver_components) > 0 and ver_components[-1][0] == 'r':
        rev = ver_components[-1]
        ver_components = ver_components[:-1]

    # check for version number
    if len(ver_components) > 0:
        ver = '-'.join(ver_components)

    return [cat, pkg, ver, rev]


def MyMessage(frame, msg, title, type="info", cancel=0):
    """Simple informational dialog"""
    if type == "info":
        icon = wxICON_INFORMATION
    elif type == "error":
        icon = wxICON_ERROR
    if cancel:
        dlg = wxMessageDialog(frame, msg, title, wxOK | wxCANCEL | icon)
    else:
        dlg = wxMessageDialog(frame, msg, title, wxOK | icon)
    if (dlg.ShowModal() == wxID_OK):
        return 1
    else:
        dlg.Destroy()
        return 0

def LogWindow(frame):
    """Show log in separate window"""
    if frame.splitter.IsSplit():
        frame.splitter.Unsplit()
        frame.logWin=panels.LogWindow(frame)
        frame.logWin.Show(True)
        frame.log.Show(True)
        frame.pref['log'] = 'window'
        frame.menu_options.Check(frame.mnuLogWindowID, 1)

def OnNoAuto(frame, event):
    """Toggle switch for FEATURES='noauto'"""
    StripNoAuto(frame)
    if frame.noauto == 1:
        frame.noauto = 0
        frame.pref['features'] = "noauto %s" % frame.pref['features'].strip()
    else:
        frame.noauto = 1
        frame.pref['features'] = "-noauto %s" % frame.pref['features'].strip()

def StripNoAuto(frame):
    """Strip noauto feature"""
    if string.find(frame.pref['features'], "-noauto") != -1:
        frame.pref['features'] = string.replace(frame.pref['features'], "-noauto", "")
    if string.find(frame.pref['features'], "noauto") != -1:
        frame.pref['features'] = string.replace(frame.pref['features'], "noauto", "")


def WriteText(frame, text):
    """Send text to log window after colorizing"""
    #TODO: No idea why this is output at the end of every ExecuteInLog:
    if string.find(text, "md5 src_uri") == 4:
        return

    if text[-1:] == '\n':
        text = text[:-1]
    color = ''
    reset = "\x1b[0m"
    if string.find(text, reset) != -1:
        text = string.replace(text, reset, '')
        for c in codes:
            if string.find(text, codes[c]) != -1:
                if c == "darkgreen":
                    color = "FOREST GREEN"
                elif c == "yellow":
                    color = "BROWN"
                elif c == "brown":
                    color = "BROWN"
                elif c == "darkred":
                    color = "RED"
                elif c == "teal":
                    color = "FOREST GREEN"
                elif c == "turquoise":
                    color = "TURQUOISE"
                elif c == "fuscia":
                    color = "PURPLE"
                elif c == "green":
                    color = "DARK GREEN"
                elif c == "red":
                    color = "RED"
                else:
                    color = "BLUE"
                text = string.replace(text, codes[c], '')
                break
    if color:
        logColor(frame, color)
        wxLogMessage(text)
        logColor(frame, "BLACK")
    else:
        if text[0:3] == ">>>" or text[0:3] == "<<<":
            logColor(frame, "BLUE")
            wxLogMessage(text)
            logColor(frame, "BLACK")
        elif text[0:3] == "!!!":
            logColor(frame, "RED")
            wxLogMessage(text)
            logColor(frame, "BLACK")
        else:
            wxLogMessage(text)

def logColor(frame, color):
    """Set color of text sent to log window"""
    frame.log.SetDefaultStyle(wxTextAttr(wxNamedColour(color)))

def write(frame, txt):
    """Send text to log window"""
    WriteText(frame, txt)

def AddNewVar(frame, var, val):
    """Add new variable on Main panel"""
    if val == '':
        val = '""'
    frame.panelMain.AddVar(var, val)

def AddCommand(frame, command):
    """Add a statement to the Misc Commands field on the main panel (i.e. inherit gnome2)"""
    t = frame.panelMain.stext.GetValue()
    t += "%s\n" % command
    frame.panelMain.stext.SetValue(t)

def PostAction(frame, action):
    """Execute code after ExecuteInLog finishes"""
    if action == 'unpack':
        PostUnpack(frame)

def PostUnpack(frame):
    """Report what directories were unpacked, try to set S if necessary"""
    import popen2
    p = GetP(frame)
    d = '%s/portage/%s/work' % (portage_tmpdir, p)
    try:
        lines = os.listdir(d)
    except:
        return
    dirs = []
    logColor(frame, "RED")
    write(frame, "Unpacked these directory(s) into ${WORKDIR}:")
    for l in lines:
        if os.path.isdir("%s/%s" % (d, l)):
            write(frame, l)
            dirs.append(l)
    if len(dirs) == 1:
        #We know we have S. Otherwise there were multiple directories unpacked
        p = dirs[0]
        if p == GetP(frame):
            write(frame, "S=${WORKDIR}/${P}")
            SetS(frame, p)
        else:
            ep = frame.panelMain.S.GetValue()
            if ep == "${WORKDIR}/${P}":
                frame.panelMain.S.SetValue("${WORKDIR}/%s" % p)
                SetS(frame, p)
    else:
        if GetS(frame) == "${WORKDIR}/${P}":
            write(frame, "More than one directory unpacked, you get to guess what ${S} is.")
    logColor(frame, "BLACK")
    ViewConfigure(frame)
    ViewMakefile(frame)

def SetS(frame, myp):
    """Set S"""
    p = GetP(frame)
    frame.s = "%s/portage/%s/work/%s" % (portage_tmpdir, p, myp)

def ExecuteInLog(frame, cmd):
    """Run a program and send stdout & stderr to the log window"""
    if frame.running:
        msg = ("Please wait till this finishes:\n %s" % frame.running)
        title = 'Abeni: Error - Wait till external program is finished.'
        MyMessage(frame, msg, title, "error")
        return
    frame.running = cmd
    frame.tb.EnableTool(frame.toolStopID, True)
    frame.process = wxProcess(frame)
    frame.process.Redirect();
    pyCmd = "python -u %s/doCmd.py %s" % (modulePath, cmd)
    frame.pid = wxExecute(pyCmd, wxEXEC_ASYNC, frame.process)
    ID_Timer = wxNewId()
    frame.timer = wxTimer(frame, ID_Timer)
    EVT_TIMER(frame,  ID_Timer, frame.OnTimer)
    frame.timer.Start(100)


def ClearNotebook(frame):
    """Delete all pages in the notebook"""
    frame.nb.DeleteAllPages()
    frame.funcList = []
    frame.statementList = []
    frame.funcOrder = []
    frame.varOrder = []

def SetFilename(frame, filename):
    """Set the ebuild full path and filename"""
    #Keep last file for viewing and creating diffs(future feature)
    frame.lastFile = frame.filename
    frame.filename = filename
    frame.sb.SetStatusText(filename, 1)

def SeparateVars(vars):
    """Separates variables into defaultVars and all others (vars)"""
    defaultVars = {}
    for key in defaults:
        if vars.has_key(key):
            defaultVars[key] = vars[key]
            del vars[key]
        else:
            defaultVars[key] = ""
    return defaultVars, vars

def VerifySaved(frame):
    """Check if the ebuild has changed and offer to save if so"""
    modified = 0
    status = 0
    for fns in frame.funcList:
        if fns.edNewFun.GetModify():
            modified = 1
            break
    if modified or not frame.saved:
        dlg = wxMessageDialog(frame, 'Save modified ebuild?\n' + frame.filename,
                'Save ebuild?', wxYES_NO | wxCANCEL | wxICON_INFORMATION)
        val = dlg.ShowModal()
        if val == wxID_YES:
            msg = checkEntries(frame)
            if msg:
                status = 1
                dlg.Destroy()
                msg = "Set your ebuild name and package name properly."
                MyMessage(frame, msg, "Can't save", "error")
                return status
            WriteEbuild(frame)
            frame.saved = 1
            status = 0
        if val == wxID_NO:
            status = 0
        if val == wxID_CANCEL:
            status = 1
        dlg.Destroy()
    return status

def PopulateForms(frame, defaultVars):
    """Fill forms with saved data"""
    frame.panelMain.Package.SetValue(defaultVars['package'])
    frame.package = defaultVars['package']
    frame.panelMain.EbuildFile.SetValue(defaultVars['ebuild_file'])
    frame.panelMain.Category.SetValue(defaultVars['category'])
    frame.panelMain.URI.SetValue(defaultVars['SRC_URI'])
    frame.panelMain.Homepage.SetValue(defaultVars['HOMEPAGE'])
    frame.panelMain.Desc.SetValue(defaultVars['DESCRIPTION'])
    frame.panelMain.S.SetValue(defaultVars['S'])
    frame.panelMain.USE.SetValue(defaultVars['IUSE'])
    frame.panelMain.Slot.SetValue(defaultVars['SLOT'])
    frame.panelMain.Keywords.SetValue(defaultVars['KEYWORDS'])
    frame.panelMain.License.SetValue(defaultVars['LICENSE'])
    d = string.split(defaultVars['DEPEND'], '\n')
    depends = []
    for s in d:
        s = s.replace('"', '')
        depends.append(s)
    frame.panelDepend.elb1.SetStrings(depends)
    r = string.split(defaultVars['RDEPEND'], '\n')
    rdepends = []
    for s in r:
        s = s.replace('"', '')
        rdepends.append(s)
    frame.panelDepend.elb2.SetStrings(rdepends)

def NewPage(frame, panel, name):
    """Add new page to notebook"""
    frame.nb.AddPage(panel, name)
    frame.tabs.append(name)

def AddFunc(frame, newFunction, val):
    """Add page in notebook for a new function"""
    n = panels.NewFunction(frame.nb)
    frame.funcList.append(n)
    NewPage(frame, n, newFunction)
    n.edNewFun.SetText(val)
    n.edNewFun.SetSavePoint()


def AddEditor(frame, name, val):
    """Add page in notebook for an editor"""
    if name == 'Output':
        n = panels.NewFunction(frame.nb)
        n.edNewFun.SetText(val)
        n.edNewFun.SetReadOnly(1)
        frame.ebuildfile = n
    else:
        n = panels.Editor(frame.nb)
        n.editorCtrl.SetText(val)
    NewPage(frame, n, name)
    if name == 'configure' or name == 'Makefile' or name == 'Environment':
        n.editorCtrl.SetReadOnly(1)


def SaveEbuild(frame):
    '''Save ebuild if entries are sane'''
    msg = checkEntries(frame)
    if not msg:
        defaultVars = getDefaultVars(frame)
        WriteEbuild(frame)
        frame.saved = 1
        DoTitle(frame)
        return 1
    else:
        title = 'Abeni: Error Saving'
        MyMessage(frame, msg, title, "error")
        return 0

def ExportEbuild(frame):
    ''' Export ebuild directory to tar file '''
    GetEnvs(frame)
    if SaveEbuild(frame):
        filelist = []
        filelist.append(GetFilename(frame))
        # auto-add the digest
        filelist.append(frame.env['FILESDIR']+"/digest-"+GetP(frame))
        auxfilelist = [f for f in os.listdir(frame.env['FILESDIR']) if f[:6] != "digest"]

        # add all filenames that are present in the ebuild and ask
        # the user about the others.
        # Hmm, the multi-choice dialog does not allow to pre-select anything
        # I'd like to select all files by default, but I guess that needs a custom dialog then.
        #ebuild_content = frame.ebuildfile.editorCtrl.GetText()
        ebuild_content = frame.ebuildfile.edNewFun.GetText()
        for f in auxfilelist:
            if re.search(f+"[^a-zA-Z0-9\-\.\?\*]", ebuild_content):
                filelist.append(frame.env['FILESDIR']+"/"+f)
                write(frame, "auto adding file: " + f)
                auxfilelist.remove(f)
        if len(auxfilelist) > 0:
            msg = "Select the files you want to include in the tarball.\n(don't worry about the digest,\nit will be included automatically)"
            fileselectdlg = wxMultipleChoiceDialog(frame, msg, "Auxiliary file selection",
                                                   auxfilelist, size=(300,min([500,150+len(auxfilelist)*20])))
            if fileselectdlg.ShowModal() == wxID_OK:
                auxfilelist = [frame.env['FILESDIR']+"/"+f for f in list(fileselectdlg.GetValueString())]
            else:
                return 0
        filelist += auxfilelist

        filelist = [f.replace(GetCategoryPath(frame)+"/", "") for f in filelist]

        tarballname = GetP(frame)+".tar.bz2"
        filemask = "BZipped tarball (*.tar.bz2)|*.tar.bz2|GZipped tarball (*.tar.gz)|*.tar.gz|Uncompressed tarball (*.tar)|*.tar|All files|*"
        filedlg = wxFileDialog(frame, "Export ebuild to tarball", "", tarballname, filemask, wxSAVE|wxOVERWRITE_PROMPT)
        if filedlg.ShowModal() == wxID_OK:
            tarballname = filedlg.GetPath()
            filedlg.Destroy()
        else:
            filedlg.Destroy()
            return 0

        if tarballname[-8:] == ".tar.bz2":
            taroptions = "-cvjf"
        elif tarballname[-7:] == ".tar.gz":
            taroptions = "-cvzf"
        else:
            taroptions = "-cvf"

        ExecuteInLog(frame, "tar "+taroptions+" "+tarballname+" -C "+GetCategoryPath(frame)+" "+reduce(lambda a,b: a+" "+b, filelist))

        # FUTURE: once we have python-2.3 we can use the following:
        #os.chdir(frame.GetCategoryPath())
        #tarball = tarfile.open(tarballname, "w:bz2")
        #for f in filelist:
        #    tarball.add(f)
        #tarball.close()
        frame.sb.SetStatusText("Ebuild exported to " + tarballname, 0)
        return 1
    else:
        return 0

def GetCatPackVer(frame):
   """Get category package version: net-www/mozilla-1.0-r1"""
   return "%s/%s" % (GetCategoryName(frame), GetP(frame))

def GetEbuildDir(frame):
    return os.path.join (GetCategoryPath(frame), GetPackageName(frame))

def GetFilename(frame):
    """Get the full path and filename of ebuild"""
    return frame.filename

#def GetFilename(frame):
#    """Get the full path and filename of ebuild"""
#    return "%s/%s/%s.ebuild" % (GetCategoryPath(frame), GetPackageName(frame), GetCatPackVer(frame))
 
def GetP(frame):
    """ Returns P from the ebuild name"""
    ebuild = frame.panelMain.EbuildFile.GetValue()
    p = string.replace(ebuild, '.ebuild', '')
    return p

def GetCategoryPath(frame):
    """Return path to category of ebuild"""
    categoryDir = os.path.join (portdir_overlay, frame.panelMain.Category.GetValue())
    return categoryDir

def GetPackageName(frame):
    """Return PN from form"""
    return frame.panelMain.GetPackageName()

def GetCategoryName(frame):
    """Return Category name from form"""
    return frame.panelMain.GetCategoryName()

def checkEntries(frame):
    """Validate entries on forms"""
    category = frame.panelMain.Category.GetValue()
    categoryDir = GetCategoryPath(frame)
    valid_cat = os.path.join(portdir, category)
    if categoryDir == portdir_overlay + '/':
        msg = "You must specify a category."
        return msg
    if not os.path.exists(valid_cat):
        msg = category + " isn't a valid category."
        return msg
    pn = frame.panelMain.GetPackageName()
    if not pn:
        msg = "You need to set the Package Name"
        return msg
    e = frame.panelMain.GetEbuildName()
    if not e:
        msg = "You need to set the Ebuild Name"
        return msg
    if e[-7:] != '.ebuild':
        msg = "Ebuild file must end with '.ebuild'"
        return msg
    p = frame.panelMain.GetPackage()
    l = pkgsplit(p)
    if not l:
        msg = "You need to fix the Package Name and Ebuild Name"
        return msg
    if pn != l[0]:
        msg = "Package Name does not match Ebuild Name"
        return msg

def DoTitle(frame):
    ''' Set application's titlebar '''
    if not frame.saved:
        frame.SetTitle(frame.panelMain.GetEbuildName() + " * Abeni " + __version__.version)
    else:
        frame.SetTitle(frame.panelMain.GetEbuildName() + " - Abeni " + __version__.version)

def AddPages(frame):
    """Add pages to blank notebook"""
    frame.panelMain=panels.main(frame.nb, env)
    frame.panelDepend=panels.depend(frame.nb)
    frame.panelChangelog=panels.changelog(frame.nb)
    NewPage(frame, frame.panelMain, "Main")
    NewPage(frame, frame.panelDepend, "Dependencies")
    NewPage(frame, frame.panelChangelog, "ChangeLog")


def isDefault(frame, var):
    """ Return 1 if varibale is in list of default ebuild variables"""
    for l in defaults:
        if var == l:
            return 1

def LoadByPackage(frame, query):
    """Offer list of ebuilds when given a package or filename on command line"""

    matches = gentoolkit.find_packages(query, masked=True)
    matches = gentoolkit.sort_package_list(matches)
    #if len(matches) > 1:
    #    print "More than one package matches that name. Use full category/packagename."
        #for pkg in matches:
        #    print pkg.get_category()+"/"+pkg.get_name()
        #return
    if len(matches):
        cat = matches[0].get_category()
        package = matches[0].get_name()
        pkgs = []
        
        print "* " + matches[0].get_category()+"/"+matches[0].get_name()+ " :"
        for pkg in matches:
                
            state = []
            unstable = 0
            overlay = ""
                
            # check if masked
            if pkg.is_masked():
                state.append("M")
            else:
                state.append(" ")

            # check if in unstable
            kwd = pkg.get_env_var("KEYWORDS")
            if "~" + gentoolkit.settings["ARCH"] in kwd.split():
                state.append("~")
                unstable = 1
            else:
                state.append(" ")
                    
            # check if installed
            if pkg.is_installed():
                state.append("I")
            else:
                state.append(" ")

            # check if this is a OVERLAY ebuild
            if pkg.is_overlay():
                overlay = " OVERLAY"

            ver = pkg.get_version()
            slot = pkg.get_env_var("SLOT")
            print " "*8 + "[" + string.join(state,"") + "] " + ver + " (" + slot + ")" + overlay
            pkgs.append (ver + " (" + slot + ")" + overlay)

 
        dlg = wxSingleChoiceDialog(frame, cat + "/" + package, 'Ebuilds Available',
                    pkgs, wxOK|wxCANCEL)
        if dlg.ShowModal() == wxID_OK:
            s = dlg.GetStringSelection().split(' ')
            version = s[0] 
            
            if len(s) == 3:
                fname = '%s/%s/%s/%s-%s.ebuild' % \
                        (portdir_overlay, cat, package, package, version)
            else:
                    fname = '%s/%s/%s/%s-%s.ebuild' % \
                            (portdir, cat, package, package, version)
            LoadEbuild(frame, fname, portdir)
        dlg.Destroy()
    else:
        print "Package " + query + " not found. Use full package name."


def GetS(frame):
    """grep S from environment file"""
    p = GetP(frame)
    e = '%s/portage/%s/temp/environment' % (portage_tmpdir, p)
    if not os.path.exists(e):
        return 0
    f = open(e, 'r')
    l = f.readline()
    while l:
        if l[0:2] == "S=":
            return l[2:].strip()
        l = f.readline()
    #This should never get reached, since there should always be an S:
    return 0


def ViewMakefile(frame):
    """Show Makefile in editor window"""
    s = GetS(frame)
    if s:
        f = '%s/Makefile' % s
        if os.path.exists(f):
            try:
                frame.nb.RemovePage(frame.tabs.index('Makefile'))
                del frame.tabs[frame.tabs.index('Makefile')]
            except:
                pass
            AddEditor(frame, 'Makefile', open(f, 'r').read())

def GetEnvs(frame):
    """Get the 'major' environmental vars"""
    frame.env = {}
    p = frame.panelMain.EbuildFile.GetValue()[:-7]
    f = '%s/portage/%s/temp/environment' % (portage_tmpdir, p)
    if not os.path.exists(f):
        cmd = '/usr/sbin/ebuild %s setup' % frame.filename
        write(frame, cmd)
        os.system(cmd)
    lines = open(f, 'r').readlines()
    #TODO: This is a partial list. Should add option to show all vars available.
    envVars = ['A', 'AA', 'AUTOCLEAN', 'BUILDDIR', 'BUILD_PREFIX', \
            'D', 'DESTTREE', 'EBUILD', 'FEATURES', 'FILESDIR', \
            'INHERITED', 'KV', 'KVERS', 'O', 'P', 'PF', 'PN', 'PV', \
            'PVR', 'RESTRICT', 'S', 'SRC_URI', 'T', 'WORKDIR']
    for l in lines:
        if "=" in l:
            s = string.split(l, '=')
            var = s[0]
            val = s[1]
            if var in envVars:
                frame.env[var] = val.strip()

def ViewConfigure(frame):
    """Show configure file in editor window"""
    s = GetS(frame)
    f = '%s/configure' % s
    if os.path.exists(f):
        try:
            frame.nb.RemovePage(frame.tabs.index('configure'))
            del frame.tabs[frame.tabs.index('configure')]
        except:
            pass
        AddEditor(frame, 'configure', open(f, 'r').read())

def CheckUnpacked(frame):
    """Return 1 if they have unpacked"""
    if os.path.exists('%s/portage/%s/.unpacked' % (portage_tmpdir, GetP(frame))):
        return 1
    else:
        return 0

def ViewEnvironment(frame):
    """Show environment file in editor window"""
    #TODO: This is brief version, the commented out line below gives full environment.
    #Add config option to show either, or menu option. Or both.
    GetEnvs(frame)
    txt = ''
    keys = frame.env.keys()
    keys.sort()
    for k in keys:
        txt += '%s=%s\n' % (k, frame.env[k])
    p = frame.panelMain.EbuildFile.GetValue()[:-7]
    f = '%s/portage/%s/temp/environment' % (portage_tmpdir, p)
    if os.path.exists(f):
        try:
            frame.nb.RemovePage(frame.tabs.index('Environment'))
            del frame.tabs[frame.tabs.index('Environment')]
        except:
            pass
        AddEditor(frame, 'Environment', txt)

def SetToNewPage(frame):
    ''' Change pages in notebook '''
    frame.nb.SetSelection(frame.nb.GetPageCount() -1)

def GetTemplates(frame):
    """Return list of Eclass templates to load"""
    import Templates
    funcs = dir(Templates)
    c = []
    for l in funcs:
        if l[0:2] == 'my':
            c.append(l[2:])
    return c

def NotGentooDev(frame):
    ''' Warn user about non-developers using CVS '''
    e = frame.pref['email']
    if not e:
        msg = "CVS options are for official Gentoo Developers:\n\n \
              Your email address is not set.\n \
              Set your email address in Options - Global Preferences."
    else:
        msg = "CVS options are for official Gentoo Developers:\n\n \
              Your email address doesn't end in @gentoo.org\n \
              Set your email address in Options - Global Preferences."
    MyMessage(frame, msg, "Gentoo Developer?", "error")


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
        write(parent, "File not found: " + filename)
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
        write(parent, "Ebuild syntax is incorrect - /bin/bash found an error. Fix this before trying to load:")
        for l in out:
            write(parent, l)
        msg = "The ebuild has a syntax error. Would you like to edit this in your external editor?"
        dlg = wxMessageDialog(parent, msg,
                'Syntax Error', wxOK | wxCANCEL | wxICON_ERROR)
        val = dlg.ShowModal()
        if val == wxID_OK:
            parent.OnMnuEdit(save=0, filename=filename)
        return
    SetFilename(parent, filename)
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

        varTest = re.search('^[A-Za-z]+.*= ?', l)

        # Match any of these:
        #  mine() {
        #  mine () {
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
        if re.search('^([a-zA-Z]|#|\[)', l):
            parent.statementList.append(l)

    f.close()

    s = string.split(filename, "/")
    parent.ebuild_file = s[len(s)-1]
    package = s[len(s)-2]
    category = s[len(s)-3]
    defaultVars = {}
    otherVars = {}
    defaultVars, otherVars = SeparateVars(vars)
    defaultVars['package'] = package
    defaultVars['ebuild_file'] = parent.ebuild_file
    defaultVars['category'] = category

    if defaultVars['S'] == '':
        defaultVars['S'] = '${WORKDIR}/${P}'

    #You must set IUSE, even if you don't use it.
    if defaultVars['IUSE'] == '':
        defaultVars['IUSE'] = '""'
    parent.editing = 1
    AddPages(parent)
    PopulateForms(parent, defaultVars)
    parent.ebuildDir = string.replace(filename, parent.ebuild_file, '')

    #Load ChangeLog if in PORTDIR_OVERLAY, otherwise check PORTDIR, else use skel
    #This is read-only, you must use "echangelog" to edit the ChangeLog
    clog = string.replace(filename, parent.ebuild_file, '') + 'ChangeLog'
    if os.path.exists(clog):
        changelog_txt = open(clog).read()
    else:
        category = parent.panelMain.Category.GetValue()
        name = parent.panelMain.Package.GetValue()
        portdir_clog = "%s/%s/%s/ChangeLog" % (portdir, category, name)
        if os.path.exists(portdir_clog):
            changelog_txt = open(portdir_clog).read()
        else:
            filename= '%s/skel.ChangeLog' % portdir
            changelog_txt = open(filename).read()
    parent.panelChangelog.Populate(changelog_txt)

    # Add original ebuild file:
    AddEditor(parent, 'Output', open(filename, 'r').read())
    #Add custom variables to Main panel

    #This was un-ordered:
    #for v in otherVars:
    #    parent.AddNewVar(v, otherVars[v])

    # Put them in panel in the order they were in the ebuild
    for n in range(len(parent.varOrder)):
        for v in otherVars:
            if v == parent.varOrder[n]:
                AddNewVar(parent, v, otherVars[v])
    if CheckUnpacked(parent):
        ViewEnvironment(parent)
        ViewConfigure(parent)
        ViewMakefile(parent)
    #TODO: Put them in logical order: pkg_setup, src_unpack, src_compile etc.
    #Add functions in order they were in in ebuild:
    for n in range(len(parent.funcOrder)):
        AddFunc(parent, parent.funcOrder[n], funcs[parent.funcOrder[n]])
    parent.panelMain.stext.SetValue(string.join(parent.statementList, '\n'))
    if parent.pref['log'] != 'bottom':
        LogWindow()
    parent.nb.SetSelection(0)

    # Set titlebar of app to ebuild name
    DoTitle(parent)

def WriteEbuild(parent, temp=0):
    """Format data into fields and output to ebuild file"""
    categoryDir = GetCategoryPath(parent)
    if not os.path.exists(categoryDir):
        os.mkdir(categoryDir)
    #TODO: Hmmm:
    parent.ebuildDir = GetEbuildDir(parent)
    if not os.path.exists(parent.ebuildDir):
        os.mkdir(parent.ebuildDir)
    filename = os.path.join(parent.ebuildDir, parent.panelMain.EbuildFile.GetValue())
    SetFilename(parent, filename)
    parent.filehistory.AddFileToHistory(filename.strip())
    f = open(filename, 'w')
    f.write('# Copyright 1999-2004 Gentoo Foundation\n')
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
            if not isDefault(parent, parent.varOrder[n]):
                f.write(parent.varOrder[n] + '=' + varDict[parent.varOrder[n]][1].GetValue() + '\n')

    f.write('\n')

    # This would print them in original order imported:
    #for n in range(len(parent.varOrder)):
    #    if parent.isDefault(parent.varOrder[n]):
    #        f.write(parent.varOrder[n] + '=' + varList[parent.varOrder[n]].GetValue() + '\n')

    #Default variables
    f.write('DESCRIPTION=' + parent.panelMain.Desc.GetValue() + '\n')
    f.write('HOMEPAGE=' + parent.panelMain.Homepage.GetValue() + '\n')
    f.write('SRC_URI=' + parent.panelMain.URI.GetValue() + '\n')
    f.write('LICENSE=' + parent.panelMain.License.GetValue() + '\n')
    f.write('SLOT=' + parent.panelMain.Slot.GetValue() + '\n')
    f.write('KEYWORDS=' + parent.panelMain.Keywords.GetValue() + '\n')
    f.write('IUSE=' + parent.panelMain.USE.GetValue() + '\n')
    my_s = parent.panelMain.S.GetValue().strip()
    # Never write S= ${WORKDIR}/${P} because its the default. Bugzilla #25708
    if my_s != "${WORKDIR}/${P}" and my_s != '"${WORKDIR}/${P}"' and my_s != "'${WORKDIR}/${P}'":
        f.write('S=' + parent.panelMain.S.GetValue() + '\n')

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

    #changelog = os.path.join(parent.ebuildDir, 'ChangeLog')
    #f = open(changelog, 'w')
    #f.write(parent.panelChangelog.edChangelog.GetText())
    #f.close()
    parent.recentList.append(filename)
    parent.sb.SetStatusText("Saved", 0)
    #parent.write("Saved %s" % filename)
    #TODO: Kludgy? It doesn't work on first save of new ebuild.
    try:
        parent.ebuildfile.edNewFun.SetReadOnly(0)
    except:
        pass
    #try:
    parent.ebuildfile.edNewFun.SetText(open(filename, 'r').read())
    #except:
    #    print "Couldn't write to Output"
    #    pass
    try:
        parent.ebuildfile.edNewFun.SetReadOnly(1)
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
    ''' Create Toolbar with icons '''
    # icons are ~28x~28
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
                            "Edit ebuild in external editor F7")
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
    EVT_TOOL(parent, xtermID, parent.OnXtermInS)

    #Load recent ebuilds to File menu
    #TODO: Delete reference if they no longer exist
    for ebuild in parent.recentList:
        parent.filehistory.AddFileToHistory(ebuild.strip())

    parent.tb.AddSeparator()
    parent.noautoID = wxNewId()
    b = wxToggleButton(parent.tb, parent.noautoID, "noauto")
    EVT_TOGGLEBUTTON(parent, parent.noautoID, OnNoAuto)
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
    #OnNoAuto(frame, -1)
    b.SetValue(True)

def DelVariable(parent):
    ''' Delete variable '''
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
