import sys
import utils
from PyQt5.QtWidgets import *

from PyQt5 import uic
import os
import json
import curses

splitter_layout = uic.loadUiType('ui/splitter.ui')[0]


class Found(Exception):
    pass


class ConcordiaAWSService(QWidget, splitter_layout):
    def __init__(self, service_description, aws_creds, parent=None):
        super(ConcordiaAWSService, self).__init__(parent)
        self.setupUi(self)
        self.aws_creds = aws_creds
        self.service_description = service_description
        self.srv_module_name = service_description['module']
        self.service_sidebar = self.get_side_bar()
        self.fill_side_bar(self.treeWidget, self.service_sidebar)

    def fill_side_bar_item(self, item, value):
        item.setExpanded(True)
        if type(value) is dict:
            for key, val in value.items():
                child = QTreeWidgetItem()
                child.setText(0, key)
                if type(val) == str:
                    self.treeWidget.currentItemChanged.connect(self.on_click)
                item.addChild(child)
                self.fill_side_bar_item(child, val)
        elif type(value) is list:
            for val in value:
                child = QTreeWidgetItem()
                item.addChild(child)
                if type(val) is dict:
                    child.setText(0, '[dict]')
                    self.fill_side_bar_item(child, val)
                elif type(val) is list:
                    child.setText(0, '[list]')
                    self.fill_side_bar_item(child, val)
                else:
                    child.setText(0, val)
                child.setExpanded(True)
        # else:
        #     child = QTreeWidgetItem()
        #     child.setText(0, value)
        #     item.addChild(child)

    def fill_side_bar(self, widget, value):
        widget.clear()
        self.fill_side_bar_item(widget.invisibleRootItem(), value)

    def find_component_class(self, tree, component_name):
        for key, value in tree.items():
            if type(value) == str and key == component_name:
                raise Found(value)
            if type(value) == dict:
                self.find_component_class(value, component_name)

    def on_click(self, current):
        try:
            self.find_component_class(self.service_sidebar, current.text(0))
        except Found as exc:
            component_class_object = utils.get_class_object(exc.args[0])
            if self.splitter.widget(1) is not None:
                self.splitter.widget(1).setParent(None)
            self.splitter.insertWidget(1, component_class_object(self.aws_creds))
        except AttributeError:
            pass

    def get_name(self):
        return "{0} | {1} | {2}".format(self.aws_creds['name'],
                                        self.aws_creds['region'],
                                        self.service_description['name'])

    def get_side_bar(self):
        with open(os.path.join(self.srv_module_name.replace('.', '/'), 'services.json'), 'r') as service_tree_file:
            service_tree = json.load(service_tree_file)
        return service_tree