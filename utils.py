import json
import os

from pydoc import safeimport


def get_class_object(path, forceload=0):
    """Locate an object by name or dotted path, importing as necessary."""
    parts = [part for part in path.split('.') if part]
    module, n = None, 0
    while n < len(parts):
        nextmodule = safeimport('.'.join(parts[:n+1]), forceload)
        if nextmodule:
            module, n = nextmodule, n + 1
        else:
            break
    if module:
        object = module
    else:
        object = None
    for part in parts[n:]:
        try:
            object = getattr(object, part)
        except AttributeError:
            return None
    return object


def get_stored_structure(file_name):
    try:
        with open(file_name) as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return None