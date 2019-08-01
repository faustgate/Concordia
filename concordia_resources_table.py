from operator import itemgetter
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import datetime

main_layout = uic.loadUiType('concordia_resources_table.ui')[0]


class ResourcesTable(QWidget, main_layout):
    show_progressbar = pyqtSignal()
    hide_progressbar = pyqtSignal()
    data_downloaded = pyqtSignal()

    def __init__(self, statusbar, parent=None):
        super(ResourcesTable, self).__init__(parent)
        self.setupUi(self)
        self.statusbar = statusbar
        self.progress_bar = QProgressBar()
        self.initialize_status_bar()
        self.reverse = False
        self.sorted = False
        self.resources_data = []
        self.resources_data_keys = set()
        self.headers = []
        self.resources_table.horizontalHeader().setSectionsMovable(True)
        self.resources_table.horizontalHeader().sectionClicked.connect(self.resort_table)
        self.hidden_fields = []
        self.main_table_fields = []
        self.show_progressbar.connect(self.progress_bar.show)
        self.hide_progressbar.connect(self.progress_bar.hide)
        self.data_downloaded.connect(self.update_main_table)
        self.splitter.splitterMoved.connect(self.on_splitter_size_change)
        self.scrollAreaWidgetContents.setLayout(self.gridLayout_2)
        self.splitter.setSizes([self.splitter.sizes()[0], 0])
        self.details_layout = None
        self.details_layout_height = 300
        self.resources_table.itemSelectionChanged.connect(self.print_details)
        self.selected_resource = None
        self.sort_field_id = 0

    def on_splitter_size_change(self):
        self.details_layout_height = self.splitter.sizes()[1]

    def set_resources_data(self, resources_data, id_field, keys_cache_key=None):
        for resource in resources_data:
            for key in resource:
                if key not in self.main_table_fields:
                    self.main_table_fields.append(key)
                if type(resource[key]) == datetime.datetime:
                    resource[key] = resource[key].strftime("%Y-%m-%d %H:%M:%S UTC")

        for resource in resources_data:
            is_resource_known = False
            for key in self.main_table_fields:
                if key not in resource:
                    resource[key] = '-'

            for idx in range(len(self.resources_data)):
                if self.resources_data[idx][id_field] == resource[id_field]:
                    is_resource_known = True
                    self.resources_data[idx] = resource
            if not is_resource_known:
                self.resources_data.append(resource)

    def set_hidden_fields(self, hidden_fields):
        self.hidden_fields = hidden_fields

    def set_main_table_fields(self, main_table_fields):
        self.main_table_fields = main_table_fields
        self._prepare_headers()

    def _prepare_headers(self):
        for header in self.resources_data_keys:
            if header not in self.main_table_fields:
                self.main_table_fields.append(header)

        for header in self.main_table_fields:
            if header not in self.hidden_fields and header not in self.headers:
                self.headers.append(header)

    def resort_table(self):
        tbl_horizontal_header = self.resources_table.horizontalHeader()
        srt_fld_id = tbl_horizontal_header.sortIndicatorSection()
        if srt_fld_id != self.sort_field_id:
            self.reverse = False
        else:
            self.reverse = not self.reverse
        self.sort_field_id = srt_fld_id
        sort_field = self.headers[srt_fld_id]
        self.resources_data.sort(key=itemgetter(sort_field), reverse=self.reverse)
        tbl_horizontal_header.setSortIndicator(srt_fld_id, int(self.reverse))
        self.update_main_table()

    def update_main_table(self):
        self.resources_table.setSortingEnabled(False)
        self.resources_table.setRowCount(len(self.resources_data))
        self.resources_table.setColumnCount(len(self.headers))
        self.resources_table.setHorizontalHeaderLabels(self.headers)
        row_pointer = 0
        for resource in self.resources_data:
            column_pointer = 0
            for header in self.headers:
                item_value = str(resource[header]).strip() if header in resource and header.strip() != '' else '-'
                self.resources_table.setItem(row_pointer,
                                             column_pointer,
                                             QTableWidgetItem(item_value))
                column_pointer += 1
            row_pointer += 1
        self.resources_table.resizeColumnsToContents()
        self.resources_table.resizeRowsToContents()
        self.resources_table.setSortingEnabled(True)

    def initialize_status_bar(self):
        self.progress_bar.setRange(0, 0)
        self.statusbar.addPermanentWidget(self.progress_bar)
        self.progress_bar.setVisible(False)

    def refresh_main_table(self):
        self.show_progressbar.emit()
        self.get_aws_resources()
        self.hide_progressbar.emit()
        self.data_downloaded.emit()

    def print_details(self):
        if len(self.resources_table.selectedItems()) > 0:
            self.splitter.setSizes([self.splitter.sizes()[0], self.details_layout_height])
            self.selected_resource = self.resources_data[self.resources_table.selectedItems()[0].row()]
            self.print_resource_details()
        else:
            self.splitter.setSizes([self.splitter.sizes()[0], 0])

    def set_details_layout(self, details_layout_file):
        self.details_layout = uic.loadUi(details_layout_file)
        self.tabWidget.addTab(self.details_layout, "Description")
