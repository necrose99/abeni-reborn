
"""utils.py

miscellaneous functions that don't belong in gui.py

"""

__revision__ = "$"


import os
import sys
import re
import popen2
import commands

import wx
from wx.lib.dialogs import MultipleChoiceDialog
from portage import config, settings
sys.path.insert(0, "/usr/lib/gentoolkit/pym")
import gentoolkit

import sudo
import options
from Dialogs import ScrolledDialog
import parse_metadata

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


def get_arch():
    """Returns first arch listed in ACCEPT_KEYWORDS in /etc/make.conf"""
    return arch

def launch_browser(parent, url):
    """launch web browser"""
    if not cmd_exists(parent.pref['browser']):
        my_message(parent, "You need to define a browser in preferences.", \
                   "Error", "error")
        return
    cmd = parent.pref['browser'] + " " + url
    os.system("%s &" % cmd)

def scroll_text_dlg(parent, filename, title):
    """Display text of filename in scrolled dialog"""
    dlg = ScrolledDialog.MyScrolledDialog(parent, filename, title)
    
def my_message(parent, msg, title, icon_type="info", cancel=0):
    """Simple informational dialog"""
    if icon_type == "info":
        icon = wx.ICON_INFORMATION
    elif icon_type == "error":
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

def refresh_d(parent):
    """Refresh ${D} file browser"""
    d_dir = get_d(parent)
    if d_dir:
        if os.path.exists(d_dir):
            #parent.sDir.onRefresh(-1)
            parent.dDir.populate(d_dir)
        else:
            parent.dDir.clearList()
        parent.button_d_view.Enable(True)
        parent.button_d_refresh.Enable(True)
    else:
        parent.dDir.clearList()

def refresh_s(parent):
    """Refresh ${S} file browser"""
    s_dir = get_s(parent)
    #print s_dir
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
        #Download URI in FILESDIR browser
        parent.filesDir.onRefresh(-1)

    if action == "setup":
        view_environment(parent)
        parent.filesDir.onRefresh(-1)
        refresh_s(parent)

    if action == "clean":
        parent.Write("))) All clean.")
        parent.filesDir.onRefresh(-1)
        parent.sDir.clearList()
        parent.dDir.clearList()
        view_environment(parent)
        set_status(parent)

    if action == 'digest':
        parent.filesDir.onRefresh(-1)

    if action == 'unpack':
        post_unpack(parent)
        parent.filesDir.onRefresh(-1)
        parent.label_s_dir.SetLabel("${S}: %s" % get_s(parent))
        refresh_s(parent)
        set_status(parent)

    if action == 'compile':
        refresh_s(parent)
        log_to_output(parent)
        parent.Write("))) compile finished")
        set_status(parent)

    if action == 'install':
        parent.label_d_dir.SetLabel("${D}: %s" % get_d(parent))
        post_install(parent)
        log_to_output(parent)
        refresh_s(parent)
        refresh_d(parent)
        parent.Write("))) install finished")
        set_status(parent)

    if action == 'qmerge':
        refresh_s(parent)
        refresh_d(parent)
        log_to_output(parent)
        parent.Write("))) qmerge finished")
        set_status(parent)

    if action == 'emerge':
        refresh_s(parent)
        refresh_d(parent)
        parent.filesDir.onRefresh(-1)
        log_to_output(parent)
        parent.Write("))) emerge finished")
        set_status(parent)
    parent.statusbar.SetStatusText("%s done." % action, 0)

def log_to_output(parent):
    """Get logfile text and display in output tab"""
    #TODO: Run through WriteText or something to get color/filter esc codes
    #lines = commands.getoutput("cat /var/tmp/abeni/emerge_log").splitlines()
    #for l in lines:
    #    parent.Write(l)
    #t = commands.getoutput("sudo cat /var/tmp/abeni/emerge_log")
    status, txt = sudo.cmd("cat /var/tmp/abeni/emerge_log")
    print txt
    print "updating log"
    parent.text_ctrl_log.AppendText("%s\n" % txt)

def export_ebuild(parent):
    """Export ebuild directory to tar file"""
    if not verify_saved(parent):
        flist = []
        flist.append(get_filename(parent))
        # auto-add the digest
        fdir = get_files_dir(parent)
        flist.append(fdir + "/digest-"+get_p(parent))
        auxflist = [f for f in os.listdir(fdir) if f[:6] != "digest"]

        # add all filenames that are present in the ebuild and ask
        # the user about the others.
        # Hmm, the multi-choice dialog does not allow to pre-select anything
        # I'd like to select all files by default, but I guess that needs a
        # custom dialog then.
        #ebuild_content = parent.ebuildfile.editorCtrl.GetText()
        ebuild_content = parent.ThisEd().GetText()
        for f in auxflist:
            if re.search(f + "[^a-zA-Z0-9\-\.\?\*]", ebuild_content):
                flist.append(fdir + "/" + f)
                parent.Write("auto adding file: " + f)
                auxflist.remove(f)
        if len(auxflist) > 0:
            msg = "Select the files you want to include in the " + \
                  "tarball.\n(don't worry about the digest,\nit " + \
                  "will be included automatically)"
            dlg = MultipleChoiceDialog(parent,
                                       msg,
                                       "Auxiliary file selection",
                                       auxflist,
                                       size=(300, min([500,
                                             150 + len(auxflist)*20]
                                            )
                                            )
                                       )
            if dlg.ShowModal() == wx.ID_OK:
                auxflist = [fdir +"/"+f for f in list(dlg.GetValueString())]
            else:
                return 0
        flist += auxflist

        flist = [f.replace(get_category_path(parent)+"/", "") for f in flist]

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

        parent.ExecuteInLog("tar " + taroptions + " " + tarballname + " -C " + get_category_path(parent) + " " + reduce(lambda a, b: a + " " + b, flist))

        # FUTURE: once we have python-2.3 we can use the following:
        #os.chdir(parent.GetCategoryPath())
        #tarball = tarfile.open(tarballname, "w:bz2")
        #for f in flist:
        #    tarball.add(f)
        #tarball.close()
        parent.statusbar.SetStatusText("Ebuild exported to " + tarballname, 0)
        return 1
    else:
        return 0

def do_sudo(cmd):
    """Execute command with sudo"""
    status, output = sudo.cmd(cmd)
    return status, output
    
def post_install(parent):
    """Change group perms of files in ${D} so we can read them"""
    p = get_p(parent)
    d = '%s/portage/%s/image' % (PORTAGE_TMPDIR, p)
    do_sudo("chmod +g+r -R %s" %  d)
    do_sudo("chmod +g+xr %s" %  d)

def get_status(parent):
    """Let us know if ebuild has been unpacked, comiled and installed"""
    p = get_p(parent)
    d = '%s/portage/%s' % (PORTAGE_TMPDIR, p)
    if not os.path.exists(d):
        return

    files = ['.unpacked', '.compiled', '.installed']
    status = []
    for check in files:
        if os.path.exists(os.path.join(d, check)): 
            status.append(check)

    return " ".join(status).replace(".", "")

def set_status(parent, page = None):
    """Set unpack/compile/install status"""
    if not page:
        page = parent.ed_shown
    status = get_status(parent)
    if status:
        parent.label_filename.SetLabel("%s    %s" % (parent.filename[page], \
                                       status))
    else:
        parent.label_filename.SetLabel(parent.filename[page])

def fix_unpacked(parent):
    """chmod for portage group read"""
    p = get_p(parent)
    d = '%s/portage/%s/work' % (PORTAGE_TMPDIR, p)
    d1 = '%s/portage/%s' % (PORTAGE_TMPDIR, p)
    print d1
    do_sudo("chmod +g+xrw -R %s" % d1)

def post_unpack(parent):
    """Report what directories were unpacked, try to set S if necessary"""
    p = get_p(parent)
    d = '%s/portage/%s/work' % (PORTAGE_TMPDIR, p)
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
            parent.Write("))) S=${WORKDIR}/${P}")
            if parent.FindReplace("S=${WORKDIR}/${P}", "") != -1:
                set_s(parent, p)
                parent.Write("))) removed S=${WORKDIR}/${P} from ebuild" + \
                             "(its not necessary)")
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
    #TODO: Is all this necessary after multi-eds?
    parent.text_ctrl_notes.SetValue('')
    parent.text_ctrl_bugz.SetValue('')
    parent.window_3.set_uri(None, None, None, None)
    parent.button_Category.Enable(True)
    parent.text_ctrl_Category.Enable(True)
    parent.text_ctrl_PN.Enable(True)
    parent.text_ctrl_PVR.Enable(True)
    parent.text_ctrl_Category.SetValue("")
    parent.text_ctrl_PN.SetValue("")
    parent.text_ctrl_PVR.SetValue("")
    #if parent.pref['clearLog'] == 1:
    #    parent.text_ctrl_log.Clear()
    parent.text_ctrl_environment.Clear()
    #Reset all file managers:
    clear_explorers(parent)
    parent.EnableToolbar(True)

def clear_explorers(parent):
    """Reset all file managers"""
    parent.filesDir.clearList()
    parent.sDir.clearList()
    parent.dDir.clearList()

def query_all_modify(parent):
    """Check if any ebuild has changed and offer to save if so"""
    buffs =  parent.QueryEditing()
    modified = 0
    for buffer in range(buffs):
        if verify_saved(parent, buffer):
            #If cancel on any stop asking
            return 1

def verify_saved(parent, buffer = None):
    """Check if buffer has changed, focus and offer to save if so"""
    status = 0
    if buffer is None:
        buffer = parent.notebook_editor.GetSelection()
    if parent.eds[buffer].GetModify():
        #In case we're going through multiple buffers
        parent.notebook_editor.SetSelection(buffer)
        dlg = wx.MessageDialog(parent, 'Save modified ebuild?\n' + parent.filename[buffer],
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
            status = 0
        if val == wx.ID_NO:
            status = 0
        if val == wx.ID_CANCEL:
            status = 1
        dlg.Destroy()
    return status

def delete_ebuild(parent):
    """Delete ebuild from disk in overlay"""
    f = parent.filename[parent.ed_shown]
    try:
        os.unlink(f)
        reset(parent)
    except:
        msg = "Couldn't delete %s" % f 
        my_message(parent, msg, "Error", "error")
    d = os.path.split(f)[0]
    if True in [ f[-7:] == '.ebuild' for f in os.listdir(d) ]:
        return
    msg = "There are no more ebuilds for this package in the overlay.\n" + \
          "Delete this directory and its entire contents?\n%s" % d
    dlg = wx.MessageDialog(parent, msg,
            'Delete dirctory?', wx.YES_NO)
    val = dlg.ShowModal()
    if val == wx.ID_YES:
        try:
            do_sudo("rm -r %s" % d)
            #See if category is empty, if not delete it
            pd = os.path.abspath("%s/.." % d)
            if not os.listdir(pd):
                try:
                    do_sudo("rmdir %s" % pd)
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
        parent.EnableSaveToolbar(False)
        #DoTitle(parent)
        return 1
    else:
        title = 'Abeni: Error Saving'
        my_message(parent, msg, title, "error")
        return 0

def get_filename(parent):
    """Get the full path and filename of ebuild"""
    return parent.filename[parent.ed_shown]

def set_filename(parent, filename):
    """Set the ebuild full path and filename"""
    #Keep last file for viewing and creating diffs(future feature)
    #parent.lastFile = parent.filename[parent.ed_shown]
    parent.filename[parent.ed_shown] = filename
    #parent.statusbar.SetStatusText(filename, 1)
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
    if os.path.exists("%s/portage/%s/.unpacked" % (PORTAGE_TMPDIR, get_p(parent))):
    #if not os.system('sudo ls %s/portage/%s/.unpacked >& /dev/null' \
    #                 % (PORTAGE_TMPDIR, get_p(parent))):
        return 1

def get_envs(parent):
    """Get the portage-related environmental vars"""
    parent.env = {}
    p = get_p(parent)
    f = '%s/portage/%s/temp/environment' % (PORTAGE_TMPDIR, p)
    if not os.path.exists(f):
        return
    lines = open(f, 'r').readlines()
    env_vars = ['A', 'AA', 'AUTOCLEAN', 'BUILDDIR', 'BUILD_PREFIX', \
            'D', 'DESTTREE', 'EBUILD', 'FEATURES', 'FILESDIR', \
            'INHERITED', 'KV', 'KVERS', 'O', 'P', 'PF', 'PN', 'PV', \
            'PVR', 'RESTRICT', 'S', 'SRC_URI', 'T', 'WORKDIR']
    for l in lines:
        if "=" in l:
            s = l.split('=')
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
    if parent.env_view == 0:
        parent.text_ctrl_environment.SetValue(txt)
    else:
        p = get_p(parent)
        f = '%s/portage/%s/temp/environment' % (PORTAGE_TMPDIR, p)
        if os.path.exists(f):
            parent.text_ctrl_environment.SetValue(open(f, 'r').read())

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
    parent.pref = options.Options().Prefs()

def query_metadata(parent):
    """Parse metadata.xml in PORTDIR"""
    if not os.path.exists("%s/metadata.xml" % get_portdir_path(parent)):
        return ("", "")
    mdata = parse_metadata.get_metadata(get_portdir_path(parent))
    if mdata.has_key("herds"):
        herds = ", ".join(mdata['herds'])
    else:
        herds = ""
    if mdata.has_key("maintainers"):
        emails = ", ".join(mdata['maintainers'])
    else:
        emails = ""
    return (herds, emails)

def set_notes(parent):
    """Load notes, set uri handler in notes for ${HOMEPAGE}"""
    set_homepage(parent)
    if parent.db:
        load_db_record(parent)

def set_homepage(parent):
    """Set uri handler for homepage in notes tab"""
    herds, maint = query_metadata(parent)
    v = parent.FindVar("HOMEPAGE")
    parent.window_3.set_uri(v, v, herds, maint)

def ebuild_exists(parent, filename):
    """Display dialog if filename doesn't exist, return 1 if exists"""
    if os.path.exists(filename):
        return 1
    else:
        parent.Write("File not found: " + filename)
        dlg = wx.MessageDialog(parent, "The file " + filename + " does not exist",
                              "File not found", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        return

def verify_ebuild_name(parent, filename):
    """Display dialog if bad ebuild name"""
    if filename[-7:] != ".ebuild":
        msg = "This file does not end in .ebuild"
        dlg = wx.MessageDialog(parent, msg,
                'File Error', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        return
    else:
        return 1

def get_portdir_path(parent):
    cat_dir = os.path.join(PORTDIR, get_category_name(parent))
    try:
        return os.path.join(cat_dir, get_pn(parent))
    except:
        return None

def get_categories():
    """Get list of all valid categories"""
    c = open('%s/profiles/categories' % PORTDIR).readlines()
    def strp(s):
        return s.strip()
    c = map(strp, c)
    c = filter(None, c)
    if os.path.exists("/etc/portage/categories"):
        d = open("/etc/portage/categories")
        d = map(strp, d)
        d = filter(None, d)
        c += d
    c.sort()
    return c

def switch_ebuilds(parent):
    """switch gui when page changes"""
    filename = parent.filename[parent.ed_shown]
    s = filename.split("/")
    # ebuild file, no path:
    parent.ebuild_file = s[len(s)-1]
    category = s[len(s)-3]
    parent.ebuild_dir = filename.replace(parent.ebuild_file, '')
    p = parent.ebuild_file[:-7]
    cat, pkg, ver, rev = gentoolkit.split_package_name("%s/%s" % (category, p))
    parent.text_ctrl_Category.SetValue(cat)
    parent.text_ctrl_PN.SetValue(pkg)
    if rev == "r0":
        parent.text_ctrl_PVR.SetValue("%s" % ver)
    else:
        parent.text_ctrl_PVR.SetValue("%s-%s" % (ver, rev))
    view_environment(parent)
    parent.filesDir.clearList()
    filesdir = "%s/files/" % os.path.split(filename)[0]
    parent.filesDir.populate(filesdir)
    parent.label_filesdir.SetLabel("${FILESDIR}: %s" % filesdir)
    s_dir = get_s(parent)
    if s_dir:
        # its unpacked:
        if os.path.exists(s_dir):
            parent.sDir.populate(s_dir)
            parent.label_s_dir.SetLabel("${S}: %s" % s_dir)
            try:
                # its installed in ${D}:
                d_dir = get_d(parent)
                parent.dDir.populate(d_dir)
                parent.label_d_dir.SetLabel("${D}: %s" % d_dir)
                parent.button_d_view.Enable(True)
                parent.button_d_refresh.Enable(True)
            except:
                parent.label_d_dir.SetLabel("${D}: ")
        else:
            parent.sDir.clearList()
    else:
        parent.label_d_dir.SetLabel("${D}: ")
        parent.label_s_dir.SetLabel("${S}: ")
        parent.sDir.clearList()
        parent.dDir.clearList()
    enable_browser_olay(parent, filename)
    set_notes(parent)

def load_ebuild(parent, filename):
    """Load ebuild from filename"""
    filename = filename.strip()
    #file exists on filesystem
    if not ebuild_exists(parent, filename):
        return
    #make sure its a valid ebuild name
    if not verify_ebuild_name(parent, filename):
        return
    #file is already opened
    if filename in parent.filename:
        parent.Write("!!! Ebuild already open.")
        return

    s = filename.split("/")
    # ebuild file, no path:
    parent.ebuild_file = s[len(s)-1]
    category = s[len(s)-3]
    parent.ebuild_dir = filename.replace(parent.ebuild_file, '')
    p = parent.ebuild_file[:-7]
    my_ebuild = open(filename, 'r').read()
    parent.loading_ebuild = 1
    parent.AddEditor(filename, p)
    parent.loading_ebuild = 0
    parent.ThisEd().SetText(my_ebuild)
    cat, pkg, ver, rev = gentoolkit.split_package_name("%s/%s" % (category, p))
    parent.text_ctrl_Category.SetValue(cat)
    parent.text_ctrl_PN.SetValue(pkg)
    if rev == "r0":
        parent.text_ctrl_PVR.SetValue("%s" % ver)
    else:
        parent.text_ctrl_PVR.SetValue("%s-%s" % (ver, rev))
    parent.ThisEd().Show()
    parent.recentList.append(filename)
    parent.ThisEd().EmptyUndoBuffer()
    parent.ThisEd().SetSavePoint()
    set_filename(parent, filename)
    parent.ThisEd().SetFocus()
    parent.ApplyPrefs()
    view_environment(parent)
    set_status(parent)
    set_notes(parent)
    parent.filesDir.clearList()
    filesdir = "%s/files/" % os.path.split(filename)[0]
    parent.filesDir.populate(filesdir)
    parent.label_filesdir.SetLabel("${FILESDIR}: %s" % filesdir)
    s_dir = get_s(parent)
    if s_dir:
        if os.path.exists(s_dir):
            parent.sDir.populate(s_dir)
            parent.label_s_dir.SetLabel("${S}: %s" % s_dir)
            try:
                d_dir = get_d(parent)
                parent.dDir.populate(d_dir)
                parent.label_d_dir.SetLabel("${D}: %s" % d_dir)
                parent.button_d_view.Enable(True)
                parent.button_d_refresh.Enable(True)
            except:
                parent.label_d_dir.SetLabel("${D}: ")
        else:
            parent.sDir.clearList()
    else:
        parent.label_d_dir.SetLabel("${D}: ")
        parent.label_s_dir.SetLabel("${S}: ")
        parent.sDir.clearList()
        parent.dDir.clearList()
    enable_browser_olay(parent, filename)
    if parent.QueryEditing() == 1:
        parent.EnableMenus()

def enable_browser_olay(parent, filename):
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
        #parent.Write("))) Save ebuild to copy it to your overlay.")
    enable_browser_buttons(parent, olay = is_overlay(parent.filename[parent.ed_shown]))


def enable_browser_buttons(parent, olay):
    """Enable all the file browser buttons"""
    if olay:
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
    else:
        parent.button_filesdir_view.Enable(False)
        parent.button_filesdir_edit.Enable(False)
        parent.button_filesdir_new.Enable(False)
        parent.button_filesdir_download.Enable(False)
        parent.button_filesdir_rename.Enable(False)
        parent.button_filesdir_delete.Enable(False)
        parent.button_filesdir_refresh.Enable(False)
        parent.button_s_view.Enable(False)
        parent.button_s_edit.Enable(False)
        parent.button_s_delete.Enable(False)
        parent.button_s_patch.Enable(False)
        parent.button_s_refresh.Enable(False)

def get_notes_info(parent):
    """Get bugzilla nbr and notes"""
    return parent.text_ctrl_bugz.GetValue(), parent.text_ctrl_notes.GetValue()

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

def make_ebuild_pathname(parent):
    """Returns full path to overlay ebuild"""
    return os.path.join(parent.ebuild_dir, "%s-%s.ebuild" % \
           (parent.text_ctrl_PN.GetValue(), parent.text_ctrl_PVR.GetValue()))

def create_ebuild_paths(parent):
    """Make dirs for new ebuild in PORTDIR_OVERLAY"""
    status = 0
    cat_dir = get_category_path(parent)
    if not os.path.exists(cat_dir):
        status = create_dir(parent, cat_dir, verbose = 1)
        if status == -1:
            return -1
    if not os.path.exists(parent.ebuild_dir):
        status = create_dir(parent, parent.ebuild_dir, verbose = 1)
        if status == -1:
            return -1

def strip_opts(cmd):
    """Strip any options from commands"""
    return cmd.split(" ")[0]

def cmd_exists(cmd):
    """Return True if command exists"""
    if not cmd:
        return
    cmd = strip_opts(cmd)
    if cmd[0] == "/":
        if os.path.exists(cmd):
            return True
    else:
        o = commands.getoutput("which %s" % cmd)
        if o[0:6] != "which:":
            return True

def create_dir(parent, path, verbose = 0):
    """Create a directory, or fail show dialog, return -1"""
    #TODO CRITICAL: chown user:portage if not owner
    try:
        os.mkdir(path)
        if verbose:
            parent.Write("))) Created %s" % path)
    #except IOError, msg:
    except OSError, msg:
        my_message(parent, msg, "Failed to create ebuild in overlay.", \
                   icon_type="error", cancel=0)
        return -1

def overwrite(parent):
    """If file exists and user wants to overwrite return 1"""
    dlg = wx.MessageDialog(parent, \
                           'File exists in overlay.\n' \
                           'Overwrite overlay version with PORTDIR ebuild?\n', \
                           'Overwrite ebuild?', wx.YES_NO \
                           | wx.ICON_INFORMATION)
    val = dlg.ShowModal()
    if val == wx.ID_YES:
        return 1

def write_ebuild(parent):
    """Write ebuild file in PORTDIR_OVERLAY"""
    new_ebuild = 0
    parent.ebuild_dir = get_ebuild_dir(parent)
    filename = make_ebuild_pathname(parent)

    if not is_overlay(parent.filename[parent.ed_shown]):
        new_ebuild = 1
        if not os.path.exists(filename):
            if create_ebuild_paths(parent) == -1:
                return

    if os.path.exists(filename):
        if new_ebuild:
            if not overwrite(parent):
                return

    set_filename(parent, filename)
    set_status(parent)
    parent.filehistory.AddFileToHistory(filename.strip())
    strip_cvs_header(parent)
    txt = strip_whitespace(parent)
    f_out = open(filename, 'w')
    f_out.write(txt)
    f_out.close()
    parent.ThisEd().EmptyUndoBuffer()
    parent.ThisEd().SetSavePoint()
    parent.recentList.append(filename)
    parent.statusbar.SetStatusText("Saved", 0)
    if parent.db:
        db_write_record(parent)
    if new_ebuild:
        parent.Write("))) Saved %s" % filename)
        enable_browser_buttons(parent, olay=1)
    filesdir = os.path.join(parent.ebuild_dir, "files")
    if not os.path.exists(filesdir):
        create_dir(parent, filesdir, verbose = 1)
    parent.filesDir.populate(filesdir)
    set_homepage(parent)
    parent.notebook_editor.SetPageText(parent.ed_shown, get_p(parent))

def strip_cvs_header(parent):
    """Strip cvs header."""
    if parent.pref['stripHeader'] == 1:
        parent.FindReplace("# $Header", '# ' + '$' + 'Header' + ': $')

def strip_whitespace(parent):
    """Strip trailing whitespace editor, update editor with text."""
    txt = parent.ThisEd().GetText()
    out = '\n'.join([t.rstrip() for t in txt.splitlines() if t != '\n'])
    out = "%s\n" % out
    if txt != out:
        parent.Write("))) Stripped trailing whitespace.")
        #TODO: Get cursor position and move back there after this:
        #Currently it moves cursor to top row
        parent.ThisEd().SetText(out)
    return out

def db_write_record(parent):
    """Write info in Notes tab to sql db"""
    my_notes = "%s" % parent.text_ctrl_notes.GetValue()
    my_bugz = "%s" % parent.text_ctrl_bugz.GetValue()
    if my_bugz:
        try:
            my_bugz = int(my_bugz) 
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

