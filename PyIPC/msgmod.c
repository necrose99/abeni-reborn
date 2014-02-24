/****************************************************************************
 * FILE:        msgmod.c                                                    *
 * Copyright (C) 2001, Neil Macneale <mac4-pyipc@theory.org>                *
 *                                                                          *
 * This library is free software; you can redistribute it and/or modify it  *
 * under the terms of the GNU Lesser General Public License as published by *
 * the Free Software Foundation; either version 2.1 of the License, or (at  *
 * your option) any later version.                                          *
 *                                                                          *
 * This library is distributed in the hope that it will be useful, but      *
 * WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser *
 * General Public License for more details.                                 *
 *                                                                          *
 * You should have received a copy of the GNU Lesser General Public License *
 * along with this library; if not, write to the Free Software Foundation,  *
 * Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA             *
 *                                                                          * 
 ****************************************************************************/
# include "ipcmod.h"

/* Some implementations define this, others do not. */
#ifdef MSGMAX
#define BUF_SIZE ( MSGMAX + sizeof(long) )
#else
#define BUF_SIZE 4096
#endif

/*****************************************************************
  * FUNCTION:   msgmod_msgget()
  * PURPOSE:    Direct wrapper of the msgget system call.  It takes
  *             two python ints, analogous to the system call.
  * ARGS:       Two ints: the first is the msg queue key, the second 
  *             flags you would like to use. See the msgget man page.
  * RETURNS:    The msg queue id, when the mesege queue is 
  *             successfully created, or found.
  * RAISE:      TypeError if the number of arguments, or there type
  *             is wrong. EnvironmentError is raised if the msgget
  *             function fails. Note that the error reported may not
  *             make much sense. These error are usually created when
  *             a process tries to acces a forbiden queue, or the 
  *             queue does not exist.  You can use the IPC_CREAT flag
  *             to create the queue if you like.  It is obtained from
  *             the ipcmod.ipd_creat() function.
  ****************************************************************/
PyObject * msgmod_msgget(PyObject * self, PyObject * args){
    key_t key = -1;
    int flg   = 0;
    int msqid = -1;
    
    if(!PyArg_ParseTuple(args, "ii", &key, &flg)) return NULL;

    msqid = msgget(key, flg);
    
    if (msqid == -1) 
        return PyErr_SetFromErrno(PyExc_EnvironmentError);
    
    return Py_BuildValue("i", msqid);
}

/*****************************************************************
  * FUNCTION:   msgmod_msgsnd()
  * PURPOSE:    Direct wrapper of the msgsnd system call.
  * ARGS:       int, string, int. 
  *             - The first int is the msg queue id, which this 
  *               process must have access to. 
  *             - The string represents both the data, and the length
  *               of the data. The string should be directly 
  *               analogous to the msgbuf struct, including the long
  *               bytes at the front of the string to specify the 
  *               message type.  You should use the struct.pack 
  *               method to create this string. the length of the 
  *               string is passed to msgsnd as msgsz.
  *             - The last int specifies the flags are discussed in 
  *               the msgsnd manpage.
  *             
  * RETURNS:    None on success.
  * RAISE:      TypeError if the number of arguments, or there type
  *             is wrong. EnvironmentError is raised if the msgset
  *             function fails. Note that the error reported may not
  *             make much sense. These error are usually created when
  *             a process tries to access a forbiden queue, or the 
  *             queue does not exist.
  ****************************************************************/
PyObject * msgmod_msgsnd(PyObject * self, PyObject * args){
    int msqid, size, flg;
    char * buf;

    if(!PyArg_ParseTuple(args, "is#i", &msqid, &buf, &size, &flg)) return NULL;
 
    if (-1 == msgsnd(msqid, (struct msgbuf *) buf, size-sizeof(long), flg))
        return PyErr_SetFromErrno(PyExc_EnvironmentError);
    
    Py_INCREF(Py_None);
    return Py_None;
}

/*****************************************************************
  * FUNCTION:   msgmod_msgrcv()
  * PURPOSE:    Direct wrapper of the msgrcv system call.
  * ARGS:       Three ints. 
  *             - The first int is the msg queue id, which this 
  *               process must have access to. 
  *             - The second int specifies the type of the message. 
  *               See the msgrcv man page.
  *             - The last int specifies the flags are discussed in 
  *               the msgrcv manpage.
  *             
  * RETURNS:    If a message is successfully read, then a string 
  *             representation of the data read will be returned.  The
  *             type of the message will the the first bytes in the string.
  *             Use struct.unpack() to decode the struct. The length of
  *             the string will be exactly the number returned by the
  *             msgrcv function, plus the length of the long int.
  *
  *             If no message is in the queue and you do not use the 
  *             NO_WAIT flag, then this function will wait until a 
  *             message is put in the queue.  see the man page for msgrcv.
  *
  *             If no message is available and you give the NO_WAIT flag,
  *             then None is returned.
  *
  * RAISE:      TypeError if the number of arguments, or there type
  *             is wrong. 
  *             EnvironmentError is raised if the msgset function fails. 
  *             Note that the error reported may not make much sense. 
  *             These error are usually created when a process tries to 
  *             access a forbiden queue, or the queue does not exist.
  ****************************************************************/
PyObject * msgmod_msgrcv(PyObject * self, PyObject * args){
    int msqid, size, flg, type;
    char buff[BUF_SIZE];

    if(!PyArg_ParseTuple(args, "iii", &msqid, &type, &flg)) return NULL;
    
    Py_BEGIN_ALLOW_THREADS
    size = msgrcv(msqid, (struct msgbuf *) buff, BUF_SIZE, type, flg);
    if (size == -1){
        Py_BLOCK_THREADS
        if (errno == ENOMSG && flg == IPC_NOWAIT){
            Py_INCREF(Py_None);
            return Py_None;
        }

        return PyErr_SetFromErrno(PyExc_EnvironmentError);
    }
    Py_END_ALLOW_THREADS

    return Py_BuildValue("s#", buff, size + sizeof(long));
}

/*****************************************************************
  * FUNCTION:   msgmod_remove()
  * PURPOSE:    Delete a message queue from the system.
  * ARGS:       One int. 
  *             - The Message queue id to remove.
  * RETURNS:    None
  * RAISE:      TypeError if the number of arguments, or there type
  *             is wrong. 
  *             EnvironmentError is raised if the caller of this
  *             function does not have the correct permossions to 
  *             delete the queue from the system.
  ****************************************************************/
PyObject * msgmod_remove(PyObject * self, PyObject * args) {
    int msqid;
    struct msqid_ds buf;
    
    if(!PyArg_ParseTuple(args, "i", &msqid)) return NULL;

    if(msgctl(msqid, IPC_RMID, &buf))
        return PyErr_SetFromErrno(PyExc_EnvironmentError);

    Py_INCREF(Py_None);
    return Py_None;
}

void _initmsgmod(void){ }
