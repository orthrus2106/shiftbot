import sqlite3
import logging
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '6030342610:AAHCPEpwOnQU8LDCJmrKFsGMa89tVDVK_C4'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
# Подключаемся к базе данных
conn = sqlite3.connect('bot.db')

# Создаем таблицу
conn.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY,
             name TEXT NOT NULL,
             hours INTEGER NOT NULL,
             total_hours INTEGER NOT NULL);''')

# Закрываем соединение с базой данных
conn.close()


@dp.message_handler(commands=['add'])
async def add_hours(message: types.Message):
    conn = sqlite3.connect('bot.db')
    # Получаем аргументы команды
    args = message.get_args().split()

    # Проверяем, что передано корректное количество аргументов
    if len(args) != 1:
        await message.answer('Некорректное количество аргументов. Используйте /add [часы]')
        return

    # Получаем количество часов из аргументов команды
    try:
        hours = int(args[0])
    except ValueError:
        await message.answer('Некорректное значение количества часов. Используйте целое число.')
        return

    # Получаем идентификатор пользователя
    user_id = message.from_user.id

    # Получаем текущее количество часов и общее количество часов пользователя
    cursor = conn.execute("SELECT hours, total_hours FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    # Обновляем количество часов и общее количество часов для пользователя
    new_hours = row[0] + hours
    new_total_hours = row[1] + hours
    conn.execute("UPDATE users SET hours = ?, total_hours = ? WHERE id = ?", (new_hours, new_total_hours, user_id))

    # Сохраняем изменения в базе данных
    conn.commit()

    # Отправляем сообщение об успешном обновлении количества часов
    await message.answer(f'Количество часов успешно обновлено. '
                         f'Текущее количество часов: {new_hours}. Общее количество часов: {new_total_hours}.')
    conn.close()

@dp.message_handler(commands=['remove'])
async def process_add_command(message: types.Message):
    conn = sqlite3.connect('bot.db')
    try:
        hours = int(message.text.split()[1])

        chat_id = message.chat.id

        cur = conn.cursor()
        cur.execute("SELECT hours FROM users WHERE id = ?", (chat_id,))
        user_hours = cur.fetchone()[0]
        if user_hours >= hours:
            conn.execute("UPDATE users SET hours = hours - ? WHERE id = ?", (hours, chat_id,))
            conn.commit()
            # Отвечаем пользователю
            await message.reply(f"Количество часов уменьшено на {hours}. Общее количество часов: {total_hours}.")
        else:
            await message.reply(f"Недостаточно часов для удаления. Общее количество часов: {total_hours}.")
    except(IndexError, ValueError):
        await message.reply("/remove <значение>")
    # Сохраняем изменения в базе данных
    conn.commit()

    # Закрываем подключение к базе данных
    conn.close()


@dp.message_handler(commands=['clear'])
async def process_add_command(message: types.Message):
    conn = sqlite3.connect('bot.db')

    # Присваиваем значение столбцу hours для всех пользователей
    new_hours = 150
    conn.execute("UPDATE users SET hours = ?", (new_hours,))

    # Сохраняем изменения в базе данных
    conn.commit()

    # Закрываем подключение к базе данных
    conn.close()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)