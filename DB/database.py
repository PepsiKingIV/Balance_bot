import psycopg2
import logging
import datetime
import configparser

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(f"DB/DataBase.log", mode="w")
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info(f"Logget for module DataBase")


config = configparser.ConfigParser()
config.read("./conf.ini")


class DB:
    conn: psycopg2.connect()
    cursor: psycopg2.connect().cursor()

    def __init__(self) -> None:
        try:
            self.conn = psycopg2.connect(
                dbname=config["DataBase"]["dbname"],
                user=config["DataBase"]["user"],
                host=config["DataBase"]["host"],
                port=config["DataBase"]["port"],
            )
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                f"CREATE TABLE users (id SERIAL PRIMARY KEY, telegram_id integer UNIQUE, ban boolean, Debit_Type text ARRAY , Credit_Type text ARRAY)"
            )
            self.cursor.execute("CREATE INDEX on users(telegram_id)")
            self.conn.commit()
            logger.info("the connection to the database was successful.")
        except Exception as e:
            self.conn.commit()
            logger.exception(f"failed to connect to the database. \n EXEPTION: {e}")

    def create_new_table(self) -> None:
        """
        The method creates two tables: debit and credit
        """
        try:
            self.cursor.execute(
                f"CREATE TABLE debit (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id), Date date, Time time, Amount numeric(8,2), Debit boolean, Type text)"
            )
            self.cursor.execute(
                f"CREATE TABLE credit (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id), Date date, Time time, Amount numeric(8,2), Debit boolean, Type text, Priority smallint)"
            )
            self.cursor.execute("CREATE INDEX on debit(user_id)")
            self.cursor.execute("CREATE INDEX on credit(user_id)")
            self.conn.commit()
            logger.info(f"Function createNewDB completed successfully")
        except Exception:
            self.conn.commit()
            logger.exception(f"Function createNewDB not completed.")

    def add_user(self, telegram_id: int | str, ban: bool) -> None:
        Nan = "{Nan}"
        try:
            self.cursor.execute(
                f"SELECT id FROM users WHERE telegram_id = {int(telegram_id)}"
            )
            id = int(self.cursor.fetchall()[0][0])
            self.conn.commit()
        except:
            try:
                self.cursor.execute(
                    f"INSERT INTO users (telegram_id, ban, debit_type, credit_type) VALUES ({telegram_id}, {ban}, '{Nan}'::text[] , '{Nan}'::text[])"
                )
                self.conn.commit()
                logger.info(f"A new user has been added. telegram_id: {telegram_id}")
            except Exception as e:
                self.conn.commit()
                logger.exception(
                    f"Failed to create a new user. telegram_id: {telegram_id} \n \
                    EXEPTION: {e}"
                )
            
    def get_user(self, telegram_id: int | str) -> bool:
        try:
            self.cursor.execute(
                    f"SELECT id FROM users WHERE telegram_id = {int(telegram_id)}"
                )
            user = self.cursor.fetchall()
            self.conn.commit()
            return bool(user)
        except:
            return False

    def data_record(
        self,
        telegram_id: int | str,
        amount: str | float,
        debit: bool,
        date=str(datetime.datetime.now().date()),
        time=str(datetime.datetime.now().time())[0:8:],
        type: str | None = None,
        priority: int = 1,
    ) -> bool:
        """
        The method saves data to the database.

        :param telegram_id: ID of the user who creates the record. The ID is provided by telegram
        :type telegram_id: :obj:`str` or `int`

        :param amount: transaction amount (in rubles). In the database, rounded to two decimal places
        :type amount: :obj:`float` or `str`

        :param debit: A logical variable corresponding to a debit or credit. Accordingly, True if debit, False if credit
        :type debit: :obj:`boolean`

        :param date: the user specifies the date of the transaction on the account, defaults the current date
        :type date: :obj:`str`, optional

        :param time: the user specifies the time of the transaction on the account, defaults the current time
        :type time: :obj:`str`, optional

        :param type: type of debit(salary, dividends) or credit (food, transport). The user defines the list of types himself. Default None
        :type type: :obj:`str`, optional

        :param priority: Spending priority. The higher the number, the greater the need for the product. If debit, the parameter is not specified. Default 1
        :type priority: :obj:`int`, optional

        :return: Returns True if the operation is successful, otherwise False
        :rtype: :obj:`boolean`
        """
        id = -1
        try:
            self.cursor.execute(
                f"SELECT id FROM users WHERE telegram_id = {int(telegram_id)}"
            )
            id = int(self.cursor.fetchall()[0][0])
            self.conn.commit()
        except Exception as e:
            logger.exception(
                f"Failed to get users with the specified telegram_id: {telegram_id}. \n \
                Request: SELECT id FROM users WHERE telegram_id = {int(telegram_id)}. \n \
                Exeption: {e}"
            )
        try:
            if debit:
                self.cursor.execute(
                    f"INSERT INTO debit (user_id, date, time, amount, debit, type) VALUES ('{id}', '{date}', '{time}', {amount}, {debit}, '{type}')"
                )
            else:
                self.cursor.execute(
                    f"INSERT INTO credit (user_id, date, time, amount, debit, type, priority)VALUES ('{id}', '{date}', '{time}', {amount}, {debit}, '{type}', {priority})"
                )
            logger.info(f"Function dataRecord completed successfully. telegram_id {telegram_id}")
            self.conn.commit()
            return True
        except Exception:
            self.conn.commit()
            logger.exception(f"Function dataRecord not completed. telegram_id {telegram_id}")
            return False

    def data_getting(
        self,
        telegram_id: int | str,
        debit: bool,
        date_from=str(datetime.datetime.now() - datetime.timedelta(days=7))[0:10:],
        date_to=str(datetime.datetime.now().date()),
        type=None,
    ) -> list:
        """
        The method gets records from the database for a certain point in time.
        You can also specify what type of expenses you need.
        If the required type of expenses is specified, then the Debit parameter can be omitted.

        :param telegram_id: ID of the user who creates the record. The ID is provided by telegram
        :type telegram_id: :obj:`int` or `str`

        :param debit: A logical variable corresponding to a debit or credit. Accordingly, True if debit, False if credit
                      If the required type of expenses is specified, then the Debit parameter can be omitted.
        :type debit: :obj:`boolean`

        :param date_from: the date from which records are needed, defaults date 7 days ago
        :type time: :obj:`str`, optional

        :param date_to: the date to which records are needed, defaults now
        :type time: :obj:`str`, optional

        :param type: type of debit(salary, dividends) or credit (food, transport). The user defines the list of types himself. Default None
        :type type: :obj:`str`, optional

        :return: List of expense or income records
        :rtype: :obj:`list` (list of tuple) if the request was successful.
        """

        id = -1
        try:
            self.cursor.execute(
                f"SELECT id FROM users WHERE telegram_id = {int(telegram_id)}"
            )
            id = int(self.cursor.fetchall()[0][0])
            self.conn.commit()
        except Exception as e:
            self.conn.commit()
            logger.exception(
                f"Failed to get users with the specified telegram_id: {telegram_id}. \n \
                Request: SELECT id FROM users WHERE telegram_id = {int(telegram_id)}. \n \
                Exeption: {e}"
            )
        try:
            if type:
                if debit:
                    req = f"SELECT * FROM debit WHERE user_id = {id} AND date >= '{date_from}' \
                        AND date <= '{date_to}' AND type = '{type}'"
                else:
                    req = f"SELECT * FROM credit WHERE user_id = {id} AND date >= '{date_from}' \
                        AND date <= '{date_to}' AND type = '{type}'"
            else:
                if debit:
                    req = f"SELECT * FROM debit WHERE date >= '{date_from}' AND date <= '{date_to}'"
                else:
                    req = f"SELECT * FROM debit WHERE date >= '{date_from}' AND date <= '{date_to}'"
            self.cursor.execute(req)
            res = self.cursor.fetchall()
            self.conn.commit()
            logger.info(
                f"Function dataGetting completed successfully. telegram_id: {telegram_id}"
            )
            return res
        except Exception as e:
            self.conn.commit()
            logger.exception(
                f"Function dataGetting not completed. telegram_id: {telegram_id} \n \
                EXEPTION: {e}"
            )

    def data_delete(
        self, telegram_id: int | str, debit: bool, date: str, amount: str, type: str
    ) -> bool:
        """
        The method deletes a record from the database. The record is selected by date and price.

        :param telegram_id: ID of the user who creates the record. The ID is provided by telegram
        :type telegram_id: :obj:`int` or `str`

        :param debit: A logical variable corresponding to a debit or credit. Accordingly, True if debit, False if credit
                      If the required type of expenses is specified, then the Debit parameter can be omitted.
        :type debit: :obj:`boolean`

        :param date: the record with the specified date will be deleted
        :type date: :obj:`str`

        :param amount: the entry with the specified price will be deleted
        :type type: :obj:`str`

        :param type: type of debit(salary, dividends) or credit (food, transport). The user defines the list of types himself. Default None
        :type type: :obj:`str`

        :return: Returns True if the operation is successful, otherwise False
        :rtype: :obj:`boolean`
        """
        id = -1
        try:
            self.cursor.execute(
                f"SELECT id FROM users WHERE telegram_id = {int(telegram_id)}"
            )
            id = int(self.cursor.fetchall()[0][0])
            self.conn.commit()
        except Exception as e:
            self.conn.commit()
            logger.exception(
                f"Failed to get users with the specified telegram_id: {telegram_id}. \n \
                Request: SELECT id FROM users WHERE telegram_id = {int(telegram_id)}. \n \
                Exeption: {e}"
            )
            return False
        try:
            if debit:
                req = f"DELETE FROM debit WHERE user_id = {id} AND amount = {amount} \
                    AND date = '{date}' AND type = '{type}'"
            else:
                req = f"DELETE FROM credit WHERE user_id = {id} AND amount = {amount} \
                    AND date = '{date}' AND type = '{type}'"
            self.cursor.execute(req)
            self.conn.commit()
            logger.info(
                f"Function data_delete completed successfully. telegram_id: {telegram_id}"
            )
            return True
        except Exception as e:
            self.conn.commit()
            logger.exception(
                f"Function dataGetting not completed. {telegram_id} \n \
                EXEPTION: {e}"
            )
            return False

    def data_selection(
        self, telegram_id: int | str, debit: bool, date: str, amount: str
    ):
        """
        An auxiliary method required to confirm the data to be deleted from the database.
        If you output several lines, the user will be asked to specify the time.

        :param telegram_id: ID of the user who creates the record. The ID is provided by telegram
        :type telegram_id: :obj:`int` or `str`

        :param debit: A logical variable corresponding to a debit or credit. Accordingly, True if debit, False if credit
        :type debit: :obj:`boolean`

        :param date: the record with the specified date will be deleted
        :type time: :obj:`str`

        :param amount: The entry with the specified price will be deleted
        :type amount: :obj:`str`

        :return: List of expense or income records
        :rtype: :obj:`list` (list of tuple) if the request was successful.
        """

        id = -1
        try:
            self.cursor.execute(
                f"SELECT id FROM users WHERE telegram_id = {int(telegram_id)}"
            )
            id = int(self.cursor.fetchall()[0][0])
            self.conn.commit()
        except Exception as e:
            logger.exception(
                f"Failed to get users with the specified telegram_id: {telegram_id}. \n \
                Request: SELECT id FROM users WHERE telegram_id = {int(telegram_id)}. \n \
                Exeption: {e}"
            )
        try:
            if debit:
                req = f"SELECT * FROM debit WHERE date = '{date}' AND amount = {amount}"
            else:
                req = f"SELECT * FROM credit WHERE user_id = {id} AND date = '{date}' AND amount = {amount}"
            self.cursor.execute(req)
            res = self.cursor.fetchall()
            logger.info(
                f"Function data_delete completed successfully. telegram_id: {telegram_id}"
            )
            self.conn.commit()
        except Exception as e:
            self.conn.commit()
            logger.exception(
                f"Function dataGetting not completed. {telegram_id} \n \
                EXEPTION: {e}"
            )
        return res

    def record_types(self, telegram_id: int | str, debit: bool, types: str | list):
        """
        A function designed to record new types of expenses and income.
        The first call creates an entry in the database.

        :param telegram_id: ID of the user who creates the record. The ID is provided by telegram
        :type telegram_id: :obj:`int` or `str`

        :param debit: A logical variable corresponding to a debit or credit. Accordingly, True if debit, False if credit
        :type debit: :obj:`boolean`

        :param types: список типов либо одиночный тип.
        :type types: :obj:`str` or :obj:`list`

        :return: Returns True if the operation is successful, otherwise False
        :rtype: :obj:`boolean`
        """

        # id = -1
        # try:
        #     self.cursor.execute(
        #         f"SELECT id FROM users WHERE telegram_id = {int(telegram_id)}"
        #     )
        #     id = int(self.cursor.fetchall()[0][0])
        # except Exception as e:
        #     logger.exception(
        #         f"Failed to get users with the specified telegram_id: {telegram_id}. \n \
        #         Request: SELECT id FROM users WHERE telegram_id = {int(telegram_id)}. \n \
        #         Exeption: {e}"
        #     )

        try:
            self.cursor.execute(f"SELECT * FROM Users WHERE telegram_id = {telegram_id}")
            data = self.cursor.fetchall()
            self.conn.commit()
            Types = []
            Nan = "{Nan}"
            # if len(data) == 0:
            #     if debit:
            #         self.cursor.execute(
            #             f"INSERT INTO users (id, telegram_id, ban, Debit_Type, Credit_Type) \
            #                 VALUES ({int(telegram_id)}, {False}, '{Nan}'::text[], '{Nan}'::text[])"
            #         )
            #     else:
            #         self.cursor.execute(
            #             f"INSERT INTO users (id, telegram_id, ban, Debit_Type, Credit_Type) \
            #                 VALUES ({int(telegram_id)}, {False}, '{Nan}'::text[], '{Nan}'::text[])"
            #         )
            if len(data) != 0:
                if debit:
                    paramDebit = "Debit_Type"
                    index = 3
                else:
                    paramDebit = "Credit_Type"
                    index = 4 
                if data[0][index][0] != "Nan":
                    for i in data[0][index]:
                        types.append(i)
                for i in types:
                    Types.append(i)
                unique_types = set(Types)
                Types = []
                TypesStr = "{"
                while unique_types:
                    TypesStr += unique_types.pop()
                    if len(unique_types) != 0:
                        TypesStr += ","
                TypesStr += "}"
                self.cursor.execute(
                    f"UPDATE users SET {paramDebit} = '{TypesStr}' WHERE telegram_id = {telegram_id} \
                        RETURNING Debit_Type, Credit_Type;"
                )
                data = self.cursor.fetchall()
                self.conn.commit()
                logger.info(
                    f"Function record_types completed successfully. telegram_id: {telegram_id}"
                )
                return True
        except Exception as e:
            self.conn.commit()
            logger.exception(
                f"Function record_types not completed. telegram_id: {telegram_id} \n \
                EXEPRION: {e}"
            )
            return False

    def type_record_delete(self, telegram_id: int | str, debit: bool, type: str) -> bool:
        # id = -1
        # try:
        #     self.cursor.execute(
        #         f"SELECT id FROM users WHERE telegram_id = {int(telegram_id)}"
        #     )
        #     id = int(self.cursor.fetchall()[0][0])
        #     self.conn.commit()
        # except Exception as e:
        #     logger.exception(
        #         f"Failed to get users with the specified telegram_id: {telegram_id}. \n \
        #         Request: SELECT id FROM users WHERE telegram_id = {int(telegram_id)}. \n \
        #         Exeption: {e}"
        #     )

        try:
            self.cursor.execute(f"SELECT * FROM Users WHERE telegram_id = {telegram_id}")
            data = self.cursor.fetchall()
            self.conn.commit()
            newData = "{"
            index = 3
            paramDebit = "Credit_Type"
            if debit:
                index = 2
                paramDebit = "Debit_Type"
            for i in range(len(data[0][index])):
                print(data[0][index][i], type)
                if data[0][index][i] != type:
                    newData += data[0][index][i]
                    if i + 1 != len(data[0][index]):
                        newData += ","
            newData += "}"
            self.cursor.execute(
                f"UPDATE users SET {paramDebit} = '{newData}' WHERE telegram_id = {telegram_id} \
                    RETURNING Debit_Type, Credit_Type;"
            )
            data = self.cursor.fetchall()
            self.conn.commit()
            logger.info(
                f"Function type_record_delete completed successfully. telegram_id: {telegram_id}"
            )
            return True
        except Exception as e:
            self.conn.commit()
            logger.exception(
                f"Function type_record_delete not completed. telegram_id: {telegram_id} \n \
                EXEPTION: {e}"
            )
            return False
    
    
    def get_types(self, telegram_id : int | str, debit : bool) -> list():
        if debit:
            operation_type = "debit_type"
        else:
            operation_type = "credit_type"
        try:
            self.cursor.execute(
                f'SELECT {operation_type} FROM users WHERE telegram_id = {telegram_id}'
            )
            types = self.cursor.fetchall()
            self.conn.commit()
            logger.info(
                f"Function get_types completed successfully. telegram_id: {telegram_id}"
            )
            return types
        except Exception as e:
            self.conn.commit()
            logger.exception(
                f"Function get_types not completed. telegram_id: {telegram_id} \n \
                EXEPTION: {e}"
            )