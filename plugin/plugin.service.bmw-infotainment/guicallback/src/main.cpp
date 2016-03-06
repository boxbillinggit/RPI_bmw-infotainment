/* 
 * File:   main.cpp
 * Author: Lars
 *
 * Created on den 20 juli 2015, 23:18
 * 
 * 
 */

#include <Python.h>
#include <iostream>

// don't need to use std::cout
using namespace std;

/*
 *  python specific variables
 */

// error class
PyObject* pyBM_Error = NULL;

// callback PyBM-objects
PyObject* pyBM_callback_onConnect = NULL;
PyObject* pyBM_callback_onDisconnect = NULL;

/*
 * Set callbacks
 * TODO: explain what's happening here below
 */

// set a callback when pressing connect button.
PyObject* pybm_set_callback_onConnect(PyObject *self, PyObject *args) {
    PyObject *result = NULL;
    PyObject *temp;

    // TODO: "O:what-the-heck-is-this-refered-to"???
    if (PyArg_ParseTuple(args, "O:setOnConnect", &temp)) {
        
        if (!PyCallable_Check(temp)) {
            PyErr_SetString(PyExc_TypeError, "parameter must be callable");
            return NULL;
        }
        
        Py_XINCREF(temp);         /* Add a reference to new callback */
        Py_XDECREF(pyBM_callback_onConnect);  /* Dispose of previous callback */
        pyBM_callback_onConnect = temp;       /* Remember new callback */
        
        /* Boilerplate to return "None" */
        Py_INCREF(Py_None);
        result = Py_None;
    }
    return result;
}

// set a callback when pressing disconnect button.
PyObject* pybm_set_callback_onDisconnect(PyObject *self, PyObject *args) {
    PyObject *result = NULL;
    PyObject *temp;

    // TODO: "O:what-the-heck-is-this-refered-to"???
    if (PyArg_ParseTuple(args, "O:setOnDisconnect", &temp)) {
        
        if (!PyCallable_Check(temp)) {
            PyErr_SetString(PyExc_TypeError, "parameter must be callable");
            return NULL;
        }
        
        Py_XINCREF(temp);         /* Add a reference to new callback */
        Py_XDECREF(pyBM_callback_onDisconnect);  /* Dispose of previous callback */
        pyBM_callback_onDisconnect = temp;       /* Remember new callback */
        
        /* Boilerplate to return "None" */
        Py_INCREF(Py_None);
        result = Py_None;
    }
    return result;
}

/*
 * trigger callbacks  from python..
 *
 */

//  trigger callback for 'connect'
PyObject* pybm_onConnect(PyObject *self, PyObject *args) {
    
    // execute callback, if we have defined a callback.
    if (pyBM_callback_onConnect) {
        
        // call the python function (without arguments=NULL). 
        //'pyBM_callback_onReconnect' is a pointer to the python-function
        PyObject* result = PyObject_CallObject(pyBM_callback_onConnect, NULL);
        
        /* Pass error back */ 
        if (result == NULL)
            return NULL; 
        
        Py_DECREF(result);
        
    } else {
        
        //throw error back?
        PyErr_SetString(pyBM_Error, "No callback is defined");
        return NULL;
        
    }
    
    // return void to python interpreter
    Py_INCREF(Py_None);
    return Py_None;
}

// trigger callback for 'disconnect'
PyObject* pybm_onDisconnect(PyObject *self, PyObject *args) {
    
    // execute callback, if we have defined a callback. Else throw error back?
    if (pyBM_callback_onDisconnect) {
        
        // call the python function (without arguments=NULL). 
        //'pyBM_callback_onReconnect' is a pointer to the python-function
        PyObject* result = PyObject_CallObject(pyBM_callback_onDisconnect, NULL);
        
        /* Pass error back */ 
        if (result == NULL)
            return NULL; 
        
        Py_DECREF(result);
        
    } else {
        
        //throw error back?
        PyErr_SetString(pyBM_Error, "No callback is defined");
        return NULL;
        
    }
    
    // return void to python interpreter
    Py_INCREF(Py_None);
    return Py_None;
}

/* hello world function */
PyObject* helloworld(PyObject *self, PyObject *args) {
    
    // a pointer
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command))
        return NULL;
    sts = system(command);
    return Py_BuildValue("i", sts);
    
}

/*
 * Define all methods for the module
 */
static PyMethodDef GUICallbackMethods[] = {
    //{"start",  pybm_start_service, METH_VARARGS, "Starts the service."},
    {"setOnConnect",  pybm_set_callback_onConnect, METH_VARARGS, "Set callback handler for 'Connect' in settings."},
    {"setOnDisconnect",  pybm_set_callback_onDisconnect, METH_VARARGS, "Set callback handler for 'Disconnect' in settings."},
    {"onConnect",  pybm_onConnect, METH_VARARGS, "Trigger callback 'onConnect' in service"},
    {"onDisconnect",  pybm_onDisconnect, METH_VARARGS, "Trigger callback 'onDisconnect' in service"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

/* 
 * Init this library 
 */
PyMODINIT_FUNC initlibguicallback(void) {
    
    PyObject *m;
    
    // set module's name
    m = Py_InitModule("libguicallback", GUICallbackMethods);
    if (m == NULL)
        return;

    // init error class
    pyBM_Error = PyErr_NewException("guicallback.error", NULL, NULL);
    Py_INCREF(pyBM_Error);
    PyModule_AddObject(m, "error", pyBM_Error);
    
}

/*
 * Main function
 */
int main(int argc, char** argv) {

    /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(argv[0]);

    /* Initialize the Python interpreter.  Required. */
    Py_Initialize();
    
    // initialize the Python extension module
    initlibguicallback();
    
    // return 0
    return (EXIT_SUCCESS);
}

