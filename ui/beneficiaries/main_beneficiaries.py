from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QSizePolicy, QHeaderView, QMessageBox, QLabel, QFileDialog
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import Qt, QSortFilterProxyModel

from ui.others.window import Window
from utils.beneficiary_calls import get_beneficiaries, delete_beneficiary
from utils.project_calls import get_projects_map
from ui.others.uppercase import UpperCaseLineEdit
from utils.helpers import resource_path
import csv


class BeneficiariesWindow(Window):
    def __init__(self):
        super().__init__(draggable=True, topbar=True)
        self.showMaximized()
        self.setWindowIcon(QIcon(resource_path("assets/peso.ico")))

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = UpperCaseLineEdit()
        self.search_input.setPlaceholderText("Search ...")
        self.search_input.setObjectName("inputField")
        self.search_input.textChanged.connect(self.apply_filter)

        self.total_beneficiaries = QLabel()
        self.total_beneficiaries.setObjectName("inputFieldWhite")

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.total_beneficiaries)

        # Table View
        self.tableView = QTableView()
        self.tableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setFixedHeight(800)
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

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("&Add")
        self.edit_btn = QPushButton("&Edit")
        self.delete_btn = QPushButton("&Delete")
        self.export_btn = QPushButton("E&xport")
        # self.import_btn = QPushButton("&Import")
        self.return_btn = QPushButton("&Return to Menu")

        for btn in (self.add_btn, self.edit_btn, self.delete_btn, self.return_btn, self.export_btn, 
                    # self.import_btn
                    ):
            btn.setObjectName("buttons")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.export_btn)
        # btn_layout.addWidget(self.import_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.return_btn)

        # Add widgets to layout
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.tableView)
        main_layout.addLayout(btn_layout)

        self.content.addLayout(main_layout)

        # Connect buttons
        self.return_btn.clicked.connect(self.return_to_menu)
        self.add_btn.clicked.connect(self.add_beneficiary)
        self.edit_btn.clicked.connect(self.edit_beneficiary)
        self.delete_btn.clicked.connect(self.delete_beneficiary)
        self.export_btn.clicked.connect(self.export_csv)
        # self.import_btn.clicked.connect(self.import_csv)

        # Load table
        self.setup_headers()
        self.load_beneficiaries()

    # Setup table headers (one time only)
    def setup_headers(self):
        headers = [
        "ID", "Last Name", "First Name", "Middle Name", "Suffix",
        "Gender", "Street", "Barangay", "Contact No.", "Projects"
        ]

        self.model.setColumnCount(len(headers))
        self.model.setHorizontalHeaderLabels(headers)

        fixed_cols = {0, 1, 2, 3, 4, 5, 7, 8}

        header = self.tableView.horizontalHeader()

        # Set fixed columns
        fixed_widths = {
            0: 60,   # ID
            1: 200,   # LName
            2: 200,   # FName
            3: 200,   # MName
            4: 100,   # Suffix
            5: 100,   # Gender
            7: 170,   # Brgy
            8: 170    # Contact No.
        }

        for col, width in fixed_widths.items():
            header.setSectionResizeMode(col, QHeaderView.Fixed)
            self.tableView.setColumnWidth(col, width)

        # Stretch the rest
        for col in range(len(headers)):
            if col not in fixed_cols:
                header.setSectionResizeMode(col, QHeaderView.Stretch)

        # Load All Data
    def load_beneficiaries(self):
        data = get_beneficiaries()
        projects_map = get_projects_map()

        self.model.setRowCount(0)
        self.model.setRowCount(len(data))

        self.total_beneficiaries.setText(
            f"Total Beneficiaries: {len(data)}"
        )

        PROJECT_COL = self.model.columnCount() - 1

        for row_idx, row_data in enumerate(data):
            for col_idx, col_value in enumerate(row_data):

                if col_idx == PROJECT_COL:
                    col_value = projects_map.get(col_value, "-")

                item = QStandardItem(str(col_value))
                item.setEditable(False)
                item.setTextAlignment(Qt.AlignCenter)

                self.model.setItem(row_idx, col_idx, item)

        # Filtering
    def apply_filter(self):
        text = self.search_input.text().strip()
        self.proxyModel.setFilterFixedString(text)

        # Buttons
    def return_to_menu(self):
        self.close()
        from ui.menu_page import MenuWindow
        menu_window = MenuWindow()
        menu_window.show()

    def add_beneficiary(self):
        from ui.beneficiaries.addedit_beneficiary import AddEditBeneficiaryForm
        self.add_window = AddEditBeneficiaryForm(is_edit=False)
        self.add_window.show()
        self.add_window.beneficiary_added.connect(self.load_beneficiaries)

    def edit_beneficiary(self):
        selection = self.tableView.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a beneficiary to edit.")
            return

        view_index = selection.selectedRows()[0]
        source_index = self.proxyModel.mapToSource(view_index)

        beneficiary_id = int(
            self.model.item(source_index.row(), 0).text()
        )

        from ui.beneficiaries.addedit_beneficiary import AddEditBeneficiaryForm
        self.editwindow = AddEditBeneficiaryForm(
            is_edit=True,
            beneficiary=beneficiary_id
        )
        self.editwindow.show()
        self.editwindow.beneficiary_added.connect(self.load_beneficiaries)

    def delete_beneficiary(self):
        selected = self.tableView.selectionModel().selectedRows()
        if selected:
            view_index = selected[0]
            source_index = self.proxyModel.mapToSource(view_index)
            row = source_index.row()
            beneficiary_id = int(self.model.item(row, 0).text())

            confirm = QMessageBox.question(
                self,
                "Confirm Delete",
                "Are you sure you want to delete this beneficiary?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm == QMessageBox.Yes:
                # Delete from database
                delete_beneficiary(beneficiary_id)
                # Remove from table
                self.model.removeRow(row)
                self.load_beneficiaries()
        else:
            QMessageBox.warning(self, "Warning", "Please select a beneficiary to delete.")
    
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "", "CSV Files (*.csv)"
        )
        if not path:
            return

        model = self.tableView.model()

        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # headers
            headers = [
                model.headerData(col, Qt.Horizontal)
                for col in range(model.columnCount())
            ]
            writer.writerow(headers)

            # data
            for row in range(model.rowCount()):
                row_data = [
                    model.index(row, col).data() or ""
                    for col in range(model.columnCount())
                ]
                writer.writerow(row_data)

    # def import_csv(self):
    #     path, _ = QFileDialog.getOpenFileName(
    #         self, "Import CSV", "", "CSV Files (*.csv)"
    #     )
    #     if not path:
    #         return

    #     model = QStandardItemModel()
    #     self.tableView.setModel(model)

    #     success_count = 0
    #     failed_rows = []

    #     with open(path, "r", encoding="utf-8") as file:
    #         reader = csv.reader(file)
    #         headers = next(reader)

    #         # Normalize headers
    #         headers = [h.strip().lower() for h in headers]
    #         model.setHorizontalHeaderLabels(headers)

    #         conn = get_connection()
    #         cursor = conn.cursor()

    #         for row_number, row in enumerate(reader, start=2):
    #             data = dict(zip(headers, row))

    #             try:
    #                 lname     = data.get("Last Name", "").strip()
    #                 fname     = data.get("First Name", "").strip()
    #                 mname     = data.get("Middle Name", "").strip()
    #                 suffix    = data.get("Suffix", "-") or "-"
    #                 gender    = data.get("Gender", "-") or "-"
    #                 street    = data.get("Street", "").strip()
    #                 barangay  = data.get("Barangay", "").strip()
    #                 contactno = data.get("Contact No.", "").strip()

    #                 # --- project_id MUST be int ---
    #                 project_raw = data.get("Projects", "").strip()
    #                 project_id = int(project_raw) if project_raw.isdigit() else None

    #             except Exception:
    #                 failed_rows.append(f"Row {row_number}: Invalid column format")
    #                 continue

    #             # --- VALIDATION ---
    #             is_valid, error_msg = validate_beneficiary(
    #                 lname, fname, suffix, project_id, mname
    #             )
    #             if not is_valid:
    #                 failed_rows.append(f"Row {row_number}: {error_msg}")
    #                 continue

    #             # --- INSERT INTO DB ---
    #             try:
    #                 cursor.execute("""
    #                     INSERT INTO beneficiaries
    #                     (lname, fname, mname, suffix, gender, street, barangay, contactno, project_id)
    #                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    #                 """, (
    #                     lname, fname, mname, suffix,
    #                     gender, street, barangay, contactno, project_id
    #                 ))
    #             except Exception as e:
    #                 failed_rows.append(f"Row {row_number}: DB error ({e})")
    #                 continue

    #             # --- ADD TO TABLE ---
    #             model.appendRow([QStandardItem(str(v)) for v in row])
    #             success_count += 1

    #         conn.commit()
    #         conn.close()

    #     msg = f"Imported {success_count} row(s) successfully."
    #     if failed_rows:
    #         msg += "\n\nFailed rows:\n" + "\n".join(failed_rows)

    #     QMessageBox.information(self, "CSV Import", msg)

