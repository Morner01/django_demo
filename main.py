import sys
import sqlite3
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

from products_window import ProductsWindow

# Pathways to resources
BASE_DIR = r"Прил_ОЗ_КОД 09.02.07-2-2026 (2)\╨Я╤А╨╕╨╗_╨Ю╨Ч_╨Ъ╨Ю╨Ф 09.02.07-2-2026\╨С╨г\╨Ь╨╛╨┤╤Г╨╗╤М 1\import"
ICON_PATH = os.path.join(BASE_DIR, "Icon.png")
LOGO_PATH = os.path.join(BASE_DIR, "picture.png")  # Wait, let's use Icon.png for now if picture not found, but find showed it exists
DB_PATH = r"shop.db"

# Global Stylesheet according to the task
STYLESHEET = """
QWidget {
    background-color: #FFFFFF;
    font-family: 'Times New Roman';
    font-size: 14pt;
}
QLineEdit {
    border: 1px solid gray;
    padding: 5px;
    background-color: #FFFFFF;
}
QPushButton {
    background-color: #7FFF00;
    border: 1px solid gray;
    border-radius: 5px;
    padding: 8px;
    min-width: 150px;
}
QPushButton:hover {
    background-color: #8FFF10;
}
QPushButton#ActionBtn {
    background-color: #00FA9A;
    font-weight: bold;
}
QPushButton#ActionBtn:hover {
    background-color: #10FAA0;
}
"""

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ООО Обувь - Авторизация")
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
            
        self.resize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Logo
        if os.path.exists(LOGO_PATH):
            self.logo_label = QLabel()
            pixmap = QPixmap(LOGO_PATH)
            # Resize pixmap preserving aspect ratio
            pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
            self.logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.logo_label)
        
        # Inputs
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        layout.addWidget(self.login_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # Login Button
        self.btn_login = QPushButton("Войти")
        self.btn_login.setObjectName("ActionBtn")
        self.btn_login.clicked.connect(self.handle_login)
        layout.addWidget(self.btn_login)
        
        # Guest Button
        self.btn_guest = QPushButton("Войти как гость")
        self.btn_guest.clicked.connect(self.handle_guest)
        layout.addWidget(self.btn_guest)
        
        self.setLayout(layout)
        
    def handle_login(self):
        login = self.login_input.text().strip()
        pwd = self.password_input.text().strip()
        
        if not login or not pwd:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля.")
            return
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                SELECT User.id, User.fullname, Role.name 
                FROM User 
                JOIN Role ON User.role_id = Role.id 
                WHERE login=? AND password=?
            """, (login, pwd))
            user = cur.fetchone()
            conn.close()
            
            if user:
                user_id, fullname, role = user
                QMessageBox.information(self, "Успех", f"Добро пожаловать, {fullname}!\nРоль: {role}")
                self.open_main_window(role=role, user_id=user_id, fullname=fullname)
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))

    def handle_guest(self):
        self.open_main_window(role="Гость")
        
    def open_main_window(self, role, user_id=None, fullname=None):
        if not fullname:
            fullname = "Гость"
        self.main_wnd = ProductsWindow(role=role, fullname=fullname)
        self.main_wnd.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec_())
