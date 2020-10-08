import vk_api
import config
import keyboard

from asyncio import create_task, run
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from database import DataBase
from stage import Stage
from strings import String

vk = ... # объект для работы с api
db = ... # объект для работы с базой данных

def getStage(user_id): # получаем текущую стадию диалога
    result = db.getOne('SELECT stage FROM users WHERE user_id = ?', [user_id])

    if result != None:
        return result[0]

def setStage(user_id, stage): # ставим текущую стадию диалога
    db.edit("UPDATE users SET stage = ? WHERE user_id = ?", [stage, user_id])

def sendMessage(user_id, text, keyboard=None): # отправка сообщения
    vk.method('messages.send', {
        'user_id': user_id,
        'message': text,
        'random_id': get_random_id(),
        'keyboard': keyboard
    })

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
            sendMessage(user_id, String.ENTER_LINK)
            setStage(user_id, Stage.ENTER_LINK)
    
    elif getStage(user_id) == Stage.ENTER_LINK: # Ввод ссылки
        if text == "Назад":
            sendMessage(user_id, String.START, keyboard.mainMenu())
            setStage(user_id, Stage.MAIN_MENU)

async def main():
    longpoll = VkLongPoll(vk)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW: # если пришло сообщение - передаем его функции onMessage
            await create_task(onMessage(event))

if __name__ == "__main__":
    vk = vk_api.VkApi(token=config.TOKEN)
    db = DataBase('database.db')
    db.edit("CREATE TABLE IF NOT EXISTS users(user_id INTEGER, stage INTEGER)")
    run(main()) # асинхронно запускаем функцию main