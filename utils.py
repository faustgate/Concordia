import json
import os

from pydoc import safeimport

from PySide2 import QtWidgets
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from pyside2uic import compileUi
from xml.etree import ElementTree
from io import StringIO


def loadUiType(design):
    """
    PySide2 equivalent of PyQt5's `uic.loadUiType()` function.

    Compiles the given `.ui` design file in-memory and executes the
    resulting Python code. Returns form and base class.
    """
    parsed_xml   = ElementTree.parse(design)
    widget_class = parsed_xml.find('widget').get('class')
    form_class   = parsed_xml.find('class').text
    with open(design) as input:
        output = StringIO()
        compileUi(input, output, indent=0)
        source_code = output.getvalue()
        syntax_tree = compile(source_code, filename='<string>', mode='exec')
        scope  = {}
        exec(syntax_tree, scope)
        form_class = scope[f'Ui_{form_class}']
        base_class = eval(f'QtWidgets.{widget_class}')
    return form_class, base_class


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


def load_ui_file(file_location):
    loader = QUiLoader()
    file = QFile(file_location)
    file.open(QFile.ReadOnly)
    my_widget = loader.load(file)
    file.close()
    return my_widget
