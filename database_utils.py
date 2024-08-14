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

    sql = """
    INSERT INTO Products (name, image, price, class)
    VALUES
       ('Colab Riki&Morty', 'static/images/pullover6.jpeg', 85.00, 'Pullover');
        
       
    """

    try:
        cursor.execute(sql)
        conn.commit()
        print("Дані успішно додані до таблиці Products.")
    except Exception as e:
        print(f"Помилка при додаванні даних: {e}")
        conn.rollback()
    finally:
        cursor.close()

def delete_product_by_id(product_id):
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=ProductsDB;Trusted_Connection=yes;')
        cursor = conn.cursor()
        
        # SQL-запрос для удаления элемента с указанным ID
        cursor.execute("DELETE FROM Products WHERE ID = ?", product_id)
        
        conn.commit()
        print(f"Элемент с ID {product_id} успешно удален.")
    
    except pyodbc.Error as e:
        print("Ошибка при выполнении SQL-запроса:", e)
    finally:
        cursor.close()


if connection:
    print("Подключение к базе данных MSSQL успешно установлено.")
    # insert_products(connection)
    # delete_product_by_id(6002)
    # delete_product_by_id(6003)
    # delete_product_by_id(6014)
    # delete_product_by_id(6016)
    print_all_products(connection)
    connection.close()
else:
    print("Не удалось установить подключение к базе данных MSSQL.")
