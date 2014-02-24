/****************************************************************************
 * FILE:        semmod.c                                                    *
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

#if defined(__GNU_LIBRARY__) && !defined(_SEM_SEMUN_UNDEFINED)
 /* gnu defines semun in sem.h */
#else
union semun {
    int val;
    struct semid_ds *buf;
    unsigned short int *array;
    struct seminfo *__buf;
};
#endif

/******************************************************************
  * FUNCTION:    semmod_remove()
  * PURPOSE:     remove a semephore set that the current process has
  *              modify access to.  This function does the job of the
  *              semctl(id, IGNORED, IPC_RMID, IGNORED).
  * ARGS:        one int, the semaphore set id.
  * RETURNS:     None on success.
  * RAISE:       An EnvironmentError will be raised if the semaphore
  *              id does not exist, or you do not have modify access 
  *              to it.
  *              A TypeError occurs if you give the wrong arguments.
  *****************************************************************/
PyObject * semmod_remove(PyObject * self, PyObject * args){
    int key;
    union semun un;

    if(!PyArg_ParseTuple(args, "i", &key)) return NULL;

    if (semctl(key, 0, IPC_RMID, un) == -1)
        return PyErr_SetFromErrno(PyExc_EnvironmentError);

    Py_INCREF(Py_None);
    return Py_None;
}


/*********************************************************************
  * FUNCTION:    semmod_setval()
  * PURPOSE:     Set the count on a specific semaphore is.
  * ARGS:        three ints.
  *              - First int is the samaphore group id
  *              - Second int is the semaphore number in the group.
  *              - Third is the int.
  * RETURNS:     None on success.
  * RAISE:       - If you do not have modify access to the semaphore 
  *                group, and EnvironmentError will be raise.
  *              - TypeError raise if your raguments are out of whack.
  *******************************************************************/
PyObject * semmod_setval(PyObject * self, PyObject * args){
    int key, semNum, newVal, ans;
    union semun un;
    
    if(!PyArg_ParseTuple(args, "iii", &key, &semNum, &newVal)) return NULL;

    un.val = newVal;

    ans = semctl(key, semNum, SETVAL, un);
    if (ans == -1)
        return PyErr_SetFromErrno(PyExc_EnvironmentError);
    
    Py_INCREF(Py_None);
    return Py_None;
}

/**********************************************************************
  * FUNCTION:    semmod_getval()
  * PURPOSE:     Determine the curent count on the semaphore.
  * ARGS:        two ints:
  *              - First int is the semaphore group id.
  *              - Second int is the specific semaphore in the group.
  * RETURNS:     the count, duh.
  * RAISE:       - TypeError if arguments are bad.
  *              - EnvironmentError if current process does not have read
  *                access.
  *********************************************************************/
PyObject * semmod_getval(PyObject * self, PyObject * args){
    int key, semNum, ans;
    union semun u;
    
    if(!PyArg_ParseTuple(args, "ii", &key, &semNum)) return NULL;

    ans = semctl(key, semNum, GETVAL, u);
    if (ans == -1)
        return PyErr_SetFromErrno(PyExc_EnvironmentError);
    
    return Py_BuildValue("i", ans);
}

/********************************************************************
  * FUNCTION:    semmod_semget()
  * PURPOSE:     wrap the semget system function.
  * ARGS:        three ints:
  *              - first is the Semaphore group key.
  *              - second is the number of semaphores in the group.
  *              - third is the permissions.  see man semget.
  * RETURNS:     The id of the semaphore group.
  * RAISE:       TypeError:  bad agruments.
  *              EnvironmentError: if the set is not available. Either
  *              the current process does not have access, or you were
  *              attempting to get an eclusive group.
  *******************************************************************/
PyObject * semmod_semget(PyObject * self, PyObject * args){
    int key, nsems, flg, ans;
    
    if(!PyArg_ParseTuple(args, "iii", &key, &nsems, &flg)) return NULL;

    ans = semget(key, nsems, flg);
    if ( ans == -1) return PyErr_SetFromErrno(PyExc_EnvironmentError);

    return Py_BuildValue("i", ans);
}

/********************************************************************
  * FUNCTION:    semmod_semop()
  * PURPOSE:     wrap the semop system function.
  * ARGS:        one int, and three strings.:
  *              - the int is the Semaphore group key.
  *              - The three strings represent int arrays, which are
  *                the sem_num, sem_op and sem_flg arguments to the
  *                semop function.
  * RETURNS:     None
  * RAISE:       - TypeError:  bad agruments. Bad arguments include not 
  *                passing one int and three strings, passing strings
  *                which are not equal size or do not have length evenly
  *                divisable by sizeof(long).
  *              - MemoryError: if a block of memory large enough to 
  *                dump the ints into sembuf structs can not be allocated.
  *                This is rare.
  *              EnvironmentError: if the set is not available. Either
  *              the current process does not have access, or you were
  *              attempting to get an eclusive group.
  *******************************************************************/
PyObject * semmod_semop(PyObject * self, PyObject * args){
    int key, ops, sem_num_size, sem_op_size, sem_flg_size, i, ans;
    int * sem_num, * sem_op, * sem_flg;

    struct sembuf * buffs;
    
    /* This line is only here to prevent annoying compiler warnings. */
    key = ops = sem_num_size = sem_op_size = sem_flg_size = 0;
   
    if(!PyArg_ParseTuple(args, "is#s#s#", &key, &sem_num, &sem_num_size,
                                                &sem_op,  &sem_op_size,
                                                &sem_flg, &sem_flg_size))
    {
        return NULL;
    }

    /* all strings  must be the same length. anyother situation would lead
     * to strange results. */
    if (sem_num_size != sem_op_size || sem_op_size != sem_flg_size){
        PyErr_SetString(PyExc_TypeError,"All strings must be the same size");
        return NULL;
    }

    /* If no strings are passed for operations, then there is nothing to do. */
    if (sem_op_size == 0) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    /* The size of the strings MUST be evenly divisable by the size of an int
     * because it would not be clear where to truncate/expand otherwise */
    if (sem_op_size % sizeof(int)){
        PyErr_SetString(PyExc_TypeError, 
                "Strings are not divisable by sizeof(int)");
        return NULL;
    }

    ops = sem_op_size / sizeof(int);
    /* Now that all the value checking is done, create the sembufs... */    
    buffs = calloc(ops, sizeof(struct sembuf));
    if (buffs == NULL){
        PyErr_SetString(PyExc_MemoryError, "Malloc Faliure. Ack!");
        return NULL;
    }
    
    /* ...and fill in their values */
    for(i = 0; i < ops; i++){
        buffs[i].sem_num = (short) sem_num[i];
        buffs[i].sem_op  = (short) sem_op[i];
        buffs[i].sem_flg = (short) sem_num[i];
    }

    /* The operation may force the thread to wait. Allow other python threads
     * to run in the mean time. */
    Py_BEGIN_ALLOW_THREADS
    ans = semop(key, buffs, ops);
    Py_END_ALLOW_THREADS

    /* Smokey says, "Prevent Memory Leaks" */
    free(buffs);
    if (ans == -1)
        return PyErr_SetFromErrno(PyExc_EnvironmentError);
    
    Py_INCREF(Py_None);
    return Py_None;
}

void _initsemmod(void){ }
