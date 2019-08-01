import sys
import utils
from PyQt5.QtWidgets import *

from PyQt5 import uic
import os
# from pycallgraph import PyCallGraph
# from pycallgraph.output import GraphvizOutput
from concordia_aws_credentials import ConcordiaAWSCredentials
from concordia_aws_credentials_manager import ConcordiaAWSCredentialsManager
from concordia_aws_service import ConcordiaAWSService

main_layout = uic.loadUiType("ui/mainwindow.ui")[0]


class ConcordiaMain(QMainWindow, main_layout):
    def __init__(self, parent=None):
        super(ConcordiaMain, self).__init__(parent)
        self.setupUi(self)
        bar = self.menuBar()
        bar.setNativeMenuBar(False)
        self.creds_dialog = ConcordiaAWSCredentials()
        self.creds_manager_dialog = ConcordiaAWSCredentialsManager()
        self.services = []
        self.region_ids = []
        self.region_names = []
        self.service_names = []
        self.active_services = []
        self.current_tab_index = -1

        self.tabWidget.tabCloseRequested.connect(self.close_tab)
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        while True:
            self.aws_creds = self.creds_dialog.get_saved_creds()
            if len(self.aws_creds) == 0:
                self.creds_dialog.exec_()
            else:
                break

        for elem in utils.get_stored_structure(
                os.path.join(os.path.dirname(__file__), 'regions.json')):
            self.region_ids.append(elem['id'])
            self.region_names.append(elem['name'])

        for elem in utils.get_stored_structure(
                os.path.join(os.path.dirname(__file__), 'services.json')):
            self.services.append(elem)
            self.service_names.append(elem['name'])

        self.regionSelect.addItems(self.region_names)
        self.serviceSelect.addItems(self.service_names)

        for creds in self.aws_creds:
            self.credsSelect.addItem(creds['name'])

        self.serviceSelect.currentIndexChanged.connect(self.on_region_changed)
        self.regionSelect.currentIndexChanged.connect(self.on_region_changed)
        self.credsSelect.currentIndexChanged.connect(self.on_region_changed)

        self.actionCredentials.triggered.connect(self.show_creds_manager_dialog)

        self.setWindowTitle("Konkordia")

    def on_region_changed(self):
        cur_creds = self.aws_creds[self.credsSelect.currentIndex()]
        cur_creds['region'] = self.region_ids[self.regionSelect.currentIndex()]
        cur_service = self.services[self.serviceSelect.currentIndex()]

        service = ConcordiaAWSService(cur_service, cur_creds, self.statusbar)
        self.active_services.append(service)
        self.tabWidget.setCurrentIndex(self.tabWidget.addTab(service,
                                                             service.get_name()))

    def close_tab(self, idx):
        self.tabWidget.removeTab(idx)

    def show_creds_manager_dialog(self):
        self.creds_manager_dialog.exec_()

    def on_tab_changed(self, new_tab_index):
        self.active_services[self.current_tab_index].set_shown(False)
        self.active_services[new_tab_index].set_shown(True)
        self.current_tab_index = new_tab_index


def main():
    app = QApplication(sys.argv)
    ex = ConcordiaMain()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    # with PyCallGraph(output=GraphvizOutput()):
    main()
