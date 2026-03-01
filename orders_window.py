import sys
import sqlite3
import os
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox, 
                             QMessageBox, QListWidget, QListWidgetItem,
                             QFrame)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt

DB_PATH = r"shop.db"

class OrderItemWidget(QFrame):
    def __init__(self, order_data):
        super().__init__()
        # order_data: id, date, delivery_date, pickup_point_id, user_fullname, receipt_code, status
        self.order_id, self.date, self.delivery_date, \
        self.pickup_point, self.user_name, self.receipt_code, self.status = order_data
        
        self.setStyleSheet("background-color: #FFFFFF; border: 1px solid gray;")
        
        layout = QHBoxLayout()
        
        details_layout = QVBoxLayout()
        details_layout.addWidget(QLabel(f"<b>Заказ №{self.order_id}</b>"))
        details_layout.addWidget(QLabel(f"Дата: {self.date} | Доставка: {self.delivery_date}"))
        details_layout.addWidget(QLabel(f"ФИО клиента: {self.user_name if self.user_name else 'Гость'}"))
        details_layout.addWidget(QLabel(f"Пункт выдачи: {self.pickup_point}"))
        
        layout.addLayout(details_layout)
        
        status_layout = QVBoxLayout()
        status_lbl = QLabel(f"Статус:\n{self.status}")
        status_lbl.setAlignment(Qt.AlignCenter)
        if self.status == "Новый":
            status_lbl.setStyleSheet("color: green; font-weight: bold; border: none;")
        elif self.status == "Завершен":
            status_lbl.setStyleSheet("color: gray; font-weight: bold; border: none;")
        else:
            status_lbl.setStyleSheet("font-weight: bold; border: none;")
        status_layout.addWidget(status_lbl)
        
        layout.addLayout(status_layout)
        self.setLayout(layout)

class OrderEditDialog(QDialog):
    def __init__(self, order_data=None):
        super().__init__()
        self.order_data = order_data
        title = "Редактирование заказа" if order_data else "Добавление заказа"
        self.setWindowTitle(title)
        self.resize(300, 400)
        self.setStyleSheet("""
            QWidget { background-color: #FFFFFF; font-family: 'Times New Roman'; font-size: 14pt; }
            QPushButton { background-color: #7FFF00; border: 1px solid gray; padding: 5px; }
            QPushButton#ActionBtn { background-color: #00FA9A; font-weight: bold; }
        """)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.inputs = {}
        fields = [
            ("Номер заказа", 0, True),
            ("Дата заказа", 1, False),
            ("Дата доставки", 2, False),
            ("ID пункта выдачи", 3, False),
            ("ФИО клиента", 4, False),
            ("Код получения", 5, False),
            ("Статус", 6, False)
        ]
        
        for name, idx, is_pk in fields:
            lbl = QLabel(name)
            inp = QLineEdit()
            if self.order_data and idx < len(self.order_data):
                inp.setText(str(self.order_data[idx]))
            if is_pk and self.order_data:
                inp.setReadOnly(True)
                inp.setStyleSheet("background-color: #e0e0e0;")
                
            self.inputs[name] = inp
            layout.addWidget(lbl)
            layout.addWidget(inp)
            
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
        
    def save_data(self):
        order_id = self.inputs["Номер заказа"].text().strip()
        date = self.inputs["Дата заказа"].text().strip()
        delivery = self.inputs["Дата доставки"].text().strip()
        pickup = self.inputs["ID пункта выдачи"].text().strip()
        status = self.inputs["Статус"].text().strip()
        
        if not all([order_id, date, delivery, pickup, status]):
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля!")
            return
            
        try:
            order_id = int(order_id)
            pickup = int(pickup)
            code = int(self.inputs["Код получения"].text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат числовых полей")
            return
            
        fn = self.inputs["ФИО клиента"].text().strip()
        
        data = (date, delivery, pickup, fn, code, status, order_id)
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            if self.order_data:
                cur.execute('''
                UPDATE "Order" SET date=?, delivery_date=?, pickup_point_id=?, 
                user_fullname=?, receipt_code=?, status=? WHERE id=?
                ''', data)
            else:
                ins_data = (order_id,) + data[:-1]
                cur.execute('''
                INSERT INTO "Order" (id, date, delivery_date, pickup_point_id, user_fullname, receipt_code, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', ins_data)
                
            conn.commit()
            conn.close()
            self.accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", f"Заказ с номером {order_id} уже существует!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))

class OrdersWindow(QWidget):
    def __init__(self, role="Менеджер"):
        super().__init__()
        self.role = role
        self.setWindowTitle("ООО Обувь - Заказы")
        self.resize(800, 600)
        self.setStyleSheet("""
            QWidget { background-color: #FFFFFF; font-family: 'Times New Roman'; font-size: 14pt; }
            QPushButton { background-color: #7FFF00; border: 1px solid gray; padding: 5px; }
            QPushButton:hover { background-color: #8FFF10; }
        """)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(f"Заказы - Роль: {self.role}"))
        header_layout.addStretch()
        btn_back = QPushButton("Закрыть")
        btn_back.clicked.connect(self.close)
        header_layout.addWidget(btn_back)
        layout.addLayout(header_layout)
        
        if self.role == "Администратор":
            admin_layout = QHBoxLayout()
            btn_add = QPushButton("Добавить заказ")
            btn_add.clicked.connect(self.add_order)
            btn_edit = QPushButton("Редактировать заказ")
            btn_edit.clicked.connect(self.edit_order)
            btn_del = QPushButton("Удалить заказ")
            btn_del.clicked.connect(self.delete_order)
            admin_layout.addWidget(btn_add)
            admin_layout.addWidget(btn_edit)
            admin_layout.addWidget(btn_del)
            layout.addLayout(admin_layout)
            
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        self.setLayout(layout)
        
    def load_data(self):
        self.list_widget.clear()
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT * FROM \"Order\"")
            orders = cur.fetchall()
            conn.close()
            
            for ord_data in orders:
                item_widget = OrderItemWidget(ord_data)
                list_item = QListWidgetItem(self.list_widget)
                list_item.setData(Qt.UserRole, ord_data)
                list_item.setSizeHint(item_widget.sizeHint())
                self.list_widget.addItem(list_item)
                self.list_widget.setItemWidget(list_item, item_widget)
        except Exception as e:
            print("Error loading orders:", e)

    def add_order(self):
        d = OrderEditDialog()
        if d.exec_() == QDialog.Accepted:
            self.load_data()
            
    def edit_order(self):
        sel = self.list_widget.currentItem()
        if not sel: return
        d = OrderEditDialog(sel.data(Qt.UserRole))
        if d.exec_() == QDialog.Accepted:
            self.load_data()
            
    def delete_order(self):
        sel = self.list_widget.currentItem()
        if not sel: return
        order_data = sel.data(Qt.UserRole)
        oid = order_data[0]
        
        reply = QMessageBox.question(self, "Удаление", f"Удалить заказ №{oid}?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("DELETE FROM OrderProduct WHERE order_id=?", (oid,))
                cur.execute("DELETE FROM \"Order\" WHERE id=?", (oid,))
                conn.commit()
                conn.close()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))
