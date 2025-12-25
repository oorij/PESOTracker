from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QFont, QIcon

from ui.others.window import Window
from utils.helpers import resource_path

class MenuWindow(Window):
    def __init__(self):
        super().__init__(draggable=True, topbar=True)

        # Window Setup
        self.setWindowIcon(QIcon(resource_path("assets/peso.ico")))
        self.setFixedSize(400, 315)
        main_layout = QVBoxLayout()
        
        font = QFont("Segoe UI", 12)

        # Buttons with Icons
        beneficiaries_btn = QPushButton("  Beneficiaries")
        beneficiaries_btn.setIcon(QIcon(resource_path("assets/beneficiaries.svg")))
        beneficiaries_btn.setObjectName("menuButtons")
        beneficiaries_btn.setFont(font)

        projects_btn = QPushButton("  Projects")
        projects_btn.setIcon(QIcon(resource_path("assets/projects.svg")))
        projects_btn.setObjectName("menuButtons")
        projects_btn.setFont(font)

        logout_btn = QPushButton("  Logout")
        logout_btn.setIcon(QIcon(resource_path("assets/logout.svg")))
        logout_btn.setObjectName("menuButtons")
        logout_btn.setFont(font)

        beneficiaries_btn.clicked.connect(self.open_beneficiaries)
        projects_btn.clicked.connect(self.open_projects)
        logout_btn.clicked.connect(self.logout)

        # Add buttons to layout
        main_layout.addWidget(beneficiaries_btn)
        main_layout.addWidget(projects_btn)
        main_layout.addWidget(logout_btn)
        main_layout.setContentsMargins(15, 15, 15, 15)
        self.content.addLayout(main_layout)

    def open_beneficiaries(self):
        from ui.beneficiaries.main_beneficiaries import BeneficiariesWindow
        beneficiaries_window = BeneficiariesWindow()
        beneficiaries_window.show()
        self.close()

    def open_projects(self):
        from ui.projects.main_projects import ProjectsWindow
        projects_window = ProjectsWindow()
        projects_window.show()
        self.close()

    def logout(self):
        from ui.login_page import LoginWindow
        login_window = LoginWindow()
        login_window.show()
        self.close()
