"""
Скрипт для заповнення бази даних тестовими даними
"""
import psycopg2
import random
from typing import Optional, List, Tuple, Union
from faker import Faker
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


def seed_database() -> None:
    """Заповнює таблиці випадковими даними"""
    fake = Faker(['uk_UA'])  # Українська локалізація
    
    conn = create_connection()
    if conn is None:
        print("Не вдалося підключитися до бази даних")
        return
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Очищуємо таблиці перед заповненням (у правильному порядку)
        print("Очищення існуючих даних...")
        cursor.execute("DELETE FROM tasks;")
        cursor.execute("DELETE FROM users;")
        
        # Генеруємо та вставляємо користувачів
        print("Створення користувачів...")
        users_data: List[Tuple[str, str]] = []
        for i in range(10):
            fullname = fake.name()
            email = fake.unique.email()
            users_data.append((fullname, email))
        
        cursor.executemany(
            "INSERT INTO users (fullname, email) VALUES (%s, %s);",
            users_data
        )
        
        # Отримуємо ID користувачів
        cursor.execute("SELECT id FROM users;")
        user_ids: List[int] = [row[0] for row in cursor.fetchall()]
        
        # Отримуємо ID статусів
        cursor.execute("SELECT id FROM status;")
        status_ids: List[int] = [row[0] for row in cursor.fetchall()]
        
        # Генеруємо та вставляємо завдання
        print("Створення завдань...")
        tasks_data: List[Tuple[str, Optional[str], int, int]] = []
        for i in range(30):
            title = fake.sentence(nb_words=4).rstrip('.')
            description: Optional[str] = fake.text(max_nb_chars=200) if random.choice([True, False, True]) else None
            status_id = random.choice(status_ids)
            user_id = random.choice(user_ids)
            tasks_data.append((title, description, status_id, user_id))
        
        cursor.executemany(
            "INSERT INTO tasks (title, description, status_id, user_id) VALUES (%s, %s, %s, %s);",
            tasks_data
        )
        
        # Підтверджуємо зміни
        conn.commit()
        print(f"База даних успішно заповнена!")
        print(f"Створено {len(users_data)} користувачів та {len(tasks_data)} завдань")
        
        # Показуємо статистику
        cursor.execute("""
            SELECT s.name, COUNT(t.id) as task_count 
            FROM status s 
            LEFT JOIN tasks t ON s.id = t.status_id 
            GROUP BY s.id, s.name 
            ORDER BY s.id;
        """)
        print("\nСтатистика завдань за статусами:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} завдань")
        
    except Exception as e:
        print(f"Помилка при заповненні бази даних: {e}")
        conn.rollback()
    finally:
        if cursor:
            cursor.close()
        conn.close()


if __name__ == "__main__":
    seed_database()
