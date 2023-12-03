"""
A thin wrapper of standard ``json`` with standard compression libraries.
adapté de https://github.com/LucaCappelletti94/compress_json/tree/master
"""
import json
from typing import Dict, Any, Optional
import os
import gzip
import bz2

_DEFAULT_EXTENSION_MAP = {
    "json": "json",
    "gz": "gzip",
    "bz2": "bz2"
}

_DEFAULT_COMPRESSION_WRITE_MODES = {
    "json": "w",
    "gzip": "wt",
    "bz2": "wt"
}

_DEFAULT_COMPRESSION_READ_MODES = {
    "json": "r",
    "gzip": "rt",
    "bz2": "rt"
}


def get_compression_write_mode(compression: str) -> str:
    """Return mode for opening file buffer for writing.

    Parameters
    -------------------
    compression: str
        The extension of the compression to be used.

    Returns
    -------------------
    The code to use for opening the file in write mode.
    """
    return _DEFAULT_COMPRESSION_WRITE_MODES[compression]


def get_compression_read_mode(compression: str) -> str:
    """Return mode for opening file buffer for reading.

    Parameters
    -------------------
    compression: str
        The extension of the compression to be used.

    Returns
    -------------------
    The code to use for opening the file in read mode.
    """
    return _DEFAULT_COMPRESSION_READ_MODES[compression]


def infer_compression_from_filename(filename: str) -> str:
    """Return the compression protocal inferred from given filename.

    Parameters
    ----------
    filename: str
        The filename for which to infer the compression protocol
    """
    return _DEFAULT_EXTENSION_MAP[filename.split(".")[-1]]


def dump(
    obj: Any,
    path: str,
    compression_kwargs: Optional[Dict] = None,
    json_kwargs: Optional[Dict] = None,
    encoding: str = "utf-8",
):
    """Dump the contents of an object to disk as json using the detected compression protocol.

    Parameters
    ----------------
    obj: any
        The object that will be saved to disk
    path: str
        The path to the file to which to dump ``obj``
    compression_kwargs: Optional[Dict] = None
        Keywords argument to pass to the compressed file opening protocol.
    json_kwargs: Optional[Dict] = None
        Keywords argument to pass to the json file opening protocol.
    encoding: str = "utf-8"
        The encoding to use to dump the document. By default, UTF8.

    Raises
    ----------------
    ValueError
        If given path is not a valid string.
    """
    if not isinstance(path, str):
        if isinstance(obj, str):
            raise ValueError(
                (
                    "The object you have provided to the dump method is a string "
                    "while the object you have provided as a path is NOT a string "
                    "but an object of type {}. Maybe you need to swap them?"
                ).format(type(path))
            )
        raise ValueError("The given path is not a string.")
    
    compression_kwargs = {} if compression_kwargs is None else compression_kwargs
    json_kwargs = {} if json_kwargs is None else json_kwargs
    compression = infer_compression_from_filename(path)
    mode = get_compression_write_mode(compression)

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    if compression is None or compression == "json":
        fout = open(path, mode=mode, encoding=encoding, **compression_kwargs)
    elif compression == "gzip":
        fout = gzip.open(path, mode=mode, encoding=encoding, **compression_kwargs)

    elif compression == "bz2":
        fout = bz2.open(path, mode=mode, encoding=encoding, **compression_kwargs)

    with fout:
        json.dump(obj, fout, **json_kwargs)


def load(
    path: str,
    compression_kwargs: Optional[Dict] = None,
    json_kwargs: Optional[Dict] = None,
    encoding: str = "utf-8"
):
    """Return json object at given path uncompressed with detected compression protocol.

    Parameters
    ----------
    path: str
        The path to the file from which to load the ``obj``
    compression_kwargs: Optional[Dict] = None
        Keywords argument to pass to the compressed file opening protocol.
    json_kwargs: Optional[Dict] = None
        Keywords argument to pass to the json file opening protocol.
    encoding: str = "utf-8"
        The encoding to use to load the document. By default, UTF8.

    Raises
    ----------------
    ValueError
        If given path is not a valid string.
    """
    if not isinstance(path, str):
        raise ValueError("The given path is not a string.")

    compression_kwargs = {} if compression_kwargs is None else compression_kwargs
    json_kwargs = {} if json_kwargs is None else json_kwargs
    compression = infer_compression_from_filename(path)
    mode = get_compression_read_mode(compression)

    if compression is None or compression == "json":
        file = open(path, mode=mode, encoding=encoding, **compression_kwargs)

    elif compression == "gzip":
        file = gzip.open(path, mode=mode, encoding=encoding, **compression_kwargs)

    elif compression == "bz2":
        file = bz2.open(path, mode=mode, encoding=encoding, **compression_kwargs)

    with file:
        json_content = json.load(file, **json_kwargs)

    return json_content

