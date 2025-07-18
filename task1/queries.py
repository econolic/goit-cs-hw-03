"""
Скрипт для виконання SQL запитів з файлу queries.sql
"""
import psycopg2
from typing import Optional, List, Tuple
from psycopg2.extensions import connection
import re
import os


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


def parse_sql_file(file_path: str) -> List[Tuple[str, str]]:
    """Парсить SQL файл і повертає список запитів з описами"""
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не знайдено")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Розділяємо по коментарях, що містять номери завдань
    queries = []
    
    # Шукаємо блоки коментарів та SQL запитів
    blocks = re.split(r'-- \d+\.', content)
    
    for i, block in enumerate(blocks):
        if i == 0:  # Пропускаємо заголовок файлу
            continue
            
        lines = block.strip().split('\n')
        if not lines:
            continue
            
        # Перший рядок - опис завдання
        description = f"{i}. {lines[0].strip()}"
        
        # Решта рядків - SQL запит
        sql_lines = []
        for line in lines[1:]:
            if line.strip() and not line.strip().startswith('--'):
                sql_lines.append(line)
        
        if sql_lines:
            sql_query = '\n'.join(sql_lines).strip()
            if sql_query.endswith(';'):
                sql_query = sql_query[:-1]  # Видаляємо крапку з комою
            queries.append((description, sql_query))
    
    return queries


def execute_query(cursor, query: str, description: str) -> None:
    """Виконує окремий SQL запит"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"SQL: {query}")
    print(f"{'-'*60}")
    
    try:
        cursor.execute(query)
        
        # Для UPDATE, INSERT, DELETE запитів показуємо кількість змінених рядків
        if query.strip().upper().startswith(('UPDATE', 'INSERT', 'DELETE')):
            print(f"Запит виконано. Змінено рядків: {cursor.rowcount}")
        else:
            # Для SELECT запитів показуємо результати
            results = cursor.fetchall()
            if results:
                # Отримуємо назви колонок
                if cursor.description:
                    column_names = [desc[0] for desc in cursor.description]
                    print("Результати:")
                    print(f"{'  |  '.join(column_names)}")
                    print("-" * (len("  |  ".join(column_names)) + 10))
                    
                    for row in results:
                        # Форматуємо None як 'NULL' для кращого відображення
                        formatted_row = ['NULL' if item is None else str(item) for item in row]
                        print(f"{'  |  '.join(formatted_row)}")
                    print(f"\nЗнайдено записів: {len(results)}")
                else:
                    print("Результати отримано, але немає інформації про колонки")
            else:
                print("Результати: порожня множина")
                
    except Exception as e:
        print(f"Помилка виконання запиту: {e}")


def execute_queries_from_file(sql_file_path: str = "queries.sql") -> None:
    """Виконує всі SQL запити з файлу"""
    
    # Парсимо SQL файл
    queries = parse_sql_file(sql_file_path)
    
    if not queries:
        print("Не знайдено запитів для виконання")
        return
    
    # Підключаємось до бази даних
    conn = create_connection()
    if conn is None:
        print("Не вдалося підключитися до бази даних")
        return
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        print("Виконання SQL запитів для системи управління завданнями")
        print("=" * 60)
        
        for description, query in queries:
            execute_query(cursor, query, description)
            
            # Для операцій зміни даних підтверджуємо транзакцію
            if query.strip().upper().startswith(('UPDATE', 'INSERT', 'DELETE')):
                conn.commit()
    
    except Exception as e:
        print(f"Загальна помилка: {e}")
        conn.rollback()
    finally:
        if cursor:
            cursor.close()
        conn.close()


def execute_single_query(query_number: int, sql_file_path: str = "queries.sql") -> None:
    """Виконує один конкретний SQL запит за номером"""
    
    # Парсимо SQL файл
    queries = parse_sql_file(sql_file_path)
    
    if not queries:
        print("Не знайдено запитів для виконання")
        return
    
    # Перевіряємо, чи існує запит з таким номером
    if query_number < 1 or query_number > len(queries):
        print(f"Запит з номером {query_number} не знайдено. Доступні запити: 1-{len(queries)}")
        return
    
    # Отримуємо конкретний запит (індекс на 1 менше за номер)
    description, query = queries[query_number - 1]
    
    # Підключаємось до бази даних
    conn = create_connection()
    if conn is None:
        print("Не вдалося підключитися до бази даних")
        return
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        print(f"Виконання запиту #{query_number}")
        print("=" * 60)
        
        execute_query(cursor, query, description)
        
        # Для операцій зміни даних підтверджуємо транзакцію
        if query.strip().upper().startswith(('UPDATE', 'INSERT', 'DELETE')):
            conn.commit()
    
    except Exception as e:
        print(f"Загальна помилка: {e}")
        conn.rollback()
    finally:
        if cursor:
            cursor.close()
        conn.close()


def show_available_queries(sql_file_path: str = "queries.sql") -> None:
    """Показує список доступних запитів"""
    queries = parse_sql_file(sql_file_path)
    
    if not queries:
        print("Не знайдено запитів у файлі")
        return
    
    print("\n" + "="*80)
    print("ДОСТУПНІ SQL ЗАПИТИ")
    print("="*80)
    
    for i, (description, query) in enumerate(queries, 1):
        print(f"\n{i}. {description.split('. ', 1)[1] if '. ' in description else description}")
        # Показуємо перші кілька слів SQL запиту
        query_preview = ' '.join(query.split()[:4]) + "..."
        print(f"   {query_preview}")
    
    print(f"\nДля виконання конкретного запиту використайте:")
    print(f"python queries.py <номер_запиту>")
    print(f"Наприклад: python queries.py 8")
    print(f"\nДля виконання всіх запитів:")
    print(f"python queries.py all")


def main():
    """Головна функція для обробки аргументів командного рядка"""
    import sys
    
    if len(sys.argv) == 1:
        # Якщо аргументів немає - показуємо список запитів
        show_available_queries()
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        
        if arg.lower() in ['all', 'всі', 'все']:
            # Виконуємо всі запити
            execute_queries_from_file()
        else:
            try:
                # Якщо є один аргумент - виконуємо конкретний запит
                query_number = int(arg)
                execute_single_query(query_number)
            except ValueError:
                print("Помилка: Номер запиту має бути цілим числом")
                print("Використання: python queries.py <номер_запиту>")
    else:
        print("Використання:")
        print("  python queries.py                 - показати список запитів")
        print("  python queries.py <номер_запиту>  - виконати конкретний запит")
        print("  python queries.py all             - виконати всі запити")


if __name__ == "__main__":
    main()
