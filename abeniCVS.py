import os
import shutil

class CVS:

    """ CVS utilities """

    def __init__(self, parent):
        self.parent = parent
        self.cvsDir = self.QueryPath()
        self.cat = self.parent.GetCat()
        self.cvsRoot = self.parent.pref['cvsRoot']
        self.package = self.parent.panelMain.Package.GetValue()
        self.ebuild = self.parent.panelMain.EbuildFile.GetValue()
        self.userName = self.parent.pref['userName']
        if not os.path.exists(self.cvsDir):
            self.CreateCVSdir
        os.chdir(self.cvsDir)
        self.cvsEbuild = "%s/%s" % (self.cvsDir, self.ebuild)

    def QueryPath(self):
        """Return CVS directory of this ebuild"""
        return "%s/%s/%s" % (self.cvsRoot, self.cat, self.package)

    def CreateCVSdir(self):
        """Create CVSroot/cat/package directory"""
        catDir = "%s/%s" % (self.cvsRoot, self.cat)
        if not os.path.exists(catDir):
            os.mkdir(catDir)
        os.mkdir(self.cvsDir)
        self.parent.write("Created %s" % self.cvsDir)

    def CVSupdate(self):
        """cvs update"""
        cmd = "/usr/bin/cvs update"
        self.Execute(cmd)
        self.parent.write("cvs update finished")

    def CopyEbuild(self):
        """Copy ebuild and ${FILES} contents from PORT_OVERLAY to CVSroot/cat/package/"""
        # TODO: Copy all files not added to CVS? Just check for patches/config files we added?
        file = self.parent.GetFilename()
        shutil.copy(file, self.cvsDir)

    def CopyMetadata(self):
        """Copy metadata.xml from PORT_OVERLAY to CVSroot/cat/package/"""
        file = ("%s/metadata.xml" % os.path.dirname(parent.filename))
        shutil.copy(file, self.cvsDir)

    def FixPerms(self):
        """ We don't run cvs as root"""
        os.system("chown %s -R %s/*" % (self.userName, self.cvsDir))

    def Repoman(self, args):
        """repoman --scan"""
        self.FixPerms()
        cmd = "su %s -c '/usr/bin/repoman %s'" % (self.userName, args)
        self.Execute(cmd)

    def RepomanCommit(self):
        msg = self.GetMsg()
        if msg:
            cmd = """su %s -c '/usr/bin/repoman --pretend commit -m "%s"'""" \
                  % (self.userName, msg)
            self.Execute(cmd)

    def GetMsg(self):
        dlg = wxTextEntryDialog(self.parent, 'Enter commit message:',
                            'Commit message:', '')
        if dlg.ShowModal() == wxID_OK:
            msg = dlg.GetValue()
        dlg.Destroy()
        return msg

    def CreateDigest(self):
        cmd = "su %s -c /usr/sbin/ebuild %s digest" % (self.userName, self.file)
        self.Execute(cmd)

    def AddEbuild(self):
        cmd = "/usr/bin/cvs add %s" % self.ebuild
        self.Execute(cmd)

    def Execute(self, cmd):
        self.parent.write("Executing %s" % cmd)
        self.parent.ExecuteInLog(cmd)

    def AddChangelog(self):
        cmd = "/usr/bin/cvs add ChangeLog"
        self.Execute(cmd)

    def Echangelog(self, cvsRoot):
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
