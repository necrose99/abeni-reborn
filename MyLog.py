import wx

class MyLog(wx.PyLog):
    def __init__(self, textCtrl, logTime=0):
        wx.PyLog.__init__(self)
        self.tc = textCtrl
        self.logTime = logTime

    def DoLogString(self, message, timeStamp):
        #TODO: Add option in Global prefs:
        #if self.logTime:
        #    message = time.strftime("%X", time.localtime(timeStamp)) + \
        if self.tc:
            self.tc.AppendText(message + '\n')

