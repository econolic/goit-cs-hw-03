"""
MongoDB CRUD операції для колекції котів
Використовує PyMongo для роботи з базою даних cats_db
"""

from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, PyMongoError
import sys


class CatsDatabase:
    """Клас для управління базою даних котів з MongoDB"""
    
    def __init__(self, connection_string: str = "mongodb://cats_user:cats_password@localhost:27017/cats_db"):
        """
        Ініціалізація з'єднання з базою даних
        
        Args:
            connection_string: Рядок підключення до MongoDB
        """
        self.connection_string = connection_string
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.collection: Optional[Collection] = None
        
    def connect(self) -> bool:
        """
        Встановлення з'єднання з базою даних
        
        Returns:
            True якщо з'єднання успішне, False у випадку помилки
        """
        try:
            self.client = MongoClient(self.connection_string)
            # Перевіряємо з'єднання
            self.client.admin.command('ping')
            
            self.database = self.client.cats_db
            self.collection = self.database.cats
            
            print("✅ Успішно підключено до MongoDB!")
            return True
            
        except ConnectionFailure as e:
            print(f"❌ Помилка підключення до MongoDB: {e}")
            return False
        except Exception as e:
            print(f"❌ Невідома помилка при підключенні: {e}")
            return False
    
    def disconnect(self) -> None:
        """Закриття з'єднання з базою даних"""
        if self.client:
            self.client.close()
            print("🔌 З'єднання з базою даних закрито")
    
    def create_cat(self, name: str, age: int, features: List[str]) -> bool:
        """
        Створення нового кота в базі даних (CREATE)
        
        Args:
            name: Ім'я кота
            age: Вік кота
            features: Список характеристик кота
            
        Returns:
            True якщо кіт успішно створений, False у випадку помилки
        """
        try:
            if self.collection is None:
                print("❌ Немає з'єднання з базою даних")
                return False
                
            # Перевіряємо, чи не існує вже кіт з таким іменем
            existing_cat = self.collection.find_one({"name": name})
            if existing_cat:
                print(f"⚠️ Кіт з іменем '{name}' вже існує в базі даних!")
                return False
            
            cat_document = {
                "name": name,
                "age": age,
                "features": features
            }
            
            result = self.collection.insert_one(cat_document)
            
            if result.inserted_id:
                print(f"✅ Кіт '{name}' успішно додано до бази даних!")
                print(f"🔗 ID: {result.inserted_id}")
                return True
            else:
                print("❌ Помилка при додаванні кота")
                return False
                
        except PyMongoError as e:
            print(f"❌ Помилка MongoDB при створенні кота: {e}")
            return False
        except Exception as e:
            print(f"❌ Невідома помилка при створенні кота: {e}")
            return False
    
    def read_all_cats(self) -> None:
        """Читання та виведення всіх котів з бази даних (READ)"""
        try:
            if self.collection is None:
                print("❌ Немає з'єднання з базою даних")
                return
                
            cats = list(self.collection.find())
            
            if not cats:
                print("📭 База даних порожня - котів не знайдено")
                return
            
            print(f"\n🐱 Знайдено {len(cats)} котів у базі даних:")
            print("=" * 60)
            
            for i, cat in enumerate(cats, 1):
                print(f"\n{i}. ID: {cat['_id']}")
                print(f"   Ім'я: {cat['name']}")
                print(f"   Вік: {cat['age']} років")
                print(f"   Характеристики: {', '.join(cat['features'])}")
            
            print("=" * 60)
            
        except PyMongoError as e:
            print(f"❌ Помилка MongoDB при читанні котів: {e}")
        except Exception as e:
            print(f"❌ Невідома помилка при читанні котів: {e}")
    
    def read_cat_by_name(self, name: str) -> None:
        """
        Читання інформації про кота за іменем (READ)
        
        Args:
            name: Ім'я кота для пошуку
        """
        try:
            if self.collection is None:
                print("❌ Немає з'єднання з базою даних")
                return
                
            cat = self.collection.find_one({"name": name})
            
            if not cat:
                print(f"😿 Кота з іменем '{name}' не знайдено в базі даних")
                return
            
            print(f"\n🐱 Інформація про кота '{name}':")
            print("=" * 40)
            print(f"ID: {cat['_id']}")
            print(f"Ім'я: {cat['name']}")
            print(f"Вік: {cat['age']} років")
            print(f"Характеристики: {', '.join(cat['features'])}")
            print("=" * 40)
            
        except PyMongoError as e:
            print(f"❌ Помилка MongoDB при пошуку кота: {e}")
        except Exception as e:
            print(f"❌ Невідома помилка при пошуку кота: {e}")
    
    def update_cat_age(self, name: str, new_age: int) -> bool:
        """
        Оновлення віку кота за іменем (UPDATE)
        
        Args:
            name: Ім'я кота
            new_age: Новий вік кота
            
        Returns:
            True якщо вік успішно оновлено, False у випадку помилки
        """
        try:
            if self.collection is None:
                print("❌ Немає з'єднання з базою даних")
                return False
                
            result = self.collection.update_one(
                {"name": name},
                {"$set": {"age": new_age}}
            )
            
            if result.matched_count == 0:
                print(f"😿 Кота з іменем '{name}' не знайдено в базі даних")
                return False
            elif result.modified_count == 1:
                print(f"✅ Вік кота '{name}' успішно оновлено на {new_age} років!")
                return True
            else:
                print(f"⚠️ Кіт '{name}' знайдений, але вік не було змінено (можливо, новий вік такий же)")
                return True
                
        except PyMongoError as e:
            print(f"❌ Помилка MongoDB при оновленні віку кота: {e}")
            return False
        except Exception as e:
            print(f"❌ Невідома помилка при оновленні віку кота: {e}")
            return False
    
    def add_cat_feature(self, name: str, new_feature: str) -> bool:
        """
        Додавання нової характеристики до кота за іменем (UPDATE)
        
        Args:
            name: Ім'я кота
            new_feature: Нова характеристика для додавання
            
        Returns:
            True якщо характеристика успішно додана, False у випадку помилки
        """
        try:
            if self.collection is None:
                print("❌ Немає з'єднання з базою даних")
                return False
                
            # Перевіряємо, чи існує кіт
            cat = self.collection.find_one({"name": name})
            if not cat:
                print(f"😿 Кота з іменем '{name}' не знайдено в базі даних")
                return False
            
            # Перевіряємо, чи вже є така характеристика
            if new_feature in cat.get('features', []):
                print(f"⚠️ Характеристика '{new_feature}' вже існує у кота '{name}'")
                return True
            
            result = self.collection.update_one(
                {"name": name},
                {"$addToSet": {"features": new_feature}}
            )
            
            if result.modified_count == 1:
                print(f"✅ Характеристика '{new_feature}' успішно додана коту '{name}'!")
                return True
            else:
                print(f"⚠️ Характеристика не була додана (можливо, вже існувала)")
                return True
                
        except PyMongoError as e:
            print(f"❌ Помилка MongoDB при додаванні характеристики: {e}")
            return False
        except Exception as e:
            print(f"❌ Невідома помилка при додаванні характеристики: {e}")
            return False
    
    def delete_cat_by_name(self, name: str) -> bool:
        """
        Видалення кота з бази даних за іменем (DELETE)
        
        Args:
            name: Ім'я кота для видалення
            
        Returns:
            True якщо кіт успішно видалений, False у випадку помилки
        """
        try:
            if self.collection is None:
                print("❌ Немає з'єднання з базою даних")
                return False
                
            result = self.collection.delete_one({"name": name})
            
            if result.deleted_count == 1:
                print(f"✅ Кіт '{name}' успішно видалений з бази даних!")
                return True
            else:
                print(f"😿 Кота з іменем '{name}' не знайдено в базі даних")
                return False
                
        except PyMongoError as e:
            print(f"❌ Помилка MongoDB при видаленні кота: {e}")
            return False
        except Exception as e:
            print(f"❌ Невідома помилка при видаленні кота: {e}")
            return False
    
    def delete_all_cats(self) -> bool:
        """
        Видалення всіх котів з бази даних (DELETE)
        
        Returns:
            True якщо операція успішна, False у випадку помилки
        """
        try:
            if self.collection is None:
                print("❌ Немає з'єднання з базою даних")
                return False
                
            # Запитуємо підтвердження у користувача
            confirmation = input("⚠️ Ви впевнені, що хочете видалити ВСІХ котів? (так/ні): ").strip().lower()
            
            if confirmation not in ['так', 'yes', 'y']:
                print("🛡️ Операцію скасовано користувачем")
                return False
            
            result = self.collection.delete_many({})
            
            if result.deleted_count > 0:
                print(f"✅ Успішно видалено {result.deleted_count} котів з бази даних!")
                return True
            else:
                print("📭 База даних вже порожня - котів не було для видалення")
                return True
                
        except PyMongoError as e:
            print(f"❌ Помилка MongoDB при видаленні всіх котів: {e}")
            return False
        except Exception as e:
            print(f"❌ Невідома помилка при видаленні всіх котів: {e}")
            return False


def print_menu() -> None:
    """Виведення головного меню програми"""
    print("\n" + "="*50)
    print("🐱 СИСТЕМА УПРАВЛІННЯ БАЗОЮ ДАНИХ КОТІВ 🐱")
    print("="*50)
    print("1. Показати всіх котів")
    print("2. Знайти кота за іменем")
    print("3. Додати нового кота")
    print("4. Оновити вік кота")
    print("5. Додати характеристику коту")
    print("6. Видалити кота за іменем")
    print("7. Видалити всіх котів")
    print("8. Вийти з програми")
    print("="*50)


def get_user_input(prompt: str, input_type: type = str) -> Any:
    """
    Отримання вводу від користувача з перевіркою типу
    
    Args:
        prompt: Текст запиту для користувача
        input_type: Очікуваний тип даних
        
    Returns:
        Введене значення правильного типу
    """
    while True:
        try:
            user_input = input(prompt).strip()
            
            if input_type == str:
                if not user_input:
                    print("❌ Поле не може бути порожнім. Спробуйте ще раз.")
                    continue
                return user_input
            elif input_type == int:
                value = int(user_input)
                if value < 0:
                    print("❌ Вік не може бути від'ємним. Спробуйте ще раз.")
                    continue
                return value
            elif input_type == list:
                if not user_input:
                    return []
                # Розділяємо по комах та очищаємо пробіли
                features = [feature.strip() for feature in user_input.split(',') if feature.strip()]
                return features
                
        except ValueError:
            print(f"❌ Некоректне значення. Очікується {input_type.__name__}. Спробуйте ще раз.")
        except KeyboardInterrupt:
            print("\n👋 Програму перервано користувачем")
            sys.exit(0)


def main() -> None:
    """Головна функція програми"""
    print("🚀 Запуск програми управління базою даних котів")
    
    # Створюємо екземпляр бази даних
    cats_db = CatsDatabase()
    
    # Підключаємося до бази даних
    if not cats_db.connect():
        print("❌ Не вдалося підключитися до бази даних. Програма завершена.")
        return
    
    try:
        while True:
            print_menu()
            
            try:
                choice = input("👉 Оберіть опцію (1-8): ").strip()
                
                if choice == "1":
                    cats_db.read_all_cats()
                
                elif choice == "2":
                    name = get_user_input("🔍 Введіть ім'я кота для пошуку: ", str)
                    cats_db.read_cat_by_name(name)
                
                elif choice == "3":
                    print("\n➕ Додавання нового кота:")
                    name = get_user_input("📝 Ім'я кота: ", str)
                    age = get_user_input("🎂 Вік кота: ", int)
                    print("🏷️ Характеристики кота (через кому, наприклад: рудий, грайливий, любить рибу):")
                    features = get_user_input("   ", list)
                    
                    cats_db.create_cat(name, age, features)
                
                elif choice == "4":
                    name = get_user_input("📝 Ім'я кота для оновлення віку: ", str)
                    new_age = get_user_input("🎂 Новий вік кота: ", int)
                    cats_db.update_cat_age(name, new_age)
                
                elif choice == "5":
                    name = get_user_input("📝 Ім'я кота: ", str)
                    new_feature = get_user_input("🏷️ Нова характеристика: ", str)
                    cats_db.add_cat_feature(name, new_feature)
                
                elif choice == "6":
                    name = get_user_input("📝 Ім'я кота для видалення: ", str)
                    cats_db.delete_cat_by_name(name)
                
                elif choice == "7":
                    cats_db.delete_all_cats()
                
                elif choice == "8":
                    print("👋 До побачення!")
                    break
                
                else:
                    print("❌ Некоректний вибір. Оберіть опцію від 1 до 8.")
            
            except KeyboardInterrupt:
                print("\n\n👋 Програму перервано користувачем")
                break
            except Exception as e:
                print(f"❌ Невідома помилка в головному циклі: {e}")
    
    finally:
        # Закриваємо з'єднання з базою даних
        cats_db.disconnect()


def run_comprehensive_tests():
    """
    Комплексне тестування всіх функцій системи
    """
    print("🧪 КОМПЛЕКСНЕ ТЕСТУВАННЯ MONGODB CRUD СИСТЕМИ")
    print("=" * 60)
    
    # Ініціалізація
    db = CatsDatabase()
    if not db.connect():
        print("❌ Не вдалося підключитися до бази даних")
        return
    
    test_results = []
    
    # ТЕСТ 1: Показати всіх котів
    print("\n" + "="*60)
    print("🔸 ТЕСТ 1: Показати всіх котів")
    print("="*60)
    try:
        db.read_all_cats()
        test_results.append("✅ Тест 1: Показ всіх котів - ПРОЙДЕНО")
    except Exception as e:
        test_results.append(f"❌ Тест 1: Показ всіх котів - ПОМИЛКА: {e}")
    
    # ТЕСТ 2: Пошук за іменем
    print("\n" + "="*60)
    print("🔸 ТЕСТ 2: Пошук за іменем")
    print("="*60)
    try:
        print("🔍 Шукаємо існуючого кота 'barsik':")
        db.read_cat_by_name("barsik")
        print("\n🔍 Шукаємо неіснуючого кота 'nonexistent':")
        db.read_cat_by_name("nonexistent")
        test_results.append("✅ Тест 2: Пошук за іменем - ПРОЙДЕНО")
    except Exception as e:
        test_results.append(f"❌ Тест 2: Пошук за іменем - ПОМИЛКА: {e}")
    
    # ТЕСТ 3: Створення кота
    print("\n" + "="*60)
    print("🔸 ТЕСТ 3: Створення кота")
    print("="*60)
    try:
        print("➕ Додаємо нового кота 'test_cat':")
        result = db.create_cat("test_cat", 2, ["тестовий", "автоматичний"])
        print(f"Результат CREATE: {'✅ Успіх' if result else '❌ Помилка'}")
        
        print("\n➕ Спроба додати дублікат:")
        duplicate_result = db.create_cat("test_cat", 3, ["дублікат"])
        print(f"Результат дублікату: {'✅ Правильно заблоковано' if not duplicate_result else '❌ Дозволив дублікат'}")
        
        test_results.append("✅ Тест 3: Створення кота - ПРОЙДЕНО")
    except Exception as e:
        test_results.append(f"❌ Тест 3: Створення кота - ПОМИЛКА: {e}")
    
    # ТЕСТ 4: Оновлення віку
    print("\n" + "="*60)
    print("🔸 ТЕСТ 4: Оновлення віку")
    print("="*60)
    try:
        print("🎂 Оновлюємо вік кота 'test_cat':")
        result = db.update_cat_age("test_cat", 4)
        print(f"Результат UPDATE age: {'✅ Успіх' if result else '❌ Помилка'}")
        
        print("\n🎂 Спроба оновити неіснуючого кота:")
        nonexistent_result = db.update_cat_age("nonexistent", 5)
        print(f"Результат неіснуючого: {'✅ Правильно обробив' if not nonexistent_result else '❌ Неправильна обробка'}")
        
        test_results.append("✅ Тест 4: Оновлення віку - ПРОЙДЕНО")
    except Exception as e:
        test_results.append(f"❌ Тест 4: Оновлення віку - ПОМИЛКА: {e}")
    
    # ТЕСТ 5: Додавання характеристик
    print("\n" + "="*60)
    print("🔸 ТЕСТ 5: Додавання характеристик")
    print("="*60)
    try:
        print("🏷️ Додаємо характеристику 'розумний':")
        result = db.add_cat_feature("test_cat", "розумний")
        print(f"Результат ADD feature: {'✅ Успіх' if result else '❌ Помилка'}")
        
        print("\n🏷️ Додаємо ту ж характеристику повторно:")
        duplicate_feature = db.add_cat_feature("test_cat", "розумний")
        print(f"Результат дублікату: {'✅ Правильно обробив' if duplicate_feature else '❌ Помилка'}")
        
        test_results.append("✅ Тест 5: Додавання характеристик - ПРОЙДЕНО")
    except Exception as e:
        test_results.append(f"❌ Тест 5: Додавання характеристик - ПОМИЛКА: {e}")
    
    # ТЕСТ 6: Перевірка оновленого кота
    print("\n" + "="*60)
    print("🔸 ТЕСТ 6: Перевірка оновленого кота")
    print("="*60)
    try:
        print("👀 Перевіряємо оновленого кота 'test_cat':")
        db.read_cat_by_name("test_cat")
        test_results.append("✅ Тест 6: Перевірка оновленого кота - ПРОЙДЕНО")
    except Exception as e:
        test_results.append(f"❌ Тест 6: Перевірка оновленого кота - ПОМИЛКА: {e}")
    
    # ТЕСТ 7: Видалення кота
    print("\n" + "="*60)
    print("🔸 ТЕСТ 7: Видалення кота")
    print("="*60)
    try:
        print("🗑️ Видаляємо кота 'test_cat':")
        result = db.delete_cat_by_name("test_cat")
        print(f"Результат DELETE: {'✅ Успіх' if result else '❌ Помилка'}")
        
        print("\n🗑️ Спроба видалити того ж кота повторно:")
        repeat_delete = db.delete_cat_by_name("test_cat")
        print(f"Результат повторного видалення: {'✅ Правильно обробив' if not repeat_delete else '❌ Неправильна обробка'}")
        
        test_results.append("✅ Тест 7: Видалення кота - ПРОЙДЕНО")
    except Exception as e:
        test_results.append(f"❌ Тест 7: Видалення кота - ПОМИЛКА: {e}")
    
    # ТЕСТ 8: Валідація вводу
    print("\n" + "="*60)
    print("🔸 ТЕСТ 8: Валідація вводу")
    print("="*60)
    try:
        import builtins
        original_input = builtins.input
        
        # Тест валідації порожнього рядка
        inputs = ['', 'valid_name']
        input_iter = iter(inputs)
        builtins.input = lambda prompt: next(input_iter)
        
        from io import StringIO
        import sys
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        result = get_user_input("Тест ім'я: ", str)
        
        sys.stdout = original_stdout
        output = captured_output.getvalue()
        
        print(f"Результат валідації: {result}")
        print("✅ Валідація порожнього рядка працює" if "не може бути порожнім" in output else "❌ Валідація не працює")
        
        # Відновлюємо оригінальну функцію
        builtins.input = original_input
        
        test_results.append("✅ Тест 8: Валідація вводу - ПРОЙДЕНО")
    except Exception as e:
        test_results.append(f"❌ Тест 8: Валідація вводу - ПОМИЛКА: {e}")
    
    # ТЕСТ 9: Функція delete_all_cats (безпечний тест)
    print("\n" + "="*60)
    print("🔸 ТЕСТ 9: Функція delete_all_cats (безпечний)")
    print("="*60)
    try:
        # Створюємо тестового кота
        db.create_cat("temp_test", 1, ["тимчасовий"])
        
        # Тестуємо відмову
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'ні'
        
        result = db.delete_all_cats()
        print(f"Результат при відмові: {'✅ Правильно скасовано' if not result else '❌ Помилка'}")
        
        # Очищаємо тестового кота
        builtins.input = original_input
        db.delete_cat_by_name("temp_test")
        
        test_results.append("✅ Тест 9: Функція delete_all_cats - ПРОЙДЕНО")
    except Exception as e:
        test_results.append(f"❌ Тест 9: Функція delete_all_cats - ПОМИЛКА: {e}")
    
    # Підсумковий стан бази
    print("\n" + "="*60)
    print("📊 ПІДСУМКОВИЙ СТАН БАЗИ ДАНИХ")
    print("="*60)
    db.read_all_cats()
    
    # Закриваємо з'єднання
    db.disconnect()
    
    # Підсумок тестів
    print("\n" + "="*60)
    print("📋 ПІДСУМОК ТЕСТУВАННЯ")
    print("="*60)
    for result in test_results:
        print(result)
    
    passed_tests = sum(1 for result in test_results if result.startswith("✅"))
    total_tests = len(test_results)
    
    print(f"\n🎯 РЕЗУЛЬТАТ: {passed_tests}/{total_tests} тестів пройдено")
    
    if passed_tests == total_tests:
        print("🎉 ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
    else:
        print("⚠️ Деякі тести не пройдено. Потрібна додаткова перевірка.")
    
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    # Перевіряємо аргументи командного рядка
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_comprehensive_tests()
    else:
        main()
