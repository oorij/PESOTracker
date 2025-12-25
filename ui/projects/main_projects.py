from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QSizePolicy, QHeaderView, QMessageBox, QLabel
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import Qt, QSortFilterProxyModel

from ui.others.window import Window
from utils.project_calls import get_projects_list, delete_project
from ui.others.uppercase import UpperCaseLineEdit
from utils.helpers import resource_path

class ProjectsWindow(Window):
    def __init__(self):
        super().__init__(draggable=True, topbar=True)
        self.setFixedSize(1000, 820)
        self.setWindowIcon(QIcon(resource_path("assets/peso.ico")))

        # --- Main layout ---
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- Search bar ---
        search_layout = QHBoxLayout()
        self.search_input = UpperCaseLineEdit()
        self.search_input.setPlaceholderText("Search ...")
        self.search_input.setObjectName("inputField")
        self.search_input.textChanged.connect(self.apply_filter)
        
        search_layout.addWidget(self.search_input)

        # Table View
        self.tableView = QTableView()
        self.tableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setFixedHeight(600)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setSelectionMode(QTableView.SingleSelection)
        self.tableView.setEditTriggers(QTableView.NoEditTriggers)
        self.tableView.setSortingEnabled(True)
        self.tableView.verticalHeader().setVisible(False)

        # Model
        self.model = QStandardItemModel()

        # Proxy model for filtering
        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxyModel.setSourceModel(self.model)

        self.proxyModel.setFilterKeyColumn(-1)

        self.tableView.setModel(self.proxyModel)

        # --- Bottom Buttons ---
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("&Add")
        self.edit_btn = QPushButton("&Edit")
        self.delete_btn = QPushButton("&Delete")
        self.return_btn = QPushButton("&Return to Menu")

        for btn in (self.add_btn, self.edit_btn, self.delete_btn, self.return_btn):
            btn.setObjectName("buttons")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.return_btn)

        # Assemble Layout
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.tableView)
        main_layout.addLayout(btn_layout)

        self.content.addLayout(main_layout)

        # Connect Buttons
        self.return_btn.clicked.connect(self.return_to_menu)
        self.add_btn.clicked.connect(self.add_project)
        self.edit_btn.clicked.connect(self.edit_project)
        self.delete_btn.clicked.connect(self.delete_project)

        self.setup_headers()
        self.load_projects()

    # Setup table headers (one time only)
    def setup_headers(self):
        headers = [
        "ID", "Project Name", "Category"
        ]

        self.model.setColumnCount(len(headers))
        self.model.setHorizontalHeaderLabels(headers)

        header = self.tableView.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.tableView.setColumnWidth(0, 80)

        for col in range(1, len(headers)):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

    def load_projects(self):
        self.model.removeRows(0, self.model.rowCount())

        data = get_projects_list()

        self.model.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            for col_idx, col_value in enumerate(row_data):
                item = QStandardItem(str(col_value))
                item.setEditable(False)
                item.setTextAlignment(Qt.AlignCenter)
                self.model.setItem(row_idx, col_idx, item)

    def apply_filter(self):
        text = self.search_input.text().strip()
        self.proxyModel.setFilterFixedString(text)

    # Buttons
    def return_to_menu(self):
        self.close()
        from ui.menu_page import MenuWindow
        menu_window = MenuWindow()
        menu_window.show()

    def add_project(self):
        from ui.projects.addedit_project import AddEditProjectForm
        self.add_window = AddEditProjectForm()
        self.add_window.show()
        self.add_window.project_added.connect(self.load_projects)

    def edit_project(self):
        selected = self.tableView.selectionModel().selectedRows()
        if selected:
            view_index = selected[0]
            source_index = self.proxyModel.mapToSource(view_index)
            row = source_index.row()
            project_id = int(self.model.item(row, 0).text())

            from ui.projects.addedit_project import AddEditProjectForm
            self.editwindow = AddEditProjectForm(is_edit=True, project=project_id)
            self.editwindow.show()
            self.editwindow.project_added.connect(self.load_projects)
        else:
            QMessageBox.warning(self, "Warning", "Please select a project to edit.")

    def delete_project(self):
        selected = self.tableView.selectionModel().selectedRows()
        if selected:
            view_index = selected[0]
            source_index = self.proxyModel.mapToSource(view_index)
            row = source_index.row()
            project_id = int(self.model.item(row, 0).text())

            confirm = QMessageBox.question(
                self,
                "Confirm Delete",
                "Are you sure you want to delete this project?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm == QMessageBox.Yes:
                # Delete from database
                delete_project(project_id)
                # Remove from table
                self.model.removeRow(row)
                self.load_projects()
        else:
            QMessageBox.warning(self, "Warning", "Please select a project to delete.")