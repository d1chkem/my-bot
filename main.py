import asyncio
import os
import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8616724303:AAFSIen0a5EkBNWvJM9f3n3i1AOEdvQCjbw"
bot = Bot(token=TOKEN)
dp = Dispatcher()

class UserState(StatesGroup):
    choosing_group = State()
    viewing_schedule = State()

def get_lesson_time(shift, day, lesson_num):
    if shift == 1:
        if day == "Понедельник":
            times = {0: "8.30 – 9.00", 1: "9.00-10.20", 2: "9.00-10.20", 3: "10.30-11.50", 4: "10.30-11.50", 5: "12.10-13.30", 6: "12.10-13.30", 7: "13.40-15.00", 8: "13.40-15.00"}
        else:
            times = {1: "8.30-9.50", 2: "8.30-9.50", 3: "10.00-11.20", 4: "10.00-11.20", 5: "11.40-13.00", 6: "11.40-13.00", 7: "13.30-14.50", 8: "13.30-14.50"}
    else:
        if day == "Понедельник":
            times = {0: "13.40 – 14.10", 1: "14.10-15.30", 2: "14.10-15.30", 3: "15.40-17.00", 4: "15.40-17.00", 5: "17.10-18.20", 6: "17.10-18.20"}
        else:
            times = {0: "11.40-13.00", 1: "13.30-14.50", 2: "13.30-14.50", 3: "15.00-16.20", 4: "15.00-16.20", 5: "16.30-17.50", 6: "16.30-17.50"}
    return times.get(lesson_num, "Время не указано")

TOTAL_SCHEDULES = {
    "2601": {"shift": 1, "schedule": {
        "Понедельник": [(0, "Классный час", "ауд. 414", ""), (1, "Физика", "ауд. 414", "Лукашова О.А."), (3, "Литература", "ауд. 311", "Гущина А.И."), (5, "Биология", "ауд. 312", "Палишев В.Н.")],
        "Вторник": [(1, "Химия", "ауд. 316", "Воробьева М.В."), (3, "Информатика", "ауд. 215", "Семенников К.А."), (5, "Математика", "ауд. 102", "Черепанова А.Ф.")]
    }},
    "2602": {"shift": 1, "schedule": {
        "Понедельник": [(0, "Классный час", "ауд. 210", ""), (1, "Математика", "ауд. 210", "Агеева О.А."), (3, "Химия", "ауд. 410", "Юричич О.В."), (5, "Физкультура", "сп.зал", "Сакнэ Ю.Л.")],
        "Вторник": [(1, "Информатика", "ауд. 215", "Семенников К.А."), (3, "История", "ауд. 315", "Морозова Е.В."), (5, "Осн. проект. деят-ти", "ауд. 311", "Гущина А.И.")]
    }},
    "2603": {"shift": 1, "schedule": {
        "Понедельник": [(0, "Классный час", "ауд. 215", ""), (1, "Информатика", "ауд. 215", "Семенников К.А."), (3, "География", "ауд. 316", "Ильиных О.А."), (5, "Осн. проект. деят-ти", "ауд. 210", "Агеева О.А.")],
        "Вторник": [(1, "Математика", "ауд. 210", "Агеева О.А."), (3, "Физика", "ауд. 414", "Лукашова О.А."), (5, "Физкультура", "сп.зал", "Сакнэ Ю.Л.")]
    }},
    "2604": {"shift": 1, "schedule": {
        "Понедельник": [(3, "Математика", "ауд. 210", "Агеева О.А."), (5, "Информатика", "ауд. 216", "Караманова"), (7, "История", "ауд. 315", "Морозова Е.В.")],
        "Вторник": [(1, "Биология", "ауд. 312", "Палишев В.Н."), (3, "Физкультура", "сп.зал", "Сакнэ Ю.Л."), (5, "ОБЖ", "ауд. 413", "Барматков А.М.")]
    }},
    "2605": {"shift": 1, "schedule": {
        "Понедельник": [(3, "Химия", "ауд. 310", "Воробьева М.В."), (5, "ОБЖ", "ауд. 413", "Барматков А.М."), (7, "Математика", "ауд. 210", "Агеева О.А.")],
        "Вторник": [(1, "Информатика", "ауд. 216", "Караманова"), (3, "Математика", "ауд. 210", "Агеева О.А."), (5, "Осн. проект. деят-ти", "ауд. 410", "Мишарина А.С.")]
    }},
    "2606": {"shift": 1, "schedule": {
        "Понедельник": [(0, "Классный час", "ауд. 216", ""), (1, "Информатика", "ауд. 216", "Караманова"), (3, "ОБЖ", "ауд. 413", "Барматков А.М."), (5, "География", "ауд. 316", "Ильиных О.А.")],
        "Вторник": [(1, "История", "ауд. 314", "Клецерман Н.Н."), (3, "Математика", "ауд. 102", "Черепанова А.Ф."), (5, "Химия", "ауд. 316", "Воробьева М.В.")]
    }},
    "2614": {
        "shift": 1,
        "schedule": {
            "Понедельник": [(0, "Классный час", "ауд. 310", ""), (1, "Химия", "ауд. 310", "Воробьева М.В."), (3, "Математика", "ауд. 101", "Черепанова А.Ф."), (5, "ПЦ: Управление ассортиментом", "ауд. 415", "Глубоких Н.А."), (7, "Биология", "ауд. 312", "Палишев В.Н.")],
            "Вторник": [(1, "Физика", "ауд. 414", "Лукашова О.А."), (3, "Литература", "ауд. 311", "Гущина А.И."), (5, "История", "ауд. 314", "Клецерман Н.Н.")],
            "Среда": [(3, "ОБЖ", "ауд. 413", "Барматков А.М."), (5, "Химия", "ауд. 316", "Воробьева М.В."), (7, "Биология", "ауд. 312", "Палишев В.Н.")],
            "Четверг": [(3, "Химия", "ауд. 316", "Воробьева М.В."), (5, "Информатика", "ауд. 215", "Семенников К.А."), (7, "Математика", "ауд. 414", "Черепанова А.Ф.")],
            "Пятница": [(1, "Биология", "дист", "Палишев В.Н."), (3, "Физика", "дист", "Лукашова О.А."), (5, "ОБЖ", "дист", "Барматков А.М.")],
            "Суббота": [(1, "Математика", "дист", "Черепанова А.Ф."), (3, "Литература", "дист", "Гущина А.И."), (5, "История", "дист", "Клецерман Н.Н.")]
        }
    }
}

def get_schedule_keyboard():
    buttons = [[KeyboardButton(text="Понедельник"), KeyboardButton(text="Вторник")], [KeyboardButton(text="Среда"), KeyboardButton(text="Четверг")], [KeyboardButton(text="Пятница"), KeyboardButton(text="Суббота")], [KeyboardButton(text="🔙 Сменить группу")]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_group_keyboard():
    group_names = sorted(list(TOTAL_SCHEDULES.keys()))
    buttons = []
    for i in range(0, len(group_names), 3):
        row = [KeyboardButton(text=f"Группа {group_names[i]}")]
        if i + 1 < len(group_names): row.append(KeyboardButton(text=f"Группа {group_names[i+1]}"))
        if i + 2 < len(group_names): row.append(KeyboardButton(text=f"Группа {group_names[i+2]}"))
        buttons.append(row)
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(UserState.choosing_group)
    await message.answer("Привет! 👋 Я бот-расписание КемТИПиСУ.\n\n*Пожалуйста, выберите учебную группу:*", reply_markup=get_group_keyboard(), parse_mode="Markdown")

@dp.message(UserState.viewing_schedule, F.text == "🔙 Сменить группу")
async def change_group(message: Message, state: FSMContext):
    await state.set_state(UserState.choosing_group)
    await message.answer("Выберите учебную группу:", reply_markup=get_group_keyboard())

@dp.message(UserState.choosing_group, F.text.startswith("Группа "))
async def group_selected(message: Message, state: FSMContext):
    selected_group = message.text.replace("Группа ", "")
    if selected_group in TOTAL_SCHEDULES:
        await state.update_data(user_group=selected_group)
        await state.set_state(UserState.viewing_schedule)
        await message.answer(f"Выбрана группа *{selected_group}*.\n\nВыберите день недели на кнопках ниже:", reply_markup=get_schedule_keyboard(), parse_mode="Markdown")
    else:
        await message.answer("Ошибка! Данные группы обновляются.")

@dp.message(UserState.viewing_schedule, F.text.in_(["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]))
async def send_schedule(message: Message, state: FSMContext):
    day = message.text
    user_data = await state.get_data()
    user_group = user_data.get("user_group")
    group_data = TOTAL_SCHEDULES[user_group]

    pair_names = {0: "⚠️ Спец-час", 1: "1-я пара", 2: "1-я пара", 3: "2-я пара", 4: "2-я пара", 5: "3-я пара", 6: "3-я пара", 7: "4-я пара", 8: "4-я пара"}
    pair_emojis = {0: "🯉", 1: "❶", 2: "❶", 3: "❷", 4: "❷", 5: "❸", 6: "❸", 7: "❹", 8: "❹"}

    # Авторасчет точной календарной даты (например, 13.10.2026)
    days_map = {"Понедельник": 0, "Вторник": 1, "Среда": 2, "Четверг": 3, "Пятница": 4, "Суббота": 5}
    today = datetime.date.today()
    current_weekday = today.weekday()
    target_day_diff = days_map[day] - current_weekday
    target_date = today + datetime.timedelta(days=target_day_diff)
    formatted_date = target_date.strftime("%d.%m.%Y")

    response = f"📅 <b>{day} ({formatted_date}) | Группа {user_group}</b>\n\n"
    day_lessons = group_data["schedule"].get(day)
    if not day_lessons:
        await message.answer(response + "🎉 <b>Занятий в этот день нет!</b>", parse_mode="HTML")
        return

    for lesson_num, subject, cabinet, teacher in day_lessons:
        time_str = get_lesson_time(group_data["shift"], day, lesson_num)
        pair_label = "Классный час" if lesson_num == 0 else pair_names.get(lesson_num, f"{lesson_num}-я пара")
        pair_icon = "🔔" if lesson_num == 0 else pair_emojis.get(lesson_num, "🔹")

        response += f"<blockquote>{pair_icon} <b>{time_str}</b>\n{pair_label}\n{subject}\n"
        emoji = "💻" if "дист" in cabinet.lower() else "📗"
        response += f"{emoji} {cabinet}\n"
        if teacher: response += f"<b>{teacher}</b>\n"
        response += "</blockquote>\n"

    await message.answer(response, parse_mode="HTML")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
