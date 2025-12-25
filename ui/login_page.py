from PyQt5.QtWidgets import (
    QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QSizePolicy, QSpacerItem
)
from PyQt5.QtGui import (
    QPixmap, QFont, QIcon
)

from utils.helpers import resource_path
from ui.others.window import Window
from utils.login_calls import validate_login

class LoginWindow(Window):
    def __init__(self, db_path=None):
        super().__init__(draggable=True, topbar=True)
        # DB
        self.db_path = db_path  # store path for later use
        self.setup_database()

        # Window Setup
        self.setWindowIcon(QIcon(resource_path("assets/peso.ico")))
        self.setFixedSize(520, 350)

        font = QFont("Segoe UI", 12)
        font2 = QFont("Segoe UI", 9)

        # Peso Image
        peso_img = QLabel()
        peso_img.setPixmap(QPixmap(resource_path("assets/peso.png")))
        peso_img.setFixedSize(220, 220)
        peso_img.setContentsMargins(20, 20, 20, 20)
        peso_img.setScaledContents(True)

        # User and Pass Inputs
        self.username_input = QLineEdit(placeholderText="Username")
        self.username_input.setMaxLength(10)
        self.username_input.setFont(font)
        self.username_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.password_input = QLineEdit(placeholderText="Password")
        self.password_input.setMaxLength(10)
        self.password_input.setFont(font)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Password Validation
        self.password_validator = QLabel() 
        self.password_validator.setStyleSheet("color: #ff6e6e;")
        self.password_validator.setFont(font2)
        self.password_validator.setFixedHeight(15)
        self.password_validator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Show Password Toggle
        self.showpass_chkbox = QCheckBox("Show Password")
        self.showpass_chkbox.setStyleSheet("color: white;")
        self.showpass_chkbox.setFont(font2)
        self.showpass_chkbox.clicked.connect(self.toggle_password)

        # Login Button
        login_btn = QPushButton("Login")
        login_btn.setObjectName("loginBtn")
        login_btn.setFont(font)
        login_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        login_btn.clicked.connect(self.handle_login)
        login_btn.setShortcut("Return")

        self.username_input.setObjectName("inputField")
        self.password_input.setObjectName("inputField")
        login_btn.setObjectName("buttons")

        # Layouts
        main_layout = QHBoxLayout()
        img_layout = QVBoxLayout()
        input_layout = QVBoxLayout()
        main_layout.setSpacing(30)
        input_layout.setSpacing(10)
        img_layout.setContentsMargins(20, 0, 0, 0)
        input_layout.setContentsMargins(0, 0, 20, 0)

        main_layout.addLayout(img_layout)
        main_layout.addLayout(input_layout)

        img_layout.addWidget(peso_img)
        img_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        input_layout.addWidget(self.username_input)
        input_layout.addWidget(self.password_input)
        input_layout.addWidget(self.password_validator)
        input_layout.addWidget(self.showpass_chkbox)
        input_layout.addWidget(login_btn)
        input_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.content.addLayout(main_layout)

    # Login Handling Function
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if validate_login(username, password):
            self.close()
            from ui.menu_page import MenuWindow
            menu = MenuWindow()
            menu.show()
        else:
            self.password_validator.setText("Username or Password is incorrect.")

    # Password Visibility Toggling Function
    def toggle_password(self):
        if self.showpass_chkbox.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.showpass_chkbox.setText("Hide Password")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.showpass_chkbox.setText("Show Password")

    def setup_database(self):
        """Connect to the SQLite database if db_path is provided"""
        if self.db_path:
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.cursor = self.conn.cursor()
                print(f"Connected to DB at: {self.db_path}")
            except Exception as e:
                print("Failed to connect to DB:", e)
        else:
            print("No database path provided")