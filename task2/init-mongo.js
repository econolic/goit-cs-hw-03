// Ініціалізація бази даних та колекції для котів
db = db.getSiblingDB('cats_db');

// Створюємо користувача для роботи з базою
db.createUser({
    user: 'cats_user',
    pwd: 'cats_password',
    roles: [
        {
            role: 'readWrite',
            db: 'cats_db'
        }
    ]
});

// Створюємо колекцію cats та вставляємо тестові дані
db.cats.insertMany([
    {
        "name": "barsik",
        "age": 3,
        "features": ["ходить в капці", "дає себе гладити", "рудий"]
    },
    {
        "name": "whiskers",
        "age": 5,
        "features": ["полює на мишей", "любить рибу", "сірий"]
    },
    {
        "name": "mura",
        "age": 2,
        "features": ["грається з клубком", "спить весь день", "чорний"]
    },
    {
        "name": "snowball",
        "age": 1,
        "features": ["дуже активний", "білий", "голубі очі"]
    },
    {
        "name": "shadow",
        "age": 4,
        "features": ["тихий", "нічний", "чорний з білими плямами"]
    }
]);

print('База даних cats_db ініціалізована з тестовими даними');
