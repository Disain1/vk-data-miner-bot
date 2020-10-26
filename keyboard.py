from vk_api.keyboard import VkKeyboard, VkKeyboardColor

def mainMenu():
    k = VkKeyboard(one_time=True)

    k.add_button('Информация о пользователе')
    k.add_line()
    k.add_button('Мониторинг друзей', color=VkKeyboardColor.NEGATIVE)
    k.add_line()
    k.add_button('Возможные дружеские связи', color=VkKeyboardColor.NEGATIVE)

    return k.get_keyboard()

def back():
    k = VkKeyboard(one_time=True)
    k.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    return k.get_keyboard()

