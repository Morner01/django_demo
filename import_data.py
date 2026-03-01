import sqlite3
import pandas as pd
import os

base_dir = r"Прил_ОЗ_КОД 09.02.07-2-2026 (2)\╨Я╤А╨╕╨╗_╨Ю╨Ч_╨Ъ╨Ю╨Ф 09.02.07-2-2026\╨С╨г\╨Ь╨╛╨┤╤Г╨╗╤М 1\import"

def create_db():
    conn = sqlite3.connect(r"shop.db")
    cursor = conn.cursor()

    cursor.executescript('''
    DROP TABLE IF EXISTS OrderProduct;
    DROP TABLE IF EXISTS "Order";
    DROP TABLE IF EXISTS Product;
    DROP TABLE IF EXISTS User;
    DROP TABLE IF EXISTS Role;
    DROP TABLE IF EXISTS PickupPoint;

    CREATE TABLE Role (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        login TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role_id INTEGER,
        FOREIGN KEY (role_id) REFERENCES Role(id)
    );

    CREATE TABLE Product (
        article TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        unit TEXT NOT NULL,
        price REAL NOT NULL,
        supplier TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        category TEXT NOT NULL,
        discount INTEGER DEFAULT 0,
        quantity INTEGER DEFAULT 0,
        description TEXT,
        image TEXT
    );

    CREATE TABLE PickupPoint (
        id INTEGER PRIMARY KEY,
        address TEXT NOT NULL
    );

    CREATE TABLE "Order" (
        id INTEGER PRIMARY KEY,
        date TEXT NOT NULL,
        delivery_date TEXT NOT NULL,
        pickup_point_id INTEGER,
        user_fullname TEXT,
        receipt_code INTEGER,
        status TEXT,
        FOREIGN KEY (pickup_point_id) REFERENCES PickupPoint(id)
    );

    CREATE TABLE OrderProduct (
        order_id INTEGER,
        product_article TEXT,
        count INTEGER,
        FOREIGN KEY (order_id) REFERENCES "Order"(id),
        FOREIGN KEY (product_article) REFERENCES Product(article),
        PRIMARY KEY (order_id, product_article)
    );
    ''')
    conn.commit()
    return conn

def import_data(conn):
    cursor = conn.cursor()

    # 1. Товар
    df_tovar = pd.read_excel(os.path.join(base_dir, "Tovar.xlsx"))
    for _, row in df_tovar.iterrows():
        cursor.execute('''
        INSERT INTO Product (article, name, unit, price, supplier, manufacturer, category, discount, quantity, description, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row['Артикул'], row['Наименование товара'], row['Единица измерения'], row['Цена'], 
              row['Поставщик'], row['Производитель'], row['Категория товара'], row.get('Действующая скидка', 0), 
              row.get('Кол-во на складе', 0), row.get('Описание товара', ''), row.get('Фото', '')))

    # 2. Роли и Пользователи
    df_user = pd.read_excel(os.path.join(base_dir, "user_import.xlsx"))
    roles = df_user['Роль сотрудника'].unique()
    for role in roles:
        # Avoid duplication
        cursor.execute('INSERT OR IGNORE INTO Role (name) VALUES (?)', (role,))
    
    for _, row in df_user.iterrows():
        cursor.execute('SELECT id FROM Role WHERE name = ?', (row['Роль сотрудника'],))
        role_id = cursor.fetchone()[0]
        cursor.execute('''
        INSERT INTO User (fullname, login, password, role_id)
        VALUES (?, ?, ?, ?)
        ''', (row['ФИО'], row['Логин'], str(row['Пароль']), role_id))

    # 3. Пункты выдачи (no header)
    df_pickup = pd.read_excel(os.path.join(base_dir, "╨Я╤Г╨╜╨║╤В╤Л ╨▓╤Л╨┤╨░╤З╨╕_import.xlsx"), header=None)
    for idx, row in df_pickup.iterrows():
        address = str(row[0]).strip()
        cursor.execute('INSERT INTO PickupPoint (id, address) VALUES (?, ?)', (idx + 1, address))

    # 4. Заказы
    df_order = pd.read_excel(os.path.join(base_dir, "╨Ч╨░╨║╨░╨╖_import.xlsx"))
    for _, row in df_order.iterrows():
        user_fn = row.get('ФИО авторизированного клиента', None)
        if pd.isna(user_fn):
            user_fn = ""
            
        cursor.execute('''
        INSERT INTO "Order" (id, date, delivery_date, pickup_point_id, user_fullname, receipt_code, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (row['Номер заказа'], str(row['Дата заказа']), str(row['Дата доставки']), 
              row['Адрес пункта выдачи'], user_fn, row['Код для получения'], row['Статус заказа']))
              
        # Parse products (Артикул заказа) -> list "Артикул, кол-во, Артикул, кол-во"
        products_str = str(row['Артикул заказа']).replace(' ', '')
        parts = products_str.split(',')
        order_id = row['Номер заказа']
        
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                art = parts[i]
                cnt = int(parts[i+1])
                try:
                    cursor.execute('''
                    INSERT INTO OrderProduct (order_id, product_article, count)
                    VALUES (?, ?, ?)
                    ''', (order_id, art, cnt))
                except sqlite3.IntegrityError:
                    pass

    conn.commit()
    print("Импорт завершен успешно!")

if __name__ == '__main__':
    conn = create_db()
    import_data(conn)
    conn.close()
