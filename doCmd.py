
import sys, popen2, string


sys.stderr.flush()
sys.stdout.flush()

cmd = sys.argv[1:]
cmd = string.join(cmd)
sys.stdout.write('\nCmd: "%s"\n' % cmd)

a = popen2.Popen4(cmd, 1)
inp = a.fromchild
pid = a.pid
sys.stdout.write("%s (PID: %s)" % (cmd, pid))
l = inp.readline()
while l:
    sys.stdout.write(l)
    l = inp.readline()
sys.stderr.flush()
sys.stdout.flush()