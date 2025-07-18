"""
Скрипт для створення таблиць бази даних
"""
import psycopg2
from typing import Optional
from psycopg2.extensions import connection


def create_connection() -> Optional[connection]:
    """Створює з'єднання з базою даних PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="task_management",
            user="postgres",
            password="password",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Помилка підключення до бази даних: {e}")
        return None


def create_tables() -> None:
    """Створює таблиці у базі даних"""
    
    # SQL для створення таблиці users
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        fullname VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL
    );
    """
    
    # SQL для створення таблиці status
    create_status_table = """
    CREATE TABLE IF NOT EXISTS status (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL
    );
    """
    
    # SQL для створення таблиці tasks
    create_tasks_table = """
    CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        description TEXT,
        status_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (status_id) REFERENCES status(id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    
    # SQL для заповнення таблиці status початковими значеннями
    insert_default_statuses = """
    INSERT INTO status (name) VALUES 
        ('new'),
        ('in progress'),
        ('completed')
    ON CONFLICT (name) DO NOTHING;
    """
    
    conn = create_connection()
    if conn is None:
        print("Не вдалося підключитися до бази даних")
        return
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Створюємо таблиці
        print("Створення таблиці users...")
        cursor.execute(create_users_table)
        
        print("Створення таблиці status...")
        cursor.execute(create_status_table)
        
        print("Створення таблиці tasks...")
        cursor.execute(create_tasks_table)
        
        # Додаємо базові статуси
        print("Додавання базових статусів...")
        cursor.execute(insert_default_statuses)
        
        # Підтверджуємо зміни
        conn.commit()
        print("Таблиці успішно створені!")
        
    except Exception as e:
        print(f"Помилка при створенні таблиць: {e}")
        conn.rollback()
    finally:
        if cursor:
            cursor.close()
        conn.close()


if __name__ == "__main__":
    create_tables()
