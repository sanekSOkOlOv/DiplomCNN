import json
import pyodbc
import requests


# ------------------------------Раздел БД----------------------------------
#(localdb)\MSSQLLocalDB


def connect_to_mssql():
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=ProductsDB;Trusted_Connection=yes;')
    return conn

connection = connect_to_mssql()

def print_all_products(conn):
    cursor = conn.cursor()

    #  SQL-запрос для выборки всех данных из таблицы Products
    sql = "SELECT * FROM Products;"

    try:
        cursor.execute(sql)
        rows = cursor.fetchall()  # Получаем все строки результата запроса

        # Перебираем каждую строку и выводим ID с данными
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Image: {row[2]}, Price: {row[3]}, Class: {row[4]}")


    except Exception as e:
        print(f"Ошибка при выполнении SQL-запроса: {e}")
    finally:
        cursor.close()

# classes = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
#                'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

def insert_products(conn):
    cursor = conn.cursor()

    # SQL-запрос для добавления данных
    sql = """
    INSERT INTO Products (name, image, price, class)
    VALUES
        ('Big Baby Bag', 'static/images/Backpage1.jpeg', 25.99, 'Bag'),
        ('Pullover Dragon King', 'static/images/switer1.jpeg', 40.00, 'Pullover'),
        ('Kargo Mini', 'static/images/pullover2.jpeg', 24.99, 'Pullover'),
        ('Kargo Mini', 'static/images/Trouser4.jpeg', 22.99, 'Trouser'),
        ('Kagro Top', 'static/images/Trouser3.jpeg', 24.99, 'Trouser'),
        ('Classic Sport', 'static/images/Trouser2.jpeg', 19.00, 'Trouser'),
        ('Kargo ZED', 'static/images/Trouser1.jpeg', 24.99, 'Trouser'),
        ('T-Short Logo', 'static/images/Tshortlogo.jpeg', 20.99, 'T-shirt/top'),
        ('T-Short Tend', 'static/images/Tshortend.jpeg', 20.99, 'T-shirt/top'),
        ('T-Short Blue', 'static/images/Tshortblue.jpeg', 20.99, 'T-shirt/top');
        
       
    """

    try:
        cursor.execute(sql)
        conn.commit()
        print("Данные успешно добавлены в таблицу Products.")
    except Exception as e:
        print(f"Ошибка при добавлении данных: {e}")
        conn.rollback()
    finally:
        cursor.close()

def delete_product_by_id(product_id):
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=ProductsDB;Trusted_Connection=yes;')
        cursor = conn.cursor()
        
        # SQL-запрос для удаления элемента с указанным ID
        cursor.execute("DELETE FROM Products WHERE ID = ?", product_id)
        
        # Подтверждаем транзакцию
        conn.commit()
        print(f"Элемент с ID {product_id} успешно удален.")
    
    except pyodbc.Error as e:
        print("Ошибка при выполнении SQL-запроса:", e)
    finally:
        cursor.close()


if connection:
    print("Подключение к базе данных MSSQL успешно установлено.")
    # insert_products(connection)
    # delete_product_by_id(4003)
    print_all_products(connection)
    connection.close()
else:
    print("Не удалось установить подключение к базе данных MSSQL.")
