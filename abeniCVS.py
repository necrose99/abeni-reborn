
import os
import popen2
import shutil
import utils

from wxPython.wx import *
from wxPython.lib.dialogs import wxMultipleChoiceDialog
from wxPython.lib.dialogs import wxScrolledMessageDialog

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
        self.category = utils.get_category_name(self.parent)
        self.package = utils.get_pn(self.parent)
        self.cvsEbuildDir = self.QueryPath()
        #CRITICAL!!!
        #TODO: check this
        self.ebuild = utils.make_olay_ebuild_filename(self.parent)
        #full path to PORTDIR_OVERLAY ebuild:
        self.overlay_file = self.parent.filename
        self.overlay_dir = os.path.dirname(self.overlay_file)
        if not os.path.exists(self.cvsEbuildDir):
            self.newPackage = 1
        else:
            self.newPackage = 0
        #full path to CVS ebuild:
        self.cvsEbuild = "%s/%s" % (self.cvsEbuildDir, self.ebuild)
        # msg for echangelog and repoman commit
        self.cmsg = ""

    def FullCommit(self):
        """Do the whole repoman CVS commit dealio"""

        try:
            cur_dir = os.getcwd()
        except:
            cur_dir = self.overlay_dir
        
        busy = wxBusyInfo("Copying ebuild and creating digest...")

        if self.newPackage:
            try:
                os.chdir("%s/%s" % (self.cvsRoot, self.category))
            except:
                self.parent.Write("!!! Failed to cd to %s/%s" % \
                            (self.cvsRoot, self.category))
                self.parent.Write("!!! Check your CVS directory setting in Developer Preferences under the Options menu.")
                self.parent.Write("!!! Aborted CVS commit.")
                return

            if (self.CreateCVSdir()):
                self.parent.Write("))) Created directory %s" % self.cvsEbuildDir)
            else:
                self.parent.Write("!!! Failed to create %s" % self.cvsEbuildDir)
                self.parent.Write("!!! Aborted CVS commit.")
                return

        if self.newPackage:
            # /usr/bin/cvs add package directory
            self.CVSAddDir()

        try:
            os.chdir(self.cvsEbuildDir)
        except:
            self.parent.Write("!!! Failed to cd to %s" % self.cvsEbuildDir)
            self.parent.Write("!!! Aborted CVS commit.")
            return


        if not self.newPackage:
            # /usr/bin/cvs update
            self.CVSupdate()

        # Copy ebuild from PORTDIR_OVERLAY to CVS_DIR
        self.CopyEbuild()
        self.parent.Write("))) Ebuild copied to CVS dir")

        # /usr/bin/cvs add ebuild
        #self.CVSAdd(self.cvsEbuild)
        self.CVSAdd(os.path.basename(self.cvsEbuild))
        self.parent.Write("))) Ebuild added to CVS repository")

        # Prompt user to copy any files from $FILESDIR to CVS_DIR/FILESDIR
        # /usr/bin/cvs add em all
        r = self.DoFilesdir()
        if r == "error":
            self.parent.Write("!!! Aborted CVS commit.")
            return
        if r == 0:
            self.parent.Write("))) No files from $FILESDIR to copy.")


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
                        self.parent.Write("!!! Failed to write metadata.xml.")
                        self.parent.Write("%s/metadata.xml" % self.cvsEbuildDir)
                        self.parent.Write("!!! Aborted CVS commit.")
                        return

            #if not self.CopyMetadata():
            #    self.parent.Write("!!! Failed to copy metadata.xml.")
            #    self.parent.Write("!!! Aborted CVS commit.")
            #    return
            busy = wxBusyInfo("Adding metadata...")
            self.CVSAdd("metadata.xml")

        # Create digest for ebuild (should auto-add to cvs)
        self.CreateDigest()
        busy = None

        # echangelog dialog
        r = self.GetMsg("Enter echangelog message                                ", \
                    "Enter echangelog message")
        if r == 0:
            self.parent.Write("!!! Aborted CVS commit.")
            return


        self.Echangelog(self.cmsg)

        if self.newPackage:
            self.CVSAdd("ChangeLog")


        # Get commit message (could be same as echangelog msg)
        r = self.GetMsg("Enter CVS commit message                                ", \
                    "Enter CVS commit message")
        if r == 0:
            self.parent.Write("!!! Aborted CVS commit.")
            return

        busy = wxBusyInfo("Running repoman full...")
        txt = self.SyncExecute("PORTDIR_OVERLAY=%s /usr/bin/repoman full" \
                                % self.cvsEbuildDir, 1, 1)
        busy=None
        dlg = wxScrolledMessageDialog(self.parent, txt, "repoman full")
        dlg.ShowModal()
        dlg.Destroy()


        msg = "Happy with repoman full?\nDo you want to run:\n \
              /usr/bin/repoman --pretend commit -m " + self.cmsg

        if (utils.my_message(self.parent, msg, "repoman --pretend commit", "info", 1)):
            busy = wxBusyInfo("Running repoman --pretend commit...")
 
            txt = self.SyncExecute(('''PORTDIR_OVERLAY=%s /usr/bin/repoman --pretend commit -m "%s"''' % (self.cvsEbuildDir, self.cmsg)), 1, 1)
            busy=None
            dlg = wxScrolledMessageDialog(self.parent, txt, "repoman --pretend commit")
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.parent.Write("!!! CVS commit Cancelled.")
            return

        msg = 'Happy with repoman --pretend commit?\nDo you want to run:\n \
              /usr/bin/repoman commit -m "%s"\n\n \
              WARNING: This will actually COMMIT to CVS with repoman!' % self.cmsg

        if (utils.my_message(self.parent, msg, "repoman commit", "info", 1)):
            busy = wxBusyInfo("Running repoman commit...")
            self.SyncExecute('PORTDIR_OVERLAY=%s /usr/bin/repoman commit -m "%s"' % (self.cvsEbuildDir, self.cmsg))
            busy=None
            self.parent.Write("))) Repoman commit finished.")
        else:
            self.parent.Write("!!! CVS commit Cancelled.")

        # go back to overlay dir
        try:
            os.chdir(cur_dir)
        except:
            pass

    def DoFilesdir(self):
        """Copy files from overlay ${FILESDIR} to CVS ${FILESDIR} """
        p = '%s/files' % utils.get_ebuild_dir(self.parent)
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
            self.parent.Write("!!! Failed to create dir: %s " % cvs_filesdir)
            return "error"
        for f in files:
            fpath = "%s/%s" % (filesdir, f)
            try:
                shutil.copy(fpath, cvs_filesdir)
                self.parent.Write("))) Copied: %s " % f)
            except:
                self.parent.Write("!!! Failed to copy %s from %s" % (f, filesdir))
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
            self.SyncExecute("mkdir %s/files" % self.cvsEbuildDir)
            return 1
        except:
            return 0

    def CVSupdate(self):
        """cvs update"""
        cmd = "/usr/bin/cvs update"
        self.SyncExecute(cmd)
        self.parent.Write("))) CVS update finished")

    def CopyEbuild(self):
        """Copy ebuild from PORT_OVERLAY to CVSroot/category/package/"""
        try:
            shutil.copy(self.overlay_file, self.cvsEbuildDir)
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


    def Repoman(self, args):
        """/usr/bin/repoman"""
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
        cmd = "/usr/bin/cvs add %s/files" % self.package
        self.SyncExecute(cmd)

    def CVSAdd(self, file):
        cmd = "/usr/bin/cvs add %s" % file
        self.SyncExecute(cmd)

    def Execute(self, cmd):
        cmd = ". ~/.keychain/localhost-sh; %s" % cmd
        self.parent.Write("))) Executing:\n)))  %s" % cmd)
        utils.ExecuteInLog(self.parent, cmd)

    def SyncExecute(self, cmd, ret=0, strip_color=0):
        cmd = ". ~/.keychain/localhost-sh; %s" % cmd
        self.parent.Write("))) Executing:\n)))  %s" % cmd)
        a = popen2.Popen4(cmd , 1)
        inp = a.fromchild
        lines = "" 
        l = inp.readline()
        self.parent.Write(l)
        if strip_color:
            l = self.StripColor(l)    
        lines += l
        while l:
            l = inp.readline()
            self.parent.Write(l)
            if strip_color:
                l = self.StripColor(l)    
            lines += l
        if ret:
            return lines

    def StripColor(self, text):
        for c in codes:
            if text.find(codes[c]) != -1:
                text = text.replace(codes[c], '')
        return text 

    def Echangelog(self, msg):
        self.SyncExecute("/usr/bin/echangelog %s" % msg)
