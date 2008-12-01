/*
  hyperestraier.c - HyperEstraier wrapper for Python
  Copyright (c) 2007, SOUNDBOARD Co.,Ltd.
  All rights reserved. 
  Written by Yusuke YOSHIDA <usk.yos_at_gmail.com>
  $Id: estraiernative.c,v 1.11 2007/04/15 05:52:47 yosida Exp $
*/

#include <Python.h>
#include <structmember.h>
#include <estraier.h>
#include <estmtdb.h>
#include <cabin.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>


#ifdef DEBUG 
static void debug(char *msg) {
  char dmsg[BUFSIZ];
  sprintf(dmsg, "DEBUG : %s\n", msg);
  fputs(dmsg, stderr);
}

static void refcount(PyObject *o, char *tag) {
    char buf[BUFSIZ];
    sprintf(buf, "REFCOUNT - %s : %d", tag, (o)->ob_refcnt);
    debug(buf);
}
#else
static void debug(char *msg) {
}
static void refcount(PyObject *o, char *tag) {
}
#endif

/* --------------------------------------------------------------------- */

/* ==================== type definition ==================== */
static PyObject *EST_Error;

typedef struct {
    PyObject_HEAD;
    ESTDOC *doc;
} PyESTDOC;
static PyTypeObject PyESTDOC_Type;
#define PyESTDOCObject_Check(v)	((v)->ob_type == &PyESTDOC_Type)

typedef struct {
    PyObject_HEAD;
    int ecode;
    ESTMTDB *db;
} PyESTDB;
static PyTypeObject PyESTDB_Type;
#define PyESTDBObject_Check(v)	((v)->ob_type == &PyESTDB_Type)

typedef struct {
    PyObject_HEAD;
    ESTCOND *cond;
} PyESTCOND;
static PyTypeObject PyESTCOND_Type;
#define PyESTCONDObject_Check(v)	((v)->ob_type == &PyESTCOND_Type)

typedef struct {
    PyObject_HEAD;
    int *ids;
    int *dbidxs;
    int num;
    CBMAP *hints;
} PyESTRES;
static PyTypeObject PyESTRES_Type;
#define PyESTRESObject_Check(v)	((v)->ob_type == &PyESTRES_Type)

static PyESTRES* estres_factory(void);

/* ==================== utility functions ==================== */
#define define_const(dic, key, val) do { \
    PyDict_SetItemString(dic, key, PyInt_FromLong(val)); \
} while (0)

#define define_const_fmt(dic, key, val, fmt) do { \
    PyObject* o = Py_BuildValue(fmt, val); \
    PyDict_SetItemString(dic, key, o); \
} while (0)

#define null_check(o, msg)	do { \
	if (o == NULL) {  \
		if (msg != NULL) \
			  PyErr_SetString(EST_Error, msg); \
		return NULL;  \
	} \
} while (0)

/* python dict object -> CBMAP */
static CBMAP*
dic2CBMAP(PyObject *dic)
{
	CBMAP *map;
	PyListObject *items;
	int items_len, i;
	PyObject *key_o, *score_o;
	char *key, *score;
	
	if (!PyDict_Check(dic)) {
		PyErr_SetString(PyExc_TypeError, "dict is expected");
		return NULL;
	}
	
	map = cbmapopen();
	null_check(map, "dic2CBMAP() - cbmapopen()");
	items = (PyListObject*)PyDict_Items(dic);
	items_len = PyList_GET_SIZE(items);
	
	for(i = 0; i < items_len; i++) {
		key_o = PyTuple_GET_ITEM(PyList_GET_ITEM(items, i), 0);
		score_o = PyTuple_GET_ITEM(PyList_GET_ITEM(items, i), 1);

		if (!(PyString_Check(key_o) && PyString_Check(score_o))) {
		  PyErr_SetString(PyExc_TypeError, "dic2CBMAP() - str is expected");
		  return NULL;
		}
		key = PyString_AS_STRING(key_o);
		score = PyString_AS_STRING(score_o);
		//key = strdup(PyString_AS_STRING(key_o));
		//score = strdup(PyString_AS_STRING(score_o));
		null_check(key, "dic2CBMAP() - strdup()");
		null_check(score, "dic2CBMAP() - strdup()");
		
		cbmapput(map, key, -1, score, -1, 1);
		refcount(key_o, "key_o");
	}
	debug("before decref");
	Py_DECREF(items);
	debug("after decref");
	return map;
}

/* CBMAP -> python dict object */
static PyObject*
CBMAP2dic(CBMAP *map)
{
	const char *key, *v;
	int ksp, vsp;
	PyObject *dic;

	dic = PyDict_New();
	null_check(dic, "CBMAP2dic() - PyDict_New()");
	refcount(dic, "dic");
    if (map == NULL) {
      return dic;
    }

    assert(map != NULL);
	cbmapiterinit(map);
	debug("c 0");
	while ((key = cbmapiternext(map, &ksp)) != NULL) {
		v = cbmapget(map, key, -1, &vsp);
		null_check(v, "CBMAP2dic() - cbmapget()");
		PyDict_SetItemString(dic, key, PyString_FromString(v));
	}
	return dic;
}

/* python list object -> CBLIST */
static CBLIST*
list2CBLIST(PyObject *list)
{
	CBLIST *cblist;
	int size, idx;
	PyObject *item;
	
	if (!PyList_Check(list)) {
		PyErr_SetString(PyExc_TypeError, "list2CBLIST() - list is expected");
		return NULL;
	}
		
	cblist = cblistopen();
	null_check(cblist, "cblistopen()");

	size = PyList_GET_SIZE(list);
	for (idx = 0; idx < size; idx++) {
		item = PyList_GET_ITEM(list, idx);
		cblistpush(cblist, PyString_AS_STRING(item), -1);
	}
	return cblist;
}

static PyObject*
CBLIST2list(CBLIST *cblist)
{
	PyObject *list;
	int size, idx;
	const char *item;

    if (cblist == NULL) {
      return PyList_New(0);
    }
	size = cblistnum(cblist);
	list = PyList_New(size);
	null_check(list, "CBLIST2list - PyList_New()");

	for (idx = 0; idx < size; idx++) {
		item = cblistval(cblist, idx, NULL);
		PyList_SetItem(list, idx, PyString_FromString(item));
	}
	return list;
}


/* =============== ESTDOC ==================*/

static PyObject*
PyESTDOC_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyESTDOC *pdoc = NULL;
    
    pdoc = (PyESTDOC*)type->tp_alloc(type, 0);
    if (pdoc == NULL) {
        return NULL;
    }
    debug("PyESTDOC_new ");
    return (PyObject*)pdoc;
}

static int
PyESTDOC_init(PyObject* self, PyObject *args, PyObject *kwds)
{
    PyESTDOC* pdoc = (PyESTDOC*)self;
    ESTDOC *doc;
    const char* draft = NULL;
    static char* keywords[] = {"draft", 0};

    assert(args != NULL);
    assert(pdoc != NULL);
    if(!PyArg_ParseTuple(args, "|s", &draft)) {
        return -1;
    }

    if (draft == NULL) {
        doc = est_doc_new();
        debug("PyESTDOC_init() : est_doc_new()");
    } else {
        doc = est_doc_new_from_draft(draft);
        debug("PyESTDOC_init() : est_doc_new_from_draft()");
    }
        
    if (doc == NULL) {
        return -1;
    }
    pdoc->doc = doc;
    debug("PyESTDOC_init : ESTDOC allocate");
	return 0;
}

static void
PyESTDOC_dealloc(PyESTDOC *self)
{
    debug("PyESTDOC_dealloc");
    if (self->doc != NULL) {
        est_doc_delete(self->doc);
        self->doc = NULL;
    }
	PyObject_Del(self);
}
       
/* ==== Document methods ==== */
static PyObject*
_est_doc_add_attr(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
	const char *name, *value;

	if (!PyArg_ParseTuple(args, "sz", &name, &value))
		return NULL;
	null_check(pdoc->doc, "this is deleted document");

	est_doc_add_attr(pdoc->doc, name, value);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject*
_est_doc_add_text(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
	const char *text;

	if (!PyArg_ParseTuple(args, "s", &text))
		return NULL;
	null_check(pdoc->doc, "this is deleted document");

	est_doc_add_text(pdoc->doc, text);
	Py_INCREF(Py_None);
	return Py_None;	   
}


static PyObject*
_est_doc_add_hidden_text(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
	const char *text;

	if (!PyArg_ParseTuple(args, "s", &text))
		return NULL;
	null_check(pdoc->doc, "this is deleted document");

	est_doc_add_hidden_text(pdoc->doc, text);
	Py_INCREF(Py_None);
	return Py_None;	   
}

static PyObject*
_est_doc_set_keywords(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
	PyObject *keyword;
	CBMAP *map;
	
	if (!PyArg_ParseTuple(args, "O!", &PyDict_Type, &keyword))
		return NULL;
	null_check(pdoc->doc, "this is deleted document");

	map = dic2CBMAP(keyword);
	null_check(map, NULL);
	debug("k 0");
	est_doc_set_keywords(pdoc->doc, map);
	debug("k 1");
	cbmapclose(map);
	debug("k 2");
	Py_INCREF(Py_None);
	debug("k 3");
	return Py_None;	   
}

static PyObject*
_est_doc_set_score(PyObject *self, PyObject *args)
{
#if (_EST_LIBVER > 814)	   
	PyESTDOC *pdoc = (PyESTDOC*)self;
	ESTDOC *doc;
	int score;
	
	if (!PyArg_ParseTuple(args, "i", &score))
		return NULL;
	null_check(pdoc->doc, "this is deleted document");

	est_doc_set_score(pdoc->doc, score);
	
	Py_INCREF(Py_None);
	return Py_None;
#else	 
	PyErr_SetString(PyExc_NotImplementedError, "_est_doc_set_score");
	return NULL;
#endif	  
}


static PyObject*
_est_doc_id(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
	int id;

	null_check(pdoc->doc, "this is deleted document");
    debug("doc_id - 2");
    
	id = est_doc_id(pdoc->doc);
    debug("doc_id - 3");
	return PyInt_FromLong(id);
}

static PyObject*
_est_doc_attr_names(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
	CBLIST *cbl;
	PyObject *list;
	
	null_check(pdoc->doc, "this is deleted document");

	cbl = est_doc_attr_names(pdoc->doc);
	list = CBLIST2list(cbl);
	cblistclose(cbl);
	return list;
}

static PyObject*
_est_doc_score(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
	long score;
	PyObject *rv;
	
	null_check(pdoc->doc, "this is deleted document");

	score = est_doc_score(pdoc->doc);
	if (score) {
		rv = PyInt_FromLong(score);
	} else {
		rv = Py_None;
		Py_INCREF(rv);
	}
	return rv;
}

static PyObject*
_est_doc_attr(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
	const char *name, *attr;
	PyObject *rv;
	
	if (!PyArg_ParseTuple(args, "s", &name))
		return NULL;
	null_check(pdoc->doc, "this is deleted document");

	attr = est_doc_attr(pdoc->doc, name);
	if (attr) {
		rv = PyString_FromString(attr);
	} else {
		rv = Py_None;
		Py_INCREF(rv);
	}
	return rv;
}

static PyObject*
_est_doc_texts(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
	CBLIST *cbl;
	PyObject *rv;
	
	null_check(pdoc->doc, "this is deleted document");
    
    // donot cblistclose(), because a life span of cbl syncs pdoc->doc.
	cbl = (CBLIST*)est_doc_texts(pdoc->doc);  
	rv = CBLIST2list(cbl);

	return rv;
}

static PyObject*
_est_doc_cat_texts(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
    PyObject *rv;
	char *ret = NULL;
	
	null_check(pdoc->doc, "this is deleted document");
    debug("null_check 0");
	ret = est_doc_cat_texts(pdoc->doc);
    debug("est_doc_cat_texts 1");
    debug(ret);
    null_check(ret, "cat_texts return NULL");
	rv = PyString_FromString(ret);
    debug("PyString_FromString 2");
    free(ret);
    return rv;
}

static PyObject*
_est_doc_keywords(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
	CBMAP *map;
	PyObject *rv;
	
	null_check(pdoc->doc, "this is deleted document");
	debug("est_doc_keywods 0");
	map = est_doc_keywords(pdoc->doc);
	debug("est_doc_keywods 1");
	rv = CBMAP2dic(map);
	debug("est_doc_keywods 2");
	//cbmapclose(map);
	debug("est_doc_keywods 3");
	return rv;
}

static PyObject*
_est_doc_dump_draft(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
	char *draft;
	PyObject *rv;
	
	null_check(pdoc->doc, "this is deleted document");

	draft = est_doc_dump_draft(pdoc->doc);
	rv = PyString_FromString(draft);
	free(draft);
	return rv;
}

static PyObject*
_est_doc_make_snippet(PyObject *self, PyObject *args)
{
	PyESTDOC *pdoc = (PyESTDOC*)self;
	PyObject *words, *rv;
	int ww, hw, aw;
	CBLIST *cbl;
	char *snippet;
	
	if (!PyArg_ParseTuple(args, "O!iii", &PyList_Type, &words, &ww, &hw, &aw))
		return NULL;
	null_check(pdoc->doc, "this is deleted document");

	cbl = list2CBLIST(words);
	null_check(cbl, NULL);
	snippet = est_doc_make_snippet(pdoc->doc, cbl, ww, hw, aw);
	rv = PyString_FromString(snippet);
	free(snippet);
	return rv;
}

static PyMethodDef PyESTDOC_methods[] = {
    {"add_attr", _est_doc_add_attr, METH_VARARGS, NULL},
    {"add_text", _est_doc_add_text, METH_VARARGS, NULL},
    {"add_hidden_text", _est_doc_add_hidden_text, METH_VARARGS, NULL},
    {"set_keywords", _est_doc_set_keywords, METH_VARARGS, NULL},
    {"set_score", _est_doc_set_score, METH_VARARGS, NULL},
    {"id", _est_doc_id, METH_NOARGS, NULL},
    {"attr_names", _est_doc_attr_names, METH_NOARGS, NULL},
    {"attr", _est_doc_attr, METH_VARARGS, NULL},
    {"score", _est_doc_score, METH_NOARGS, NULL},
    {"texts", _est_doc_texts, METH_NOARGS, NULL},
    {"cat_texts", _est_doc_cat_texts, METH_NOARGS, NULL},
    {"keywords", _est_doc_keywords, METH_NOARGS, NULL},
    {"dump_draft", _est_doc_dump_draft, METH_NOARGS, NULL},
    {"make_snippet", _est_doc_make_snippet, METH_VARARGS, NULL},
    {NULL, NULL}
};

static PyTypeObject PyESTDOC_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyObject_HEAD_INIT(NULL)
	0,                                  /*ob_size*/
	"_estraiernative.PyESTDOC",		/*tp_name*/
	sizeof(PyESTDOC),                     /*tp_basicsize*/
	0,                            /*tp_itemsize*/
	(destructor)PyESTDOC_dealloc, /*tp_dealloc*/
	0,                                  /*tp_print*/
	0, /*tp_getattr*/
	0, /*tp_setattr*/
	0,			/*tp_compare*/
	0,			/*tp_repr*/
	0,			/*tp_as_number*/
	0,			/*tp_as_sequence*/
	0,			/*tp_as_mapping*/
	0,			/*tp_hash*/
    0,                      /*tp_call*/
    0,                      /*tp_str*/
    0,                      /*tp_getattro*/
    0,                      /*tp_setattro*/
    0,                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,     /*tp_flags*/
    0,                      /*tp_doc*/
    0,            /* tp_traverse */
    0,                    /* tp_clear */
    0,                       /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                              /* tp_iter */
    0,                                      /* tp_iternext */
    PyESTDOC_methods,                           /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    PyESTDOC_init,                    /* tp_init */
    0,                    /* tp_alloc */
    PyESTDOC_new,                      /* tp_new */
    0,                        /* tp_free */
};


/* =============== ESTMTDB ==================*/

static PyObject *
PyESTDB_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyESTDB *pdb = NULL;
    pdb = (PyESTDB*)type->tp_alloc(type, 0);

	if (pdb != NULL) {
        pdb->db = NULL;
        pdb->ecode = ESTENOERR;
    }

	return (PyObject*)pdb;
}

static void
PyESTDB_dealloc(PyESTDB *self)
{
    debug("PyESTDB_dealloc bgn");
    assert(self != NULL);
    assert(PyESTDBObject_Check(self));
    if (self->db != NULL) {
        int ret;
        debug("est_mtdb_close() pre");
		ret = est_mtdb_close(self->db, &(self->ecode));
        if (ret) {
            debug("est_mtdb_close() post");
            self->db = NULL;
        } else {
            debug("est_mtdb_close() is failed");
        }
	}
	PyObject_Del(self);
    debug("PyESTDB_dealloc fin.");
}


/* ==== Database methods ==== */
static PyObject*
_est_err_msg(PyObject *self, PyObject *args)
{
	int ecode;
	char errmsg[BUFSIZ];
	PyObject *rv;
	
	if (!PyArg_ParseTuple(args, "i:err_msg", &ecode))
		return NULL;

	strcpy(errmsg, est_err_msg(ecode)); // len(est_err_msg()) < BUFSIZ
	rv = PyString_FromString(errmsg);

	if (rv == NULL) {
		Py_INCREF(Py_None);
		return Py_None;
	} else {
		return rv;
	}
}

static PyObject*
_est_db_open(PyObject *self, PyObject *args)
{
	char *name;
	int omode, ecp;
	ESTMTDB *db;
	PyESTDB *pdb = (PyESTDB*)self;

    if (pdb->db != NULL && !est_mtdb_close(pdb->db, &(pdb->ecode))) {
        pdb->db = NULL;
        Py_INCREF(Py_False);
        return Py_False;
    }
	
	if (!PyArg_ParseTuple(args, "si", &name, &omode))
		return NULL;

	db = est_mtdb_open(name, omode, &(pdb->ecode));
	if (db != NULL) {
		pdb->db = db;
        Py_INCREF(Py_True);
		return Py_True;
	} else {
        Py_INCREF(Py_False);
		return Py_False;
	}
}

static PyObject*
_est_db_close(PyObject *self, PyObject *args)
{
	PyESTDB *pdb = (PyESTDB*)self;
	int ecp, ret;
	PyObject *rv;

    null_check(pdb->db, "db is closed");
    ret = est_mtdb_close(pdb->db, &(pdb->ecode));
    pdb->db = NULL;
	if (ret) {
		rv = Py_True;
	} else {
        //pdb->ecode = est_mtdb_error(pdb->db);
		rv = Py_False;
	}
	Py_INCREF(rv);
	return rv;
}

static PyObject*
_est_db_error(PyObject *self, PyObject *args)
{
	PyObject *po;
    PyESTDB *pdb = (PyESTDB*)self;

    //null_check(pdb->db, "db is closed");
    //pdb->ecode = est_mtdb_error(pdb->db);
    return PyInt_FromLong(pdb->ecode);
}

static PyObject*
_est_db_fatal(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    int ret;
    PyObject *rv;

    null_check(pdb->db, "db is closed");

    ret = est_mtdb_error(pdb->db);
    if (ret) {
        rv = Py_True;
    } else {
        rv = Py_False;
    }
    Py_INCREF(rv);
    return rv;
}

static PyObject*
_est_db_add_attr_index(PyObject *self, PyObject *args)
{
#if (_EST_LIBVER > 805)
    PyESTDB *pdb = (PyESTDB*)self;
    char *name;
    int type, ret;
    PyObject *rv;

    if (!PyArg_ParseTuple(args, "si", &name, &type))
        return NULL;
    null_check(pdb->db, "db is closed");
    
    ret = est_mtdb_add_attr_index(pdb->db, name, type);
    if (ret) {
        rv = Py_True;
    } else {
        rv = Py_False;
        pdb->ecode = est_mtdb_error(pdb->db);
    }
    Py_INCREF(rv);
    return rv;
#else
    PyErr_SetString(PyExc_NotImplementedError, "add_attr_index");
    return NULL;
#endif
}

static PyObject*
_est_db_flush(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    int max, ret;
    PyObject *rv;

    if (!PyArg_ParseTuple(args, "i", &max))
        return NULL;
    null_check(pdb->db, "db is closed");
    
    ret = est_mtdb_flush(pdb->db, max);
    if (ret) {
        rv = Py_True;
    } else {
        rv = Py_False;
        pdb->ecode = est_mtdb_error(pdb->db);
    }
    Py_INCREF(rv);
    return rv;
}

static PyObject*
_est_db_sync(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    int ret;
    PyObject *rv;

    null_check(pdb->db, "db is closed");
    
    ret = est_mtdb_sync(pdb->db);
    if (ret) {
        rv = Py_True;
    } else {
        rv = Py_False;
        pdb->ecode = est_mtdb_error(pdb->db);
    }
    Py_INCREF(rv);
    return rv;
}

static PyObject*
_est_db_optimize(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    int opts, ret;
    PyObject *rv;

    if (!PyArg_ParseTuple(args, "i", &opts))
        return NULL;
    null_check(pdb->db, "db is closed");
    
    ret = est_mtdb_optimize(pdb->db, opts);
    if (ret) {
        rv = Py_True;
    } else {
        rv = Py_False;
        pdb->ecode = est_mtdb_error(pdb->db);
    }
    Py_INCREF(rv);
    return rv;
}

static PyObject*
_est_db_merge(PyObject *self, PyObject *args)
{
#if (_EST_LIBVER > 814)    
    PyESTDB *pdb = (PyESTDB*)self;
    char *name;
    int opts, ret;
    PyObject *rv;

    if (!PyArg_ParseTuple(args, "si", &name, &opts))
        return NULL;
    null_check(pdb->db, "db is closed");
    
    ret = est_mtdb_merge(pdb->db, name, opts);
    if (ret) {
        rv = Py_True;
    } else {
        rv = Py_False;
        pdb->ecode = est_mtdb_error(pdb->db);
    }
    Py_INCREF(rv);
    return rv;
#else
    PyErr_SetString(PyExc_NotImplementedError, "_est_db_merge");
    return NULL;
#endif
}

static PyObject*
_est_db_put_doc(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    PyESTDOC *pdoc;
    int opts, ret;
    PyObject *rv;

    if (!PyArg_ParseTuple(args, "O!i", &PyESTDOC_Type, &pdoc, &opts))
        return NULL;
    null_check(pdb->db, "db is closed");
    null_check(pdoc->doc, "this is deleted document");
    
    ret = est_mtdb_put_doc(pdb->db, pdoc->doc, opts);
    if (ret) {
        rv = Py_True;
    } else {
        rv = Py_False;
        pdb->ecode = est_mtdb_error(pdb->db);
    }
    Py_INCREF(rv);
    return rv;    
}

static PyObject*
_est_db_out_doc(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    int id, opts, ret;
    PyObject *rv;

    if (!PyArg_ParseTuple(args, "ii", &id, &opts))
        return NULL;
    null_check(pdb->db, "db is closed");
    
    ret = est_mtdb_out_doc(pdb->db, id, opts);
    if (ret) {
        rv = Py_True;
    } else {
        rv = Py_False;
        pdb->ecode = est_mtdb_error(pdb->db);
    }
    Py_INCREF(rv);
    return rv;    
}

static PyObject*
_est_db_edit_doc(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    PyESTDOC *pdoc;
    int ret;
    PyObject *rv;

    if (!PyArg_ParseTuple(args, "O!", &PyESTDOC_Type, &pdoc))
        return NULL;
    null_check(pdb->db, "db is closed");
    null_check(pdoc->doc, "this is deleted document");
    
    ret = est_mtdb_edit_doc(pdb->db, pdoc->doc);
    if (ret) {
        rv = Py_True;
    } else {
        rv = Py_False;
        pdb->ecode = est_mtdb_error(pdb->db);
    }
    Py_INCREF(rv);
    return rv;        
}

static PyObject*
_est_db_get_doc(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    int id, opts;
    PyESTDOC *pdoc;
    ESTDOC *doc;
    
    if (!PyArg_ParseTuple(args, "ii", &id, &opts))
        return NULL;

    null_check(pdb->db, "db is closed");

    doc = est_mtdb_get_doc(pdb->db, id, opts);
    if (doc) {
        pdoc = PyObject_New(PyESTDOC, &PyESTDOC_Type);
        pdoc->doc = doc;
        return (PyObject*)pdoc;
    } else {
        Py_INCREF(Py_None);
        pdb->ecode = est_mtdb_error(pdb->db);
        return Py_None;
    }
}

static PyObject*
_est_db_get_doc_attr(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    int id;
    char *name, *attr;
    PyObject *rv;

    if (!PyArg_ParseTuple(args, "is", &id, &name))
        return NULL;

    null_check(pdb->db, "db is closed");

    attr = est_mtdb_get_doc_attr(pdb->db, id, name);
    if (attr) {
        rv = PyString_FromString(attr);
        free(attr);
        return rv;
    } else {
        Py_INCREF(Py_None);
        pdb->ecode = est_mtdb_error(pdb->db);
        return Py_None;
    }
}

static PyObject*
_est_db_uri_to_id(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    char *uri;
    int id;

    if(!PyArg_ParseTuple(args, "s", &uri))
        return NULL;

    null_check(pdb->db, "db is closed");

    id = est_mtdb_uri_to_id(pdb->db, uri);
    if (id == -1) {
        pdb->ecode = est_mtdb_error(pdb->db);
    }
    return PyInt_FromLong(id);
}

static PyObject*
_est_db_name(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    const char *name;

    null_check(pdb->db, "db is closed");

    name = est_mtdb_name(pdb->db);
    return PyString_FromString(name);
}

static PyObject*
_est_db_doc_num(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    int docnum;

    null_check(pdb->db, "db is closed");

    docnum = est_mtdb_doc_num(pdb->db);
    return PyInt_FromLong(docnum);
}


static PyObject*
_est_db_word_num(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    int wordnum;

    null_check(pdb->db, "db is closed");

    wordnum = est_mtdb_word_num(pdb->db);
    return PyInt_FromLong(wordnum);
}


static PyObject*
_est_db_size(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    double dbsize;

    null_check(pdb->db, "db is closed");

    dbsize = est_mtdb_size(pdb->db);
    return PyFloat_FromDouble(dbsize);
}

static PyObject*
_est_db_search(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    PyESTCOND *pcond;
    PyESTRES *res;
    int nump, *ret, i;
    PyObject *hints, *list;
    CBMAP *map;
    
    if (!PyArg_ParseTuple(args, "O!", &PyESTCOND_Type, &pcond))
        return NULL;
    null_check(pdb->db, "db is closed");
    null_check(pcond->cond, "this is deleted condition");
    debug("null_check");

    res = estres_factory();
    null_check(res, "_est_db_search() - estres_factory()");
    map = cbmapopen();
    debug("_est_db_search() - cbmapopen()");

    ret = est_mtdb_search(pdb->db, pcond->cond, &nump, map);
    debug("_est_db_search() - est_mtdb_search()");

    res->ids = ret;
    res->num = nump;
    res->hints = map;    
    debug("_est_db_search() - ids, num, hints");
    refcount(res, "db_search");
    return (PyObject*)res;
}

static PyObject*
_est_db_search_meta(PyObject *self, PyObject *args)
{
    PyErr_SetString(PyExc_NotImplementedError, "_est_db_search_meta");
    return NULL;
}

static PyObject*
_est_db_scan_doc(PyObject *self, PyObject *args)
{
    PyESTDB *pdb = (PyESTDB*)self;
    PyESTDOC *pdoc;
    PyESTCOND *pcond;
    int ret;
    PyObject *rv;
    
    if (!PyArg_ParseTuple(args, "O!O!",
                          &PyESTDOC_Type, &pdoc,
                          &PyESTCOND_Type, &pcond))
        return NULL;
    null_check(pdb->db, "db is closed");
    null_check(pdoc->doc, "this is deleted document");
    null_check(pcond->cond, "this is deleted condition");

    ret = est_mtdb_scan_doc(pdb->db, pdoc->doc, pcond->cond);
    if (ret) {
        rv = Py_True;
    } else {
        rv = Py_False;
    }
    Py_INCREF(rv);
    return rv;            
}

static PyObject*
_est_db_set_cache_size(PyObject *self, PyObject *args, PyObject* kwargs)
{
    PyESTDB *pdb = (PyESTDB*)self;
    size_t sz = -1;
    int anum = -1, tnum = -1, rnum = -1;
    static char* keywords[] = {"size", "anum", "tnum", "rnum", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|iiii", keywords,
                                     &sz, &anum, &tnum, &rnum))
        return NULL;

    null_check(pdb->db, "db is closed");

    if ( sz != -1 || anum != -1 || tnum != -1 || rnum != -1) {
        est_mtdb_set_cache_size(pdb->db, sz, anum, tnum, rnum);
    }
    Py_INCREF(Py_None);
    return Py_None;
}
#ifdef DEBUG
static PyObject*
_dic2dic(PyObject *self, PyObject *args)
{
    PyObject *dic, *rv;
    CBMAP *map;
    debug("d 0");    
    if (!PyArg_ParseTuple(args, "O!", &PyDict_Type, &dic))
        return NULL;
    debug("d 1");
    map = dic2CBMAP(dic);
    debug("d 2");
    rv = CBMAP2dic(map);
    debug("d 3");
    return rv;
}
#endif

static PyMethodDef PyESTDB_methods[] = {
    /* Database functions */
    {"err_msg", _est_err_msg, METH_VARARGS, NULL},
    {"open", _est_db_open, METH_VARARGS, NULL},
    {"close", _est_db_close, METH_NOARGS, NULL},
    {"error", _est_db_error, METH_NOARGS, NULL},
    {"fatal", _est_db_fatal, METH_NOARGS, NULL},
    {"add_attr_index", _est_db_add_attr_index, METH_VARARGS, NULL},
    {"flush", _est_db_flush, METH_VARARGS, NULL},
    {"sync", _est_db_sync, METH_NOARGS, NULL},
    {"optimize", _est_db_optimize, METH_VARARGS, NULL},
    {"merge", _est_db_merge, METH_VARARGS, NULL},
    {"put_doc", _est_db_put_doc, METH_VARARGS, NULL},
    {"out_doc", _est_db_out_doc, METH_VARARGS, NULL},
    {"edit_doc", _est_db_edit_doc, METH_VARARGS, NULL},
    {"get_doc", _est_db_get_doc, METH_VARARGS, NULL},
    {"get_doc_attr", _est_db_get_doc_attr, METH_VARARGS, NULL},
    {"uri_to_id", _est_db_uri_to_id, METH_VARARGS, NULL},
    {"name", _est_db_name, METH_NOARGS, NULL},
    {"doc_num", _est_db_doc_num, METH_NOARGS, NULL},
    {"word_num", _est_db_word_num, METH_NOARGS, NULL},
    {"size", _est_db_size, METH_NOARGS, NULL},
    {"search", _est_db_search, METH_VARARGS, NULL},
    {"search_meta", _est_db_search_meta, METH_VARARGS, NULL},
    {"scan_doc", _est_db_scan_doc, METH_VARARGS, NULL},
    {"cache_size", (PyCFunction)_est_db_set_cache_size,
     METH_VARARGS | METH_KEYWORDS, NULL},
#ifdef DEBUG
    {"dic2dic", _dic2dic, METH_VARARGS, NULL},
#endif
    {NULL, NULL}
};

static PyTypeObject PyESTDB_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyObject_HEAD_INIT(NULL)
	0,			/*ob_size*/
	"_estraiernative.PyESTDB",		/*tp_name*/
	sizeof(PyESTDB),	/*tp_basicsize*/
	0,			/*tp_itemsize*/
	(destructor)PyESTDB_dealloc, /*tp_dealloc*/
	0,			/*tp_print*/
	0, /*tp_getattr*/
	0, /*tp_setattr*/
	0,			/*tp_compare*/
	0,			/*tp_repr*/
	0,			/*tp_as_number*/
	0,			/*tp_as_sequence*/
	0,			/*tp_as_mapping*/
	0,			/*tp_hash*/
	0,						/*tp_call*/
	0,						/*tp_str*/
	0,						/*tp_getattro*/
	0,						/*tp_setattro*/
	0,						/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,		/*tp_flags*/
	0,						/*tp_doc*/
    0,            /* tp_traverse */
    0,                    /* tp_clear */
    0,                       /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                              /* tp_iter */
    0,                                      /* tp_iternext */
    PyESTDB_methods,                           /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    0,                    /* tp_init */
    0,                    /* tp_alloc */
    PyESTDB_new,                      /* tp_new */
    0,                        /* tp_free */
};

/* --------------------------------------------------------------------- */


/* =============== ESTCOND ==================*/

static PyObject*
PyESTCOND_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyESTCOND *pcond;
    
	pcond = (PyESTCOND*)type->tp_alloc(type, 0);
    if (pcond != NULL) {
        pcond->cond = NULL;
    }
	return (PyObject*)pcond;
}

static int
PyESTCOND_init(PyObject* self, PyObject *args, PyObject *kwds) {
    PyESTCOND *pcond = (PyESTCOND*)self;
    ESTCOND *cond;

    cond = est_cond_new();
    if (cond == NULL) {
        return -1;
    }
    
    pcond->cond = cond;
    debug("PyESTCOND_init");
    return 0;
    
}

static void
PyESTCOND_dealloc(PyESTCOND *self)
{
    debug("PyESTCOND_dealloc");
    if (self->cond != NULL) {
        est_cond_delete(self->cond);
        self->cond = NULL;
    }
	PyObject_Del(self);
}

/* ==== Condition functions ==== */

static PyObject*
_est_cond_set_phrase(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	const char *phrase;
	
	if (!PyArg_ParseTuple(args, "s", &phrase))
		return NULL;

	if (pcond->cond == NULL) {
		PyErr_SetString(EST_Error, "this is deleted condition");
		return NULL;
	}

	est_cond_set_phrase(pcond->cond, phrase);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject*
_est_cond_add_attr(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	const char *expr;
	
	if (!PyArg_ParseTuple(args, "s", &expr))
		return NULL;

	null_check(pcond->cond, "this is deleted condition");

	est_cond_add_attr(pcond->cond, expr);
	Py_INCREF(Py_None);
	return Py_None;	   
}

static PyObject*
_est_cond_set_order(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	const char *expr;
	
	if (!PyArg_ParseTuple(args, "s", &expr))
		return NULL;

	null_check(pcond->cond, "this is deleted condition");

	est_cond_set_order(pcond->cond, expr);
	Py_INCREF(Py_None);
	return Py_None;	   
}

static PyObject*
_est_cond_set_max(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	int i;
	
	if (!PyArg_ParseTuple(args, "i", &i))
		return NULL;

	null_check(pcond->cond, "this is deleted condition");

	est_cond_set_max(pcond->cond, i);
	Py_INCREF(Py_None);
	return Py_None;	   
}

static PyObject*
_est_cond_set_skip(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	int i;
	
	if (!PyArg_ParseTuple(args, "i", &i))
		return NULL;

	null_check(pcond->cond, "this is deleted condition");

	est_cond_set_skip(pcond->cond, i);
	Py_INCREF(Py_None);
	return Py_None;	   
}

static PyObject*
_est_cond_set_options(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	int i;
	
	if (!PyArg_ParseTuple(args, "i", &i))
		return NULL;

	null_check(pcond->cond, "this is deleted condition");

	est_cond_set_options(pcond->cond, i);
	Py_INCREF(Py_None);
	return Py_None;	   
}

static PyObject*
_est_cond_set_auxiliary(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	int i;
	
	if (!PyArg_ParseTuple(args, "i", &i))
		return NULL;

	null_check(pcond->cond, "this is deleted condition");

	est_cond_set_auxiliary(pcond->cond, i);
	Py_INCREF(Py_None);
	return Py_None;	   
}

static PyObject*
_est_cond_set_eclipse(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	double d;
	
	if (!PyArg_ParseTuple(args, "d", &d))
		return NULL;

	null_check(pcond->cond, "this is deleted condition");

	est_cond_set_auxiliary(pcond->cond, d);
	Py_INCREF(Py_None);
	return Py_None;	   
}

static PyObject*
_est_cond_set_distinct(PyObject *self, PyObject *args)
{
#if (_EST_LIBVER > 814)	   
	PyESTCOND *pcond = (PyESTCOND*)self;
    char *name;
	
	if (!PyArg_ParseTuple(args, "s", &name))
		return NULL;

	null_check(pcond->cond, "this is deleted condition");

	est_cond_set_distinct(pcond->cond, name);
	Py_INCREF(Py_None);
	return Py_None;
#else
	PyErr_SetString(PyExc_NotImplementedError, "_est_cond_set_distinct");
	return NULL;	
#endif	  
}

static PyObject*
_est_cond_set_mask(PyObject *self, PyObject *args)
{
#if (_EST_LIBVER > 814)	   
	PyESTCOND *pcond = (PyESTCOND*)self;
	int i;
	
	if (!PyArg_ParseTuple(args, "i", &i))
		return NULL;

	null_check(pcond->cond, "this is deleted condition");

	est_cond_set_mask(pcond->cond, i);
	Py_INCREF(Py_None);
	return Py_None;
#else
	PyErr_SetString(PyExc_NotImplementedError, "_est_cond_set_mask");
	return NULL;	
#endif	  
}

static PyObject*
_est_cond_get_phrase(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	const char *p;

	null_check(pcond->cond, "this is deleted condition");

	p = est_cond_phrase(pcond->cond);
	if (p) {
	  return PyString_FromString(p);
	} else {
	  Py_INCREF(Py_None);
	  return Py_None;
	}
}

static PyObject*
_est_cond_get_attrs(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	const CBLIST *cbl;
	PyObject *rv;

	null_check(pcond->cond, "this is deleted condition");

    // donot call cblistclose(), cbl and pcond->cond are in the same boat.
	cbl = est_cond_attrs(pcond->cond);
	if (cbl) {
	  return CBLIST2list((CBLIST*)cbl);
	} else {
	  Py_INCREF(Py_None);
	  return Py_None;
	}
}

static PyObject*
_est_cond_get_order(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	const char *o;

	null_check(pcond->cond, "this is deleted condition");

	o = est_cond_order(pcond->cond);
	if (o) {
	  return PyString_FromString(o);
	} else {
	  Py_INCREF(Py_None);
	  return Py_None;
	}
}

static PyObject*
_est_cond_get_max(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	int i;

	null_check(pcond->cond, "this is deleted condition");

	i = est_cond_max(pcond->cond);
	return PyInt_FromLong(i);
}

static PyObject*
_est_cond_get_skip(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	int i;

	null_check(pcond->cond, "this is deleted condition");

	i = est_cond_skip(pcond->cond);
	return PyInt_FromLong(i);
}

static PyObject*
_est_cond_get_options(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	int i;

	null_check(pcond->cond, "this is deleted condition");

	i = est_cond_options(pcond->cond);
	return PyInt_FromLong(i);
}


static PyObject*
_est_cond_get_auxiliary(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	int i;

	null_check(pcond->cond, "this is deleted condition");

	i = est_cond_auxiliary(pcond->cond);
	return PyInt_FromLong(i);
}


static PyObject*
_est_cond_get_distinct(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	const char *d;

	null_check(pcond->cond, "this is deleted condition");
	d = est_cond_distinct(pcond->cond);
	if (d) {
	  return PyString_FromString(d);
	} else {
	  Py_INCREF(Py_None);
	  return Py_None;
	}
}

static PyObject*
_est_cond_get_mask(PyObject *self, PyObject *args)
{
	PyESTCOND *pcond = (PyESTCOND*)self;
	int i;

	null_check(pcond->cond, "this is deleted condition");

	i = est_cond_mask(pcond->cond);
	return PyInt_FromLong(i);
}

static PyMethodDef PyESTCOND_methods[] = {
    /* Condition functions */
    {"set_phrase", _est_cond_set_phrase, METH_VARARGS, NULL},
    {"add_attr", _est_cond_add_attr, METH_VARARGS, NULL},
    {"set_order", _est_cond_set_order, METH_VARARGS, NULL},
    {"set_max", _est_cond_set_max, METH_VARARGS, NULL},
    {"set_skip", _est_cond_set_skip, METH_VARARGS, NULL},
    {"set_options", _est_cond_set_options, METH_VARARGS, NULL},
    {"set_auxiliary", _est_cond_set_auxiliary, METH_VARARGS, NULL},
    {"set_eclipse", _est_cond_set_eclipse, METH_VARARGS, NULL},
    {"set_mask", _est_cond_set_mask, METH_VARARGS, NULL},
    {"get_phrase", _est_cond_get_phrase, METH_NOARGS, NULL},
    {"get_attrs", _est_cond_get_attrs, METH_NOARGS, NULL},
    {"get_order", _est_cond_get_order, METH_NOARGS, NULL},
    {"get_max", _est_cond_get_max, METH_NOARGS, NULL},
    {"get_skip", _est_cond_get_skip, METH_NOARGS, NULL},
    {"get_options", _est_cond_get_options, METH_NOARGS, NULL},
    {"get_auxliary", _est_cond_get_auxiliary, METH_NOARGS, NULL},
    {"get_distinct", _est_cond_get_distinct, METH_NOARGS, NULL},
    {"get_mask", _est_cond_get_mask, METH_NOARGS, NULL},
    
	{NULL,		NULL}		/* sentinel */
};

static PyTypeObject PyESTCOND_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyObject_HEAD_INIT(NULL)
	0,			/*ob_size*/
	"_estraiernative.PyESTCOND",		/*tp_name*/
	sizeof(PyESTCOND),	/*tp_basicsize*/
	0,			/*tp_itemsize*/
	/* methods */
	(destructor)PyESTCOND_dealloc, /*tp_dealloc*/
	0,			/*tp_print*/
	0, /*tp_getattr*/
	0, /*tp_setattr*/
	0,			/*tp_compare*/
	0,			/*tp_repr*/
	0,			/*tp_as_number*/
	0,			/*tp_as_sequence*/
	0,			/*tp_as_mapping*/
	0,			/*tp_hash*/
    0,                      /*tp_call*/
    0,                      /*tp_str*/
    0,                      /*tp_getattro*/
    0,                      /*tp_setattro*/
    0,                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,     /*tp_flags*/
    0,                      /*tp_doc*/
    0,            /* tp_traverse */
    0,                    /* tp_clear */
    0,                       /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                              /* tp_iter */
    0,                                      /* tp_iternext */
    PyESTCOND_methods,                           /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    PyESTCOND_init,                    /* tp_init */
    0,                    /* tp_alloc */
    PyESTCOND_new,                      /* tp_new */
    0,                        /* tp_free */
};
/* --------------------------------------------------------------------- */

/* =============== ESTRES ==================*/
static PyESTRES*
estres_factory(void)
{
    PyESTRES *res;
    //res = PyESTRES_Type.tp_alloc(&PyESTRES_Type, 0);
    res = PyObject_New(PyESTRES, &PyESTRES_Type);
    if (res == NULL) {
        return NULL;
    }
    res->ids = NULL;
    res->dbidxs = NULL;
    res->num = 0;
    res->hints = NULL;
    debug("estres_factory");
    refcount(res, "estres_factory");
    return res;
}

static PyObject*
PyESTRES_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    debug("PyESTRES_new");
    return (PyObject*)estres_factory();
}

static void
PyESTRES_dealloc(PyESTRES *self)
{
    assert(self != NULL);
    if (self->ids != NULL) {
        free(self->ids);
    }
    if (self->dbidxs != NULL) {
        free(self->dbidxs);
    }
    if (self->hints != NULL) {
        cbmapclose(self->hints);
    }
    debug("PyESTERS_dealloc");
    PyObject_Del(self);
}

/* ==== Result methods ==== */
static PyObject*
_est_res_doc_num(PyObject *self, PyObject *args)
{
    PyESTRES* res = (PyESTRES*)self;
    assert(res != NULL);
    debug("doc_num");
    return PyInt_FromLong(res->num);
}

static PyObject*
_est_res_get_doc_id(PyObject *self, PyObject *args)
{
    PyESTRES* res = (PyESTRES*)self;
    int idx;
    
    if (!PyArg_ParseTuple(args, "i", &idx))
        return NULL;

    if (!res->ids || idx < 0 || idx >= res->num) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return NULL;
    }
    
    return PyInt_FromLong(res->ids[idx]);
}

static PyObject*
_est_res_get_dbidx(PyObject *self, PyObject *args)
{
    PyESTRES* res = (PyESTRES*)self;
    int idx;
    
    if (!PyArg_ParseTuple(args, "i", &idx))
        return NULL;

    if (!res->ids || idx < 0 || idx >= res->num) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return NULL;
    }
    
    return PyInt_FromLong(res->dbidxs[idx]);
}
static PyObject*
_est_res_hint_words(PyObject *self, PyObject *args)
{
    PyESTRES* res = (PyESTRES*)self;
    PyObject *rv;
    CBLIST *words;
    int i;
    const char* vbuf;
    
    if (res->hints == NULL) {
        return PyList_New(0);
    }

    words = cbmapkeys(res->hints);
    for (i=0; i < CB_LISTNUM(words); i++) {
        vbuf = CB_LISTVAL(words, i);
        if (vbuf[0] == '\0') {
            free(cblistremove(words, i, NULL));
            break;
        }
    }
    rv = CBLIST2list(words);
    cblistclose(words);
    return rv;
}

static PyObject*
_est_res_hint(PyObject *self, PyObject *args)
{
    PyESTRES* res = (PyESTRES*)self;
    char *word;
    const char* vbuf;
    
    if (!PyArg_ParseTuple(args, "s", word)) {
        return NULL;
    }
    if (res->hints != NULL) {
        return PyInt_FromLong(0);
    }
    vbuf = cbmapget(res->hints, word, -1, NULL);
    if (vbuf == NULL) {
        return PyInt_FromLong(0);
    }
    return PyInt_FromLong(atoi(vbuf));
}

static PyObject*
_est_res_get_score(PyObject *self, PyObject *args)
{
    PyESTRES* res = (PyESTRES*)self;
    int idx;

	PyErr_SetString(PyExc_NotImplementedError, "_est_cond_set_mask");
	return NULL;	
}
static PyObject*
_est_res_get_shadows(PyObject *self, PyObject *args)
{
    PyESTRES* res = (PyESTRES*)self;

	PyErr_SetString(PyExc_NotImplementedError, "_est_cond_set_mask");
	return NULL;	
}

static PyMethodDef PyESTRES_methods[] = {
    {"doc_num", _est_res_doc_num, METH_NOARGS, NULL},
    {"get_doc_id", _est_res_get_doc_id, METH_VARARGS, NULL},
    {"get_dbidx", _est_res_get_dbidx, METH_VARARGS, NULL},
    {"hint_words", _est_res_hint_words, METH_NOARGS, NULL},
    {"hint", _est_res_hint, METH_VARARGS, NULL},
    {"get_score", _est_res_get_score, METH_VARARGS, NULL},
    {"get_shadows", _est_res_doc_num, METH_VARARGS, NULL},
    {NULL, NULL}
};


static PyTypeObject PyESTRES_Type = {
	/* The ob_type field must be initialized in the module init function
	 * to be portable to Windows without using C++. */
	PyObject_HEAD_INIT(NULL)
	0,			/*ob_size*/
	"_estraiernative.PyESTRES",		/*tp_name*/
	sizeof(PyESTRES),	/*tp_basicsize*/
	0,			/*tp_itemsize*/
	(destructor)PyESTRES_dealloc, /*tp_dealloc*/
	0,			/*tp_print*/
	0, /*tp_getattr*/
	0, /*tp_setattr*/
	0,			/*tp_compare*/
	0,			/*tp_repr*/
	0,			/*tp_as_number*/
	0,			/*tp_as_sequence*/
	0,			/*tp_as_mapping*/
	0,			/*tp_hash*/
    0,                      /*tp_call*/
    0,                      /*tp_str*/
    0,                      /*tp_getattro*/
    0,                      /*tp_setattro*/
    0,                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,     /*tp_flags*/
    0,                      /*tp_doc*/
    0,            /* tp_traverse */
    0,                    /* tp_clear */
    0,                       /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                              /* tp_iter */
    0,                                      /* tp_iternext */
    PyESTRES_methods,                           /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    0,                    /* tp_init */
    0,                    /* tp_alloc */
    PyESTRES_new,                      /* tp_new */
    0,                        /* tp_free */
};


/* --------------------------------------------------------------------- */

static PyMethodDef hyperest_methods[] = {
    {NULL, NULL}
};

PyDoc_STRVAR(module_doc,
"This is a template module just for instruction.");

/* Initialization function for the module (*must* be called initxx) */

PyMODINIT_FUNC
init_estraiernative(void)
{
	PyObject *m;
    PyObject *d;

    if (PyType_Ready(&PyESTDOC_Type) < 0)
		return;

	if (PyType_Ready(&PyESTCOND_Type) < 0)
		return;

    if (PyType_Ready(&PyESTDB_Type) < 0)
        return;

    if (PyType_Ready(&PyESTRES_Type) < 0)
		return;
    
	m = Py_InitModule3("_estraiernative", hyperest_methods, module_doc);
    
    // Document
    Py_INCREF(&PyESTDOC_Type);
    PyModule_AddObject(m, "Document", (PyObject*)&PyESTDOC_Type);

    // Condition
    d = PyESTCOND_Type.tp_dict;
    define_const(d, "SURE", ESTCONDSURE);
    define_const(d, "USUAL", ESTCONDUSUAL);
    define_const(d, "FAST", ESTCONDFAST);
    define_const(d, "AGITO", ESTCONDAGITO);
    define_const(d, "NOIDF", ESTCONDNOIDF);
    define_const(d, "SIMPLE", ESTCONDSIMPLE);
    define_const(d, "ROUGH", ESTCONDROUGH);
    define_const(d, "UNION", ESTCONDUNION);
    define_const(d, "ISECT", ESTCONDISECT);
    Py_INCREF(&PyESTCOND_Type);
    PyModule_AddObject(m, "Condition", (PyObject*)&PyESTCOND_Type);

    // Database
    d = PyESTDB_Type.tp_dict;
    define_const_fmt(d, "VERSION", est_version, "s");
    define_const(d, "ERRNOERR", ESTENOERR);
    define_const(d, "ERRINVAL", ESTEINVAL);
    define_const(d, "ERRACCES", ESTEACCES);
    define_const(d, "ERRLOCK", ESTELOCK);
    define_const(d, "ERRDB", ESTEDB);
    define_const(d, "ERRIO", ESTEIO);
    define_const(d, "ERRNOITEM", ESTENOITEM);
    define_const(d, "ERRMISC", ESTEMISC);
    define_const(d, "DBREADER", ESTDBREADER);
    define_const(d, "DBWRITER", ESTDBWRITER);
    define_const(d, "DBCREAT", ESTDBCREAT);
    define_const(d, "DBTRUNC", ESTDBTRUNC);
    define_const(d, "DBNOLCK", ESTDBNOLCK);
    define_const(d, "DBLCKNB", ESTDBLCKNB);
    define_const(d, "DBPERFNG", ESTDBPERFNG);
    define_const(d, "DBCHRCAT", ESTDBCHRCAT);
    define_const(d, "DBSMALL", ESTDBSMALL);
    define_const(d, "DBLARGE", ESTDBLARGE);
    define_const(d, "DBHUGE", ESTDBHUGE);
    define_const(d, "DBHUGE2", ESTDBHUGE2);
    define_const(d, "DBHUGE3", ESTDBHUGE3);
    define_const(d, "DBSCVOID", ESTDBSCVOID);
    define_const(d, "DBSCINT", ESTDBSCINT);
    define_const(d, "DBSCASIS", ESTDBSCASIS);
    define_const(d, "IDXATTRSEQ", ESTIDXATTRSEQ);
    define_const(d, "IDXATTRSTR", ESTIDXATTRSTR);
    define_const(d, "IDXATTRNUM", ESTIDXATTRNUM);
    define_const(d, "OPTNOPURGE", ESTOPTNOPURGE);
    define_const(d, "OPTNODBOPT", ESTOPTNODBOPT);
    define_const(d, "MGCLEAN", ESTMGCLEAN);
    define_const(d, "PDCLEAN", ESTPDCLEAN);
    define_const(d, "PDWEIGHT", ESTPDWEIGHT);
    define_const(d, "ODCLEAN", ESTODCLEAN);
    define_const(d, "GDNOATTR", ESTGDNOATTR);
    define_const(d, "GDNOTEXT", ESTGDNOTEXT);

    Py_INCREF(&PyESTDB_Type);
    PyModule_AddObject(m, "Database", (PyObject*)&PyESTDB_Type);

    // Result
    Py_INCREF(&PyESTRES_Type);
    PyModule_AddObject(m, "Result", (PyObject*)&PyESTRES_Type);

	/* Add some symbolic constants to the module */
    EST_Error = PyErr_NewException("_estraiernative.Error", NULL, NULL);
    if (EST_Error == NULL)
        return;
	PyModule_AddObject(m, "EstError", EST_Error);

    debug("init_estraeirnative fin.");
}
     
     
