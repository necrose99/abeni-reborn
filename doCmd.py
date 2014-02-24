
import sys
import popen2
import string
import os


#pid_file = '/var/run/abeni_proc.pid'
#f = open(pid_file, 'w')

cmd = sys.argv[1:]
cmd = string.join(cmd)

#cmd = "%s 2>&1" % cmd
os.system(cmd)
#sys.stdout.write('\nCmd: "%s"\n' % cmd)
#cmd = "%s 2>&1" % cmd
#a = popen2.Popen4(cmd , 1)
#inp = a.fromchild
#pid = a.pid
#n = 0
##f.write("%s\n" % pid)
##f.close()

##sys.stdout.write("%s (PID: %s)\n" % (cmd, pid))
#l = inp.readline()
#while l:
#    sys.stdout.write("%s %s" % (n,l))
#    n += 1
#    l = inp.readline()

#os.unlink(pid_file)
#sys.stderr.flush()
#sys.stdout.flush()
