-- Завдання 1: SQL запити для системи управління завданнями

-- 1. Отримати всі завдання певного користувача (user_id = 1)
SELECT t.id, t.title, t.description, s.name as status, u.fullname as user_name
FROM tasks t
JOIN users u ON t.user_id = u.id
JOIN status s ON t.status_id = s.id
WHERE t.user_id = 1;

-- 2. Вибрати завдання за певним статусом ('new')
SELECT t.id, t.title, t.description, u.fullname as user_name
FROM tasks t
JOIN users u ON t.user_id = u.id
WHERE t.status_id = (SELECT id FROM status WHERE name = 'new');

-- 3. Оновити статус конкретного завдання (id = 1 на 'in progress')
UPDATE tasks 
SET status_id = (SELECT id FROM status WHERE name = 'in progress')
WHERE id = 1;

-- 4. Отримати список користувачів, які не мають жодного завдання
SELECT u.id, u.fullname, u.email
FROM users u
WHERE u.id NOT IN (SELECT DISTINCT user_id FROM tasks WHERE user_id IS NOT NULL);

-- 5. Додати нове завдання для конкретного користувача
INSERT INTO tasks (title, description, status_id, user_id)
VALUES (
    'Нове тестове завдання',
    'Опис нового завдання для тестування',
    (SELECT id FROM status WHERE name = 'new'),
    1
);

-- 6. Отримати всі завдання, які ще не завершено
SELECT t.id, t.title, t.description, s.name as status, u.fullname as user_name
FROM tasks t
JOIN users u ON t.user_id = u.id
JOIN status s ON t.status_id = s.id
WHERE s.name != 'completed';

-- 7. Видалити конкретне завдання (id = 1)
DELETE FROM tasks WHERE id = 1;

-- 8. Знайти користувачів з певною електронною поштою (домен gmail)
SELECT id, fullname, email
FROM users
WHERE email LIKE '%gmail%';

-- 9. Оновити ім'я користувача (id = 1)
UPDATE users 
SET fullname = 'Оновлене Ім''я Користувача'
WHERE id = 1;

-- 10. Отримати кількість завдань для кожного статусу
SELECT s.name as status_name, COUNT(t.id) as task_count
FROM status s
LEFT JOIN tasks t ON s.id = t.status_id
GROUP BY s.id, s.name
ORDER BY s.id;

-- 11. Отримати завдання користувачів з певним доменом електронної пошти
SELECT t.id, t.title, t.description, u.fullname, u.email, s.name as status
FROM tasks t
JOIN users u ON t.user_id = u.id
JOIN status s ON t.status_id = s.id
WHERE u.email LIKE '%@example.com';

-- 12. Отримати список завдань, що не мають опису
SELECT t.id, t.title, u.fullname as user_name, s.name as status
FROM tasks t
JOIN users u ON t.user_id = u.id
JOIN status s ON t.status_id = s.id
WHERE t.description IS NULL OR t.description = '';

-- 13. Вибрати користувачів та їхні завдання зі статусом 'in progress'
SELECT u.fullname, u.email, t.title, t.description
FROM users u
INNER JOIN tasks t ON u.id = t.user_id
INNER JOIN status s ON t.status_id = s.id
WHERE s.name = 'in progress';

-- 14. Отримати користувачів та кількість їхніх завдань
SELECT u.id, u.fullname, u.email, COUNT(t.id) as task_count
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.id, u.fullname, u.email
ORDER BY task_count DESC, u.fullname;
