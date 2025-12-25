from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from ui.others.window import Window
from ui.others.uppercase import UpperCaseLineEdit
from utils.beneficiary_calls import add_beneficiary, validate_beneficiary, edit_beneficiary, get_beneficiary_by_id
from utils.project_calls import get_projects_list


class AddEditBeneficiaryForm(Window):
    beneficiary_added = pyqtSignal()

    def __init__(self, beneficiary=None, is_edit=False):
        super().__init__(draggable=False, topbar=False)

        self.setFixedSize(700, 400)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setWindowModality(Qt.ApplicationModal)

        # Main Layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Form Fields
        self.fname_input = UpperCaseLineEdit()
        self.lname_input = UpperCaseLineEdit()
        self.mname_input = UpperCaseLineEdit()
        self.street_input = UpperCaseLineEdit()
        self.barangay_input = UpperCaseLineEdit()
        self.contactno_input = UpperCaseLineEdit()
        self.suffix_combo = QComboBox()
        self.gender_combo = QComboBox()
        self.projects_combo = QComboBox()

        for w in [
            self.fname_input, self.lname_input, self.mname_input, self.street_input, self.barangay_input, self.contactno_input, 
            self.projects_combo, self.gender_combo, self.suffix_combo
        ]:
            w.setObjectName("inputField")
        
        self.lname_input.setPlaceholderText("Last Name")
        self.fname_input.setPlaceholderText("First Name")
        self.mname_input.setPlaceholderText("Middle Name")
        self.street_input.setPlaceholderText("Street")
        self.barangay_input.setPlaceholderText("Barangay")
        self.contactno_input.setPlaceholderText("Contact No.")

        self.gender_combo.addItems(["- GENDER -", "MALE", "FEMALE", "OTHER"])
        self.suffix_combo.addItems(["- SUFFIX -", "SR.", "JR.", "II", "III, IV, V, etc."])

        self.projects_combo.clear()

        self.projects_combo.addItem("- PROJECTS -", None)
        self.projects_combo.setItemData(0, 0, Qt.UserRole - 1)
        for project_id, project_name, category in get_projects_list():
            display_text = f"{project_name}"
            self.projects_combo.addItem(display_text, project_id)

        # Name rows
        name1 = QHBoxLayout()
        name1.addWidget(self.lname_input)
        name1.addWidget(self.fname_input)

        name2 = QHBoxLayout()
        name2.addWidget(self.mname_input)
        name2.addWidget(self.suffix_combo)
        name2.addWidget(self.gender_combo)

        # Address rows
        addr1 = QHBoxLayout()
        addr1.addWidget(self.street_input)
        addr1.addWidget(self.barangay_input)

        addr2 = QHBoxLayout()
        addr2.addWidget(self.contactno_input)
        addr2.addWidget(self.projects_combo)

        # Buttons
        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("Save" if is_edit else "Add")
        cancel_btn = QPushButton("Cancel")

        self.submit_btn.setObjectName("buttons")
        cancel_btn.setObjectName("buttons")

        self.submit_btn.clicked.connect(self.handle_submit)
        self.submit_btn.setShortcut("Return")
        cancel_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(cancel_btn)

        # Assemble Layout
        layout.addLayout(name1)
        layout.addLayout(name2)
        layout.addLayout(addr1)
        layout.addLayout(addr2)
        layout.addLayout(btn_layout)

        self.content.addLayout(layout)

        self.beneficiary_id = beneficiary
        self.populate_field(self.beneficiary_id)
        self.isEdit = is_edit

    # SUBMIT HANDLER
    def handle_submit(self):
        def normalize_combo(combo):
            return "-" if combo.currentIndex() == 0 else combo.currentText()
        
        beneficiary_id = self.beneficiary_id
        lname = self.lname_input.text().strip()
        fname = self.fname_input.text().strip()
        mname = self.mname_input.text().strip()
        suffix = normalize_combo(self.suffix_combo)
        gender = normalize_combo(self.gender_combo)
        street = self.street_input.text().strip()
        barangay = self.barangay_input.text().strip()
        contactno = self.contactno_input.text().strip()
        project_id = self.projects_combo.currentData()

        if self.isEdit:
            valid, msg = validate_beneficiary(
                lname, fname, suffix, project_id, mname, beneficiary_id
            )
        else:
            valid, msg = validate_beneficiary(lname, fname, suffix, project_id, mname)

        if valid:
            if self.isEdit:
                edit_beneficiary(
                    self.beneficiary_id, lname, fname, project_id,
                    mname, suffix, gender, street, barangay, contactno
                )
            else:
                add_beneficiary(
                    lname, fname, project_id,
                    mname, suffix, gender, street, barangay, contactno
                )
            self.beneficiary_added.emit()
            self.close()
        else:
            QMessageBox.warning(self, "Notification", msg)


    def populate_field(self, beneficiary_id):
        data = get_beneficiary_by_id(beneficiary_id)
        if data:
            lname, fname, mname, suffix, gender, street, barangay, contactno, project = data
            
            self.lname_input.setText(lname)
            self.fname_input.setText(fname)
            self.mname_input.setText(mname)
            self.street_input.setText(street)
            self.barangay_input.setText(barangay)
            self.contactno_input.setText(contactno)

            if gender in ["MALE", "FEMALE", "OTHER"]:
                index = self.gender_combo.findText(gender)
                self.gender_combo.setCurrentIndex(index)
            else:
                self.gender_combo.setCurrentIndex(0)

            if suffix in ["SR.", "JR.", "II", "III, IV, V, etc."]:
                index = self.suffix_combo.findText(suffix)
                self.suffix_combo.setCurrentIndex(index)
            else:
                self.suffix_combo.setCurrentIndex(0)

            index = self.projects_combo.findData(project)
            if index != -1:
                self.projects_combo.setCurrentIndex(index)
            else:
                self.projects_combo.setCurrentIndex(0)

    # POSITIONING
    def showEvent(self, event):
        super().showEvent(event)

        if self.parent():
            p = self.parent().geometry()
            x = p.x() + (p.width() - self.width()) // 3
            y = p.y() + (p.height() - self.height()) // 3
            self.move(x, y)

        self.fname_input.setFocus()

