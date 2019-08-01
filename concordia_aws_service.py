from threading import Thread, Event
import time

from PyQt5.QtCore import QTimer, pyqtSignal

import utils
from PyQt5.QtWidgets import *

from PyQt5 import uic
import os
import json

splitter_layout = uic.loadUiType('ui/splitter.ui')[0]


class Found(Exception):
    pass


class ConcordiaAWSService(QWidget, splitter_layout):
    name_changed = pyqtSignal(str)

    def __init__(self, service_description, aws_creds, statusbar, parent=None):
        self.statusbar = statusbar
        super(ConcordiaAWSService, self).__init__(parent)
        self.setupUi(self)
        self.aws_creds = aws_creds
        self.service_description = service_description
        self.srv_module_name = service_description['module']
        self.service_entities_tree = self.get_service_entities_tree()
        self.fill_side_bar(self.entities_tree_widget, self.service_entities_tree)
        self.entities_tree_widget.currentItemChanged.connect(self.on_new_service_entity_selected)
        self.service_entity = None
        self.service_entity_name = None
        self.refresher = QTimer()
        self.refresher.timeout.connect(self.refresh_info)

    def fill_side_bar_item(self, item, value):
        item.setExpanded(True)
        if type(value) is dict:
            for key, val in value.items():
                child = QTreeWidgetItem()
                child.setText(0, key)
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

    def fill_side_bar(self, widget, service_entities_tree):
        widget.clear()
        self.fill_side_bar_item(widget.invisibleRootItem(), service_entities_tree)

    def find_service_entity_class(self, tree, service_entity_name):
        for key, value in tree.items():
            if type(value) == str and key == service_entity_name:
                raise Found(value)
            if type(value) == dict:
                self.find_service_entity_class(value, service_entity_name)

    def on_new_service_entity_selected(self, current_service_entity):
        try:
            self.find_service_entity_class(self.service_entities_tree,
                                           current_service_entity.text(0))
        except Found as exc:
            self.service_entity = utils.get_class_object(exc.args[0])(self.aws_creds, self.statusbar)
            if self.splitter.widget(1) is not None:
                self.splitter.widget(1).setParent(None)
            self.splitter.insertWidget(1, self.service_entity)
            Thread(target=self.service_entity.refresh_main_table).start()
            if not self.refresher.isActive():
                self.start_refresher()
            self.service_entity_name = current_service_entity.text(0)
            self.name_changed.emit(self.get_name())
        except AttributeError:
            pass

    def refresh_info(self):
        if self.service_entity is not None:
            Thread(target=self.service_entity.refresh_main_table).start()

    def get_name(self):
        name = "{0} | {1} | {2}".format(self.aws_creds['name'],
                                        self.aws_creds['region'],
                                        self.service_description['name'])
        if self.service_entity is not None:
            name = "{0} | {1}".format(name, self.service_entity_name)
        return name

    def get_service_entities_tree(self):
        with open(os.path.join(self.srv_module_name.replace('.', '/'),
                               'service_entities.json'), 'r') as service_entities_tree_file:
            service_entities_tree = json.load(service_entities_tree_file)
        return service_entities_tree

    def stop_refresher(self):
        self.refresher.stop()

    def start_refresher(self):
        self.refresher.start(10000)
