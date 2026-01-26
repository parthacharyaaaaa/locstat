#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdbool.h>
#ifdef _WIN32
// TODO: Add appropriate header file
#else
#include <sys/mman.h>
#endif

static bool _is_ignorable(unsigned char c) {
    return ((c == 0x20) || (c == 0x09) || (c == 0x0D)
            || (c == 0x0B) || (c == 0x0C));
}

#ifdef _WIN32
// TODO: Add _parse_file_vm_map equivalent for Windows systems
#else
    static PyObject *
    _parse_file_vm_map(PyObject *self, PyObject *args){
        const char *filename,
        *singleline_character,
        *multiline_start_character, *multiline_end_character;
        
        Py_ssize_t singleline_length,
        multiline_start_length,
        multiline_end_length,
        minimum_characters;

        if (!PyArg_ParseTuple(args,
            "sz#z#z#n",
            &filename,
            &singleline_character, &singleline_length,
            &multiline_start_character, &multiline_start_length,
            &multiline_end_character, &multiline_end_length,
            &minimum_characters)){
                return NULL;
        }

        FILE *file = fopen(filename, "rb");
        if (!file){
            PyErr_SetFromErrnoWithFilename(PyExc_OSError, filename);
            return NULL;
        }

        struct stat st;
        if (fstat(fileno(file), &st) == -1){
            fclose(file);
            PyErr_SetFromErrnoWithFilename(PyExc_OSError, filename);
            return NULL;
        }

        if (st.st_size == 0){
            fclose(file);
            return Py_BuildValue("ii", 0, 0);
        }
        void *mapped_region = mmap(0, st.st_size, PROT_READ, MAP_PRIVATE, fileno(file), 0);
        if (mapped_region == MAP_FAILED){
            fclose(file);
            PyErr_SetFromErrnoWithFilename(PyExc_OSError, filename);
            return NULL;
        }

        const unsigned char *view = (unsigned char *) mapped_region;
        bool commented_block = false, singleline_comment = false;
        int multiline_start_pointer = 0, multiline_end_pointer = 0,
        singleline_pointer = 0;
        int total_lines = 0, loc = 0, valid_symbols = 0;
        Py_ssize_t i = 0;
        for (;i < st.st_size; i++){
            if (view[i] & 0b10000000){
                multiline_start_pointer = 0;
                multiline_end_pointer = 0;
                singleline_pointer = 0;
                continue;
            }
            else if (_is_ignorable(view[i])){
                multiline_start_pointer = 0;
                multiline_end_pointer = 0;
                singleline_pointer = 0;
                continue;
            }

            // Substring matching to determine parsing states
            if (!commented_block){
                if (multiline_start_character
                    && view[i] == multiline_start_character[multiline_start_pointer]){
                    multiline_start_pointer++;
                    if (multiline_start_pointer == multiline_start_length){
                        commented_block = true;
                        multiline_start_pointer = 0;
                    }
                    continue;
                }
                else if (singleline_character
                    && view[i] == singleline_character[singleline_pointer]){
                    singleline_pointer++;
                    if (singleline_pointer == singleline_length){
                        singleline_comment = true;
                        singleline_pointer = 0;
                        for (;i < st.st_size && view[i] != '\n'; i++);
                    }
                    continue;
                }
            }

            else if (commented_block
                && multiline_start_character
                && view[i] == multiline_end_character[multiline_end_pointer]){
                    multiline_end_pointer++;
                    if (multiline_end_pointer == multiline_end_length){
                        commented_block = false;
                        multiline_end_pointer = 0;
                    }
                    continue;
            }

            valid_symbols += !(commented_block || singleline_comment);

            multiline_start_pointer = 0;
            multiline_end_pointer = 0;
            singleline_pointer = 0;
            
            if (view[i] == '\n'){
                total_lines++;
                if (valid_symbols > minimum_characters){
                    loc++;
                }
                valid_symbols = 0;
                singleline_comment = false;
            }
        }
        // Files not terminating with newline
        if (view[i-1] != '\n'){
            total_lines++;
            if (valid_symbols > minimum_characters){
                loc++;
            }
        }

        fclose(file);
        munmap(mapped_region, st.st_size);
        return Py_BuildValue("ii", total_lines, loc);
    }

#endif

static PyObject *_parse_file(PyObject *self, PyObject *args){
    const char *filename,
    *singleline_character,
    *multiline_start_character, *multiline_end_character;
    
    Py_ssize_t singleline_length,
    multiline_start_length,
    multiline_end_length,
    minimum_characters;

    if (!PyArg_ParseTuple(args,
        "sz#z#z#n",
        &filename,
        &singleline_character, &singleline_length,
        &multiline_start_character, &multiline_start_length,
        &multiline_end_character, &multiline_end_length,
        &minimum_characters)){
            return NULL;
    }

    bool commented_block = false, singleline_comment = false;
    int multiline_start_pointer = 0, multiline_end_pointer = 0,
    singleline_pointer = 0;
    int total_lines = 0, loc = 0, valid_symbols = 0;
    FILE *file = fopen(filename, "rb");
    Py_ssize_t i;

    const unsigned int buffer_size = 4 * 1024 * 1024;
    unsigned char buffer[buffer_size];

    size_t chunk_size;
    while ((chunk_size = fread(buffer, 1, buffer_size, file)) > 0){
        for (i = 0; i < chunk_size; i++){
            if (buffer[i] & 0b10000000){
                multiline_start_pointer = 0;
                multiline_end_pointer = 0;
                singleline_pointer = 0;
                continue;
            }
            else if (_is_ignorable(buffer[i])){
                multiline_start_pointer = 0;
                multiline_end_pointer = 0;
                singleline_pointer = 0;
                continue;
            }
    
            // Substring matching to determine parsing states
            if (!commented_block){
                if (multiline_start_character
                    && buffer[i] == multiline_start_character[multiline_start_pointer]){
                    multiline_start_pointer++;
                    if (multiline_start_pointer == multiline_start_length){
                        commented_block = true;
                        multiline_start_pointer = 0;
                    }
                    continue;
                }
                else if (singleline_character
                    && buffer[i] == singleline_character[singleline_pointer]){
                    singleline_pointer++;
                    if (singleline_pointer == singleline_length){
                        singleline_comment = true;
                        singleline_pointer = 0;
                        for (;i < chunk_size && buffer[i] != '\n'; i++);
                    }
                    continue;
                }
            }
    
            else if (commented_block
                && multiline_start_character
                && buffer[i] == multiline_end_character[multiline_end_pointer]){
                    multiline_end_pointer++;
                    if (multiline_end_pointer == multiline_end_length){
                        commented_block = false;
                        multiline_end_pointer = 0;
                    }
                    continue;
            }
    
            valid_symbols += !(commented_block || singleline_comment);
    
            multiline_start_pointer = 0;
            multiline_end_pointer = 0;
            singleline_pointer = 0;
            
            if (buffer[i] == '\n'){
                total_lines++;
                if (valid_symbols > minimum_characters){
                    loc++;
                }
                valid_symbols = 0;
                singleline_comment = false;
            }
        }
    }
    // Files not terminating with newline
    if (buffer[i-1] != '\n'){
        total_lines++;
        if (valid_symbols > minimum_characters){
            loc++;
        }
    }
    fclose(file);
    return Py_BuildValue("ii", total_lines, loc);
}

static PyObject *
_parse_file_no_chunk(PyObject *self, PyObject *args){
    const char *filename,
    *singleline_character,
    *multiline_start_character, *multiline_end_character;
    
    Py_ssize_t singleline_length,
    multiline_start_length,
    multiline_end_length,
    minimum_characters;

    if (!PyArg_ParseTuple(args,
        "sz#z#z#n",
        &filename,
        &singleline_character, &singleline_length,
        &multiline_start_character, &multiline_start_length,
        &multiline_end_character, &multiline_end_length,
        &minimum_characters)){
            return NULL;
    }

    FILE *file = fopen(filename, "rb");
    if (!file){
        PyErr_SetFromErrnoWithFilename(PyExc_OSError, filename);
        return NULL;
    }

    fseek(file, 0, SEEK_END);
    long filelength = ftell(file);
    fseek(file, 0, SEEK_SET);

    unsigned char * buffer = malloc(filelength);
    if (!buffer){
        PyErr_Format(PyExc_MemoryError,
            "Failed to open file %s of size %d bytes",
            filename, filelength);
        return NULL;
    }
    fread(buffer, 1, filelength, file);
    
    bool commented_block = false, singleline_comment = false;
    int multiline_start_pointer = 0, multiline_end_pointer = 0,
    singleline_pointer = 0;
    int total_lines = 0, loc = 0, valid_symbols = 0;
    Py_ssize_t i;

    for (i = 0; i < filelength; i++){
        if (buffer[i] & 0b10000000){
            multiline_start_pointer = 0;
            multiline_end_pointer = 0;
            singleline_pointer = 0;
            continue;
        }
        else if (_is_ignorable(buffer[i])){
            multiline_start_pointer = 0;
            multiline_end_pointer = 0;
            singleline_pointer = 0;
            continue;
        }

        // Substring matching to determine parsing states
        if (!commented_block){
            if (multiline_start_character
                && buffer[i] == multiline_start_character[multiline_start_pointer]){
                multiline_start_pointer++;
                if (multiline_start_pointer == multiline_start_length){
                    commented_block = true;
                    multiline_start_pointer = 0;
                }
                continue;
            }
            else if (singleline_character
                && buffer[i] == singleline_character[singleline_pointer]){
                singleline_pointer++;
                if (singleline_pointer == singleline_length){
                    singleline_comment = true;
                    singleline_pointer = 0;
                    for (;i < filelength && buffer[i] != '\n'; i++);
                }
                continue;
            }
        }

        else if (commented_block
            && multiline_start_character
            && buffer[i] == multiline_end_character[multiline_end_pointer]){
                multiline_end_pointer++;
                if (multiline_end_pointer == multiline_end_length){
                    commented_block = false;
                    multiline_end_pointer = 0;
                }
                continue;
        }

        valid_symbols += !(commented_block || singleline_comment);

        multiline_start_pointer = 0;
        multiline_end_pointer = 0;
        singleline_pointer = 0;
        
        if (buffer[i] == '\n'){
            total_lines++;
            if (valid_symbols > minimum_characters){
                loc++;
            }
            valid_symbols = 0;
            singleline_comment = false;
        }
    }
    // Files not terminating with newline
    if (buffer[i-1] != '\n'){
        total_lines++;
        if (valid_symbols > minimum_characters){
            loc++;
        }
    }
    fclose(file);
    return Py_BuildValue("ii", total_lines, loc);
}

PyDoc_STRVAR(_parse_file_vm_map_doc, "Parse a UTF-8 byte stream to count total lines and lines of code (LOC)");
PyDoc_STRVAR(_parse_file_doc, "Parse a UTF-8 encoded file to count total lines and lines of code (LOC)");
PyDoc_STRVAR(_parse_file_no_chunk_doc,
    "Parse a UTF-8 encoded file to count total lines and lines of code (LOC), reading the entire file at once");

static PyMethodDef methods[] = {
    {
        .ml_name = "_parse_file_vm_map",
        .ml_doc = _parse_file_vm_map_doc,
        .ml_flags = METH_VARARGS,
        .ml_meth = _parse_file_vm_map,
    },
    {
        .ml_name = "_parse_file",
        .ml_doc = _parse_file_doc,
        .ml_flags = METH_VARARGS,
        .ml_meth = _parse_file,
    },
    {
        .ml_name = "_parse_file_no_chunk",
        .ml_doc = _parse_file_no_chunk_doc,
        .ml_flags = METH_VARARGS,
        .ml_meth = _parse_file_no_chunk,
    },
    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(module_doc, "Internal module for parsing files");
static PyModuleDef module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_parsing",
    .m_doc = module_doc,
    .m_size = -1,
    .m_methods = methods
};

PyMODINIT_FUNC
PyInit__parsing(void){
    return PyModule_Create(&module);
}