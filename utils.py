
"""utils.py

miscellaneous functions that don't belong in gui.py

"""

__revision__ = "$"


import os
import string
import sys
import re
import popen2

import wx
from wx.lib.dialogs import MultipleChoiceDialog
from portage import config, portdb, db, settings
sys.path.insert(0, "/usr/lib/gentoolkit/pym")
import gentoolkit

import sudo
import options


try:
    env = config(clone=settings).environ()
except:
    print "ERROR: Can't read portage configuration from /etc/make.conf"
    sys.exit(1)


PORTDIR = env['PORTDIR']
PORTDIR_OVERLAY = env['PORTDIR_OVERLAY'].split(" ")[0]
if PORTDIR_OVERLAY[-1] == "/":
    PORTDIR_OVERLAY = PORTDIR_OVERLAY[:-1]
PORTAGE_TMPDIR = env['PORTAGE_TMPDIR']

#Lets choose the first arch they have, in case of multiples.
#TODO: Mention in documentation
#arch = '~%s' % env['ACCEPT_KEYWORDS'].split(' ')[0].replace('~', '')
arch = '%s' % env['ACCEPT_KEYWORDS'].split(' ')[0]


#TODO: We might get this every time from /etc/make.conf in case
#      its changed while Abeni is running? 
def get_arch():
    """Returns first arch listed in ACCEPT_KEYWORDS in /etc/make.conf"""
    return arch

def search(search_key):
    matches = []
    for package in portdb.cp_all():
        package_parts = package.split("/")
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


def my_message(parent, msg, title, icon_type="info", cancel=0):
    """Simple informational dialog"""
    if icon_type == "info":
        icon = wx.ICON_INFORMATION
    elif type == "error":
        icon_type = wx.ICON_ERROR
    if cancel:
        dlg = wx.MessageDialog(parent, msg, title, wx.OK | wx.CANCEL | icon)
    else:
        dlg = wx.MessageDialog(parent, msg, title, wx.OK | icon)
    if (dlg.ShowModal() == wx.ID_OK):
        return 1
    else:
        dlg.Destroy()
        return 0

def refresh_s(parent):
    """Refresh ${S} file browser"""
    s_dir = get_s(parent)
    print s_dir
    if s_dir:
        if os.path.exists(s_dir):
            #parent.sDir.onRefresh(-1)
            parent.sDir.populate(s_dir)
        else:
            parent.sDir.clearList()
    else:
        parent.sDir.clearList()

def post_action(parent, action):
    """Execute code after asynchronous job done with ExecuteInLog finishes"""
    if action == "download":
        parent.filesDir.onRefresh(-1)
    if action == "setup":
        view_environment(parent)
        parent.filesDir.onRefresh(-1)
        refresh_s(parent)
    if action == "clean":
        parent.Write("))) All clean.")
        parent.filesDir.onRefresh(-1)
        parent.sDir.clearList()
        view_environment(parent)
    if action == 'digest':
        parent.filesDir.onRefresh(-1)
    if action == 'unpack':
        post_unpack(parent)
        parent.filesDir.onRefresh(-1)
        refresh_s(parent)
    if action == 'compile':
        refresh_s(parent)
        log_to_output(parent)
        parent.Write("))) compile finished")
    if action == 'install':
        post_install(parent)
        log_to_output(parent)
        refresh_s(parent)
        parent.Write("))) install finished")
    if action == 'qmerge':
        refresh_s(parent)
        log_to_output(parent)
        parent.Write("))) qmerge finished")
        parent.button_d_view.Enable(True)
        parent.button_d_refresh.Enable(True)
    if action == 'emerge':
        refresh_s(parent)
        parent.filesDir.onRefresh(-1)
        log_to_output(parent)
        parent.Write("))) emerge finished")
    parent.statusbar.SetStatusText("%s done." % action, 0)

def log_to_output(parent):
    """Get logfile text and display in output tab"""
    #TODO: Run through WriteText or something to get color/filter esc codes
    #lines = commands.getoutput("cat /var/tmp/abeni/emerge_log").splitlines()
    #for l in lines:
    #    parent.Write(l)
    #t = commands.getoutput("sudo cat /var/tmp/abeni/emerge_log")
    status, txt = sudo.cmd("cat /var/tmp/abeni/emerge_log")
    parent.text_ctrl_log.AppendText("%s\n" % txt)

def export_ebuild(parent):
    """Export ebuild directory to tar file"""
    if not verify_saved(parent):
        filelist = []
        filelist.append(get_filename(parent))
        # auto-add the digest
        fdir = get_files_dir(parent)
        filelist.append(fdir + "/digest-"+get_p(parent))
        auxfilelist = [f for f in os.listdir(fdir) if f[:6] != "digest"]

        # add all filenames that are present in the ebuild and ask
        # the user about the others.
        # Hmm, the multi-choice dialog does not allow to pre-select anything
        # I'd like to select all files by default, but I guess that needs a
        # custom dialog then.
        #ebuild_content = parent.ebuildfile.editorCtrl.GetText()
        ebuild_content = parent.STCeditor.GetText()
        for f in auxfilelist:
            if re.search(f+"[^a-zA-Z0-9\-\.\?\*]", ebuild_content):
                filelist.append(fdir +"/"+f)
                parent.Write("auto adding file: " + f)
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

        filelist = [f.replace(get_category_path(parent)+"/", "") for f in filelist]

        tarballname = get_p(parent)+".tar.bz2"
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

        parent.ExecuteInLog("tar "+taroptions+" "+tarballname+" -C "+get_category_path(parent)+" "+reduce(lambda a,b: a+" "+b, filelist))

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

def do_sodo(cmd):
    """Execute command with sudo"""
    status, output = sudo.cmd(cmd)
    return status, output
    
def post_install(parent):
    """Change group perms of files in ${D} so we can read them"""
    p = get_p(parent)
    d = '%s/portage/%s/image' % (PORTAGE_TMPDIR, p)
    do_sodo("chmod +g+r -R %s" %  d)
    do_sodo("chmod +g+xr %s" %  d)

def get_status(parent):
    """Let us know if ebuild has been unpacked, comiled and installed"""
    p = get_p(parent)
    d = '%s/portage/%s' % (PORTAGE_TMPDIR, p)
    if not os.path.exists(d):
        return
    fs = ['.unpacked', '.compiled', '.installed']
    out = []
    for f in fs:
        if os.path.exists(os.path.join(d, f)): 
            out.append(f)
    if len(out):
        parent.Write("))) This package is:")
        for o in out:
            if o == ".unpacked":
                parent.Write(")))     unpacked")
                fix_unpacked(parent)
            if o == ".compiled":
                parent.Write(")))     compiled")
            if o == ".installed":
                parent.Write(")))     installed")

def fix_unpacked(parent):
    """chmod for portage group read"""
    p = get_p(parent)
    d = '%s/portage/%s/work' % (PORTAGE_TMPDIR, p)
    d1 = '%s/portage/%s' % (PORTAGE_TMPDIR, p)
    do_sodo("chmod +g+xrw -R %s" % d1)

def post_unpack(parent):
    """Report what directories were unpacked, try to set S if necessary"""
    p = get_p(parent)
    d = '%s/portage/%s/work' % (PORTAGE_TMPDIR, p)
    d1 = '%s/portage/%s' % (PORTAGE_TMPDIR, p)
    fix_unpacked(parent)
    try:
        lines = os.listdir(d)
    except:
        return
    dirs = []
    #logColor(parent, "RED")
    parent.Write("))) These directory(s) are in ${WORKDIR}:")
    for l in lines:
        if os.path.isdir("%s/%s" % (d, l)):
            parent.Write(" * %s" % l)
            dirs.append(l)
    if len(dirs) == 1:
        #We know we have S. Otherwise there were multiple directories unpacked
        p = dirs[0]
        if p == get_p(parent):
            parent.Write(" * S=${WORKDIR}/${P}")
            if parent.FindReplace("S=${WORKDIR}/${P}", "") != -1:
                set_s(parent, p)
                parent.Write("))) removed S=${WORKDIR}/${P} from ebuild (its not necessary)")
        else:
            ep = get_s(parent)
            if ep == "${WORKDIR}/${P}":
                parent.Write("S=${WORKDIR}/%s" % p)
                set_s(parent, p)
    else:
        if get_s(parent) == "${WORKDIR}/${P}":
            parent.Write("))) More than one directory unpacked, you get to guess what ${S} is.")
    #parent.log_color("BLACK")

def set_s(parent, myp):
    """Set S"""
    p = get_p(parent)
    parent.s = "%s/portage/%s/work/%s" % (PORTAGE_TMPDIR, p, myp)

def reset(parent):
    """Reset abeni for new/loaded ebuild"""
    parent.text_ctrl_notes.SetValue('')
    parent.text_ctrl_bugz.SetValue('')
    parent.window_3.set_uri(None, None)
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
    parent.EnableToolbar(True)

def verify_saved(parent):
    """Check if the ebuild has changed and offer to save if so"""
    status = 0

    if parent.STCeditor.GetModify() or not parent.saved:
        dlg = wx.MessageDialog(parent, 'Save modified ebuild?\n' + parent.filename,
                'Save ebuild?', wx.YES_NO | wx.CANCEL | wx.ICON_INFORMATION)
        val = dlg.ShowModal()
        if val == wx.ID_YES:
            msg = check_entries(parent)
            if msg:
                status = 1
                dlg.Destroy()
                msg = "Check your category, package name and package version."
                my_message(parent, msg, "Can't save", "error")
                return status
            write_ebuild(parent)
            parent.saved = 1
            status = 0
        if val == wx.ID_NO:
            status = 0
        if val == wx.ID_CANCEL:
            status = 1
        dlg.Destroy()
    return status

def delete_ebuild(parent):
    """Delete ebuild from disk in overlay"""
    f = parent.filename
    try:
        os.unlink(f)
        reset(parent)
    except:
        msg = "Couldn't delete %s" % f 
        my_message(parent, msg, "Error", "error")
    d = os.path.split(f)[0]
    if True in [ f[-7:] == '.ebuild' for f in os.listdir(d) ]:
        return
    msg = "There are no more ebuilds for this package in the overlay.\nWould you like to delete this directory and its entire contents?\n%s" % d
    dlg = wx.MessageDialog(parent, msg,
            'Delete dirctory?', wx.YES_NO)
    val = dlg.ShowModal()
    if val == wx.ID_YES:
        try:
            do_sodo("rm -r %s" % d)
            #See if category is empty, if not delete it
            pd = os.path.abspath("%s/.." % d)
            if not os.listdir(pd):
                try:
                    do_sodo("rmdir %s" % pd)
                except:
                    msg = "Couldn't delete empty category directory %s" % pd
                    my_message(parent, msg, "Error", "error")
        except:
            msg = "Couldn't delete %s" % d
            my_message(parent, msg, "Error", "error")

def save_ebuild(parent):
    """Save ebuild if entries are sane"""
    msg = check_entries(parent)
    if not msg:
        write_ebuild(parent)
        parent.saved = 1
        parent.EnableSaveToolbar(False)
        #DoTitle(parent)
        return 1
    else:
        title = 'Abeni: Error Saving'
        my_message(parent, msg, title, "error")
        return 0

def get_filename(parent):
    """Get the full path and filename of ebuild"""
    return parent.filename

def set_filename(parent, filename):
    """Set the ebuild full path and filename"""
    #Keep last file for viewing and creating diffs(future feature)
    #parent.lastFile = parent.filename
    parent.filename = filename
    parent.statusbar.SetStatusText(filename, 1)
    #DoTitle(parent)

def get_cpvr(parent):
    """Get category package version: net-www/mozilla-1.0-r1"""
    return "%s/%s" % (get_category_name(parent), get_p(parent))

def get_ebuild_dir(parent):
    """Get directory ebuild lives in"""
    return os.path.join(get_category_path(parent), get_pn(parent))

def get_files_dir(parent):
    """Get ${FILESDIR}"""
    return os.path.join(get_ebuild_dir(parent), "files")

def get_p(parent):
    """ Returns P from parent"""
    return get_pn(parent) + "-" + get_pvr(parent)

def get_category_path(parent):
    """Return path to category of ebuild"""
    return os.path.join (PORTDIR_OVERLAY, get_category_name(parent))

def get_portdir_path_version(parent):
    cat_dir = os.path.join (PORTDIR, get_category_name(parent))
    try:
        return os.path.join(cat_dir, get_pn(parent))
    except:
        return None

def get_pn(parent):
    """Return PN from form"""
    return parent.text_ctrl_PN.GetValue()

def get_pvr(parent):
    """Return PVR from form"""
    return parent.text_ctrl_PVR.GetValue()


def get_category_name(parent):
    """Return Category name from form"""
    return parent.text_ctrl_Category.GetValue()

def check_entries(parent):
    """Validate entries on forms"""
    category = get_category_name(parent)
    cat_dir = get_category_path(parent)
    valid_cat = os.path.join(PORTDIR, category)
    if cat_dir == PORTDIR_OVERLAY + '/':
        msg = "You must specify a category."
        return msg
    if not os.path.exists(valid_cat):
        msg = category + " isn't a valid category."
        return msg
    pn = get_pn(parent)
    if not pn:
        msg = "You need to set the Package Name"
        return msg

    pvr = get_pvr(parent)
    #TODO: verify valid $P
    if not pvr:
        msg = "You need to set $PVR (Package Version)"
        return msg

def load_by_package(parent, query):
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
                        (PORTDIR_OVERLAY, cat, package, package, version)
            else:
                fname = '%s/%s/%s/%s-%s.ebuild' % \
                        (PORTDIR, cat, package, package, version)
            load_ebuild(parent, fname)
    else:
        print "Package " + query + " not found. Use full category/package name."

def get_d(parent):
    """return ${D} if it exists"""
    p = get_p(parent)
    #TODO: use os path join
    d = '%s/portage/%s/image' % (PORTAGE_TMPDIR, p)
    if os.path.exists(d):
        return d

def get_cvs_dir(parent):
    """If cvs root is defined return path else None""" 
    cvs_dir = parent.pref['cvsRoot']
    if not cvs_dir:
        return
    if os.path.exists(cvs_dir):
        return cvs_dir

def get_s(parent):
    """grep S from environment file"""
    p = get_p(parent)
    e = '%s/portage/%s/temp/environment' % (PORTAGE_TMPDIR, p)
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

def is_unpacked(parent):
    """Return 1 if they have unpacked"""
    #if os.path.exists('%s/portage/%s/.unpacked' % (PORTAGE_TMPDIR, GetP(parent))):
    if not os.system('sudo ls %s/portage/%s/.unpacked >& /dev/null' % (PORTAGE_TMPDIR, get_p(parent))):
        return 1
    else:
        return 0

def get_envs(parent):
    """Get the 'major' environmental vars"""
    parent.env = {}
    p = get_p(parent)
    f = '%s/portage/%s/temp/environment' % (PORTAGE_TMPDIR, p)
    if not os.path.exists(f):
        #cmd = '/usr/sbin/ebuild %s setup' % parent.filename
        #os.system(cmd)
        #parent.Write(cmd)
        return
    lines = open(f, 'r').readlines()
    #TODO: This is a partial list. Should add option to show all vars available.
    env_vars = ['A', 'AA', 'AUTOCLEAN', 'BUILDDIR', 'BUILD_PREFIX', \
            'D', 'DESTTREE', 'EBUILD', 'FEATURES', 'FILESDIR', \
            'INHERITED', 'KV', 'KVERS', 'O', 'P', 'PF', 'PN', 'PV', \
            'PVR', 'RESTRICT', 'S', 'SRC_URI', 'T', 'WORKDIR']
    for l in lines:
        if "=" in l:
            s = string.split(l, '=')
            var = s[0]
            val = s[1]
            if var in env_vars:
                parent.env[var] = val.strip()
    return 1

def view_environment(parent):
    """Show environment file in editor window"""
    if not get_envs(parent):
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
        p = get_p(parent)
        f = '%s/portage/%s/temp/environment' % (PORTAGE_TMPDIR, p)
        if os.path.exists(f):
            parent.text_ctrl_environment.SetValue(open(f, 'r').read())

def add_inherit(parent, eclass):
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

def run_ext_cmd(cmd):
    """Run program and return exit code, output in a list"""
    #TODO: Replace with commands.getoutput?
    out = []
    p = popen2.Popen4(cmd , 1)
    inp = p.fromchild
    l = inp.readline()
    while l:
        out.append(l.strip())
        l = inp.readline()
    r = p.wait()
    return r, out

def get_options(parent):
    """Global options from abenirc file"""
    my_options = options.Options()
    parent.pref = my_options.Prefs()

def load_ebuild(parent, filename):
    """Load ebuild from filename"""
    filename = string.strip(filename)
    if not os.path.exists(filename):
        parent.Write("File not found: " + filename)
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
    cmd = "/bin/bash -n %s" % filename
    r, out = run_ext_cmd(cmd)
    if r:
        parent.Write("Ebuild syntax is incorrect - /bin/bash found an error:")
        for l in out:
            parent.Write(l)
        msg = "The ebuild has a syntax error."
        dlg = wx.MessageDialog(parent, msg,
                'Syntax Error', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()

    s = string.split(filename, "/")
    # ebuild file, no path:
    parent.ebuild_file = s[len(s)-1]

    category = s[len(s)-3]
    parent.ebuildDir = string.replace(filename, parent.ebuild_file, '')
    p = parent.ebuild_file[:-7]
    my_ebuild = open(filename, 'r').read()
    parent.STCeditor.SetText(my_ebuild)
    cat, pkg, ver, rev = gentoolkit.split_package_name("%s/%s" % (category, p))
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
    set_filename(parent, filename)
    parent.STCeditor.SetFocus()
    parent.ApplyPrefs()
    view_environment(parent)
    get_status(parent)
    v = parent.FindVar("HOMEPAGE")
    parent.window_3.set_uri(v, v)
    if parent.db:
        load_db_record(parent)
    f = "%s/files/" % os.path.split(filename)[0]

    parent.filesDir.clearList()

    parent.filesDir.populate(f)
    s = get_s(parent)
    if s:
        if os.path.exists(s):
            parent.sDir.populate(s)
        else:
            parent.sDir.clearList()
    else:
        parent.sDir.clearList()
    if is_overlay(filename):
        parent.button_filesdir_edit.Enable(True)
        parent.button_filesdir_new.Enable(True)
        parent.button_filesdir_download.Enable(True)
        parent.button_filesdir_delete.Enable(True)
    else:
        parent.button_filesdir_edit.Enable(False)
        parent.button_filesdir_new.Enable(False)
        parent.button_filesdir_download.Enable(False)
        parent.button_filesdir_delete.Enable(False)

    enable_browser_buttons(parent)

def enable_browser_buttons(parent):
    """Enable all the file browser buttons"""
    parent.button_filesdir_view.Enable(True)
    parent.button_filesdir_edit.Enable(True)
    parent.button_filesdir_new.Enable(True)
    parent.button_filesdir_download.Enable(True)
    parent.button_filesdir_rename.Enable(True)
    parent.button_filesdir_delete.Enable(True)
    parent.button_filesdir_refresh.Enable(True)
    parent.button_s_view.Enable(True)
    parent.button_s_edit.Enable(True)
    parent.button_s_delete.Enable(True)
    parent.button_s_patch.Enable(True)
    parent.button_s_refresh.Enable(True)

def load_db_record(parent):
    """Load db record for current ebuild"""
    cpvr = get_cpvr(parent)
    try:
        e = parent.db.Ebuild.byCpvr(cpvr)
        if e.notes:
            parent.text_ctrl_notes.SetValue(e.notes)
        if e.bugz:
            parent.text_ctrl_bugz.SetValue("%s" % e.bugz)
    except:
        pass

def get_ebuild_filebase(parent):
    """Returns ebuild file base from form: foo-1.0.ebuild"""
    return os.path.join(parent.ebuildDir, "%s-%s.ebuild" % \
           (parent.text_ctrl_PN.GetValue(), parent.text_ctrl_PVR.GetValue()))

def write_ebuild(parent, temp=0):
    """Write ebuild file in PORTDIR_OVERLAY"""
    #TODO: temp variable is unused
    cat_dir = get_category_path(parent)
    if not os.path.exists(cat_dir):
        os.mkdir(cat_dir)
        parent.Write("))) Created %s" % cat_dir)
    parent.ebuildDir = get_ebuild_dir(parent)
    if not os.path.exists(parent.ebuildDir):
        os.mkdir(parent.ebuildDir)
        parent.Write("))) Created %s" % parent.ebuildDir)
    filename = get_ebuild_filebase(parent)
    set_filename(parent, filename)
    parent.filehistory.AddFileToHistory(filename.strip())
    if parent.pref['stripHeader'] == 1:
        parent.FindReplace("# $Header", '# ' + '$' + 'Header' + ': $')
    txt = parent.STCeditor.GetText()
    # strip trailing whitespace
    out = '\n'.join([t.rstrip() for t in txt.splitlines() if t != '\n'])
    out += '\n'
    if txt != out:
        parent.Write("))) Stripped trailing whitespace.")
        parent.STCeditor.SetText(out)
    if parent.FindReplace("S=${WORKDIR}/${P}", "") != -1:
        parent.Write("))) removed S=${WORKDIR}/${P} from ebuild (its not necessary)")
    f_out = open(filename, 'w')
    f_out.write(out)
    f_out.close()
    parent.STCeditor.EmptyUndoBuffer()
    parent.STCeditor.SetSavePoint()
    parent.recentList.append(filename)
    parent.statusbar.SetStatusText("Saved", 0)
    if parent.db:
        db_write_record(parent)
    #TODO: Add option in prefs to show this optionally:
    parent.Write("))) Saved %s" % filename)

def db_write_record(parent):
    """Write Notes tab to db backend"""
    my_notes = "%s" % parent.text_ctrl_notes.GetValue()
    my_bugz = "%s" % parent.text_ctrl_bugz.GetValue()
    if my_bugz:
        try:
            my_bugz = string.atoi(my_bugz) 
        except:
            my_bugz = None
    my_cpvr = get_cpvr(parent)
    try:
        #Update existing record:
        e = parent.db.Ebuild.byCpvr(my_cpvr)
        if my_bugz:
            e.bugz = my_bugz
        if my_notes:
            e.notes = my_notes 
    except:
        #New record:
        e = parent.db.Ebuild(cpvr = my_cpvr, bugz = my_bugz, notes = my_notes)

def is_overlay(ebuild_path):
    """Returns 1 if this ebuild is in PORTDIR_OVERLAY, None if in PORTDIR"""
    if ebuild_path[0:len(PORTDIR_OVERLAY)] == PORTDIR_OVERLAY:
        return 1

