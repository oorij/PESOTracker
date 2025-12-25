import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.login_page import LoginWindow
from utils.helpers import resource_path
# from ui.menu_page import MenuWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    stylesheet_path = resource_path("assets/styles.qss")
    with open(stylesheet_path, "r") as f:
        app.setStyleSheet(f.read())

    db_path = resource_path("assets/database.db")
    print("Database path:", db_path)

    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
