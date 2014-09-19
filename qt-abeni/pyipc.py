############################################################################
# FILE:        pyipc.py                                                    #
# Copyright (C) 2001, Neil Macneale <mac4-pyipc@theory.org>                #
#                                                                          #
# This library is free software; you can redistribute it and/or modify it  #
# under the terms of the GNU Lesser General Public License as published by #
# the Free Software Foundation; either version 2.1 of the License, or (at  #
# your option) any later version.                                          #
#                                                                          #
# This library is distributed in the hope that it will be useful, but      #
# WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser #
# General Public License for more details.                                 #
#                                                                          #
# You should have received a copy of the GNU Lesser General Public License #
# along with this library; if not, write to the Free Software Foundation,  #
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA             #
#                                                                          # 
############################################################################


import ipcmod
import cPickle
import cStringIO
import struct
from   types      import *

import sys 

if sys.hexversion < 0x02000000:
    raise ImportError, "Python 2.0 required for pyipc"


# Initialize values which were #defined in the C headers.
IPC_CREAT    = ipcmod.IPC_CREAT
IPC_PRIVATE  = ipcmod.IPC_PRIVATE
IPC_EXCL     = ipcmod.IPC_EXCL
IPC_NOWAIT   = ipcmod.IPC_NOWAIT
SHMLBA       = ipcmod.SHMLBA            # The system page size.

try:
    MSG_EXCEPT   = ipcmod.MSG_EXCEPT    # flag to indicate the desire for the
                                        # invers message type. This flag is
                                        # not defined on all platforms.
except:
    pass

SEM_UNDO     = ipcmod.SEM_UNDO          # flag to indicate that semaphore
                                        # changes should be reversed when a 
                                        # process exits.
SHM_RDONLY   = ipcmod.SHM_RDONLY        # flag to indicate read-only attach

SIZE_LONG    = len(struct.pack('l',0))
MAX_INDEX    = 0x7FFFFFFF               # 2**31 - 1, maximum index of a slice.

#---------------------------------------------------------------------- ftok()
def ftok(filename, proj = 0):
    """
    ftok(filename, proj = 0)
    
    PURPOSE: Direct wrapper for the unix ftok function.  Take a file name and
             combine it with an int to get a key number which is relatively
             unique.  Note it is not gaurenteed to be unique, but it usually is.
             This is the standard way of getting a key for an ipc component.
    ARGS:    filename, a string which indicates an absolute path.
             prog = 0, an int which is the project id.
    RETURN:  An int, which is the key.
    """
    if not -128 <= proj <= 127:
        raise ValueError, "Project must be a legal char value"

    return ipcmod.ftok(filename, proj)

#---------------------------------------------------------------- obj2string()
def obj2string(obj):
    """
    obj2string(obj)
    
    PURPOSE: Take an object, pickle it, write it to a StringIO, then return
             its value. The reason for this is that you need to convert a
             python object to binary data to move it through the ipc system.
             Passing the string returned throught the string2obj function will
             reverse the process.
    ARGS:    Any object.
    RETURN:  A stirng, representing the object.  This is the same string that
             would be written to a pickle file.
    """
    str = cStringIO.StringIO()
    cPickle.dump(obj, str)
    return str.getvalue()

#---------------------------------------------------------------- string2obj()
def string2obj(str):
    """
    string2obj(str)
    
    PURPOSE: Take in a string created by the obj2string method, and convert it
             to an object.
    ARGS:    A string which is in the python pickle format.
    RETURN:  The unpickled object.
    """
    str = cStringIO.StringIO(str)
    return cPickle.load(str)

#-------------------------------------------------------------- tups2strings()
def tups2strings(*l):
    """
    tups2strings((a,b,c), ... )
    
    PURPOSE: This function takes in 0 or more three int tuples. The three int
             tuples represent the operations on a semaphore which are  passed
             into the sembuf when performing an operation on a semaphore.
             If any of the items are not tuples, or any of the tuples do not 
             contain three ints, a TypeError will be raised.  To understand 
             what the arguments should be, see the semop manpage.

             I can't imagine why anyone would need to call this method outside
             of this module, but there is really no harm in doing so :)
    ARGS:    Any number of three into tuples.
    RETURN:  Three strings in a tuple, each string being the composite of all
             there respective ints. IE, all of the first ints in the tuples 
             will be concatonated into the first string returned, all the
             second ints will be in the 2nd, and the third ints in the third.
    """
    num = cStringIO.StringIO()
    op  = cStringIO.StringIO()
    flg = cStringIO.StringIO()
    
    try:
        for ea in l:
            if len(ea) != 3: raise "ANYTHING"
            num.write(struct.pack("i",ea[0]))
            op.write(struct.pack("i",ea[1]))
            flg.write(struct.pack("i",ea[2]))

    except:
        raise TypeError, "Argument list improperly formatted."

    return (num.getvalue(),op.getvalue(), flg.getvalue())

#----------------------------------------------------------------- removeIPC()
def removeIPC(ipc):
    """
    removeIPC(ipc)
    
    PURPOSE: Remove a MessageQueue, SharedMemory, or SemaphoreGroup from the 
             system. This method is not associated with a class because 
             removing one ipc instance could very easily affect other 
             instances which were created with the same key number.  This is not
             to say that this protects from destroying an ipc component that is
             still being used by some other object. You need to keep track of
             that, though that functionality may be added later.

             The caller of this method must have modify permision, otherwise an 
             EnvironmentError is raised.

             Note: The system immediatly destroys message queues and 
             semaphores, but waits until the last process detaches from a 
             shared memory block. See  man pages: shmctl, msgctl, semctl.
    ARGS:    An ipc object. IE, a SharedMemory, MessageQueue, or SemaphoreGroup
    RETURN:  If successfull, None returned. Otherwise, an EnvirnomentError
             is raised.
    """
    if isinstance(ipc, MessageQueue):
        ipcmod.msgremove(ipc._msgq)
    elif isinstance(ipc, SharedMemory):
        ipcmod.shmremove(ipc._shm_id)
    elif isinstance(ipc, SemaphoreGroup):
        ipcmod.semremove(ipc._sem_id)
    else:
        raise TypeError, "Arg not a ipc instance" 
    
#======================================================== CLASS: MessageQueue
class MessageQueue: 
    """
    CLASS:   MessageQueue
    PURPOSE: The MessageQueue is a class interface to the System V msg.h
             functions.  You can create a message object, and write and recieve
             messages from other processes.  The other processes can be written
             in any language since binary data is all that is passed between
             them.
    
             A successful creation of an instance assures that the queue 
             exists, and can either be read from, written to, or both.  See 
             the manpages msgget, msgsnd, msgrcv for more details about the 
             base module, icpmod.               
    
            If both processes are python processes, you can use the send_p and
            receive_p methods to pass python objects directly.
    """

    #-------------------------------------------------------------- __init__()
    def __init__(self, key, perm=(0600|IPC_CREAT)):
        """
        __init__(self, key, perm=(0600|IPC_CREAT))
        
        PURPOSE: This Constructor is equivalent to msgget. 
        
        and the flags to open it with.  The flags you pass for the
                 permissions is usually, '0600 | pyipc.IPC_CREAT' stating that
                 only this user who can read and write to it are you only, and
                 if the queue does not exist, create it.

                 If you really want to know what you are doing, look at 'man
                 msgget'
                                                
        ARGS:    key- an int which indicates which key you would like the
                   MessageQueue to communicate with.  Unless you want a private
                   queue (which defeats the purpose of interprocess 
                   communication) you need to use a key greater than 0.
                 perm=(0600|IPC_CREAT)-  The premissions of of the
                   MessageQueue.  The Octal number is similar to unix file
                   systems.  IE, 0666 lets everyone read and write to it. This
                   value can be 'or'ed with certain flags:
                       IPC_CREAT: to indicate that the a message queue can be 
                                 created, if it does not exist.
                       IPC_EXCL: To force that you are the only one using this
                                 key.  Use this in conjunction with IPC_CREAT 
                                 to assure that you are the owner of the 
                                 message queue.
        """
        self._msgq = ipcmod.msgget(key, perm)
    
    #-------------------------------------------------------------------- id()
    def id(self): 
        """
        id(self)
        
        PURPOSE: Access the id that this MessageQueue is associated with.
        RETURN:  An int, greater or equal to 0.
        """
        return self._msgq
    
    #------------------------------------------------------------------ send()
    def send(self, str, flags=0):
        """
        send(self, str, flags=0)
        
        PURPOSE: Send a string of bytes the the message system. Since there is
                 not really a notion of memory in python, we use strings. This
                 is a wrapper for the msgsnd function, you should read it's man
                 page.
                    
                 The standard way to send a message is to create a string with
                 struck.pack().  The first bytes make up a long which is
                 the type of the message.  Note that the type can never
                 be 0, so make sure that any string you pass to this function
                 has some bit set in the first bytes (sizeof(long), that is).

                 You can set the flags to give different behavior.  Using the
                 IPC_NOWAIT flag can be used, but is pretty lame.  Using it
                 would cause an exception to be thrown if there happened to be
                 another process sending.  It makes more sense, to wait the
                 extra millisecond.  The default flags argument waits.
                 
        ARGS:    str- The string to be sent. Note that this string should 
                 already have the type specified by appending a long int to 
                 the front of the message.
        RETURN:  None.  If the message queue has been destroyed, or you do not
                 have write access, an EnvironmentError will be thrown.
        """
        ipcmod.msgsnd(self._msgq,str, flags)

    #---------------------------------------------------------------- send_p()
    def send_p(self, obj, type=1, flags=0):
        """
        send_p(self, obj, type=1, flags=0)
        
        PURPOSE: Send a python object as a pickled string.  This is used to 
                 make communicating between python processes easier.
        ARGS:    obj- the object to be sent.
                 type=1- an int which indicates where the object should be in
                   the priority of the message queue.  The default is the
                   highest priority that a message can have.
                 flags=0- see send()
        RETURN:  None. If the message queue has been destroyed, or you do not
                 have write access, an EnvironmentError will be thrown.
                         
        """
        s   = obj2string(obj)
        fmt = "l" + str(len(s)) + "s"
        s = struct.pack(fmt, type, obj2string(obj))
        self.send(s, flags)
    
    #--------------------------------------------------------------- receive()
    def receive(self, type=0, flags=IPC_NOWAIT):
        """
        receive(self, type=0, flags=IPC_NOWAIT)
        
        PURPOSE: Remove a message from the MessageQueue.
        ARGS:    type=0- The type of message that you wish to read. The
                   default will always return the first pessage place in the
                   queue, regardless of type. If you specify a type greater 
                   than 0, then the first message placed in the queue with 
                   that type value will be returned. If a negative type is
                   given, the first message with the lowest type less than or
                   equal to the absolute value of type will be read.
                 flags=IPC_NOWAIT- The flags value will let you change the way
                   the receive function behaves. The default value will
                   indicate that this function is not supposed to stall
                   waiting for a message. If the flag used is 0, then the
                   function will stall indefinately.  You can also or this
                   flag with the MSG_EXCEPT value which indicates that you
                   want the first message placed in the queue that does not
                   have the type specified by the type value.
        RETURN:  The message is returned as a string WITH the type bytes at
                 the beginning of the string. If you cut SIZE_LONG bytes off
                 the front of the string, you will get the intended message.
            
                 If you use the default values for this method, you will get
                 the next message if there is one, whatever type it is.  The
                 defaults do not wait though, so if there are no message, None
                 will be returned.                                          
        """
        return ipcmod.msgrcv(self._msgq, type, flags)   

    #------------------------------------------------------------- receive_p()
    def receive_p(self, type=0, flags=IPC_NOWAIT):
        """
        receive_p(self, type=0, flags=IPC_NOWAIT)
        
        PURPOSE: Receive a message from the queue and treat it as a python
                 pickled object.
        ARGS:    Same as receive() method.
        RETURN:  A tuple, (type, object) is returned.  the type is the long
                 value placed at the front of the message as the type. The
                 object, well, its the object...

                 If you used the IPC_NOWAIT flag, and there was not message
                 waiting in the queue, None will be returned.
        """
        s   = self.receive(type, flags)
        if s == None: return None

        fmt = "l"+ str(len(s)-SIZE_LONG) + "s"
        type, s = struct.unpack(fmt,s)
        return (type, string2obj(s))
    
#======================================================== CLASS: SharedMemory
class SharedMemory:
    """
    CLASS:   SharedMemory
    PURPOSE: A shared memory block is a block of memory which can be read and 
             written to by multiple processes.  It is the fasted method of
             sharing information because the kernel is not involved.  (Note
             that this implementation does do a memory copy from python to C,
             so it is not that fast)

             Shared Memory is raw, and you must keep track of the details. You
             should also become familiar with the system semaphores supplied
             by this module so that you can avoid synchronization error.

             Each Shared memory object should only attach to the block once.
             The attach function does its best to prevent it, but you can
             break it if you make an effort.

             Since attaching once is kind of expected, the class constructor
             attaches by default.  You can do it manually on instances that
             you created without linking.  You can also attach again after you
             detach.

             man shmmem for more detials.
    """
    #-------------------------------------------------------------- __init__()
    def __init__(self, key, size=SHMLBA, flags=(0600|IPC_CREAT), attach=1):
        """
        __init__(self, key, size=SHMLBA, flags=(0600|IPC_CREAT), attach=1)
        
        ARGS:   key- The key value you would like to either attache to, or
                  create.
                size=SHMLBA- The size of the memory block you would like ot
                  attach to.  This value should be a multiple of SHMLBA, but
                  is not required to be.
                flags=(0600|IPC_CREAT)- the flags to determine the type of
                  memory block you would like to use. The octal number behaves
                  similarly to the unix file system. you can or the value with
                  the following flags to get other results:
                       IPC_CREAT: to indicate that the a message queue can be 
                                 created, if it does not exist.
                       IPC_EXCL: To force that you are the only one using this
                                 key.  Use this in conjunction with IPC_CREAT 
                                 to assure that you are the owner of the 
                                 message queue.
                attach=1- A boolean flag to indicate if this object should be
                  automatically attached to the memory block. 
        """
        self._shm_id = ipcmod.shmget(key,size, flags)
        self._size = size
        self._addr = None # a _addr value of None indicated that this 
                          # object is not attached.
        
        if attach: self.attach()

    #------------------------------------------------------------ isAttached()
    def isAttached(self):
        """
        isAttached(self)
        
        PURPOSE: Determine if this object is attached to the memory block.
        ARGS:    None
        RETURN:  1 if attached, 0 if not.
        """
        if self._addr: return 1
        return 0

    #------------------------------------------------------------ readUShort()
    def readUShort(self, loc):
        """
        readUShort(self, loc)
        
        PURPOSE: Read an unsigned short int from the memory block.
        ARGS:    loc- an int which indicates how many bytes from the beginning
                   of the block to read the int.
        RETURN:  The int that was in memory.
        """
        return struct.unpack("H", self[loc : loc + struct.calcsize("H")])[0]

    #----------------------------------------------------------- writeUShort()
    def writeUShort(self, loc, val):
        """
        writeUShort(self, loc, val)
        
        PURPOSE: Write an unsigned short int value to the memory block at a 
                 specific location.
        ARGS:    loc- The number of bytes between the start of the memory
                   block and where the short is written. Note that word
                   boundaries are not important.
                 val- the value you would like to write to memory.
        RETURN:  None
        """
        self[loc] = struct.pack("H", val)
        
    #-------------------------------------------------------------- readUInt()
    def readUInt(self, loc):
        return struct.unpack("I", self[loc : loc + struct.calcsize("I")])[0]
    #------------------------------------------------------------- writeUInt()
    def writeUInt(self, loc, val):
        self[loc] = struct.pack("I", val)
    #------------------------------------------------------------- readUByte()
    def readUByte(self, loc):
        return struct.unpack("B", self[loc])[0]
    #------------------------------------------------------------ writeUByte()
    def writeUByte(self, loc, val):
        self[loc] = struct.pack("B", val)
    #--------------------------------------------------------------- readInt()
    def readInt(self, loc):
        return struct.unpack("i", self[loc : loc + struct.calcsize("i")])[0]
    #-------------------------------------------------------------- writeInt()
    def writeInt(self, loc, val):
        self[loc] = struct.pack("i", val)    
    #------------------------------------------------------------- readShort()
    def readShort(self, loc):
        return struct.unpack("h", self[loc : loc + struct.calcsize("h")])[0]
    #------------------------------------------------------------ writeShort()
    def writeShort(self, loc, val):
        self[loc] = struct.pack("h", val)
    #-------------------------------------------------------------- readByte()
    def readByte(self, loc):
        return struct.unpack("b", self[loc : loc + struct.calcsize("b")])[0]
    #------------------------------------------------------------- writeByte()
    def writeByte(self, loc, val):
        self[loc] = struct.pack("b", val)

    #------------------------------------------------------------- readFloat()
    def readFloat(self, loc):
        return struct.unpack("f", self[loc : loc + struct.calcsize("f")])[0]
    #------------------------------------------------------------ writeFloat()
    def writeFloat(self, loc, val):
        self[loc] = struct.pack("f", val)

#---------------------------------------------------------------- attach()
    def attach(self, addr=0, flags=0):
        """
        attach(self, addr=0, flags=0)
        
        PURPOSE: Create a link in the current processes page table which
                 points to a shared memory block.

                 The attach method should only be called once, unless you
                 detatch prior to calling it again.  This function checks if
                 there is a valid link currently, but you could break this
                 check realatively easilly.

                 Note, it is no problem to have multiple SharedMemory objects
                 refering to the same memory block in the same process.
                 
        ARGS:    addr=0- You can set an offset for the link to be made to.
                   This is rarely required, so the default is 0.
                 flags=0- The flags only make sence when you are attaching
                   away from the beginning of the block. Since I am not
                   endorsing it, read the man page for mor details :)
        RETURN:     
        """
        if self._addr == None:
            self._addr = ipcmod.shmat(self._shm_id, addr, flags)

    #---------------------------------------------------------------- detach()
    def detach(self):
        """
        detach(self)
        
        PURPOSE: Unlink this object from the memory block. This will not
                 affect other SharedMemory objects
        ARGS:    None 
        RETURN:  None
        """
        try:
            ipcmod.shmdt(self._addr)
            self._addr = None
        except:
            pass

    #--------------------------------------------------------------- __del__()
    def __del__(self): self.detach()

    #--------------------------------------------------------------- __len__()
    def __len__(self): return self._size

    #----------------------------------------------------------- __getitem__()
    def __getitem__(self, index):
        """
        __getitem__(self, index)
        
        PURPOSE: Get a byte from the memory block. This function lets you
                 treat the memory block like an array of bytes, which can be
                 indexed in the same way that python arrays are indexed.
        ARGS:    The index of the byte from where you attached to it. If the
                 index is negative, the indexing will be done from the end of
                 the memoryblock.
        RETURN:  A string of length 1 which is the byte requested.
                 An IndexError will be raised if the index is out of bounds.
        """
        if index < 0:
            index += self._size
            
        if 0 <= index < self._size:
            return self._get(index, 1)
        
        raise IndexError, "Index of of memory block range"

    #---------------------------------------------------------- __getslice__()
    def __getslice__(self, i, j):
        """
        __getslice__(self, i, j)
        
        PURPOSE: Get a range of bytes from the memory block. Similar to
                 getting the slice of a string.
        ARGS:    i- The beginning location of the slice.
                 j- The ending location of the slice.
        RETURN:  If either of the values are negative, they will be increased 
                 by the size of the block. this, in effect, indexes from the 
                 end of the block, similar to python lists.

                 If, after shifting, i < j, a string of length j-i will be
                 returned. if i >= j, and empty string will be returned.
        
                 If an index is out of bounds, then an IndexError will be 
                 raised.
        """
        if j == MAX_INDEX: j = self._size
        if j < 0: j += self._size
        if i < 0: i += self._size

        if i == j - 1:
            return self[i]
        
        if i >= j - 1:
            return ""

        if j > self._size:
            raise IndexError, "Slice out of range" 
            
        return self._get(i,j-i)

    #----------------------------------------------------------- __setitem__()
    def __setitem__(self, index, str):
        """
        __setitem__(self, index, str)
        
        PURPOSE: Write to memory block. 
        ARGS:    index- number of bytes from beginning of block to write
                   string at.
                 str- a string to write. Note that you use this function as as
                   a subscript notation:
                       sharedmem_object[0] = "Hello"
                   will write the 'Hello' characters from 0 to the lenght of
                   the string.
        RETURN:  None.
        """ 
        if type(str) != StringType:
            raise ValueError, "A string argument required"
    
        # if the length is 0, do nothing.
        l = len(str)
        if l==0: return
       
        # Try to normalize negative values.
        if index < 0: index += self._size

        if 1 <= index < self._size:
            if (index + l) > self._size:
                raise IndexError, "String exceeds array bounds"
            self._set(index,str)
        else:
            raise IndexError, "Index out of range"

    #---------------------------------------------------------- __setslice__()
    def __setslice__(self, i,j,o):
        """Illegal instruction, AttributeError always thrown"""
        raise AttributeError, "Shared Memory does not support __setslice__"
            
    #------------------------------------------------------------------ _get()
    def _get(self,offset, len):
        """
        _get(self,offset, len)
        
        PURPOSE: Get memory from the memory block 
        ARGS:    offset- Number of bytes from attach point to start reading.
                 len- number of bytes to read.
        RETURN:  A string with the bytes requested. If this object is not
                 attached, then None will be returned.
                 Otherwise, a ValueError may be raised if you request strange
                 values, and in the worst case, if you set self._addr to 0,
                 will likely get a Segmentation Fault. For these reasons,
                 leave the hidden data alone!
        """
        # return None if not attached.
        if not self.isAttached(): return None

        if offset < 0 or len < 0:
            raise ValueError, "Offset and length must not be less than 0"

        return ipcmod.rawmemrd(self._addr + offset, len)

    #------------------------------------------------------------------ _set()
    def _set(self, offset, str):
        """
        _set(self, offset, str)
        
        PURPOSE: Write a stirng of bytes to the memory block. 
        ARGS:    offset- number of bytes from the attach point to srite to.
                 str- the string to write to mem.
        RETURN:  None
        """
        
        # Return if not attached.
        if not self.isAttached(): return
        
        if offset < 0:
            raise ValueError, "offset must be greater or equal to 0"
    
        ipcmod.rawmemwt(self._addr + offset, str)

#====================================================== CLASS: SemaphoreGroup
class SemaphoreGroup:
    """
    CLASS:   SemaphoreGroup
    PURPOSE: A wrapper for ipc semaphores. This class leaves a little to be
             desired. I have not really needed it for anything more than
             single semaphores, so that is how it works now. You can have
             larger groups of semephores, but the wait and signal methods only
             affect one at a time, which kind of defeats the purpose of having
             multiple.  It's open source, so send me your changes, and I'll
             put them in!
    """
    #-------------------------------------------------------------- __init__()
    def __init__(self, key, sems=1, flags=0600, create=1):
        """
        __init__(self, key, sems=1, flags=0600, create=1)
        
        ARGS: key- The key to create the semaphores with. Usually obtained
                with the ftok method.
              sems=1- Number of semaphores in the group.
              flags=0600- the permissions which the group has. Similar to unix
                file permissions.
              cerate=1- boolean specifying if constructor should force the
                creation of the group.

              It works like this: If you set the create flag, then the
              constructor will attempt to create the group with the IPC_CREAT
              and IPC_EXCL flags set. If this is successful, then the values
              of each semephore will be set to 1. this means that the
              semaphore is AVAILABLE. If the group can not be obtained
              exclusively, another attempt to join a group alread formed will
              be made.  If this is successful, then the values will be
              unaltered.  If you set the create flag to 0, then only one
              attempt to obtain the group is made, and the values are not
              changed.
        """
        if sems < 1: raise ValueError, "sems must be a number greater than 0"
        self._sems = sems
        
        if not create:
            self._sem_id = ipcmod.semget(key, sems, flags)
            return

        try:
            self._sem_id = ipcmod.semget(key, sems, flags|IPC_CREAT|IPC_EXCL)
            # if successful, then this process is the creator.
            # We want initialize the values to 1
            for i in range(sems):
                ipcmod.semsetval(self._sem_id , i , 1)

        except EnvironmentError:
            # If this is reached, then the group probably exists.
            # We want to obtain it only.
            self._sem_id = ipcmod.semget(key, sems, flags)
    
    #------------------------------------------------------------------ wait()
    def wait(self, semid=0):
        """
        wait(self, semid=0)
        
        PURPOSE: Specify a semaphore in the group to reduce its value by one.
                 If the semaphore value is already 0 or lower, then this 
                 thread will wait until there have been enough signals to get
                 the value back up to one. Note that this does not prevent 
                 other python threads from running.
        ARGS:    semid=0- the number of the semaphore in the group that you
                   want to wait on.
        RETURN:  None 
        """
        if 0 <= semid < self._sems:
            num, op, flg = tups2strings((semid, -1, SEM_UNDO))
            ipcmod.semop(self._sem_id, num,op,flg)
        else:
            raise ValueError, "semid out of range"
    
    #---------------------------------------------------------------- signal()
    def signal(self, semid=0):
        """
        signal(self, semid=0)
        
        PURPOSE: Specify a semaphore in the group to increase its value by
                 one. This will allow one other thread or process to run if
                 it is currently waiting on the semaphore.
        ARGS:    semid=0- the number of the semaphore in the group that you
                   want to wait on.
        RETURN:  None
        """
        if 0 <= semid <self._sems:
            num,op,flg = tups2strings((semid, 1 , SEM_UNDO))
            ipcmod.semop(self._sem_id, num,op,flg)
        else:
            raise ValueError, "semid out of range"

    #----------------------------------------------------------------- value()
    def value(self, semid=0):
        """
        value(self, semid=0)
        
        PURPOSE: Get the value of a semaphore.
        ARGS:    semid=0- the number of the semaphore in the group that you
                   want to wait on.
        RETURN:  The value of the semaphore. 1 indicates that it is available.
                 Values less than 1 indicate that the semaphore is currently
                 unavailable.
        """
        return ipcmod.semgetval(self._sem_id, semid) 
#------------------------------- END pyipc.py -------------------------------
