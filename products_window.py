import sys
import sqlite3
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox, 
                             QListWidget, QListWidgetItem, QGridLayout,
                             QScrollArea, QFrame, QMessageBox)
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize

from admin_products_window import ProductEditDialog
from orders_window import OrdersWindow

BASE_DIR = r"Прил_ОЗ_КОД 09.02.07-2-2026 (2)\╨Я╤А╨╕╨╗_╨Ю╨Ч_╨Ъ╨Ю╨Ф 09.02.07-2-2026\╨С╨г\╨Ь╨╛╨┤╤Г╨╗╤М 1\import"
LOGO_PATH = os.path.join(BASE_DIR, "picture.png")
ICON_PATH = os.path.join(BASE_DIR, "Icon.png")
DB_PATH = r"shop.db"

class ProductItemWidget(QFrame):
    def __init__(self, product_data):
        super().__init__()
        # product_data: article, name, unit, price, supplier, manufacturer, category, discount, quantity, description, image
        self.article, self.name, self.unit, self.price, \
        self.supplier, self.manufacturer, self.category, \
        self.discount, self.quantity, self.description, self.image = product_data
        
        # Apply discount color
        self.discount = int(self.discount) if self.discount else 0
        if self.discount > 15:
            self.setStyleSheet("background-color: #2E8B57; border: 1px solid gray;")
        else:
            self.setStyleSheet("background-color: #FFFFFF; border: 1px solid gray;")
            
        layout = QHBoxLayout()
        
        # Image
        self.img_label = QLabel()
        img_full_path = os.path.join(BASE_DIR, str(self.image) if self.image else "")
        if os.path.exists(img_full_path) and str(self.image) != "nan" and str(self.image) != "":
            pixmap = QPixmap(img_full_path)
            if not pixmap.isNull():
                self.img_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.img_label.setText("Нет фото")
        else:
            self.img_label.setText("Нет фото")
        self.img_label.setFixedSize(100, 100)
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("border: none; background-color: transparent;")
        layout.addWidget(self.img_label)
        
        # Details
        details_layout = QVBoxLayout()
        name_lbl = QLabel(f"<b>{self.name}</b>")
        name_lbl.setStyleSheet("border: none; background-color: transparent; font-size: 16pt;")
        details_layout.addWidget(name_lbl)
        
        desc_lbl = QLabel(f"{self.description}")
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("border: none; background-color: transparent;")
        details_layout.addWidget(desc_lbl)
        
        info_lbl = QLabel(f"Производитель: {self.manufacturer} | Цена: {self.price} руб.")
        info_lbl.setStyleSheet("border: none; background-color: transparent;")
        details_layout.addWidget(info_lbl)
        
        layout.addLayout(details_layout)
        
        # Discount
        discount_lbl = QLabel(f"Скидка {self.discount}%")
        discount_lbl.setAlignment(Qt.AlignCenter)
        discount_lbl.setStyleSheet("border: none; background-color: transparent; font-weight: bold;")
        layout.addWidget(discount_lbl)
        
        self.setLayout(layout)

class ProductsWindow(QWidget):
    def __init__(self, role="Гость", fullname="Гость"):
        super().__init__()
        self.role = role
        self.fullname = fullname
        self.setWindowTitle("ООО Обувь - Товары")
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
            
        self.resize(800, 600)
        self.setStyleSheet("""
            QWidget { background-color: #FFFFFF; font-family: 'Times New Roman'; font-size: 14pt; }
            QPushButton { background-color: #7FFF00; border: 1px solid gray; padding: 5px; }
            QPushButton:hover { background-color: #8FFF10; }
        """)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Header (Logo, FIO, Back)
        header_layout = QHBoxLayout()
        logo_lbl = QLabel()
        if os.path.exists(LOGO_PATH):
            pixmap = QPixmap(LOGO_PATH).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pixmap)
        header_layout.addWidget(logo_lbl)
        
        user_lbl = QLabel(f"{self.fullname} ({self.role})")
        header_layout.addWidget(user_lbl)
        
        header_layout.addStretch()
        
        btn_back = QPushButton("Выход")
        btn_back.clicked.connect(self.close)
        header_layout.addWidget(btn_back)
        
        main_layout.addLayout(header_layout)
        
        # Controls (Manager, Admin only)
        if self.role in ["Менеджер", "Администратор"]:
            controls_layout = QHBoxLayout()
            
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Поиск...")
            self.search_input.textChanged.connect(self.load_data)
            controls_layout.addWidget(self.search_input)
            
            self.sort_combo = QComboBox()
            self.sort_combo.addItems(["Сортировка", "По возрастанию цены", "По убыванию цены"])
            self.sort_combo.currentIndexChanged.connect(self.load_data)
            controls_layout.addWidget(self.sort_combo)
            
            self.filter_combo = QComboBox()
            self.filter_combo.addItems(["Все производители"])
            self.load_manufacturers()
            self.filter_combo.currentIndexChanged.connect(self.load_data)
            controls_layout.addWidget(self.filter_combo)
            
            main_layout.addLayout(controls_layout)
            
        # Admin controls
        if self.role == "Администратор":
            admin_layout = QHBoxLayout()
            btn_add = QPushButton("Добавить товар")
            btn_add.clicked.connect(self.add_product)
            btn_edit = QPushButton("Редактировать товар")
            btn_edit.clicked.connect(self.edit_product)
            btn_del = QPushButton("Удалить товар")
            btn_del.clicked.connect(self.delete_product)
            admin_layout.addWidget(btn_add)
            admin_layout.addWidget(btn_edit)
            admin_layout.addWidget(btn_del)
            main_layout.addLayout(admin_layout)
            
        # Manager/Admin Orders
        if self.role in ["Менеджер", "Администратор"]:
            orders_layout = QHBoxLayout()
            btn_orders = QPushButton("Управление заказами")
            btn_orders.clicked.connect(self.open_orders)
            orders_layout.addWidget(btn_orders)
            main_layout.addLayout(orders_layout)
            
        # List products
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)
        
        self.count_lbl = QLabel("Отображено: 0 из 0")
        main_layout.addWidget(self.count_lbl)
        
        self.setLayout(main_layout)
        
    def load_manufacturers(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT manufacturer FROM Product")
            mans = [row[0] for row in cur.fetchall()]
            self.filter_combo.addItems(mans)
            conn.close()
        except Exception as e:
            print("Error loading manufacturers:", e)
            
    def load_data(self):
        self.list_widget.clear()
        query = "SELECT * FROM Product WHERE 1=1"
        params = []
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # Count total
            cur.execute("SELECT COUNT(*) FROM Product")
            total_count = cur.fetchone()[0]
            
            if self.role in ["Менеджер", "Администратор"]:
                search_text = self.search_input.text().strip()
                if search_text:
                    query += " AND (name LIKE ? OR description LIKE ? OR manufacturer LIKE ? OR price LIKE ?)"
                    p = f"%{search_text}%"
                    params.extend([p, p, p, p])
                    
                filter_val = self.filter_combo.currentText()
                if filter_val != "Все производители":
                    query += " AND manufacturer=?"
                    params.append(filter_val)
                    
                sort_idx = self.sort_combo.currentIndex()
                if sort_idx == 1:
                    query += " ORDER BY price ASC"
                elif sort_idx == 2:
                    query += " ORDER BY price DESC"
                    
            cur.execute(query, params)
            products = cur.fetchall()
            conn.close()
            
            self.count_lbl.setText(f"Отображено: {len(products)} из {total_count}")
            
            for prod in products:
                item_widget = ProductItemWidget(prod)
                list_item = QListWidgetItem(self.list_widget)
                # Store product data in data role for easy access
                list_item.setData(Qt.UserRole, prod) 
                list_item.setSizeHint(item_widget.sizeHint())
                self.list_widget.addItem(list_item)
                self.list_widget.setItemWidget(list_item, item_widget)
                
        except Exception as e:
            print("Error loading products:", e)

    def add_product(self):
        dialog = ProductEditDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()
            
    def edit_product(self):
        selected = self.list_widget.currentItem()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите товар для редактирования!")
            return
            
        prod_data = selected.data(Qt.UserRole)
        dialog = ProductEditDialog(prod_data)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()
            
    def delete_product(self):
        selected = self.list_widget.currentItem()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите товар для удаления!")
            return
            
        prod_data = selected.data(Qt.UserRole)
        article = prod_data[0]
        name = prod_data[1]
        
        reply = QMessageBox.question(self, "Подтверждение", f"Вы уверены, что хотите удалить товар '{name}' ({article})?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                # Check for orders referencing this product (OrderProduct table)
                cur.execute("SELECT COUNT(*) FROM OrderProduct WHERE product_article=?", (article,))
                if cur.fetchone()[0] > 0:
                    QMessageBox.warning(self, "Ошибка", "Невозможно удалить товар, так как он присутствует в заказах!")
                    conn.close()
                    return
                    
                cur.execute("DELETE FROM Product WHERE article=?", (article,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Успех", "Товар успешно удален!")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))
                
    def open_orders(self):
        self.orders_wnd = OrdersWindow(role=self.role)
        self.orders_wnd.show()
