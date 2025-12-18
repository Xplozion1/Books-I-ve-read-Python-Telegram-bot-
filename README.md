# Books-I-ve-read-Python-Telegram-bot-
Этот Telegram‑бот на Python предназначен для ведения личного журнала прочитанных книг. Пользователь может добавлять книги, указывая автора, название и дату прочтения, а затем просматривать сохранённые записи: полный список, книги за определённый месяц или год. Бот хранит данные в базе SQLite и фактически выступает как персональная «история чтения» в удобном формате чата.

## Использованные технологии

- **Язык программирования**: Python 3.10  
- **Telegram‑фреймворк**: [aiogram 2.x](https://docs.aiogram.dev/) — асинхронная работа с Telegram Bot API, FSM для управления диалогами  
- **База данных**: SQLite (локальный файл `books_database.db`)  
- **ORM**: SQLAlchemy — описание моделей и работа с БД через объектный интерфейс  
- **Логирование**: стандартный модуль `logging` и `LoggingMiddleware` из aiogram  
- **Управление состояниями пользователей**: FSM (`StatesGroup`, `State`, `FSMContext`) из aiogram  
- **Среда разработки**: Visual Studio, виртуальное окружение Python (`venv`)

Скриншот бота:



![photo_2025-12-18_16-45-06](https://github.com/user-attachments/assets/603eec22-b82a-40aa-83e5-6835ff777f53)

Скриншот регистрации:

![photo_2025-12-18_16-45-07](https://github.com/user-attachments/assets/b0b1d60a-a68a-4dad-884e-d22a8ed3477d)

Скриншот ввода информации о прочитанной книге (ФИО автора, название книги):

![photo_2025-12-18_16-45-08](https://github.com/user-attachments/assets/6ddfcd62-56e9-4641-9cc1-6934bb04ca1a)

Скриншот вывода информации о прочитанных книгах (можно вывести информацию о всех прочитанных книгах, либо за определенный месяц, либо за год):

![photo_2025-12-18_16-45-10 (2)](https://github.com/user-attachments/assets/2fb527a5-e779-4ba1-9a32-1800847b8e4c)

БД в SQLite:

<img width="504" height="173" alt="image" src="https://github.com/user-attachments/assets/9423e7a0-6aa0-4f47-8477-389c83dd978b" />
