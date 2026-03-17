import telebot
import config
import database

# Инициализация бота
bot = telebot.TeleBot(config.BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Сохраняем пользователя в БД
    database.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Логируем сообщение
    database.log_message(user.id, message.text, message.chat.id)
    
    # Отправляем приветствие
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        f"✅ Ты успешно сохранён в базе данных!\n"
        f"📊 Используй /stats для статистики"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Обработчик команды /stats"""
    user = message.from_user
    
    # Сохраняем в БД
    database.log_message(user.id, message.text, message.chat.id)
    
    # Получаем статистику
    stats = database.get_user_stats()
    
    if stats and stats['total_users']:
        stats_text = (
            f"📊 Статистика бота:\n\n"
            f"👥 Всего пользователей: {stats['total_users']}\n"
            f"🆔 Уникальных: {stats['unique_users']}\n"
            f"📅 Первый пользователь: {stats['first_user_date']}"
        )
    else:
        stats_text = "📊 Пока нет статистики"
    
    bot.reply_to(message, stats_text)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Обработчик всех остальных сообщений"""
    user = message.from_user
    
    # Сохраняем сообщение в БД
    database.log_message(user.id, message.text, message.chat.id)
    
    # Отвечаем
    bot.reply_to(message, f"Ты написал: {message.text}")

@bot.message_handler(commands=['help'])
def help_command(message):
    """Обработчик команды /help"""
    database.log_message(message.from_user.id, message.text, message.chat.id)
    
    help_text = (
        "📚 Доступные команды:\n\n"
        "/start - Начать работу\n"
        "/stats - Статистика бота\n"
        "/help - Это сообщение\n\n"
        "Просто отправь любое сообщение - я отвечу!"
    )
    bot.reply_to(message, help_text)

if __name__ == '__main__':
    print("🤖 Бот запущен...")
    print(f"📦 База данных: PostgreSQL")
    bot.infinity_polling()
