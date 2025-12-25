from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from ui.others.window import Window
from ui.others.uppercase import UpperCaseLineEdit
from utils.project_calls import add_project, validate_project, edit_project, get_project_by_id


class AddEditProjectForm(Window):
    project_added = pyqtSignal()

    def __init__(self, project=None, is_edit=False):
        super().__init__(draggable=False, topbar=False)

        self.setFixedSize(900, 250)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setWindowModality(Qt.ApplicationModal)

        # Main Layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Form Fields
        self.projectname_input = UpperCaseLineEdit()
        self.category_combo = QComboBox()

        for w in [
            self.projectname_input, self.category_combo
        ]:
            w.setObjectName("inputField")

        self.projectname_input.setPlaceholderText("Project Name")
        self.category_combo.setPlaceholderText("CATEGORY")
        self.category_combo.addItems(["- CATEGORY -",
                                      "SPECIAL PROGRAM FOR THE EMPLOYMENT OF STUDENTS AND OUT-SCHOOL YOUTH (SPES) IMPLEMENTATION",
                                      "LIVELIHOOD ASSISTANCE REGISTRATION", 
                                      "OFW/MGIRANT DESK ASSISTANCE", 
                                      "SKILLS TRAINING PROGRAM REGISTRATION", 
                                      "GOVERNEMENT INTERNSHIP PROGRAM (GIP) APPLICATION", 
                                      "JOB REFERRAL ISSUANCE", 
                                      "ESTABLISHMENT ACCREDITATION"])
        
        self.category_combo.setCurrentIndex(0)

        # Project rows
        project_layout = QVBoxLayout()
        project_layout.addWidget(self.projectname_input)
        project_layout.addWidget(self.category_combo)

        # Buttons
        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("Save" if is_edit else "Add")
        cancel_btn = QPushButton("Cancel")

        self.submit_btn.setObjectName("buttons")
        cancel_btn.setObjectName("buttons")

        self.submit_btn.clicked.connect(self.handle_submit)
        self.submit_btn.setShortcut("Return")   # Enter = submit
        cancel_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(cancel_btn)

        # Assemble Layout
        layout.addLayout(project_layout)
        layout.addLayout(btn_layout)

        self.content.addLayout(layout)

        self.project_id = project
        self.populate_field(self.project_id)
        self.isEdit = is_edit

    # SUBMIT HANDLER
    def handle_submit(self):
        project_id = self.project_id
        project_name = self.projectname_input.text().strip()
        category = self.category_combo.currentText()

        success, msg= (validate_project(project_name, category))

        if success:
            if self.isEdit:
                edit_project(project_id, project_name, category)
                self.project_added.emit()
                self.close()
            else:
                add_project(project_name, category)
                self.project_added.emit()
                self.close()
        else:
            QMessageBox.warning(self, "Notification", msg)

    def populate_field(self, project_id):
        data = get_project_by_id(project_id)
        if data:
            project_name, category = data

            self.projectname_input.setText(project_name)

            if category in ["SPECIAL PROGRAM FOR THE EMPLOYMENT OF STUDENTS AND OUT-SCHOOL YOUTH (SPES) IMPLEMENTATION",
                                      "LIVELIHOOD ASSISTANCE REGISTRATION", 
                                      "OFW/MGIRANT DESK ASSISTANCE", 
                                      "SKILLS TRAINING PROGRAM REGISTRATION", 
                                      "GOVERNEMENT INTERNSHIP PROGRAM (GIP) APPLICATION", 
                                      "JOB REFERRAL ISSUANCE", 
                                      "ESTABLISHMENT ACCREDITATION"]:
                index = self.category_combo.findText(category)
                self.category_combo.setCurrentIndex(index)
            else:
                self.category_combo.setCurrentIndex(-1)

    # POSITIONING
    def showEvent(self, event):
        super().showEvent(event)

        if self.parent():
            p = self.parent().geometry()
            x = p.x() + (p.width() - self.width()) // 3
            y = p.y() + (p.height() - self.height()) // 3
            self.move(x, y)

        self.projectname_input.setFocus()
