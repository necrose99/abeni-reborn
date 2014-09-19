/****************************************************************************
 * FILE:        ipcmod.c                                                    *
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

/*************************************************************************
  * All of the functions defined here are simply for accessing
  * values defined in the C libraries which need to be used in the python
  * module.  You should not ever need to call these functions directly
  * because the standard names are given in pyipc for your use.
  ************************************************************************/

/*Python module method definitions */
static PyMethodDef meth[] = {
    {"ftok",         ipcmod_ftok,      METH_VARARGS},
    {"msgget",       msgmod_msgget,    METH_VARARGS},
    {"msgsnd",       msgmod_msgsnd,    METH_VARARGS},
    {"msgrcv",       msgmod_msgrcv,    METH_VARARGS},
    {"msgremove",    msgmod_remove,    METH_VARARGS},
    {"semget",       semmod_semget,    METH_VARARGS},
    {"semop" ,       semmod_semop,     METH_VARARGS},
    {"semgetval",    semmod_getval,    METH_VARARGS},
    {"semsetval",    semmod_setval,    METH_VARARGS},
    {"semremove",    semmod_remove,    METH_VARARGS},
    {"shmget",       shmmod_shmget,    METH_VARARGS},
    {"shmat",        shmmod_shmat,     METH_VARARGS},
    {"shmdt",        shmmod_shmdt,     METH_VARARGS},
    {"shmremove",    shmmod_remove,    METH_VARARGS},
    {"rawmemwt",     rawmem_wt,        METH_VARARGS},
    {"rawmemrd",     rawmem_rd,        METH_VARARGS},
    {NULL,NULL}
};



/* The function below was ripped from the Python OpenSSL Wrappers package
 * written by Peter Shannon.
 * http://www.sourceforge.net/projects/pow
 */
static void install_int_const( PyObject *d, char *name, int value ) {
    PyObject *v = PyInt_FromLong( (long)value );
    
    if (!v || PyDict_SetItemString(d, name, v) ) PyErr_Clear();
    
    Py_XDECREF(v);
}


/** This function is called when the module is initialized.  It calles three
  * other initializers which, at this point, do nothing. */
void initipcmod(){
    PyObject *obj;
        
    _initmsgmod();
    _initshmmod();
    _initsemmod();

    obj = Py_InitModule("ipcmod", meth);
    obj = PyModule_GetDict(obj);
    install_int_const(obj , "IPC_CREAT"   , IPC_CREAT   );
    install_int_const(obj , "IPC_PRIVATE" , IPC_PRIVATE );
    install_int_const(obj , "IPC_EXCL"    , IPC_EXCL    );
    install_int_const(obj , "IPC_NOWAIT"  , IPC_NOWAIT  );
#ifdef MSG_EXCEPT
    install_int_const(obj , "MSG_EXCEPT"  , MSG_EXCEPT  );
#endif
    install_int_const(obj , "SEM_UNDO"    , SEM_UNDO    );
    install_int_const(obj , "SHMLBA"      , SHMLBA      );
    install_int_const(obj , "SHM_RND"     , SHM_RND     );
    install_int_const(obj , "SHM_RDONLY"  , SHM_RDONLY  );
}

/******************** END ipcmod.c ***********************/
