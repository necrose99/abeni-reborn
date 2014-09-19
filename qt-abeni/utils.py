import commands
import pwd
import os
import string
import sys
import re
import popen2
import shutil

import wx
from wx.lib.dialogs import MultipleChoiceDialog
from portage import config, portdb, db, pkgsplit, catpkgsplit, settings
sys.path.insert(0, "/usr/lib/gentoolkit/pym")
import gentoolkit

import options
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

#Lets choose the first arch they have, in case of multiples.
#TODO: Mention in documentation
#arch = '~%s' % env['ACCEPT_KEYWORDS'].split(' ')[0].replace('~', '')
arch = '%s' % env['ACCEPT_KEYWORDS'].split(' ')[0]


#TODO: We might get this every time from /etc/make.conf in case
#      its changed while Abeni is running? 
def GetArch():
    """Returns first arch listed in ACCEPT_KEYWORDS in /etc/make.conf"""
    return arch

def search(search_key):
    matches = []
    for package in portdb.cp_all():
        package_parts=package.split("/")
        if re.search(search_key.lower(), package_parts[1].lower()):
            matches.append(package)
    return matches

def versions(query):
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


def MyMessage(parent, msg, title, type="info", cancel=0):
    """Simple informational dialog"""
    if type == "info":
        icon = wx.ICON_INFORMATION
    elif type == "error":
        icon = wx.ICON_ERROR
    if cancel:
        dlg = wx.MessageDialog(parent, msg, title, wx.OK | wx.CANCEL | icon)
    else:
        dlg = wx.MessageDialog(parent, msg, title, wx.OK | icon)
    if (dlg.ShowModal() == wx.ID_OK):
        return 1
    else:
        dlg.Destroy()
        return 0

def LogWindow(parent):
    """Show log in separate window"""
    if parent.splitter.IsSplit():
        parent.splitter.Unsplit()
        parent.logWin=MyLog.LogWindow(parent)
        parent.logWin.Show(True)
        parent.text_ctrl_log.Show(True)
        parent.pref['log'] = 'window'
        parent.menu_options.Check(parent.mnuLogWindowID, 1)

#TODO: Add this option back in? I never actually used it myself.
def LogBottom(parent, log):
    """Show log at the bottom"""
    parent.menu_options.Check(parent.mnuLogBottomID, 1)
    parent.text_ctrl_log = log
    parent.text_ctrl_log.Reparent(parent.splitter)
    wx.Log_SetActiveTarget(MyLog(parent.text_ctrl_log))
    parent.splitter.SplitHorizontally(parent.nb, parent.text_ctrl_log, 400)
    parent.splitter.SetMinimumPaneSize(20)
    parent.text_ctrl_log.Show(True)
    parent.pref['log'] = 'bottom'


def WriteText(parent, text):
    """Send text to log window after colorizing"""
    parent.busywriting = 1
    #TODO: No idea why this is output at the end of every ExecuteInLog:
    #TODO: Log file to disk code can go here 
    if string.find(text, "md5 src_uri") == 4:
        if parent.action != 'unpack':
            return

    if parent.pref['logfile'] == 1:
        parent.logfile.write(text + "\n")

    if text[-1:] == '\n':
        text = text[:-1]
    #Remove color and other esc codes
    text = text.replace('\b', '')
    text = text.replace("\x1b[0m" , '')
    text = text.replace("\x1b[01m", '')
    text = text.replace("\x1b[32;01m" , '')
    text = text.replace("\x1b[32;06m" , '')
    text = text.replace("\x1b[31;06m", '')
    text = text.replace("\x1b[31;01m", '')
    text = text.replace("\x1b[33;06m", '')
    text = text.replace("\x1b[33;01m", '')
    text = text.replace("\x1b[32;06m", '')
    text = text.replace("\x1b[32;01m", '')
    text = text.replace("\x1b[34;06m", '')
    text = text.replace("\x1b[35;06m", '')
    text = text.replace("\x1b[34;01m", '')
    text = text.replace("\x1b[35;01m", '')
    text = text.replace("\x1b[36;01m", '')
    text = text.replace("\x1b[36;06m", '')
    # For the [ok]'s
    text = text.replace("\x1b[A", '')
    text = text.replace("\x1b[-7G", '')

    pref = text[0:3]
    if pref == ">>>" or pref == "<<<" or pref == "---" \
         or pref == ")))" or  pref == " * ":
        log_color(parent, "BLUE")
        wx.LogMessage(text)
        log_color(parent, "BLACK")
    elif pref == "!!!":
        log_color(parent, "RED")
        wx.LogMessage(text)
        log_color(parent, "BLACK")
    else:
        wx.LogMessage(text)

    parent.busywriting = 0

def log_color(parent, color):
    """Set color of text sent to log window"""
    parent.text_ctrl_log.SetDefaultStyle(wx.TextAttr(wx.NamedColour(color)))

def write(parent, txt):
    """Send text to log window"""
    if parent.stdout:
        print txt
    WriteText(parent, txt)

def PostAction(parent, action):
    """Execute code after asynchronous job done with ExecuteInLog finishes"""
    if action == "setup":
        ViewEnvironment(parent)
        parent.RefreshExplorer()
    if action == "clean":
        write(parent, "))) All clean.")
        parent.RefreshExplorer()
        ViewEnvironment(parent)
    if action == 'digest':
        parent.RefreshExplorer()
    if action == 'unpack':
        PostUnpack(parent)
        parent.RefreshExplorer()
    if action == 'compile':
        parent.RefreshExplorer()
        log_to_output(parent)
        write(parent, "))) compile finished")
    if action == 'install':
        PostInstall(parent)
        log_to_output(parent)
        parent.RefreshExplorer()
        write(parent, "))) install finished")
    if action == 'qmerge':
        parent.RefreshExplorer()
        log_to_output(parent)
        write(parent, "))) qmerge finished")
    if action == 'emerge':
        parent.RefreshExplorer()
        log_to_output(parent)
        write(parent, "))) emerge finished")
    parent.statusbar.SetStatusText("%s done." % action, 0)

def log_to_output(parent):
    """Get logfile text and display in output tab"""
    #TODO: Run through WriteText or something to get color/filter esc codes
    t = commands.getoutput("sudo cat /var/tmp/abeni/emerge_log")
    parent.text_ctrl_log.AppendText("%s\n" % t)

def ExportEbuild(parent):
    """Export ebuild directory to tar file"""
    if not VerifySaved(parent):
        filelist = []
        filelist.append(GetFilename(parent))
        # auto-add the digest
        fdir = GetFilesDir(parent)
        filelist.append(fdir + "/digest-"+getP(parent))
        auxfilelist = [f for f in os.listdir(fdir) if f[:6] != "digest"]

        # add all filenames that are present in the ebuild and ask
        # the user about the others.
        # Hmm, the multi-choice dialog does not allow to pre-select anything
        # I'd like to select all files by default, but I guess that needs a custom dialog then.
        #ebuild_content = parent.ebuildfile.editorCtrl.GetText()
        ebuild_content = parent.STCeditor.GetText()
        for f in auxfilelist:
            if re.search(f+"[^a-zA-Z0-9\-\.\?\*]", ebuild_content):
                filelist.append(fdir +"/"+f)
                write(parent, "auto adding file: " + f)
                auxfilelist.remove(f)
        if len(auxfilelist) > 0:
            msg = "Select the files you want to include in the tarball.\n(don't worry about the digest,\nit will be included automatically)"
            fileselectdlg = MultipleChoiceDialog(parent, msg, "Auxiliary file selection",
                                                   auxfilelist, size=(300,min([500,150+len(auxfilelist)*20])))
            if fileselectdlg.ShowModal() == wx.ID_OK:
                auxfilelist = [fdir +"/"+f for f in list(fileselectdlg.GetValueString())]
            else:
                return 0
        filelist += auxfilelist

        filelist = [f.replace(GetCategoryPath(parent)+"/", "") for f in filelist]

        tarballname = getP(parent)+".tar.bz2"
        filemask = "BZipped tarball (*.tar.bz2)|*.tar.bz2|GZipped tarball (*.tar.gz)|*.tar.gz|Uncompressed tarball (*.tar)|*.tar|All files|*"
        filedlg = wx.FileDialog(parent, "Export ebuild to tarball", "", tarballname, filemask, wx.SAVE|wx.OVERWRITE_PROMPT)
        if filedlg.ShowModal() == wx.ID_OK:
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

        ExecuteInLog(parent, "tar "+taroptions+" "+tarballname+" -C "+GetCategoryPath(parent)+" "+reduce(lambda a,b: a+" "+b, filelist))

        # FUTURE: once we have python-2.3 we can use the following:
        #os.chdir(parent.GetCategoryPath())
        #tarball = tarfile.open(tarballname, "w:bz2")
        #for f in filelist:
        #    tarball.add(f)
        #tarball.close()
        parent.statusbar.SetStatusText("Ebuild exported to " + tarballname, 0)
        return 1
    else:
        return 0

def PostInstall(parent):
    """Change group perms of files in ${D} so we can read them"""
    p = getP(parent)
    d = '%s/portage/%s/image' % (portage_tmpdir, p)
    os.system("sudo chmod +g+r -R %s" %  d)
    os.system("sudo chmod +g+xr %s" %  d)

def get_status(parent):
    """Let us know if ebuild has been unpacked, comiled and installed"""
    p = getP(parent)
    d = '%s/portage/%s' % (portage_tmpdir, p)
    if not os.path.exists(d):
        return
    fs = ['.unpacked', '.compiled', '.installed']
    out = []
    for f in fs:
        if os.path.exists(os.path.join(d,f)): 
            out.append(f)
    if len(out):
        write(parent, "))) This package is:")
        for o in out:
            if o == ".unpacked":
                write(parent, ")))     unpacked")
                fix_unpacked(parent)
            if o == ".compiled":
                write(parent, ")))     compiled")
            if o == ".installed":
                write(parent, ")))     installed")

def fix_unpacked(parent):
    """chmod for portage group read"""
    p = getP(parent)
    d = '%s/portage/%s/work' % (portage_tmpdir, p)
    d1 = '%s/portage/%s' % (portage_tmpdir, p)
    #uname = pwd.getpwuid(os.getuid())[0]
    #Yay! Can we say 'kludge'?
    #print uname, d
    #os.system("sudo chown %s -R %s" % (uname, d1))
    os.system("sudo chmod +g+xrw -R %s &" % d1)

def PostUnpack(parent):
    """Report what directories were unpacked, try to set S if necessary"""
    p = getP(parent)
    d = '%s/portage/%s/work' % (portage_tmpdir, p)
    d1 = '%s/portage/%s' % (portage_tmpdir, p)
    #uname = pwd.getpwuid(os.getuid())[0]
    #Yay! Can we say 'kludge'?
    #print uname, d
    #os.system("sudo chown %s -R %s" % (uname, d1))
    fix_unpacked(parent)
    #print "done"
    try:
        lines = os.listdir(d)
    except:
        return
    dirs = []
    #logColor(parent, "RED")
    write(parent, "))) These directory(s) are in ${WORKDIR}:")
    for l in lines:
        if os.path.isdir("%s/%s" % (d, l)):
            write(parent, " * %s" % l)
            dirs.append(l)
    if len(dirs) == 1:
        #We know we have S. Otherwise there were multiple directories unpacked
        p = dirs[0]
        if p == getP(parent):
            write(parent, " * S=${WORKDIR}/${P}")
            if parent.FindReplace("S=${WORKDIR}/${P}", "") != -1:
                SetS(parent, p)
                write(parent, "))) removed S=${WORKDIR}/${P} from ebuild (its not necessary)")
        else:
            ep = GetS(parent)
            if ep == "${WORKDIR}/${P}":
                write(parent, "S=${WORKDIR}/%s" % p)
                SetS(parent, p)
    else:
        if GetS(parent) == "${WORKDIR}/${P}":
            write(parent, "))) More than one directory unpacked, you get to guess what ${S} is.")
    log_color(parent, "BLACK")

def SetS(parent, myp):
    """Set S"""
    p = getP(parent)
    parent.s = "%s/portage/%s/work/%s" % (portage_tmpdir, p, myp)

def ExecuteInLog(parent, cmd, logMsg=''):
    """Run a program and send stdout & stderr to the log window"""
    if parent.running:
        msg = ("Please wait till this finishes:\n %s" % parent.running)
        title = 'Abeni: Error - Wait till external program is finished.'
        MyMessage(parent, msg, title, "error")
        return
    if logMsg:
        write(parent, logMsg)
    parent.running = cmd
    parent.toolbar.EnableTool(parent.StopID, True)
    parent.process = wx.Process(parent)
    parent.process.Redirect();
    pyCmd = "python -u %s/doCmd.py %s" % (modulePath, cmd)
    parent.pid = wx.Execute(pyCmd, wx.EXEC_ASYNC, parent.process)
    #parent.pid = wx.Execute("sh -c '%s'" % cmd, wx.EXEC_ASYNC, parent.process)
    #TODO: Maybe add option to show commands as they execute
    #write(parent, cmd)
    ID_Timer = wx.NewId()
    parent.timer = wx.Timer(parent, ID_Timer)
    wx.EVT_TIMER(parent,  ID_Timer, parent.OnTimer)
    parent.timer.Start(100)

def Reset(parent):
    """Reset abeni for new/loaded ebuild"""
    parent.button_Category.Enable(True)
    parent.text_ctrl_Category.Enable(True)
    parent.text_ctrl_PN.Enable(True)
    parent.text_ctrl_PVR.Enable(True)
    parent.text_ctrl_Category.SetValue("")
    parent.text_ctrl_PN.SetValue("")
    parent.text_ctrl_PVR.SetValue("")
    parent.STCeditor.SetText("")
    if parent.pref['clearLog'] == 1:
        parent.text_ctrl_log.Clear()
    parent.text_ctrl_environment.Clear()
    parent.editing = 0
    parent.statusbar.SetStatusText('', 1)
    parent.filename = ""

def VerifySaved(parent):
    """Check if the ebuild has changed and offer to save if so"""
    status = 0

    if parent.STCeditor.GetModify() or not parent.saved:
        dlg = wx.MessageDialog(parent, 'Save modified ebuild?\n' + parent.filename,
                'Save ebuild?', wx.YES_NO | wx.CANCEL | wx.ICON_INFORMATION)
        val = dlg.ShowModal()
        if val == wx.ID_YES:
            msg = checkEntries(parent)
            if msg:
                status = 1
                dlg.Destroy()
                msg = "Check your category, package name and package version."
                MyMessage(parent, msg, "Can't save", "error")
                return status
            WriteEbuild(parent)
            parent.saved = 1
            status = 0
        if val == wx.ID_NO:
            status = 0
        if val == wx.ID_CANCEL:
            status = 1
        dlg.Destroy()
    return status

def DeleteEbuild(parent):
   """Delete ebuild from disk in overlay"""

   f = parent.filename
   try:
       os.unlink(f)
       Reset(parent)
   except:
      msg = "Couldn't delete %s" % f 
      MyMessage(parent, msg, "Error", "error")

def SaveEbuild(parent):
    """Save ebuild if entries are sane"""
    msg = checkEntries(parent)
    if not msg:
        WriteEbuild(parent)
        parent.saved = 1
        #DoTitle(parent)
        return 1
    else:
        title = 'Abeni: Error Saving'
        MyMessage(parent, msg, title, "error")
        return 0

def GetFilename(parent):
    """Get the full path and filename of ebuild"""
    return parent.filename

def SetFilename(parent, filename):
    """Set the ebuild full path and filename"""
    #Keep last file for viewing and creating diffs(future feature)
    #parent.lastFile = parent.filename
    parent.filename = filename
    parent.statusbar.SetStatusText(filename, 1)
    #DoTitle(parent)

def GetCatPackVer(parent):
    """Get category package version: net-www/mozilla-1.0-r1"""
    return "%s/%s" % (GetCategoryName(parent), getP(parent))

def GetEbuildDir(parent):
    """Get directory ebuild lives in"""
    return os.path.join(GetCategoryPath(parent), getPN(parent))

def GetFilesDir(parent):
    """Get ${FILESDIR}"""
    return os.path.join(GetEbuildDir(parent), "files")

def getP(parent):
    """ Returns P from parent"""
    return getPN(parent) + "-" + getPVR(parent)

def GetCategoryPath(parent):
    """Return path to category of ebuild"""
    return os.path.join (portdir_overlay, GetCategoryName(parent))

def GetPortdirPathVersion(parent):
    categoryDir = os.path.join (portdir, GetCategoryName(parent))
    try:
        return os.path.join(categoryDir, getPN(parent))
    except:
        return None

def getPN(parent):
    """Return PN from form"""
    return parent.text_ctrl_PN.GetValue()

def getPVR(parent):
    """Return PVR from form"""
    return parent.text_ctrl_PVR.GetValue()


def GetCategoryName(parent):
    """Return Category name from form"""
    return parent.text_ctrl_Category.GetValue()

def checkEntries(parent):
    """Validate entries on forms"""
    category = GetCategoryName(parent)
    categoryDir = GetCategoryPath(parent)
    valid_cat = os.path.join(portdir, category)
    if categoryDir == portdir_overlay + '/':
        msg = "You must specify a category."
        return msg
    if not os.path.exists(valid_cat):
        msg = category + " isn't a valid category."
        return msg
    pn = getPN(parent)
    if not pn:
        msg = "You need to set the Package Name"
        return msg

    pvr = getPVR(parent)
    #TODO: verify valid $P
    if not pvr:
        msg = "You need to set $PVR (Package Version)"
        return msg

def DoTitle(parent):
    """Set application's titlebar"""
    p = parent.GetParent()
    if p.STCeditor.GetModify():
        p.SetTitle(getP(p) + " * Abeni " + __version__.version)
    else:
        p.SetTitle(getP(p) + " - Abeni " + __version__.version)

def LoadByPackage(parent, query):
    """Offer list of ebuilds when given a package or filename on command line"""

    #TODO: This was all snarfed from an old version of etcat, which was split
    #      off into gentoolkit.py
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
        
        #print "* " + matches[0].get_category()+"/"+matches[0].get_name()+ " :"
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
            #print " "*8 + "[" + string.join(state,"") + "] " + ver + " (" + slot + ")" + overlay
            pkgs.append (ver + " (" + slot + ")" + overlay)

 
        dlg = wx.SingleChoiceDialog(parent, cat + "/" + package, 'Ebuilds Available',
                    pkgs, wx.OK|wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            s = dlg.GetStringSelection().split(' ')
            version = s[0] 
            
            if len(s) == 3:
                fname = '%s/%s/%s/%s-%s.ebuild' % \
                        (portdir_overlay, cat, package, package, version)
            else:
                    fname = '%s/%s/%s/%s-%s.ebuild' % \
                            (portdir, cat, package, package, version)
            LoadEbuild(parent, fname)
    else:
        print "Package " + query + " not found. Use full category/package name."

def GetD(parent):
    """return ${D} if it exists"""
    p = getP(parent)
    #TODO: use os path join
    d = '%s/portage/%s/image' % (portage_tmpdir, p)
    if os.path.exists(d):
        return d

def GetCVSDir(parent):
    """return cvs_root""" 
    cvs_dir = parent.pref['cvsRoot']
    if not cvs_dir:
        return
    if os.path.exists(cvs_dir):
        return cvs_dir

def GetS(parent):
    """grep S from environment file"""
    p = getP(parent)
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

def CheckUnpacked(parent):
    """Return 1 if they have unpacked"""
    #if os.path.exists('%s/portage/%s/.unpacked' % (portage_tmpdir, getP(parent))):
    if not os.system('sudo ls %s/portage/%s/.unpacked >& /dev/null' % (portage_tmpdir, getP(parent))):
        return 1
    else:
        return 0

def GetEnvs(parent):
    """Get the 'major' environmental vars"""
    parent.env = {}
    p = getP(parent)
    f = '%s/portage/%s/temp/environment' % (portage_tmpdir, p)
    if not os.path.exists(f):
        #cmd = '/usr/sbin/ebuild %s setup' % parent.filename
        #os.system(cmd)
        #write(parent, cmd)
        return
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
                parent.env[var] = val.strip()
    return 1

def ViewEnvironment(parent):
    """Show environment file in editor window"""
    if not GetEnvs(parent):
        t = "To generate the enviornment file, press F9 then choose 'setup'"
        parent.text_ctrl_environment.SetValue(t)
        return
    txt = ''
    keys = parent.env.keys()
    keys.sort()
    for k in keys:
        txt += '%s=%s\n' % (k, parent.env[k])
    if parent.envView == 0:
        parent.text_ctrl_environment.SetValue(txt)
    else:
        p = getP(parent)
        f = '%s/portage/%s/temp/environment' % (portage_tmpdir, p)
        if os.path.exists(f):
            parent.text_ctrl_environment.SetValue(open(f, 'r').read())

def NotGentooDev(parent):
    ''' Warn user about non-developers using CVS '''
    e = parent.pref['email']
    if not e:
        msg = "CVS options are for official Gentoo Developers:\n\n \
              Your email address is not set.\n \
              Set your email address in Options - Global Preferences."
    else:
        msg = "CVS options are for official Gentoo Developers:\n\n \
              Your email address doesn't end in @gentoo.org\n \
              Set your email address in Options - Global Preferences."
    MyMessage(parent, msg, "Gentoo Developer?", "error")

def AddInherit(parent, eclass):
    """Add inherit"""
    #TODO: grab code from CreatePatch and replace this function
    misc = parent.panelMain.stext.GetValue().split("\n")
    # inherit should always be the first misc statement
    found = 0
    for n in range(len(misc)):
        if misc[n][:7] == "inherit":
            found = 1
            if string.find(misc[n], eclass) == -1:
                misc[n] = "inherit %s%s" % (eclass, misc[n][7:])     
                parent.panelMain.stext.SetValue(string.join(misc, "\n"))
    if not found:
        misc[len(misc)] = "inherit %s" % eclass
        parent.panelMain.stext.SetValue(string.join(misc, "\n"))

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
    """Global options from abenirc file"""
    myOptions = options.Options()
    parent.pref = myOptions.Prefs()

def LoadEbuild(parent, filename):
    """Load ebuild from filename"""
    filename = string.strip(filename)
    if not os.path.exists(filename):
        write(parent, "File not found: " + filename)
        dlg = wx.MessageDialog(parent, "The file " + filename + " does not exist",
                              "File not found", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        return

    if filename[-7:] != ".ebuild":
        msg = "This file does not end in .ebuild"
        dlg = wx.MessageDialog(parent, msg,
                'File Error', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        return

    #Check if ebuild has syntax errors before loading.
    #If there are errors ask if they want to edit it in external editor.
    #Try to load again after exiting external editor.
    #busy = wx.BusyInfo("Checking syntax...")
    os.system("chmod +x %s" % filename)
    cmd = "/bin/bash -n %s" % filename
    r, out = RunExtProgram(cmd)
    os.system("chmod -x %s" % filename)
    if r:
        busy=None
        write(parent, "Ebuild syntax is incorrect - /bin/bash found an error:")
        for l in out:
            write(parent, l)
        msg = "The ebuild has a syntax error."
        dlg = wx.MessageDialog(parent, msg,
                'Syntax Error', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()

    s = string.split(filename, "/")
    # ebuild file, no path:
    parent.ebuild_file = s[len(s)-1]

    pn = s[len(s)-2]
    category = s[len(s)-3]
    parent.ebuildDir = string.replace(filename, parent.ebuild_file, '')
    p = parent.ebuild_file[:-7]
    
    #if isValidP(parent, filename.repla):
    my_ebuild = open(filename, 'r').read()
    parent.STCeditor.SetText(my_ebuild)
    cat,pkg,ver,rev=gentoolkit.split_package_name("%s/%s" % (category, p))
    parent.text_ctrl_Category.SetValue(cat)
    parent.text_ctrl_PN.SetValue(pkg)
    if rev == "r0":
        parent.text_ctrl_PVR.SetValue("%s" % ver)
    else:
        parent.text_ctrl_PVR.SetValue("%s-%s" % (ver, rev))
    parent.editing = 1
    parent.STCeditor.Show()
    parent.recentList.append(filename)
    parent.saved = 1
    parent.STCeditor.EmptyUndoBuffer()
    parent.STCeditor.SetSavePoint()
    SetFilename(parent, filename)
    parent.STCeditor.SetFocus()
    parent.window_1_pane_2.Hide()
    parent.tree_ctrl_1.UnselectAll()
    parent.ApplyPrefs()
    ViewEnvironment(parent)
    get_status(parent)

def isValidP(parent, filename):
    """Return cat,pkg,ver,rev if valid otherwise 0"""
    p = string.replace(filename, ".ebuild", "")
	#cat,pkg,ver,rev = gentoolkit.split_package_name(p)
    if not pkg:
        msg = "$PN is not valid. Check the package name."
        dlg = wx.MessageDialog(parent, msg,
                '$PN Error', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        return

    if not ver:
        msg = "$PV is not valid. Check the package version."
        dlg = wx.MessageDialog(parent, msg,
                '$PV Error', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        return

    return cat, pkg, ver, rev

def GetEbuildFileBase(parent):
    """Returns ebuild file base from form: foo-1.0.ebuild"""
    return os.path.join(parent.ebuildDir, "%s-%s.ebuild" % \
           (parent.text_ctrl_PN.GetValue(), parent.text_ctrl_PVR.GetValue()))

def WriteEbuild(parent, temp=0):
    """Write ebuild file in PORTDIR_OVERLAY"""
    categoryDir = GetCategoryPath(parent)
    if not os.path.exists(categoryDir):
        os.mkdir(categoryDir)
        write(parent, "))) Created %s" % categoryDir)
    parent.ebuildDir = GetEbuildDir(parent)
    if not os.path.exists(parent.ebuildDir):
        os.mkdir(parent.ebuildDir)
        write(parent, "))) Created %s" % parent.ebuildDir)
    filename = GetEbuildFileBase(parent)
    SetFilename(parent, filename)
    parent.filehistory.AddFileToHistory(filename.strip())
    if parent.pref['stripHeader'] == 1:
        parent.FindReplace("# $Header", '# ' + '$' + 'Header' + ': $')
    txt = parent.STCeditor.GetText()
    # strip trailing whitespace
    out = '\n'.join([t.rstrip() for t in txt.splitlines() if t != '\n'])
    out += '\n'
    if txt != out:
        write(parent, "))) Stripped trailing whitespace.")
        parent.STCeditor.SetText(out)
    if parent.FindReplace("S=${WORKDIR}/${P}", "") != -1:
        write(parent, "))) removed S=${WORKDIR}/${P} from ebuild (its not necessary)")
    f_out = open(filename, 'w')
    f_out.write(out)
    f_out.close()
    parent.STCeditor.EmptyUndoBuffer()
    parent.STCeditor.SetSavePoint()
    parent.recentList.append(filename)
    parent.statusbar.SetStatusText("Saved", 0)
    #TODO: Add option in prefs to show this:
    write(parent, "))) Saved %s" % filename)

def IsOverlay(parent, ebuild_path):
    """Returns 1 if this ebuild is in PORTDIR_OVERLAY, None if in PORTDIR"""
    if ebuild_path[0:len(portdir_overlay)] == portdir_overlay:
        return 1

