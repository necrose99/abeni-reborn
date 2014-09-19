/****************************************************************************
 * FILE:        rawmem.c                                                    *
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
#include <string.h>


/****************************************************************************
  * FUNCTION:   rawmem_wt()                                                 *
  * PURPOSE:    This function allows you to write a series of bytes into    *
  *             Memory.                                                     *
  * ARGS:       long, string:                                               *
  *             - The long is the real address of the memory. The string    *
  *               that is passed into the function will be copied into      *
  *               memory starting at the address given.                     *
  *             - The string is the series of bytes which will be written   *
  *               to memory, if possible. Mpte that the strirng may have    *
  *               null bytes.                                               *
  *                                                                         *
  * RETURNS:    None.                                                       *
  *                                                                         *
  * RAISE:      - TypeError if the number of arguments, or there type       *
  *               is wrong.                                                 *
  *             - Its quite possible that a segmentation fault will result  *
  *               by using a bad address.  Be sure that you use a value     *
  *               you know is a memory address.                             *
  ***************************************************************************/
PyObject * rawmem_wt(PyObject * self, PyObject * args){
    char * addr, * buf;
    size_t  len;
    
    if(!PyArg_ParseTuple(args, "ls#", &addr, &buf, &len)) return NULL;

    memcpy(addr,buf, len);

    Py_INCREF(Py_None);
    return Py_None;
}

/****************************************************************************
  * FUNCTION:   rawmem_rd()                                                 *
  * PURPOSE:    This function allows you to read a series of bytes and      *
  *             return them to python as a string.                          *
  * ARGS:       long, int:                                                  *
  *             - The long is the real address of the memory.               *
  *             - The int is the number of bytes that you want to look at.  *
  *                                                                         *
  * RETURNS:    A string of the bytes you are interested in.                *
  *                                                                         *
  * RAISE:      - TypeError if the number of arguments, or there type       *
  *               is wrong.                                                 *
  *             - A seg fault could result from using a strange address.    *
  ***************************************************************************/
PyObject * rawmem_rd(PyObject * self, PyObject * args){
    char * addr;
    int len;

    if(!PyArg_ParseTuple(args, "li", &addr, &len)) return NULL;

    return Py_BuildValue("s#", addr, len);
}

/************************* End rawmem.c ************************************/
