/****************************************************************************
 * FILE:        shmmod.c                                                    *
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

#include "ipcmod.h"

/****************************************************************************
  * FUNCTION:   shmmod_shmget()                                             *
  * PURPOSE:    Direct wrapper of the shmget system call.                   *
  * ARGS:       Three ints:                                                 *
  *             - The first int is the key of the Shared memory block       *
  *             - The second indicated the desired size, in bytes, of the   *
  *               shared memory block.  Note that this size is rounded up   *
  *               to the nearest page size.                                 *
  *             - The last int indicate the flags to create the block.      *
  *                                                                         *
  *             Note that these ints are passed directly into the shmget    *
  *             method, so see the man page for more details.               *
  *                                                                         *
  * RETURNS:    The memory segment identifier.                              *
  *                                                                         *
  * RAISE:      - TypeError if the number of arguments, or there type       *
  *               is wrong.                                                 *
  *             - EnvironmentError is raised if the shmget                  *
  *               function fails. Note that the error reported may not      *
  *               make much sense. These error are usually created when     *
  *               a process tries to acces a fobidden key, or the           *
  *               block does not exist.  You can use the IPC_CREAT flag     *
  *               to create the block if you like.                          *
  ***************************************************************************/
PyObject * shmmod_shmget(PyObject * self, PyObject * args){
    int key, size, flg, ans; 

    if(!PyArg_ParseTuple(args, "iii", &key, &size, &flg)) return NULL;
    
    ans = shmget(key, size, flg);
    if ( ans == -1) return PyErr_SetFromErrno(PyExc_EnvironmentError);

    return Py_BuildValue("i", ans);
}

/*****************************************************************
  * FUNCTION:   shmmod_shmat()
  * PURPOSE:    Direct wrapper of the shmat system call.
  * ARGS:       three ints:
  *             - The first int is the key of the Shared memory block
  *             - The second indicates what address you would like to 
  *               bind to.  I STRONGLY SUGGEST USING 0 because you have
  *               no idea where your memory space is in python.  See the
  *               man page if you want to screw around with setting the
  *               attach address, but I think it is a waste :)
  *             - The last int indicate the flags to create the block.
  *
  *             Note that these ints are passed directly into the shmget
  *             method, so see the man page for more details.
  *
  * RETURNS:    The address which now points to the shared block of 
  *             memory.  This is the address of the start, and in python
  *             addresses by them selfves do not mean much, so you will
  *             need to make use of the rawmem.c functions.
  *
  * RAISE:      - TypeError if the number of arguments, or there type
  *               is wrong. 
  *             - EnvironmentError is raised if the msgget
  *               function fails. Note that the error reported may not
  *               make much sense. These error are usually created when
  *               a process tries to acces a forbiden queue, or the 
  *               queue does not exist.  You can use the IPC_CREAT flag
  *               to create the queue if you like.  It is obtained from
  *               the ipcmod.ipd_creat() function.
  ****************************************************************/
PyObject * shmmod_shmat(PyObject * self, PyObject * args){
    int key, flg;
    long addr;
    void * ans; 
    
    if(!PyArg_ParseTuple(args, "ili", &key, &addr, &flg)) return NULL;
    
    ans = shmat(key, (void *) addr, flg);
    if (((int) ans) == -1) 
        return PyErr_SetFromErrno(PyExc_EnvironmentError);

    return Py_BuildValue("l", ans);
}

/*****************************************************************
  * FUNCTION:   shmmod_shmdt()
  * PURPOSE:    Direct wrapper of the shmdt system call.
  * ARGS:       one long:
  *             - The long is the address of the block which you want 
  *               to unlink the current process from. Note that this number
  *               should be the same as a number passed back only once
  *               by the shmat function previously.
  *
  * RETURN:     None
  *
  * RAISE:      TypeError if the arguments are incorrct.
  *             If shmdt fails, there is not really anthing we can do,
  *             so no action is taken.
  ****************************************************************/
PyObject * shmmod_shmdt(PyObject * self, PyObject * args){
    long addr;
    if(!PyArg_ParseTuple(args, "l", &addr))  return NULL;
    
    shmdt((void *)addr);

    Py_INCREF(Py_None);
    return Py_None;
}

/*****************************************************************
  * FUNCTION:   shmmod_remove()
  * PURPOSE:    Remove the Shared Memory Block.
  * ARGS:       one long:
  *             - The long is the address of the block which to delete 
  *               from the system.
  *
  * RETURN:     None
  *
  * RAISE:      TypeError if the arguments are incorrct.
  *             If the current process does not have modify 
  *             permissions on the block, and EnvironmentError
  *             is raised.
  ****************************************************************/
PyObject * shmmod_remove(PyObject * self, PyObject * args){
    int shmid;
    struct shmid_ds buf;
    
    if(!PyArg_ParseTuple(args, "i", &shmid)) return NULL;

    if(shmctl(shmid, IPC_RMID, &buf))
        return PyErr_SetFromErrno(PyExc_EnvironmentError);

    Py_INCREF(Py_None);
    return Py_None;
}

void _initshmmod(void){ }
