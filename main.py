import vk_api
import config
import keyboard
import data

from asyncio import create_task, run
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from database import DataBase
from stage import Stage
from strings import String
from datetime import datetime

bot = ... # объект для работы с ботом
vk = ... # объект для работы с методами вк
db = ... # объект для работы с базой данных

def getStage(user_id): # получаем текущую стадию диалога
    result = db.getOne('SELECT stage FROM users WHERE user_id = ?', [user_id])

    if result != None:
        return result[0]

def setStage(user_id, stage): # ставим текущую стадию диалога
    db.edit("UPDATE users SET stage = ? WHERE user_id = ?", [stage, user_id])

def sendMessage(user_id, text, keyboard=None): # отправка сообщения
    bot.method('messages.send', {
        'user_id': user_id,
        'message': text,
        'random_id': get_random_id(),
        'keyboard': keyboard
    })

async def getData(user_id): # получение информации о пользователе (возраст, город, школа)
    try:
        search_id = await data.resolveScreenName(user_id, vk)
        friends = await data.getFriends(search_id, vk)
        user_ids = str(friends).replace('[', '').replace(']', '') # так надо
        search_result = await data.search(user_ids, vk)
    except Exception:
        search_result = None

    return search_result

async def genetateStats(search_result):
    bdate = int(await data.sort_data(search_result[1]))
    year = int(datetime.now().year)

    city = await data.sort_data(search_result[0])
    age = year - bdate
    school = await data.sort_data(search_result[2])

    return String.USER_INFORMATION.format(city, age, bdate, school)

async def onMessage(event):
    user_id = event.user_id
    text = event.text
    
    if text == "Начать": # Первый запуск
        result = db.getOne("SELECT user_id FROM users WHERE user_id = ?", [user_id])
        if result == None:
            sendMessage(user_id, String.FIRST_START, keyboard.mainMenu())
            db.edit("INSERT INTO users VALUES(?, ?)", [user_id, Stage.MAIN_MENU]) # добавляем нового пользователя в базу
        else:
            sendMessage(user_id, String.START, keyboard.mainMenu())
            setStage(user_id, Stage.MAIN_MENU)
    
    elif getStage(user_id) == Stage.MAIN_MENU: # Главное меню
        if text == "Информация о пользователе":
            sendMessage(user_id, String.ENTER_LINK, keyboard.back())
            setStage(user_id, Stage.USER_ENTER_LINK)
        elif text == "Мониторинг друзей":
            sendMessage(user_id, String.FUNCTION_ERROR, keyboard.mainMenu())
        elif text == "Возможные дружеские связи":
            sendMessage(user_id, String.FUNCTION_ERROR, keyboard.mainMenu())
    
    elif getStage(user_id) == Stage.USER_ENTER_LINK: # Информация о пользователе
        if text == "Назад":
            sendMessage(user_id, String.START, keyboard.mainMenu())
            setStage(user_id, Stage.MAIN_MENU)
        else:
            data = await getData(text.split('/')[-1])
            if data == None:
                sendMessage(user_id, String.SEARCH_ERROR)
                return

            setStage(user_id, Stage.MAIN_MENU)
            sendMessage(user_id, await genetateStats(data), keyboard.mainMenu())

async def main():
    longpoll = VkLongPoll(bot)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me: # если пришло сообщение - передаем его функции onMessage
            await create_task(onMessage(event))

if __name__ == "__main__":
    bot = vk_api.VkApi(token=config.BOT_TOKEN)
    vk = vk_api.VkApi(token=config.VK_TOKEN)

    db = DataBase('database.db')
    db.edit("CREATE TABLE IF NOT EXISTS users(user_id INTEGER, stage INTEGER)")

    run(main()) # асинхронно запускаем функцию main