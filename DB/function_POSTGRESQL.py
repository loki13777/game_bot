import psycopg2
from psycopg2 import Error
from psycopg2 import OperationalError
import datetime

class DB:
    def __init__(self, db_name):
        """инициализайция соединения с БД"""
        self.connection = psycopg2.connect(
            database=db_name,
            user="",
            password="",
            host="",
            port="",
        )
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

    def show_tables(self):
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema','pg_catalog');"
        self.cursor.execute(query)
        print(self.cursor.fetchall())

    def create_table(self, text):
        self.cursor.execute(text)

    def write(self, name_table, **kwargs):
        tuple_field = tuple(kwargs.keys())
        tuple_value = tuple(kwargs.values())
        field_str = f'({", ".join(tuple_field)})'
        value_str = f'({", ".join(["%s"] * len(tuple_value))})'
        insert_query = (
            f"INSERT INTO {name_table} {field_str} VALUES {value_str}"
        )
        self.cursor.execute(insert_query, tuple_value)

    def check_list_info_user(self, user_id_tg):
        insert_query = (
            f"SELECT first_name, username, balance_rub FROM bot_users WHERE user_id_tg = %s"
        )
        self.cursor.execute(insert_query, (user_id_tg,))
        return self.cursor.fetchone()

    def update_info_user(self, first_name, username, user_id_tg):
        insert_query = (
            f"UPDATE bot_users SET first_name = %s, username = %s WHERE user_id_tg = %s"
        )
        self.cursor.execute(insert_query, (first_name, username, user_id_tg))


    def chek_balance_user(self, user_id_tg):
        insert_query = (
            f"SELECT balance_rub FROM bot_users WHERE user_id_tg = %s"
        )
        self.cursor.execute(insert_query, (user_id_tg,))
        return self.cursor.fetchone()

    def read_on_user_id_tg(self, user_id_tg):
        insert_query = (
            f"SELECT user_id_tg FROM bot_users WHERE user_id_tg = %s"
        )
        self.cursor.execute(insert_query, (user_id_tg, ))
        return self.cursor.fetchone()

    def read_user_info_on_id(self, user_id_tg):
        insert_query = (
            f"SELECT first_name, username  FROM bot_users WHERE user_id_tg = %s"
        )
        self.cursor.execute(insert_query, (user_id_tg,))
        return self.cursor.fetchone()

    def check_payment_on_database_yoomoney(self, user_id_tg, value_rub):
        query = (
            f"SELECT label, payment_is_completed FROM payment_yoomoney "
            f"WHERE user_id_tg = {user_id_tg} and value_rub = {value_rub} "
            f"ORDER BY date_start_payment DESC"

        )
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if not result:
            return (None, None)
        else:
            return result

    def set_date_start_payment_now(self, user_id_tg, label):
        query = f"UPDATE payment_yoomoney SET date_start_payment = %s WHERE user_id_tg = {user_id_tg} and label = '{label}' "
        self.cursor.execute(query, (datetime.datetime.now(),))

    def read_last_payment(self, user_id_tg, payment_is_completed=False):
        query = f'SELECT label, value_rub FROM payment_yoomoney WHERE ' \
             f'user_id_tg = {user_id_tg} and payment_is_completed = {payment_is_completed} ORDER BY date_start_payment DESC'
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result

    def update_payment_status_and_date_end_payment(self, user_id_tg, label):
        query = f"UPDATE payment_yoomoney SET payment_is_completed = True, date_end_payment = %s WHERE user_id_tg = {user_id_tg} and label = '{label}'"
        self.cursor.execute(query, (datetime.datetime.now(),))

    def update_balance_user(self, user_id_tg, value_rub):
        query = f"UPDATE bot_users SET balance_rub = balance_rub + %s WHERE user_id_tg = {user_id_tg}"
        self.cursor.execute(query, (value_rub,))

    def update_balance_user_minus(self, user_id_tg, value_rub):
        query = f"UPDATE bot_users SET balance_rub = balance_rub - %s WHERE user_id_tg = {user_id_tg}"
        self.cursor.execute(query, (value_rub,))

    def set_start_values_king_hill(self):
        query = f"UPDATE king_of_the_hill SET bank = %s, last_bet = %s, leader_name = %s," \
                f"leader_id_tg = %s, date_end_game = %s "
        self.cursor.execute(query, (0, 0, None, None, None))

    def update_values_king_hill(self, bank, last_bet, leader_name, leader_id_tg, date_end_game):
        query = f"UPDATE king_of_the_hill SET bank = %s, last_bet = %s, leader_name = %s," \
                f"leader_id_tg = %s, date_end_game = %s "
        self.cursor.execute(query, (bank, last_bet, leader_name, leader_id_tg, date_end_game))

    def read_king_hill(self):
        query = f"SELECT * FROM king_of_the_hill"
        self.cursor.execute(query)
        data = self.cursor.fetchall()[0]
        dict_data = {}
        dict_data['bank'] = data[0]
        dict_data['last_bet'] = data[1]
        dict_data['leader_name'] = data[2]
        dict_data['leader_id_tg'] = data[3]
        dict_data['date_end_game'] = data[4]
        return dict_data

    def write_game_of_dice(self, dicer_name, dicer_id_tg, result, in_game, date):
        query = f"INSERT INTO game_of_dice_1 (dicer_name, dicer_id_tg, result, in_game, date) VALUES (%s, %s, %s, %s, %s)"
        try:
            self.cursor.execute(query, (dicer_name, dicer_id_tg, result, in_game, date))
        except Error:
            return True
    def clear_game_of_dice(self):
        query = f"TRUNCATE game_of_dice_1"
        self.cursor.execute(query)

    def read_game_of_dice(self):
        query = f"SELECT * FROM game_of_dice_1"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def read_game_of_dice_with_username(self):
        query = f"SELECT game_of_dice_1.dicer_id_tg, game_of_dice_1.result, game_of_dice_1.in_game, bot_users.username," \
                f" game_of_dice_1.dicer_name" \
                f" FROM game_of_dice_1 " \
                f"JOIN bot_users on game_of_dice_1.dicer_id_tg = bot_users.user_id_tg"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def kick_player_game_of_dice(self, dicer_id_tg):
        query = "UPDATE game_of_dice_1 SET in_game = FALSE WHERE dicer_id_tg = %s"
        self.cursor.execute(query, (dicer_id_tg,))

    def start_game_of_dice(self):
        query = "UPDATE game_of_dice_1 SET game_is_started = TRUE"
        self.cursor.execute(query)

    def end_game_of_dice(self):
        query = "UPDATE game_of_dice_1 SET game_is_started = FALSE"
        self.cursor.execute(query)

    def check_date_start_game_dice(self, dicer_id_tg):
        query = "SELECT date FROM game_of_dice_1 WHERE dicer_id_tg = %s"
        self.cursor.execute(query, (dicer_id_tg, ))
        return self.cursor.fetchone()

    def check_registration_game_dice(self, dicer_id_tg):
        query = "SELECT game_is_started FROM game_of_dice_1 WHERE dicer_id_tg = %s"
        self.cursor.execute(query, (dicer_id_tg,))
        return self.cursor.fetchone()

    def delete_dicer(self, dicer_id_tg):
        query = "DELETE FROM game_of_dice_1 WHERE dicer_id_tg = %s"
        self.cursor.execute(query, (dicer_id_tg,))

    def write_result_game_dice(self, result, dicer_id_tg):
        query = "UPDATE game_of_dice_1 SET result = %s WHERE dicer_id_tg = %s"
        self.cursor.execute(query, (result, dicer_id_tg))


    def read_all_table(self, name_table):
        insert_query = f"SELECT * FROM {name_table}"
        self.cursor.execute(insert_query)
        return self.cursor.fetchall()

    def delete_table(self, name_table):
        delete_table = f"DROP TABLE {name_table} CASCADE"
        self.cursor.execute(delete_table)

    def query(self, text, val):
        self.cursor.execute(text, val)
        # return self.cursor.fetchone()

    def close(self):
        self.cursor.close()
        self.connection.close()


# sql = DB('telegram_game_bot')
# sql.create_table()
# sql.ex()
# sql.delit()
# a = sql.read()
# for el in a:
#     print(el)
# print(sql.show_tables())
# sql.close()
