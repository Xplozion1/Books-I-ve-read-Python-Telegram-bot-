import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlalchemy import create_engine, Column, Integer, String, DateTime, extract
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import locale

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен вашего бота. Здесь нужно вести созданный токен
API_TOKEN = 'YOUR TOKEN'

# Инициализация бота, хранилища и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# URL для базы данных SQLite
DATABASE_URL = "sqlite:///./books_database.db"
engine = create_engine(DATABASE_URL)

# Объявление базовой модели SQLAlchemy
from sqlalchemy.orm import declarative_base
Base = declarative_base()

# Объявление модели книги
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String)
    title = Column(String)
    date = Column(DateTime)

# Создание таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создание сессии для взаимодействия с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Определение состояний для FSM
class RegistrationForm(StatesGroup):
    full_name = State()
    phone_number = State()

class BookEntryForm(StatesGroup):
    author = State()
    title = State()
    date = State()

class ViewBooksForm(StatesGroup):
    view_month = State()
    view_year = State()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("Привет! Для начала регистрации введите фамилию, имя и отчество.")
    await RegistrationForm.full_name.set()

# Обработчик состояния full_name
@dp.message_handler(state=RegistrationForm.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['full_name'] = message.text
    await message.reply("Отлично! Теперь отправьте свой номер телефона.")
    await RegistrationForm.next()

# Обработчик состояния phone_number
@dp.message_handler(state=RegistrationForm.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text
    await message.reply("Регистрация завершена! Теперь вы можете добавлять прочитанные книги.\n"
                         "Для внесения данных о книге, используйте команду /add_book")
    await state.finish()

# Обработчик команды /add_book
@dp.message_handler(commands=['add_book'])
async def cmd_add_book(message: types.Message):
    await message.reply("Отлично! Для начала отправьте имя автора книги.")
    await BookEntryForm.author.set()

# Обработчик состояния author
@dp.message_handler(state=BookEntryForm.author)
async def process_author(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['author'] = message.text
    await message.reply("Теперь отправьте название книги.")
    await BookEntryForm.next()

# Обработчик состояния title
@dp.message_handler(state=BookEntryForm.title)
async def process_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    await message.reply("Теперь отправьте месяц и год, когда вы прочитали книгу (например, Январь 2023).")
    await BookEntryForm.next()

# Обработчик состояния date
@dp.message_handler(state=BookEntryForm.date)
async def process_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        locale.setlocale(locale.LC_TIME, 'ru_RU')
        data['date'] = datetime.strptime(message.text, '%B %Y')
    session = SessionLocal()
    new_book = Book(author=data['author'], title=data['title'], date=data['date'])
    session.add(new_book)
    session.commit()
    session.close()
    await message.reply(f"Ура! Вы успешно добавили данные о прочитанной книге.\nЧтобы добавить новую книгу, напишите команду /add_book.\nЧтобы посмотреть список прочитанных книг используйте команду /view_books")
    await state.finish()


@dp.message_handler(commands=['view_books'])
async def cmd_view_books(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Показать все"))
    keyboard.add(types.KeyboardButton(text="Показать за месяц"))
    keyboard.add(types.KeyboardButton(text="Показать за год"))
    await message.reply("Выберите опцию:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text.lower() == "показать за год", state=None)
async def choose_year(message: types.Message):
    await message.reply("Введите год для просмотра (например, 2023):")
    await ViewBooksForm.view_year.set()

# Обработчик состояния view_year
@dp.message_handler(state=ViewBooksForm.view_year)
async def process_year(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['year'] = int(message.text)
    session = SessionLocal()
    books_for_year = session.query(Book).filter(
        extract('year', Book.date) == data['year']
    ).all()
    session.close()
    if books_for_year:
        books_info = "\n".join(
            [f"{book.date.year}, {book.date.strftime('%m')}, {book.author}, {book.title}" for book in books_for_year])
        reply_text = f"Прочитанные книги за {data['year']} год:\n{books_info}"
    else:
        reply_text = f"Нет информации о прочитанных книгах за {data['year']} год."
    await message.reply(reply_text)

    # Добавляем сообщение-приглашение
    await message.reply("Выберите опцию:")
    await state.finish()


@dp.message_handler(lambda message: message.text.lower() == "показать все", state=None)
async def view_all_books(message: types.Message):
    session = SessionLocal()
    all_books = session.query(Book).all()
    session.close()
    if all_books:
        books_info = "\n".join([f"{book.author}, {book.title}" for book in all_books])
        reply_text = f"Прочитанные книги:\n{books_info}"
    else:
        reply_text = "Нет информации о прочитанных книгах."
    await message.reply(reply_text)
    await bot.send_message(message.chat.id, "Выберите опцию:")

@dp.message_handler(lambda message: message.text.lower() == "показать за месяц", state=None)
async def choose_month(message: types.Message):
    await message.reply("Выберите месяц для просмотра (например, Январь):", reply_markup=get_keyboard_for_month())
    await ViewBooksForm.view_month.set()

month_ru_to_en = {
    'Январь': '01',
    'Февраль': '02',
    'Март': '03',
    'Апрель': '04',
    'Май': '05',
    'Июнь': '06',
    'Июль': '07',
    'Август': '08',
    'Сентябрь': '09',
    'Октябрь': '10',
    'Ноябрь': '11',
    'Декабрь': '12'
}

# Обработчик состояния view_month
@dp.message_handler(state=ViewBooksForm.view_month)
async def process_month(message: types.Message, state: FSMContext):
    if message.text == "Завершить выбор месяца":
        # Если пользователь выбрал завершение выбора, завершаем состояние
        await state.finish()
        await message.reply("Выбор месяца завершен. Напишите /view_books, если вы хотите еще раз посмотреть список прочитанных книг.")
    else:
        # Если пользователь выбрал месяц, обрабатываем его выбор
        async with state.proxy() as data:
            data['month'] = month_ru_to_en.get(message.text)
        session = SessionLocal()
        books_for_month = session.query(Book).filter(
            extract('month', Book.date) == data['month']
        ).all()
        session.close()
        if books_for_month:
            books_info = "\n".join(
                [f"{book.date.year}, {book.date.strftime('%m')}, {book.author}, {book.title}" for book in books_for_month])
            reply_text = f"Прочитанные книги за {message.text}:\n{books_info}"
        else:
            reply_text = f"Нет информации о прочитанных книгах за {message.text}."
        await message.reply(reply_text)

        # Предложение выбрать месяцы снова
        await message.reply("Выберите другой месяц или нажмите 'Завершить выбор месяца':", reply_markup=get_keyboard_for_month())


# Функция для формирования клавиатуры с месяцами
def get_keyboard_for_month():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for month in ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']:
        keyboard.add(types.KeyboardButton(text=month))
    # Добавляем кнопку "Завершить выбор месяца"
    keyboard.add(types.KeyboardButton(text="Завершить выбор месяца"))
    return keyboard

if __name__ == '__main__':
    from aiogram import executor

    # Запуск бота
    executor.start_polling(dp, skip_updates=True)


