// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
#include <Python.h>

#include "Radxa_Zero/rzero_dht_mraa_read.h"

// Wrap calling dht_read function and expose it as a DHT.read Python module & function.
static PyObject* Radxa_Zero_mraa_Driver_read(PyObject *self, PyObject *args)
{
	// Parse sensor and pin integer arguments.
    int sensor, pin;
    if (!PyArg_ParseTuple(args, "ii", &sensor, &pin)) {
        return NULL;
    }
    // Call dht_read and return result code, humidity, and temperature.
    float humidity = 0, temperature = 0;
    int result = rzero_dht_mraa_read(sensor, pin, &humidity, &temperature);
    return Py_BuildValue("iff", result, humidity, temperature);
}

// Boilerplate python module method list and initialization functions below.

static PyMethodDef module_methods[] = {
    {"read", Radxa_Zero_mraa_Driver_read, METH_VARARGS, "Read DHT sensor value on a Radxa Zero using libmraa."},
    {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION > 2
static struct PyModuleDef rzero_mraa_dht_module = {
    PyModuleDef_HEAD_INIT,
    "Radxa_Zero_mraa_Driver",        // name of module
    NULL,                      // module documentation, may be NULL
    -1,                        // size of per-interpreter state of the module, or -1 if the module keeps state in global variables.
    module_methods
};
#endif

#if PY_MAJOR_VERSION > 2
PyMODINIT_FUNC PyInit_Radxa_Zero_mraa_Driver(void)
#else
PyMODINIT_FUNC initRadxa_Zero_mraa_Driver(void)
#endif
{    
    #if PY_MAJOR_VERSION > 2
      PyObject* module = PyModule_Create(&rzero_mraa_dht_module);
    #else
      Py_InitModule("Radxa_Zero_mraa_Driver", module_methods);
    #endif

    #if PY_MAJOR_VERSION > 2
       return module;
    #else
       return;
    #endif
}
