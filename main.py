import asyncio
import sys
import requests
import datetime
import random
from yoomoney import Quickpay
from yoomoney import Client


import aiogram.contrib.fsm_storage.memory
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from keyboards import start_menu, start_menu_inline, put_on_balance_inline, chek_payment_inline, \
    remove_from_balance_inline, king_of_the_hill_menu, game_of_dice_menu, game_of_dice_menu_rules, \
    king_of_the_hill_menu_1, game_of_dice_menu_1
from state import Test
import config
from DB.function_POSTGRESQL import DB

storage = aiogram.contrib.fsm_storage.memory.MemoryStorage()
token = config.token
BOT = Bot(token=token)
COMMANDS = Dispatcher(BOT, storage=storage)
state_dict = {}


list_images_id = ['AgACAgIAAxkBAAO5Y4TzJNDeGpgNNcv6KHUbIeYnc2QAAo3FMRsxdyhIRqlHcYKmUJQBAAMCAAN5AAMrBA',
                  'AgACAgIAAxkBAAPvY4T2wDR2Y5qgUmvGv6DWogheDbcAAqjFMRsxdyhI2Zmk1mcs4esBAAMCAAN5AAMrBA',
                  'AgACAgIAAxkBAAPTY4T1X1QI6IX5c9z3hlgFpoYf3TcAAqLFMRsxdyhIHOVb347iyPEBAAMCAAN5AAMrBA',
                  'AgACAgIAAxkBAAPDY4T1EQsV255QAr6NJDu4UiEj2ukAApnFMRsxdyhIUOFVnBB2bZgBAAMCAAN4AAMrBA',
                  'AgACAgIAAxkBAAID4WOjKmVP2w_sOlnfZqSCdUtTcX_IAAIfyDEbdCoZSUDHp_60EG3SAQADAgADeAADLAQ',
                  'AgACAgIAAxkBAAID42OjKo2MfrPzU_359pFxNC0rxGCeAAIgyDEbdCoZSdy6p8nJceJsAQADAgADeQADLAQ',
                  'AgACAgIAAxkBAAID5WOjKqVfDWPnpOWkLXcjyAGjdsdaAAIhyDEbdCoZSVHlULlJJuZeAQADAgADeAADLAQ'
                  ]


@COMMANDS.message_handler(state=Test.state1)
async def write_info(message: types.Message, state: FSMContext):
    pass


@COMMANDS.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет")
    await BOT.send_photo(message.chat.id, random.choice(list_images_id), reply_markup=start_menu_inline)
    sql = DB('telegram_game_bot')
    if not sql.read_on_user_id_tg(message.from_user.id):
        sql.write('bot_users', user_id_tg=message.from_user.id,
                  first_name=message.from_user.first_name,
                  last_name=message.from_user.last_name,
                  username=message.from_user.username,
                  balance_rub=0,
                  date_registration=datetime.datetime.now())
    sql.close()



@COMMANDS.message_handler(regexp='Меню')
async def texts(message: types.Message):
    await BOT.send_photo(message.chat.id, random.choice(list_images_id), reply_markup=start_menu_inline)


@COMMANDS.message_handler(content_types=types.ContentType.PHOTO)
async def texts(message: types.Message):
    await message.reply(message.photo[-1].file_id)


@COMMANDS.callback_query_handler(text="balance")
async def add_chat(call: types.CallbackQuery):
    sql = DB('telegram_game_bot')
    user_info_db = list(sql.check_list_info_user(call.from_user.id))
    user_info_tg = [call.from_user.first_name, call.from_user.username]
    balance = user_info_db[2]
    if user_info_tg != user_info_db[:2]:
        sql.update_info_user(call.from_user.first_name, call.from_user.username, call.from_user.id)
    sql.close()
    await BOT.answer_callback_query(call.id, text=f'Ваш баланс {balance} Руб.', show_alert=True)


@COMMANDS.callback_query_handler(text="cash_in")
async def add_chat(call: types.CallbackQuery):
    await BOT.edit_message_reply_markup(call.from_user.id, call.message.message_id, call.inline_message_id,
                                        reply_markup=put_on_balance_inline)


@COMMANDS.callback_query_handler(text="cash_out")
async def add_chat(call: types.CallbackQuery):
    await BOT.edit_message_reply_markup(call.from_user.id, call.message.message_id, call.inline_message_id,
                                        reply_markup=remove_from_balance_inline)


@COMMANDS.callback_query_handler(text="inline_menu")
async def add_chat(call: types.CallbackQuery):
    photo = types.InputMedia(type=types.ContentType.PHOTO, media=random.choice(list_images_id))
    await BOT.edit_message_media(photo, call.from_user.id, call.message.message_id, call.inline_message_id,
                                 reply_markup=start_menu_inline)


@COMMANDS.callback_query_handler(text="inline_menu_from_payment")
async def add_chat(call: types.CallbackQuery):
    try:
        await BOT.delete_message(call.from_user.id, call.message.message_id)
    except aiogram.exceptions.MessageCantBeDeleted:
        await BOT.edit_message_reply_markup(call.from_user.id, call.message.message_id)
    await BOT.send_photo(call.from_user.id, random.choice(list_images_id), reply_markup=start_menu_inline)


async def get_winner_king_hill(sql: DB, dict_data_game: dict):
    if dict_data_game['date_end_game']:
        if dict_data_game["date_end_game"] < datetime.datetime.now().replace(microsecond=0):
            sql.update_balance_user(dict_data_game["leader_id_tg"], dict_data_game["bank"])
            sql.set_start_values_king_hill()
            await BOT.send_message(dict_data_game["leader_id_tg"],
                                   f'Вы царь горы! Ваш выигрыш {dict_data_game["bank"]} руб ')
            return True


async def process_game_king_hill():
    sql = DB('telegram_game_bot')
    dict_data_game = sql.read_king_hill()
    text_game = 'Игра не начата, Вы можете сделать первую ставку и стать царём горы!' \
                '\nБанк                                      0 руб' \
                '\nЛидирующая ствка      0 руб' \
                '\nИмя лидера                      нет' \
                '\nId лидера                           нет' \
                '\nВремя до победы          0 мин' \
                '\n\nСледующая ставка 100 руб'
    text_game_html = '<b><i>Игра не начата, Вы можете сделать первую ставку и стать царём горы!</i></b>' \
                '\n<b>Банк</b>                                      <i>0 руб</i>' \
                '\n<b>Лидирующая ствка</b>      <i>0 руб</i>' \
                '\n<b>Имя лидера</b>                      <i>нет</i>' \
                '\n<b>Id лидера</b>                           <i>нет</i>' \
                '\n<b>Время до победы</b>          <i>0 мин</i>' \
                '\n\n<i>Следующая ставка 100 руб</i>'
    if dict_data_game["date_end_game"]:
        if not await get_winner_king_hill(sql, dict_data_game):
            time_to_end = dict_data_game["date_end_game"] - datetime.datetime.now().replace(microsecond=0)
            text_game = 'Игра началась!' \
                        f'\nБанк                                      {dict_data_game["bank"]} руб' \
                        f'\nЛидирующая ствка      {dict_data_game["last_bet"]} руб' \
                        f'\nИмя лидера                      {dict_data_game["leader_name"]}' \
                        f'\nId лидера                           {dict_data_game["leader_id_tg"]}' \
                        f'\nВремя до победы          {time_to_end} сек' \
                        f'\n\nСледующая ставка {dict_data_game["last_bet"] + 100} руб'
            text_game_html = '<b><i>Игра началась!</i></b>' \
                        f'\n<b>Банк</b>                                      <i>{dict_data_game["bank"]} руб</i>' \
                        f'\n<b>Лидирующая ствка</b>      <i>{dict_data_game["last_bet"]} руб</i>' \
                        f'\n<b>Имя лидера</b>                      <i>{dict_data_game["leader_name"]}</i>' \
                        f'\n<b>Id лидера</b>                           <i>{dict_data_game["leader_id_tg"]}</i>' \
                        f'\n<b>Время до победы</b>          <i>{time_to_end} сек</i>' \
                        f'\n\n<i>Следующая ставка {dict_data_game["last_bet"] + 100} руб</i>'
    sql.close()
    return text_game, text_game_html


@COMMANDS.callback_query_handler(text="king_of_the_hill")
async def add_chat(call: types.CallbackQuery):
    text_game, text_game_html = await process_game_king_hill()
    try:
        await BOT.delete_message(call.from_user.id, call.message.message_id)
    except aiogram.exceptions.MessageCantBeDeleted:
        await BOT.edit_message_reply_markup(call.from_user.id, call.message.message_id)
    await BOT.send_photo(call.from_user.id, 'AgACAgIAAxkBAAIEPmOjOjnUHJJ4M4R4Jh_ibRohZzJ8AAJpyDEbdCoZSVWo1gtgdUm4AQADAgADeQADLAQ', text_game_html, reply_markup=king_of_the_hill_menu, parse_mode='HTML')


@COMMANDS.callback_query_handler(text="update_results")
async def update_results_king_hill(call: types.CallbackQuery):
    text_game, text_game_thml = await process_game_king_hill()
    if text_game == call.message.caption:
        await BOT.answer_callback_query(call.id, text=f'Результаты обновлены')
    else:
        await BOT.edit_message_caption(call.from_user.id, call.message.message_id, call.inline_message_id, text_game_thml, reply_markup=king_of_the_hill_menu, parse_mode='HTML')
        await BOT.answer_callback_query(call.id, text=f'Результаты обновлены')


@COMMANDS.callback_query_handler(text="make_a_bet")
async def add_chat(call: types.CallbackQuery):
    index = call.message.caption.find('Следующая ставка')
    current_bet_from_message = float(call.message.caption[index:].split(' ')[2])
    sql = DB('telegram_game_bot')
    dict_data_game = sql.read_king_hill()
    if await get_winner_king_hill(sql, dict_data_game):
        dict_data_game = sql.read_king_hill()
    balance_user = sql.chek_balance_user(call.from_user.id)[0]
    current_bet = dict_data_game["last_bet"] + 100
    if current_bet_from_message == current_bet:
        if dict_data_game["leader_id_tg"] == call.from_user.id:
            await BOT.answer_callback_query(call.id, text=f'Ваша ставка уже лидирует')
        else:
            if current_bet > balance_user:
                await BOT.answer_callback_query(call.id, text=f'У Вас недостаточно средств, пополните баланс', show_alert=True)
            else:
                sql.update_balance_user_minus(call.from_user.id, current_bet)
                sql.update_values_king_hill(dict_data_game["bank"]+current_bet, current_bet, call.from_user.first_name,
                                            call.from_user.id, datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(minutes=2))
                await BOT.answer_callback_query(call.id, text=f'Тепер Вы царь горы!', show_alert=True)
                await update_results_king_hill(call)
    else:
        await BOT.answer_callback_query(call.id, text=f'Данные не совпали')
        await update_results_king_hill(call)
    sql.close()


@COMMANDS.callback_query_handler(text="game_of_dice")
async def func_game_dice(call: types.CallbackQuery):
    try:
        await BOT.delete_message(call.from_user.id, call.message.message_id)
    except aiogram.exceptions.MessageCantBeDeleted:
        await BOT.edit_message_reply_markup(call.from_user.id, call.message.message_id)
    sql = DB('telegram_game_bot')
    data_game = sql.read_game_of_dice()
    len_game = len(data_game)
    if len_game < config.number_dicers:
        text_game_html = f'<b><i>В игре участвуют {config.number_dicers} человек, ставка каждого игрока: {config.bet_dicer} руб, победитель забирает всё!' \
                         f'\nУчаствующие игроки: </i></b>'
        for el in data_game:
            text_game_html += f'\n{el[0]} id {el[1]}'

        await BOT.send_photo(call.from_user.id,
                             'AgACAgIAAxkBAAIFKmOxyjqFy7w9lZNucIO2iPP2ySJbAAKqwzEbHFWQSdLmAAHDygsPCwEAAwIAA3kAAy0E',
                             text_game_html, reply_markup=game_of_dice_menu, parse_mode='HTML')
    else:
        text_game_html = f'<b><i>Игра запущена!</i></b>'
        await BOT.send_photo(call.from_user.id,
                             'AgACAgIAAxkBAAIFKmOxyjqFy7w9lZNucIO2iPP2ySJbAAKqwzEbHFWQSdLmAAHDygsPCwEAAwIAA3kAAy0E',
                             text_game_html, reply_markup=game_of_dice_menu_1, parse_mode='HTML')
    sql.close()


@COMMANDS.callback_query_handler(text="refresh_game_dice")
async def func_refresh_game_dice(call: types.CallbackQuery):
    sql = DB('telegram_game_bot')
    data_game = sql.read_game_of_dice()
    len_game = len(data_game)
    if len_game < config.number_dicers:
        text_game = f'В игре участвуют {config.number_dicers} человек, ставка каждого игрока: {config.bet_dicer} руб, победитель забирает всё!' \
                         f'\nУчаствующие игроки: '
        text_game_html = f'<b><i>В игре участвуют {config.number_dicers} человек, ставка каждого игрока: {config.bet_dicer} руб, победитель забирает всё!' \
                         f'\nУчаствующие игроки: </i></b>'
        markup = game_of_dice_menu
        for el in data_game:
            text_user = f'\n{el[0]} id {el[1]}'
            text_game_html += text_user
            text_game += text_user
    else:
        text_game = f'Игра запущена!'
        text_game_html = f'<b><i>Игра запущена!</i></b>'
        markup = game_of_dice_menu_1
    if text_game == call.message.caption:
        await BOT.answer_callback_query(call.id, text=f'Результаты обновлены')
    else:
        await BOT.edit_message_caption(call.from_user.id, call.message.message_id, call.inline_message_id,
                                       text_game_html, reply_markup=markup, parse_mode='HTML')
        await BOT.answer_callback_query(call.id, text=f'Результаты обновлены')
    sql.close()


@COMMANDS.callback_query_handler(text="dice_registration")
async def add_chat(call: types.CallbackQuery):
    sql = DB('telegram_game_bot')
    balance_user = sql.chek_balance_user(call.from_user.id)[0]
    if balance_user >= config.bet_dicer:
        data_game = sql.read_game_of_dice()
        if len(data_game) < config.number_dicers-1:
            error_registration = sql.write_game_of_dice(call.from_user.first_name, call.from_user.id, None, True, datetime.datetime.now())
            if error_registration:
                await BOT.answer_callback_query(call.id, text=f'Ошибка, вы уже в игре', show_alert=True)
            else:
                sql.update_balance_user_minus(call.from_user.id, config.bet_dicer)
                await BOT.answer_callback_query(call.id, text=f'Вы успешно зарегистрированы', show_alert=True)
                await func_refresh_game_dice(call)
        elif len(data_game) == config.number_dicers-1:
            error_registration = sql.write_game_of_dice(call.from_user.first_name, call.from_user.id, None, True, datetime.datetime.now())
            if error_registration:
                await BOT.answer_callback_query(call.id, text=f'Ошибка, вы уже в игре', show_alert=True)
            else:
                sql.update_balance_user_minus(call.from_user.id, config.bet_dicer)
                await BOT.answer_callback_query(call.id, text=f'Вы успешно зарегистрированы', show_alert=True)
                await func_refresh_game_dice(call)
                await process_game_dice()
        else:
            await BOT.answer_callback_query(call.id, text=f'Нет мест', show_alert=True)
            await func_refresh_game_dice(call)
    else:
        await BOT.answer_callback_query(call.id, text=f'Не хватает денег', show_alert=True)


async def process_game_dice():
    sql = DB('telegram_game_bot')
    data_game = sql.read_game_of_dice_with_username()
    text_for_group = 'Игра в кости\n'
    for el in data_game:
        user_id = el[0]
        in_game = el[2]
        username = el[3]
        name = el[4]
        if in_game:
            result = await BOT.send_dice(user_id)
            value = result.dice.value
            sql.write_result_game_dice(value, user_id)
            text_for_group += f'игрок {name} c юзернеймом @{username} выбросил {value}\n'
    await BOT.send_message(config.group_reports_id, text_for_group)
    winner = get_winner()
    if winner:
        win_value = config.bet_dicer*config.number_dicers
        sql.clear_game_of_dice()
        sql.update_balance_user(winner[0], win_value)
        await BOT.send_message(winner[0], f'Вы побели! Ваш выигрыш {win_value} руб.')
        name, username = sql.read_user_info_on_id(winner[0])
        await BOT.send_message(config.group_reports_id, f'Игра в кости, победил игрок {name} c юзернеймом @{username}, выйгрыш {win_value}')
        sql.close()
    else:
        sql.close()
        await process_game_dice()



@COMMANDS.callback_query_handler(text="dice_cancel_registration")
async def add_chat(call: types.CallbackQuery):
    sql = DB('telegram_game_bot')
    registration = sql.check_registration_game_dice(call.from_user.id)
    if not registration:
        await BOT.answer_callback_query(call.id, text=f'Вы не зарегистрированы', show_alert=True)
    elif registration[0]:
        await BOT.answer_callback_query(call.id, text=f'Нельзя отменить регистрацию во время игры', show_alert=True)
        await func_refresh_game_dice(call)
    elif not registration[0]:
        sql.delete_dicer(call.from_user.id)
        sql.update_balance_user(call.from_user.id, config.bet_dicer)
        await BOT.answer_callback_query(call.id, text=f'Вы успешно удалены из игры', show_alert=True)
        await func_refresh_game_dice(call)



def get_winner():
    sql = DB('telegram_game_bot')
    table = sql.read_game_of_dice()
    if table:
        winner_list = []
        winner_value = 1
        for el in table:
            dicer_id_tg = el[1]
            result = el[2]
            in_game = el[3]
            if in_game:
                if result > winner_value:
                    winner_list.clear()
                    winner_list.append(dicer_id_tg)
                    winner_list.append(result)
                    winner_value = result
                elif result == winner_value:
                    winner_list.append(dicer_id_tg)
                    winner_list.append(result)
        for el in table:
            dicer_id_tg = el[1]
            in_game = el[3]
            if in_game:
                if dicer_id_tg not in winner_list:
                    sql.kick_player_game_of_dice(dicer_id_tg)
        sql.close()
        if len(winner_list) == 2:
            return winner_list
        else:
            return False


@COMMANDS.callback_query_handler(text="rules_game_dice")
async def add_chat(call: types.CallbackQuery):
    text_game_html = f'<b><i>Игра в кости</i></b>\n' \
                     f'В игре участвуют от 3 до 10 человек.\n' \
                     f'Каждый игрок делает ставку нажимая кнопку "Зарегистрироваться" . ' \
                     f'Как только набирается необходимое количество участников бот присылает ' \
                     f'каждому игроку кубик и сравнивает результаты , победитель забирает все ставки, ' \
                     f'если есть 2 и более победителя они повторно выбрасывают кубик.\n' \
                     f'Кнопка "Отменить регистрацию" удалит вас из игры и вернёт ставку\n' \
                     f'Кнопка "Обновить" покажет актуальное количество зарегистрированных игроков'
    await BOT.edit_message_caption(call.from_user.id, call.message.message_id, call.inline_message_id,
                                   text_game_html, reply_markup=game_of_dice_menu_rules, parse_mode='HTML')


@COMMANDS.callback_query_handler(text="rules_game_king_hill")
async def f_rules_game_king_hill(call: types.CallbackQuery):
    text = '<b><i>Царь горы</i></b>\n' \
           'Количество игроков не ограничено.\n' \
           'Нажимая кнопку "Сделать ставку" у Вас списывается сумма ' \
           'указанная в поле "Следующая ставка" и вы становитесь "царем горы" ' \
           'в этот момент запускается таймер (2 минуты), если никто не поставит ' \
           'больше в течении этого времени вы забираете весь банк. В банк складываются ' \
           'все ставки игроков. Каждая последующая ставка больше на 100 руб.\n' \
           'Кнопка "Обновить результаты" показывает актуальную информацию о игре.'

    await BOT.edit_message_caption(call.from_user.id, call.message.message_id, call.inline_message_id, text, reply_markup=king_of_the_hill_menu_1, parse_mode='HTML')


@COMMANDS.callback_query_handler(text="tg_premium_draw")
async def add_chat(call: types.CallbackQuery):
    text_game_html = f'<b><i>Игра в кости</i></b>\n' \
                     f'В игре участвуют от 3 до 10 человек.\n' \
                     f'Каждый игрок делает ставку нажимая кнопку "Зарегистрироваться" . ' \
                     f'Как только набирается необходимое количество участников бот присылает ' \
                     f'каждому игроку кубик и сравнивает результаты , победитель забирает все ставки, ' \
                     f'если есть 2 и более победителя они повторно выбрасывают кубик.\n' \
                     f'Кнопка "Отменить регистрацию" удалит вас из игры и вернёт ставку\n' \
                     f'Кнопка "Обновить" покажет актуальное количество зарегистрированных игроков'
    await BOT.edit_message_caption(call.from_user.id, call.message.message_id, call.inline_message_id,
                                   text_game_html, reply_markup=game_of_dice_menu_rules, parse_mode='HTML')


@COMMANDS.callback_query_handler(text="yoomoney")
async def add_chat(call: types.CallbackQuery):
    try:
        await BOT.delete_message(call.from_user.id, call.message.message_id)
    except aiogram.exceptions.MessageCantBeDeleted:
        await BOT.edit_message_reply_markup(call.from_user.id, call.message.message_id)
    await BOT.send_message(call.from_user.id, 'Введите сумму пополнения в сообщении⬇️. Сумма в рублях. вводите только'
                                              ' цифры, минимум 100, максимум 10000.\nДля выхода в меню введите "отмена"')
    await Test.state0.set()


@COMMANDS.message_handler(state=Test.state0)
async def write_info(message: types.Message, state: FSMContext):
    if not message.text:
        await BOT.send_message(message.from_user.id, 'Вы неичего не ввели, повторите ввод⬇️')
        await Test.state0.set()
    elif message.text.lower() == 'отмена' or message.text.lower() == 'jnvtyf':
        await BOT.send_photo(message.chat.id, random.choice(list_images_id), reply_markup=start_menu_inline)
        await state.finish()
    else:
        if not message.text.isdigit():
            await BOT.send_message(message.from_user.id, 'Вводите только цифры!, повторите ввод⬇️')
            await Test.state0.set()
        elif int(message.text) < 100 or int(message.text) > 10000:
            await BOT.send_message(message.from_user.id,
                                   'Вы ввели недопустимое значение, минимум 100, максимум 10000!, повторите ввод⬇️')
            await Test.state0.set()
        else:
            value_rub = message.text
            sql = DB('telegram_game_bot')
            label, payment_completed = sql.check_payment_on_database_yoomoney(message.from_user.id, value_rub)
            if not label and not payment_completed:
                label = f'{message.from_user.id}_{value_rub}_1'
                sql.write('payment_yoomoney', user_id_tg=message.from_user.id,
                          value_rub=value_rub,
                          label=label,
                          date_start_payment=datetime.datetime.now(),
                          date_end_payment=None,
                          payment_is_completed=False)
                quickpay = Quickpay(
                    receiver="4100117795337162",
                    quickpay_form="shop",
                    targets="Sponsor this project",
                    paymentType="SB",
                    sum=value_rub,
                    label=label
                )
                await BOT.send_message(message.from_user.id, f'Перейдите по ссылке и завершите оплату: <a href="{quickpay.base_url}">➡️ ССЫЛКА НА ОПЛАТУ</a> ⬅️',
                                       reply_markup=chek_payment_inline, parse_mode='HTML')
            elif label and not payment_completed:
                sql.set_date_start_payment_now(message.from_user.id, label)
                quickpay = Quickpay(
                    receiver="4100117795337162",
                    quickpay_form="shop",
                    targets="Sponsor this project",
                    paymentType="SB",
                    sum=value_rub,
                    label=label
                )
                await BOT.send_message(message.from_user.id,
                                       f'Вы уже запрашивали эту сумму но не оплатили, перейдите по ссылке и завершите оплату: <a href="{quickpay.base_url}">➡️ ССЫЛКА НА ОПЛАТУ</a> ⬅️',
                                       reply_markup=chek_payment_inline, parse_mode='HTML')
            elif label and payment_completed:
                number_label = int(label.split('_')[2]) + 1
                label = f'{message.from_user.id}_{value_rub}_{number_label}'
                sql.write('payment_yoomoney', user_id_tg=message.from_user.id,
                          value_rub=value_rub,
                          label=label,
                          date_start_payment=datetime.datetime.now(),
                          date_end_payment=None,
                          payment_is_completed=False)
                quickpay = Quickpay(
                    receiver="4100117795337162",
                    quickpay_form="shop",
                    targets="Sponsor this project",
                    paymentType="SB",
                    sum=value_rub,
                    label=label
                )
                await BOT.send_message(message.from_user.id,
                                       f'Вы уже пополняли баланс на эту сумму, вот новая <a href="{quickpay.base_url}">➡️ ССЫЛКА НА ОПЛАТУ</a> ⬅️',
                                       reply_markup=chek_payment_inline, parse_mode='HTML')
            sql.close()
            await state.finish()


@COMMANDS.callback_query_handler(text="chek_payment")
async def add_chat(call: types.CallbackQuery, state: FSMContext):
    try:
        await BOT.delete_message(call.from_user.id, call.message.message_id)
    except aiogram.exceptions.MessageCantBeDeleted:
        await BOT.edit_message_reply_markup(call.from_user.id, call.message.message_id)
    await BOT.send_message(call.from_user.id,
                           'Ухожу на проверку, во время проверки не буду отвечать на команды, сообщу о результате через 3 секунды ',
                           parse_mode='HTML')
    await Test.state1.set()
    await asyncio.sleep(3)
    token1 = config.YOOMONEY_TOKEN
    client = Client(token1)
    sql = DB('telegram_game_bot')
    req = sql.read_last_payment(call.from_user.id)
    label = req[0]
    value_rub_db = float(req[1])
    history = client.operation_history(label=label)
    if history.operations:
        value_rub_yomoney = history.operations[0].amount
        if value_rub_yomoney:
            if value_rub_db - value_rub_db * 0.02 <= value_rub_yomoney <= value_rub_db + value_rub_db * 0.02:
                await BOT.send_message(call.from_user.id, f'Оплата прошла, деньги на балансе')
                sql.update_balance_user(call.from_user.id, value_rub_db)
                sql.update_payment_status_and_date_end_payment(call.from_user.id, label)
                await BOT.send_message(config.admin_id_tg, f'Пополнение, {value_rub_yomoney}')
            else:
                await BOT.send_message(call.from_user.id, f'Сумма не соответствует указанной, обратитесь в тех поддержку')
        else:
            await BOT.send_message(call.from_user.id, f'С оплатой что-то не так')
    else:
        await BOT.send_message(call.from_user.id, f'Оплатa не найдена')
    await BOT.send_photo(call.from_user.id, random.choice(list_images_id), reply_markup=start_menu_inline)
    sql.close()
    await state.finish()


@COMMANDS.callback_query_handler(text="cash_out_yoomoney")
async def add_chat(call: types.CallbackQuery):
    try:
        await BOT.delete_message(call.from_user.id, call.message.message_id)
    except aiogram.exceptions.MessageCantBeDeleted:
        await BOT.edit_message_reply_markup(call.from_user.id, call.message.message_id)
    await BOT.send_message(call.from_user.id, 'Введите сумму для вывода в сообщении⬇️. Сумма в рублях. вводите только'
                                              ' цифры, минимум 100, максимум 10000. Коммиссия бота 10%\nДля выхода в меню введите "отмена"')
    await Test.state2.set()


@COMMANDS.callback_query_handler(text="cash_out_operator")
async def add_chat(call: types.CallbackQuery):
    try:
        await BOT.delete_message(call.from_user.id, call.message.message_id)
    except aiogram.exceptions.MessageCantBeDeleted:
        await BOT.edit_message_reply_markup(call.from_user.id, call.message.message_id)
    await BOT.send_message(call.from_user.id, 'Введите сумму для вывода в сообщении⬇️. Сумма в рублях. вводите только'
                                              ' цифры, минимум 100, максимум 10000. Коммиссия бота 10%\nДля выхода в меню введите "отмена"')
    await Test.state4.set()


@COMMANDS.message_handler(state=Test.state2)
async def write_info(message: types.Message, state: FSMContext):
    if not message.text:
        await BOT.send_message(message.from_user.id, 'Вы неичего не ввели, повторите ввод⬇️')
        await Test.state2.set()
    elif message.text.lower() == 'отмена' or message.text.lower() == 'jnvtyf':
        await BOT.send_photo(message.chat.id, random.choice(list_images_id), reply_markup=start_menu_inline)
        await state.finish()
    else:
        if not message.text.isdigit():
            await BOT.send_message(message.from_user.id, 'Вводите только цифры! Повторите ввод⬇️')
            await Test.state2.set()
        elif int(message.text) < 100 or int(message.text) > 10000:
            await BOT.send_message(message.from_user.id,
                                   'Вы ввели недопустимое значение, минимум 100, максимум 10000!, повторите ввод⬇️')
            await Test.state2.set()
        else:
            value_rub = float(message.text)
            sql = DB('telegram_game_bot')
            balance = sql.chek_balance_user(message.from_user.id)[0]
            if value_rub > balance:
                await BOT.send_message(message.from_user.id,
                                       f'На балансе не достаточно средств! У Вас в кошельке {balance} руб., повторите ввод⬇️')
                await Test.state2.set()
            else:
                await state.update_data(state2=value_rub)
                await BOT.send_message(message.from_user.id,
                                       'Хорошо, теперь введите номер Вашего кошелька yoomoney без пробелов (состоит из 16 цифр)')
                await Test.state3.set()
            sql.close()


@COMMANDS.message_handler(state=Test.state4)
async def write_info(message: types.Message, state: FSMContext):
    if not message.text:
        await BOT.send_message(message.from_user.id, 'Вы неичего не ввели, повторите ввод⬇️')
        await Test.state4.set()
    elif message.text.lower() == 'отмена' or message.text.lower() == 'jnvtyf':
        await BOT.send_photo(message.chat.id, random.choice(list_images_id), reply_markup=start_menu_inline)
        await state.finish()
    else:
        if not message.text.isdigit():
            await BOT.send_message(message.from_user.id, 'Вводите только цифры! Повторите ввод⬇️')
            await Test.state4.set()
        elif int(message.text) < 100 or int(message.text) > 10000:
            await BOT.send_message(message.from_user.id,
                                   'Вы ввели недопустимое значение, минимум 100, максимум 10000!, повторите ввод⬇️')
            await Test.state4.set()
        else:
            value_rub = float(message.text)
            sql = DB('telegram_game_bot')
            balance = sql.chek_balance_user(message.from_user.id)[0]
            if value_rub > balance:
                await BOT.send_message(message.from_user.id,
                                       f'На балансе не достаточно средств! У Вас в кошельке {balance} руб., повторите ввод⬇️')
                await Test.state4.set()
            else:
                await state.update_data(state4=value_rub)
                await BOT.send_message(message.from_user.id,
                                       'Хорошо, теперь введите номер карты без пробелов или номер телефона (kiwi)')
                await Test.state5.set()
            sql.close()


@COMMANDS.message_handler(state=Test.state5)
async def write_info(message: types.Message, state: FSMContext):
    if not message.text:
        await BOT.send_message(message.from_user.id, 'Вы неичего не ввели, повторите ввод⬇️')
        await Test.state5.set()
    elif message.text.lower() == 'отмена' or message.text.lower() == 'jnvtyf':
        await BOT.send_photo(message.chat.id, random.choice(list_images_id), reply_markup=start_menu_inline)
        await state.finish()
    else:
        if not message.text.isdigit():
            await BOT.send_message(message.from_user.id, 'Вводите только цифры! Повторите ввод⬇️')
            await Test.state5.set()
        else:
            data = await state.get_data()
            value_rub = int(data.get('state4'))
            value_rub_with_commission = value_rub - value_rub * 0.1
            await BOT.send_message(config.admin_id_tg, f'Запрос на вывод \nid {message.from_user.id}\n'
                                                       f'username @{message.from_user.username}\n'
                                                       f'Сумма {value_rub_with_commission}\n'
                                                       f'Номер счёта {message.text}')
            await BOT.send_photo(message.chat.id, random.choice(list_images_id), reply_markup=start_menu_inline)



def func_process_payment(request_id):
    header_params = {
        'POST': '/api/request-payment HTTP/1.1',
        'Host': 'yoomoney.ru',
        'Authorization': f'Bearer {config.YOOMONEY_TOKEN}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    body = f'request_id={request_id}'
    process_payment = requests.post(url='https://yoomoney.ru/api/process-payment',
                                    headers=header_params, data=body)
    return process_payment

def func_request_payment(wallet_number, value_rub):
    header_params = {
        'POST': '/api/request-payment HTTP/1.1',
        'Host': 'yoomoney.ru',
        'Authorization': f'Bearer {config.YOOMONEY_TOKEN}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    body = f'pattern_id=p2p&to={wallet_number}&amount={int(value_rub)}.00'
    request_payment = requests.post(url='https://yoomoney.ru/api/request-payment', headers=header_params,
                                    data=body)
    return request_payment


@COMMANDS.message_handler(state=Test.state3)
async def write_info(message: types.Message, state: FSMContext):
    if not message.text:
        await BOT.send_message(message.from_user.id, 'Вы неичего не ввели, повторите ввод⬇️')
        await Test.state3.set()
    elif message.text.lower() == 'отмена' or message.text.lower() == 'jnvtyf':
        await BOT.send_photo(message.chat.id, random.choice(list_images_id), reply_markup=start_menu_inline)
        await state.finish()
    else:
        if not message.text.isdigit():
            await BOT.send_message(message.from_user.id, 'Вводите только цифры! Повторите ввод⬇️')
            await Test.state3.set()
        elif not len(message.text) == 16:
            await BOT.send_message(message.from_user.id,
                                   'Недопустимое количество символов! Номер кошелька yoomoney состоит из 16 цифр, повторите ввод⬇️')
            await Test.state3.set()
        else:
            sql = DB('telegram_game_bot')
            data = await state.get_data()
            value_rub = int(data.get('state2'))
            value_rub_with_commission = value_rub - value_rub * 0.1
            request_payment = func_request_payment(message.text, value_rub_with_commission)
            if request_payment.status_code == 200:
                ansver_yoomoney_1 = request_payment.json()
                if ansver_yoomoney_1["status"] == "success":
                    await BOT.send_message(message.from_user.id, 'Платёж одобрен, подтверждаю перевод...')
                    request_id = ansver_yoomoney_1['request_id']
                    process_payment = func_process_payment(request_id)
                    if process_payment.status_code == 200:
                        ansver_yoomoney_2 = process_payment.json()
                        if ansver_yoomoney_2["status"] == "success":
                            await BOT.send_message(message.from_user.id, 'Платёж завершён')
                            sql.update_balance_user_minus(message.from_user.id, value_rub)
                            await BOT.send_message(config.admin_id_tg, f'Вывод, остаток на балансе {ansver_yoomoney_2["balance"]}')
                            if int(ansver_yoomoney_2["balance"]) < config.critical_balance:
                                sys.exit()
                        elif ansver_yoomoney_2["status"] == "in_progress":
                            await BOT.send_message(message.from_user.id, 'Платёж в обработке, повторный запрос через 30 секунд, ожидайте')
                            await asyncio.sleep(30)
                            process_payment = func_process_payment(request_id)
                            if process_payment.status_code == 200:
                                ansver_yoomoney_2 = process_payment.json()
                                if ansver_yoomoney_2["status"] == "success":
                                    await BOT.send_message(message.from_user.id, 'Платёж завершён')
                                    sql.update_balance_user_minus(message.from_user.id, value_rub)
                                    await BOT.send_message(config.admin_id_tg,
                                                           f'Вывод, остаток на балансе {ansver_yoomoney_2["balance"]}')
                                    if int(ansver_yoomoney_2["balance"]) < config.critical_balance:
                                        sys.exit()
                                elif ansver_yoomoney_2["status"] == "in_progress":
                                    await BOT.send_message(message.from_user.id,
                                                           'Ошибка, платёж обрабатывается слишком долго, обратитесь в тех поддержку')
                                elif ansver_yoomoney_2["status"] == "refused":
                                    await BOT.send_message(message.from_user.id, ansver_yoomoney_2["error_description"])
                            else:
                                await BOT.send_message(message.from_user.id,
                                                       f'Ошибка соединения, статус {process_payment.status_code}')
                        elif ansver_yoomoney_2["status"] == "refused":
                            await BOT.send_message(message.from_user.id, ansver_yoomoney_2["error_description"])
                    else:
                        await BOT.send_message(message.from_user.id,
                                               f'Ошибка соединения, статус {process_payment.status_code}')
                elif ansver_yoomoney_1["status"] == "refused":
                    if ansver_yoomoney_1["error_description"] == 'Unknown reciever':
                        await BOT.send_message(message.from_user.id, 'Такого кошелька не существует')
                    else:
                        await BOT.send_message(message.from_user.id, ansver_yoomoney_1["error_description"])
            else:
                await BOT.send_message(message.from_user.id, f'Ошибка соединения, статус {request_payment.status_code}')
            sql.close()
            await BOT.send_photo(message.chat.id, random.choice(list_images_id), reply_markup=start_menu_inline)
            await state.finish()




if __name__ == "__main__":
    executor.start_polling(COMMANDS, skip_updates=True)
