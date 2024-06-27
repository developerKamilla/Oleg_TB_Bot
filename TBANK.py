import telebot
import json
import os
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("agg")
from datetime import datetime

TOKEN = "7468399496:AAFZFj5tqxjTvT4HglQp9ULlv7V5WpW6xkw"
bot = telebot.TeleBot(TOKEN)

# Словарь всех данных
data = {
    "budget": 0,
    "balance": 0,
    "expenses": {
        "развлечения": 0,
        "медицина": 0,
        "маркеты": 0,
        "фудкорты": 0,
        "такси": 0,
        "одежда": 0,
        "дом": 0,
    },
    "financial_goals": {},
    "allmoney": [],
}


#Функция для сохранения данных в файл
def save_data():
    with open("data.json", "w") as f:
        json.dump(data, f)


# Функция для загрузки данных из файла
def load_data():
    global data
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            data = json.load(f)


# Загружаем данные при запуске
load_data()


# Команда и функция для добавления дохода
@bot.message_handler(commands=["addincome"])
def add_income(message):
    try:
        command, money, about = message.text.split(maxsplit=2)
        money = float(money)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["balance"] += money
        data["allmoney"].append(
            {"type": "income", "money": money, "description": about, "date": now}
        )
        save_data()
        bot.reply_to(message, f"Сумма в {money} руб успешно добавлена.")
    except Exception as e:
        bot.reply_to(
            message,
            "Неправильный формат команды. Используйте команду в формате: /addincome [money] [description]",
        )


# Команда и функция для добавления расхода
@bot.message_handler(commands=["addexpense"])
def add_expense(message):
    try:
        command, money, categ = message.text.split()
        money = float(money)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if categ in data["expenses"]:
            data["balance"] -= money
            data["expenses"][categ] += money
            data["allmoney"].append(
                {"type": "expense", "amount": money, "description": categ, "date": now}
            )
            save_data()
            bot.reply_to(
                message, f"Сумма в {money} руб успешно вычтена в категорию {categ}."
            )
        else:
            bot.reply_to(message, "Такой категории не существует.")
    except Exception as e:
        bot.reply_to(
            message,
            "Неправильный формат команды. Используйте команду в формате: /addexpense [сумма] [описание]",
        )


# Команда и функция для проверки текущего баланса
@bot.message_handler(commands=["balance"])
def check_budget(message):
    bot.reply_to(message, f"Ваш текущий баланс: {data['balance']} руб")


# Команда и функция для установки бюджета
@bot.message_handler(commands=["setbudget"])
def set_budget(message):
    try:
        command, budget = message.text.split()
        budget = float(budget)
        now = datetime.now()
        data["budget"] = int(budget)
        save_data()
        bot.reply_to(message, f"Бюджет обновлен: {budget}")
    except ValueError:
        bot.reply_to(
            message,
            "Некорректный формат команды. Пожалуйста, используйте формат: /setbudget [сумма]",
        )


# Команда и функция для установки финансовой цели
@bot.message_handler(commands=["setgoal"])
def set_goal(message):
    try:
        command, money, about = message.text.split(maxsplit=2)
        money = float(money)
        if about not in data["financial_goals"]:
            data["financial_goals"][about] = {
                "goal": about,
                "amount": money,
                "progress": 0.0,
            }
            save_data()
            bot.reply_to(message, f'Цель "{about}" с суммой {money} была установлена.')
        else:
            bot.reply_to(message, f'Цель "{about}" уже существует.')
    except Exception as e:
        bot.reply_to(
            message,
            "Неправильный формат команды. Используйте команду в формате: /setgoal [сумма] [цель]",
        )

# Команда и функция для просмотра целей
@bot.message_handler(commands=["goals"])
def view_goals(message):
    if not data["financial_goals"]:
        bot.reply_to(message, "У вас нет установленных целей.")
    else:
        response = "Ваши цели:\n"
        for goal in data["financial_goals"].values():
            response += f"Цель: {goal['goal']}, Сумма: {goal['amount']}, Текущий прогресс: {goal['progress']}\n"
        bot.reply_to(message, response)


# Команда и функция  для отображения категорий
@bot.message_handler(commands=["categories"])
def send_categories(message):
    response = "Вот доступные категории расходов:\n"
    for category in data["expenses"].keys():
        response += f"- {category.capitalize()}\n"
    response += "\nЧтобы узнать расходы по конкретной категории, введите команду вида /expense <категория>"
    bot.send_message(message.chat.id, response)


# Обработчик команды /expense
@bot.message_handler(commands=["expense"])
def send_expense(message):
    try:
        category = message.text.split()[1].lower()
        if category in data["expenses"]:
            bot.send_message(
                message.chat.id,
                f"Расходы по категории '{category.capitalize()}': {data['expenses'][category]} руб.",
            )
        else:
            bot.send_message(
                message.chat.id,
                "Такой категории нет. Попробуйте команду /categories для списка доступных категорий.",
            )
    except IndexError:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, укажите категорию. Пример: /expense развлечения",
        )


# Команда и функция для отображения графика расходов
@bot.message_handler(commands=["expensechart"])
def expense_chart(message):
    categories = list(data["expenses"].keys())
    amounts = list(data["expenses"].values())

    plt.figure(figsize=(10, 6))
    plt.bar(categories, amounts)
    plt.xlabel("Категории")
    plt.ylabel("Расходы (в рублях)")
    plt.title("Расходы по категориям")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Сохраняем диаграмму в файл
    chart_filename = "expense_chart.png"
    plt.savefig(chart_filename)
    plt.close()

    # Отправляем файл пользователю
    with open(chart_filename, "rb") as chart:
        bot.send_photo(message.chat.id, chart)


bot.polling(none_stop=True)
