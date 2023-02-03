from aiogram import types

start_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
start_menu.add("Меню")

start_menu_inline = types.InlineKeyboardMarkup()
b1 = types.InlineKeyboardButton(text="Мой баланс", callback_data="balance")
b2 = types.InlineKeyboardButton(text="Пополнить", callback_data="cash_in")
c1 = types.InlineKeyboardButton(text="Вывод средств", callback_data="cash_out")
c2 = types.InlineKeyboardButton(text="Царь горы 👑⛰", callback_data="king_of_the_hill")
c3 = types.InlineKeyboardButton(text="Игра в кости 🎲", callback_data="game_of_dice")
c4 = types.InlineKeyboardButton(text="Розыгрыш ТГ премиум", callback_data="tg_premium_draw")
c5 = types.InlineKeyboardButton(text="Тех поддержка", url='https://t.me/dfhgfdthj')
c6 = types.InlineKeyboardButton(text="Группа с отзывами", url='https://t.me/ezwinf')
c7 = types.InlineKeyboardButton(text="Группа с отчётами", url='https://t.me/ezwinreports')
start_menu_inline.add(*(b1, b2, c1)).add(*(c2, c3)).add(c5).add(*(c6, c7))

king_of_the_hill_menu = types.InlineKeyboardMarkup()
j1 = types.InlineKeyboardButton(text="Сделать ставку", callback_data="make_a_bet")
j2 = types.InlineKeyboardButton(text="Обновить результаты", callback_data="update_results" )
j3 = types.InlineKeyboardButton(text="Правила игры", callback_data="rules_game_king_hill")
j4 = types.InlineKeyboardButton(text="Меню", callback_data="inline_menu")
king_of_the_hill_menu.add(*(j2, j1)).add(j3).add(j4)

king_of_the_hill_menu_1 = types.InlineKeyboardMarkup()
j6 = types.InlineKeyboardButton(text="Назад", callback_data="update_results")
king_of_the_hill_menu_1.add(j6).add(j4)

game_of_dice_menu = types.InlineKeyboardMarkup()
g1 = types.InlineKeyboardButton(text="Зарегистрироваться", callback_data="dice_registration")
g2 = types.InlineKeyboardButton(text="Отменить регистрацию", callback_data="dice_cancel_registration" )
g3 = types.InlineKeyboardButton(text="Правила игры", callback_data="rules_game_dice")
g5 = types.InlineKeyboardButton(text="Обновить", callback_data="refresh_game_dice")
g4 = types.InlineKeyboardButton(text="Меню", callback_data="inline_menu")
game_of_dice_menu.add(*(g1, g2)).add(*(g3, g5)).add(g4)

game_of_dice_menu_1 = types.InlineKeyboardMarkup()

game_of_dice_menu_1.add(*(g3, g5)).add(g4)

game_of_dice_menu_rules = types.InlineKeyboardMarkup()
g6 = types.InlineKeyboardButton(text="Назад", callback_data="refresh_game_dice")
game_of_dice_menu_rules.add(g6).add(g4)


put_on_balance_inline = types.InlineKeyboardMarkup()
b4 = types.InlineKeyboardButton(text="Пополнить через yoomoney, kiwi, карта РФ", callback_data="yoomoney")
# b5 = types.InlineKeyboardButton(text="Как пополнять?", callback_data="instruction_yoomoney")
b6 = types.InlineKeyboardButton(text="Меню", callback_data="inline_menu")
put_on_balance_inline.add(b4).add(b6)

remove_from_balance_inline = types.InlineKeyboardMarkup()
b4 = types.InlineKeyboardButton(text="На кошелёк yoomoney", callback_data="cash_out_yoomoney")
# b5 = types.InlineKeyboardButton(text="Как выводить?", callback_data="instruction_yoomoney")
b6 = types.InlineKeyboardButton(text="На карту РФ, kiwi через оператора", callback_data="cash_out_operator")
b7 = types.InlineKeyboardButton(text="Меню", callback_data="inline_menu")
remove_from_balance_inline.add(*(b4, b6)).add(b7)

chek_payment_inline = types.InlineKeyboardMarkup()
b7 = types.InlineKeyboardButton(text="я оплатил", callback_data="chek_payment")
b8 = types.InlineKeyboardButton(text="Меню", callback_data="inline_menu_from_payment")
chek_payment_inline.add(*(b7, b8))

