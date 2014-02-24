/****************************************************************************
 * FILE:        ipcmod.h                                                    *
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

/**************************************************************************** 
 * This header simply states the methods which are used in the global       *
 * scope, specifically, the python module functions.  It also makes it      *
 * so each of the other files only needs to import one header. How nice :)  *
 ****************************************************************************/

#ifndef __IPCMOD_H__
#define __IPCMOD_H__

#include <Python.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <sys/shm.h>
#include <sys/sem.h>

PyObject * ipcmod_ftok(PyObject * self, PyObject * args);

PyObject * msgmod_msgsnd(PyObject * self, PyObject * args);
PyObject * msgmod_msgrcv(PyObject * self, PyObject * args);
PyObject * msgmod_msgget(PyObject * self, PyObject * args);
PyObject * msgmod_remove(PyObject * self, PyObject * args);
void _initmsgmod(void);

PyObject * shmmod_shmget(PyObject * self, PyObject * args);
PyObject * shmmod_shmat (PyObject * self, PyObject * args);
PyObject * shmmod_shmdt (PyObject * self, PyObject * args);
PyObject * shmmod_remove(PyObject * self, PyObject * args);
void _initshmmod(void);

PyObject * semmod_semget(PyObject * self, PyObject * args);
PyObject * semmod_semop (PyObject * self, PyObject * args);
PyObject * semmod_getval(PyObject * self, PyObject * args);
PyObject * semmod_setval(PyObject * self, PyObject * args);
PyObject * semmod_remove(PyObject * self, PyObject * args);
void _initsemmod(void);

PyObject * rawmem_wt    (PyObject * self, PyObject * args);
PyObject * rawmem_rd    (PyObject * self, PyObject * args);

void initipcmod(void);

#endif /* __IPCMOD_H__ */
