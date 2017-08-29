import os
import popen2
import shutil
import utils
import string

from wx import *
import wx.lib.dialogs
from wx.lib.dialogs import MultipleChoiceDialog
from wx.lib.dialogs import ScrolledMessageDialog

import MetadataDialog

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
codes["reset"] = "\x1b[0m"


class CVS:

    """ CVS utilities imported from gui.py """

    def __init__(self, parent):
        self.parent = parent
        self.cvsRoot = self.parent.pref['cvsRoot']
        self.category = utils.GetCategoryName(self.parent)
        self.package = utils.getPN(self.parent)
        self.cvsEbuildDir = self.QueryPath()
        self.ebuild = utils.GetEbuildFileBase(self.parent)
        #full path to PORTDIR_OVERLAY ebuild:
        self.overlay_file = self.parent.filename
        self.overlay_dir = os.path.dirname(self.overlay_file)
        self.userName = self.parent.pref['userName']
        if not os.path.exists(self.cvsEbuildDir):
            self.newPackage = 1
        else:
            self.newPackage = 0
        #full path to CVS ebuild:
        self.cvsEbuild = "%s/%s" % (self.cvsEbuildDir, self.ebuild)
        # msg for echangelog and repoman commit
        self.cmsg = ""

    def FullCommit(self):
        """Does the whole repoman CVS commit dealio"""

        try:
            cur_dir = os.getcwd()
        except:
            cur_dir = self.overlay_dir
        
        busy = wxBusyInfo("Copying ebuild and creating digest...")

        if self.newPackage:
            try:
                os.chdir("%s/%s" % (self.cvsRoot, self.category))
            except:
                utils.write(self.parent, "!!! Failed to cd to %s/%s" % \
                            (self.cvsRoot, self.category))
                utils.write(self.parent, "!!! Check your CVS directory setting in Developer Preferences under the Options menu.")
                utils.write(self.parent, "!!! Aborted CVS commit.")
                return

            if (self.CreateCVSdir()):
                utils.write(self.parent, "))) Created directory %s" % self.cvsEbuildDir)
            else:
                utils.write(self.parent, "!!! Failed to create %s" % self.cvsEbuildDir)
                utils.write(self.parent, "!!! Aborted CVS commit.")
                return

        if self.newPackage:
            # /usr/bin/cvs add package directory
            self.CVSAddDir()

        try:
            os.chdir(self.cvsEbuildDir)
        except:
            utils.write(self.parent, "!!! Failed to cd to %s" % self.cvsEbuildDir)
            utils.write(self.parent, "!!! Aborted CVS commit.")
            return


        if not self.newPackage:
            # /usr/bin/cvs update
            self.CVSupdate()

        # Copy ebuild from PORTDIR_OVERLAY to CVS_DIR
        self.CopyEbuild()
        utils.write(self.parent, "))) Ebuild copied to CVS dir")

        # /usr/bin/cvs add ebuild
        #self.CVSAdd(self.cvsEbuild)
        self.CVSAdd(os.path.basename(self.cvsEbuild))
        utils.write(self.parent, "))) Ebuild added to CVS repository")

        # Prompt user to copy any files from $FILESDIR to CVS_DIR/FILESDIR
        # /usr/bin/cvs add em all
        r = self.DoFilesdir()
        if r == "error":
            utils.write(self.parent, "!!! Aborted CVS commit.")
            return
        if r == 0:
            utils.write(self.parent, "))) No files from $FILESDIR to copy.")


        # Show dialog with metadata.xml in case they need to change it
        #  or create it

        if self.newPackage:
            busy = None
            if not os.path.exists("%s/metadata.xml" % self.overlay_dir):
                dlg = MetadataDialog.MetadataDialog(self.parent, -1, "metadata.xml", \
                                                   size=wxSize(350, 200), \
                                                   style = wxDEFAULT_DIALOG_STYLE \
                                                   )
                dlg.CenterOnScreen()
                v = dlg.ShowModal()
                if v == wxID_OK:
                    t = dlg.metadata_out.GetText()
                    try:
                        f = open("%s/metadata.xml" % self.cvsEbuildDir, "w")
                        f.write(t)
                        f.close()
                    except:
                        utils.write(self.parent, "!!! Failed to write metadata.xml.")
                        utils.write(self.parent, "%s/metadata.xml" % self.cvsEbuildDir)
                        utils.write(self.parent, "!!! Aborted CVS commit.")
                        return

            #if not self.CopyMetadata():
            #    utils.write(self.parent, "!!! Failed to copy metadata.xml.")
            #    utils.write(self.parent, "!!! Aborted CVS commit.")
            #    return
            self.FixPerms()
            busy = wxBusyInfo("Adding metadata...")
            self.CVSAdd("metadata.xml")

        self.FixPerms()
        # Create digest for ebuild (should auto-add to cvs)
        self.CreateDigest()
        wxYield()
        busy = None

        # echangelog dialog
        r = self.GetMsg("Enter echangelog message                                ", \
                    "Enter echangelog message")
        if r == 0:
            utils.write(self.parent, "!!! Aborted CVS commit.")
            return


        self.Echangelog(self.cmsg)

        if self.newPackage:
            self.CVSAdd("ChangeLog")

        wxYield()

        # Get commit message (could be same as echangelog msg)
        r = self.GetMsg("Enter CVS commit message                                ", \
                    "Enter CVS commit message")
        if r == 0:
            utils.write(self.parent, "!!! Aborted CVS commit.")
            return

        busy = wxBusyInfo("Running repoman full...")
        txt = self.SyncExecute("PORTDIR_OVERLAY=%s /usr/bin/repoman full" \
                                % self.cvsEbuildDir, 1, 1)
        busy=None
        dlg = wxScrolledMessageDialog(self.parent, txt, "repoman full")
        dlg.ShowModal()
        dlg.Destroy()

        wxYield()

        msg = "Happy with repoman full?\nDo you want to run:\n \
              /usr/bin/repoman --pretend commit -m " + self.cmsg

        if (utils.MyMessage(self.parent, msg, "repoman --pretend commit", "info", 1)):
            busy = wxBusyInfo("Running repoman --pretend commit...")
 
            txt = self.SyncExecute(('''PORTDIR_OVERLAY=%s /usr/bin/repoman --pretend commit -m "%s"''' % (self.cvsEbuildDir, self.cmsg)), 1, 1)
            busy=None
            dlg = wxScrolledMessageDialog(self.parent, txt, "repoman --pretend commit")
            dlg.ShowModal()
            dlg.Destroy()
        else:
            utils.write(self.parent, "!!! CVS commit Cancelled.")
            return

        wxYield()
        msg = 'Happy with repoman --pretend commit?\nDo you want to run:\n \
              /usr/bin/repoman commit -m %s\n\n \
              WARNING: This will actually COMMIT to CVS with repoman!' % self.cmsg

        if (utils.MyMessage(self.parent, msg, "repoman commit", "info", 1)):
            busy = wxBusyInfo("Running repoman commit...")
            self.SyncExecute('PORTDIR_OVERLAY=%s /usr/bin/repoman commit -m %s' % (self.cvsEbuildDir, self.cmsg))
            busy=None
            wxYield()
            utils.write(self.parent,"))) Repoman commit finished.")
        else:
            utils.write(self.parent, "!!! CVS commit Cancelled.")

        # go back to overlay dir
        try:
            os.chdir(cur_dir)
        except:
            pass

    def DoFilesdir(self):
        """Copy files from overlay ${FILESDIR} to CVS ${FILESDIR} """
        p = '%s/files' % utils.GetEbuildDir(self.parent)
        if not os.path.exists(p):
            return 0
        files = os.listdir(p)
        def strp(s): return s.strip()
        files = map(strp, files )
        files = filter(None, files)
        files.sort()
        my_files = []
        for f in files:
            if f[:7] != "digest-":
                my_files.append(f)
        if not my_files:
            return 0
        dlg = wxMultipleChoiceDialog(self.parent, 'Choose one or more:', '${FILESDIR}', my_files)
        if dlg.ShowModal() == wxID_OK:
            files = dlg.GetValueString()
        else:
            dlg.Destroy()
            return 0

        filesdir = "%s/files" % self.overlay_dir
        cvs_filesdir = "%s/files/" % self.cvsEbuildDir 
        try:
            os.mkdir(cvs_filesdir)
        except:
            utils.write(self.parent, "!!! Failed to create dir: %s " % cvs_filesdir)
            return "error"
        for f in files:
            fpath = "%s/%s" % (filesdir, f)
            try:
                shutil.copy(fpath, cvs_filesdir)
                utils.write(self.parent, "))) Copied: %s " % f)
            except:
                utils.write(self.parent, "!!! Failed to copy %s from %s" % (f, filesdir))
                return "error"
            self.CVSAdd("files/%s" % f)
        return 1

    def QueryPath(self):
        """Return CVS directory of this ebuild"""
        return "%s/%s/%s" % (self.cvsRoot, self.category, self.package)

    def CreateCVSdir(self):
        """Create CVSroot/category/package directory"""
        try:
            self.SyncExecute("mkdir %s" % self.cvsEbuildDir)
            return 1
        except:
            return 0

    def CVSupdate(self):
        """cvs update"""
        cmd = "/usr/bin/cvs update"
        self.SyncExecute(cmd)
        utils.write(self.parent, "))) CVS update finished")

    def CopyEbuild(self):
        """Copy ebuild from PORT_OVERLAY to CVSroot/category/package/"""
        try:
            shutil.copy(self.overlay_file, self.cvsEbuildDir)
            self.FixPerms()
            return 1
        except:
            return 0

    def CopyMetadata(self):
        """Copy metadata.xml from PORT_OVERLAY to CVSroot/category/package/"""
        file = "%s/metadata.xml" % self.overlay_dir
        try:
            shutil.copy(file, self.cvsEbuildDir)
            return 1
        except:
            return 0

    def FixPerms(self):
        """ Nothing in CVS should be owned as root """
        os.system("chown %s:portage -R %s/*" % (self.userName, self.cvsEbuildDir))

    def Repoman(self, args):
        """/usr/bin/repoman"""
        self.FixPerms()
        cmd = "/usr/bin/repoman %s" % (args)
        self.Execute(cmd)

    def RepomanCommit(self):
        msg = self.GetMsg()
        if msg:
            cmd = "/usr/bin/repoman commit -m '%s'" %  msg
            self.SyncExecute(cmd)

    def GetMsg(self, caption, title):
        dlg = wxTextEntryDialog(self.parent, caption, title, self.cmsg)
        if dlg.ShowModal() == wxID_OK:
            self.cmsg = dlg.GetValue()
            dlg.Destroy()
            return 1
        else:
            dlg.Destroy()
            return 0

    def CreateDigest(self):
        cmd = "/usr/sbin/ebuild %s digest" % os.path.basename(self.cvsEbuild)
        self.SyncExecute(cmd)

    def CVSAddDir(self):
        cmd = "/usr/bin/cvs add %s" % self.package
        self.SyncExecute(cmd)

    def CVSAdd(self, file):
        cmd = "/usr/bin/cvs add %s" % file
        self.SyncExecute(cmd)

    def Execute(self, cmd):
        su_cmd = '''su %s -c ". ~%s/.keychain/localhost-sh; %s"''' % (self.userName, self.userName, cmd)
        utils.write(self.parent, "))) Executing:\n)))  %s" % su_cmd)
        utils.ExecuteInLog(self.parent, su_cmd)

    def SyncExecute(self, cmd, ret=0, strip_color=0):
        su_cmd = '''su %s -c ". ~%s/.keychain/localhost-sh; %s"''' % (self.userName, self.userName, cmd)
        utils.write(self.parent, "))) Executing:\n)))  %s" % su_cmd)
        a = popen2.Popen4(su_cmd , 1)
        inp = a.fromchild
        lines = "" 
        l = inp.readline()
        utils.write(self.parent, l)
        if strip_color:
            l = self.StripColor(l)    
        lines += l
        while l:
            l = inp.readline()
            utils.write(self.parent, l)
            if strip_color:
                l = self.StripColor(l)    
            lines += l
        if ret:
            return lines

    def StripColor(self, text):
        for c in codes:
            if string.find(text, codes[c]) != -1:
                text = string.replace(text, codes[c], '')
        return text 

    def Echangelog(self, msg):
        self.SyncExecute("/usr/bin/echangelog %s" % msg)
