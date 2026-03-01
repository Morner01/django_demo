import sys
import sqlite3
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox, 
                             QMessageBox, QFileDialog)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

DB_PATH = r"shop.db"

class ProductEditDialog(QDialog):
    def __init__(self, product_data=None):
        super().__init__()
        # product_data: article, name, unit, price, supplier, manufacturer, category, discount, quantity, description, image
        self.product_data = product_data
        title = "Редактирование товара" if product_data else "Добавление товара"
        self.setWindowTitle(title)
        self.resize(400, 500)
        self.setStyleSheet("""
            QWidget { background-color: #FFFFFF; font-family: 'Times New Roman'; font-size: 14pt; }
            QPushButton { background-color: #7FFF00; border: 1px solid gray; padding: 5px; }
            QPushButton#ActionBtn { background-color: #00FA9A; font-weight: bold; }
        """)
        self.image_path = product_data[10] if (product_data and len(product_data) > 10) else ""
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Fields
        self.inputs = {}
        fields = [
            ("Артикул", 0, True),
            ("Наименование", 1, False),
            ("Единица измерения", 2, False),
            ("Цена", 3, False),
            ("Поставщик", 4, False),
            ("Производитель", 5, False),
            ("Категория", 6, False),
            ("Скидка (%)", 7, False),
            ("Кол-во на складе", 8, False),
            ("Описание", 9, False)
        ]
        
        for name, idx, is_pk in fields:
            lbl = QLabel(name)
            inp = QLineEdit()
            if self.product_data and idx < len(self.product_data):
                inp.setText(str(self.product_data[idx]))
            if is_pk and self.product_data:
                inp.setReadOnly(True)  # Cannot change PK
                inp.setStyleSheet("background-color: #e0e0e0;")
            
            self.inputs[name] = inp
            layout.addWidget(lbl)
            layout.addWidget(inp)
            
        # Image
        img_layout = QHBoxLayout()
        self.lbl_img = QLabel(self.image_path if self.image_path else "Нет фото")
        btn_img = QPushButton("Выбрать фото")
        btn_img.clicked.connect(self.select_image)
        img_layout.addWidget(self.lbl_img)
        img_layout.addWidget(btn_img)
        layout.addLayout(img_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Сохранить")
        self.btn_save.setObjectName("ActionBtn")
        self.btn_save.clicked.connect(self.save_data)
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите картинку", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.image_path = os.path.basename(path)
            self.lbl_img.setText(self.image_path)
            
    def save_data(self):
        # Validate required fields
        article = self.inputs["Артикул"].text().strip()
        name = self.inputs["Наименование"].text().strip()
        unit = self.inputs["Единица измерения"].text().strip()
        price = self.inputs["Цена"].text().strip()
        
        if not all([article, name, unit, price]):
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля: Артикул, Наименование, Ед.изм, Цена")
            return
            
        try:
            price = float(price)
            discount = int(self.inputs["Скидка (%)"].text() or 0)
            qty = int(self.inputs["Кол-во на складе"].text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат числовых полей")
            return
            
        data = (
            name, unit, price,
            self.inputs["Поставщик"].text().strip(),
            self.inputs["Производитель"].text().strip(),
            self.inputs["Категория"].text().strip(),
            discount, qty,
            self.inputs["Описание"].text().strip(),
            self.image_path,
            article
        )
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            if self.product_data:
                # Update
                cur.execute('''
                UPDATE Product SET name=?, unit=?, price=?, supplier=?, manufacturer=?, category=?,
                discount=?, quantity=?, description=?, image=? WHERE article=?
                ''', data)
            else:
                # Insert
                # Reorder data for insert (article is first)
                ins_data = (article,) + data[:-1]
                cur.execute('''
                INSERT INTO Product (article, name, unit, price, supplier, manufacturer, category, discount, quantity, description, image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', ins_data)
                
            conn.commit()
            conn.close()
            self.accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", f"Товар с артикулом {article} уже существует!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))
