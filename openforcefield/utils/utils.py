#!/usr/bin/env python

"""
Utility subroutines

"""
#=============================================================================================
# GLOBAL IMPORTS
#=============================================================================================

import contextlib

#=============================================================================================
# UTILITY SUBROUTINES
#=============================================================================================

def inherit_docstrings(cls):
    """Inherit docstrings from parent class"""
    from inspect import getmembers, isfunction
    for name, func in getmembers(cls, isfunction):
        if func.__doc__: continue
        for parent in cls.__mro__[1:]:
            if hasattr(parent, name):
                func.__doc__ = getattr(parent, name).__doc__
    return cls

def all_subclasses(cls):
    """Recursively retrieve all subclasses of the specified class"""
    return cls.__subclasses__() + [ g for s in cls.__subclasses__() for g in all_subclasses(s) ]

@contextlib.contextmanager
def temporary_cd(dir_path):
    """Context to temporary change the working directory.

    Parameters
    ----------
    dir_path : str
        The directory path to enter within the context

    Examples
    --------
    >>> dir_path = '/tmp'
    >>> with temporary_cd(dir_path):
    ...     # do something in dir_path

    """
    import os
    prev_dir = os.getcwd()
    os.chdir(os.path.abspath(dir_path))
    try:
        yield
    finally:
        os.chdir(prev_dir)

@contextlib.contextmanager
def temporary_directory():
    """Context for safe creation of temporary directories."""

    import tempfile
    tmp_dir = tempfile.mkdtemp()
    try:
        yield tmp_dir
    finally:
        import shutil
        shutil.rmtree(tmp_dir)

def get_data_filename(relative_path):
    """Get the full path to one of the reference files in testsystems.
    In the source distribution, these files are in ``openforcefield/data/``,
    but on installation, they're moved to somewhere in the user's python
    site-packages directory.
    Parameters
    ----------
    name : str
        Name of the file to load (with respect to the repex folder).
    """

    from pkg_resources import resource_filename
    import os
    fn = resource_filename('openforcefield', os.path.join('data', relative_path))

    if not os.path.exists(fn):
        raise ValueError("Sorry! %s does not exist. If you just added it, you'll have to re-install" % fn)

    return fn

def serialize_numpy(np_array):
    """
    Serializes a numpy array into a JSON-compatible string. Leverages the numpy.save function,
    thereby preserving the shape of the input array

    from https://stackoverflow.com/questions/30698004/how-can-i-serialize-a-numpy-array-while-preserving-matrix-dimensions#30699208

    Parameters
    ----------
    np_array : A numpy array
        Input numpy array

    Returns
    -------
    serialized : str
        A serialized representation of the numpy array.
    shape : tuple of ints
        The shape of the serialized array
    """
    # This version ties us to numpy -- Making a more general solution
    #import io
    #import numpy
    #import json
    #memfile = io.BytesIO()
    #numpy.save(memfile, np_array)
    #memfile.seek(0)
    #serialized = json.dumps(memfile.read().decode('latin-1'))
    #dt = np.dtype('float')
    bigendian_array = np_array.newbyteorder('>')
    serialized =bigendian_array.tobytes()
    shape = np_array.shape
    return serialized, shape

def deserialize_numpy(serialized_np, shape):
    """
    Deserializes a numpy array from a JSON-compatible string.

    from https://stackoverflow.com/questions/30698004/how-can-i-serialize-a-numpy-array-while-preserving-matrix-dimensions#30699208

    Parameters
    ----------
    serialized_np : str
        A serialized numpy array
    shape : tuple of ints
        The shape of the serialized array
    Returns
    -------
    np_array : numpy.ndarray
        The deserialized numpy array
    """
    #import io
    #import numpy
    #import json
    #memfile = io.BytesIO()
    #memfile.write(json.loads(serialized_np).encode('latin-1'))
    #memfile.seek(0)
    #np_array = numpy.load(memfile)
    #return np_array
    import numpy as np
    dt = np.dtype('float')
    dt.newbyteorder('>') # set to big-endian
    np_array = np.frombuffer(serialized_np, dtype=dt)
    np_array = np_array.reshape(shape)
    return np_array
