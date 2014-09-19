/****************************************************************************
 * FILE:        ftokmod.c                                                   *
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
  * This function is a direct wrapper for the ftok unix function. See its   *
  * man page.  Please note that this function does not gaurentee a unique   *
  * key.  It is best if you specify your own key, then make sure all        *
  * processes know what key to you by some other means.                     *
  ***************************************************************************/
PyObject * ipcmod_ftok(PyObject * self, PyObject * args){
    char * file;
    int  proj_int;
    char proj_char;
    key_t ftok_key = -1;
    
    if(!PyArg_ParseTuple(args, "si:ipcmod_ftok", &file, &proj_int)) 
        return NULL;

    proj_char = (char) proj_int;

    ftok_key = ftok(file, proj_char);
    if (ftok_key == -1)
        return PyErr_SetFromErrno(PyExc_EnvironmentError);

    return Py_BuildValue("i", ftok_key);
}


