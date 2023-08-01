import psycopg2
import logging
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler(f'DataBase.log', mode='w')
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info(f'Logget for module DataBase')


class DB:

    conn: psycopg2.connect()
    cursor: psycopg2.connect().cursor()

    def __init__(self) -> None:
        try:
            self.conn = psycopg2.connect(
                dbname='Balance', user='aleksandr', host='127.0.0.1', port='5432')
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            logger.info('the connection to the database was successful.')
        except Exception:
            logger.exception('failed to connect to the database')

    def create_new_table(self, userID):
        """
        The method creates two tables: debit and credit
        
        :param userID: ID of the user who creates the record. The ID is provided by telegram
        :type userID: :obj:`str`
        """
        try:
            self.cursor.execute(f'CREATE TABLE User{userID}Debit (Date date, Time time, Amount numeric(8,2), Debit boolean, Type text)')
            self.cursor.execute(f'CREATE TABLE User{userID}Credit (Date date, Time time, Amount numeric(8,2), Debit boolean, Type text, Priority smallint)')
            logger.info(f'Function createNewDB completed successfully. User{userID}')
        except Exception:
            logger.exception(f'Function createNewDB not completed. User{userID}')
            
            
    def data_record(self, userID : str, amount, debit, date = str(datetime.datetime.now().date()), time = str(datetime.datetime.now().time())[0:8:], type = None, priority = 1):
        """
        The method saves data to the database.

        :param userID: ID of the user who creates the record. The ID is provided by telegram
        :type userID: :obj:`str`
        
        :param amount: transaction amount (in rubles). In the database, rounded to two decimal places
        :type amount: :obj:`float`
        
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
        try:
            if debit:
                self.cursor.execute(f"INSERT INTO User{userID}Debit (date, time, amount, debit, type)\
                                VALUES ('{date}', '{time}', {amount}, {debit}, '{type}')")
            else:
                self.cursor.execute(f"INSERT INTO User{userID}Credit (date, time, amount, debit, type, priority)\
                                VALUES ('{date}', '{time}', {amount}, {debit}, '{type}', {priority})")
            logger.info(f'Function dataRecord completed successfully. User{userID}')
            return True
        except Exception:
            logger.exception(f'Function dataRecord not completed. User{userID}')
            return False


    def data_getting(self, userID, debit,
                    date_from = str(datetime.datetime.now() - datetime.timedelta(days=7))[0:10:],
                    date_to = str(datetime.datetime.now().date()), type = None):
        
        """
        The method gets records from the database for a certain point in time.
        You can also specify what type of expenses you need.
        If the required type of expenses is specified, then the Debit parameter can be omitted.

        :param userID: ID of the user who creates the record. The ID is provided by telegram
        :type userID: :obj:`str`
        
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
        
        try:
            if type:
                    self.cursor.execute(f"SELECT * FROM User{userID}Credit WHERE date >= '{date_from}' AND date <= '{date_to}' AND type = {type}")
                    date = self.cursor.fetchall()
            else:
                if debit:
                    self.cursor.execute(f"SELECT * FROM User{userID}Debit WHERE date >= '{date_from}' AND date <= '{date_to}'")
                    date = self.cursor.fetchall()
                else:
                    self.cursor.execute(f"SELECT * FROM User{userID}Credit WHERE date >= '{date_from}' AND date <= '{date_to}'")
                    date = self.cursor.fetchall()
            logger.info(f'Function dataGetting completed successfully. User{userID}')
            return date
        except Exception:
            logger.exception(f'Function dataGetting not completed. User{userID}')
            return None

        
    def data_delete(self, userID, debit, date, amount, time = None):
        
        """
        The method deletes a record from the database. The record is selected by date and price.

        :param userID: ID of the user who creates the record. The ID is provided by telegram
        :type userID: :obj:`str`
        
        :param debit: A logical variable corresponding to a debit or credit. Accordingly, True if debit, False if credit
                      If the required type of expenses is specified, then the Debit parameter can be omitted.
        :type debit: :obj:`boolean`

        :param date: the record with the specified date will be deleted
        :type time: :obj:`str`
        
        :param amount: the entry with the specified price will be deleted
        :type type: :obj:`str`
        
        :param time: the record with the specified time will be deleted, default None
        :type time: :obj:`str`, optional

        :return: Returns True if the operation is successful, otherwise False
        :rtype: :obj:`boolean` 
        """
        
        try:
            if debit:
                if time: 
                    self.cursor.execute(f"REMOVE * FROM user{userID}Debit WHERE amount = {amount} AND data = '{date}' AND time = {time}")
                    return True
                else:
                    self.cursor.execute(f"REMOVE * FROM user{userID}Debit WHERE amount = {amount} AND data = '{date}'")
                    return True
            else:
                if time: 
                    self.cursor.execute(f"REMOVE * FROM user{userID}Credib WHERE amount = {amount} AND data = '{date}' AND time = {time}")
                    return True
                else:
                    self.cursor.execute(f"REMOVE * FROM user{userID}Credit WHERE amount = {amount} AND data = '{date}'")
                    return True
        except Exception:
            logger.exception(f'Function dataGetting not completed. User{userID}')
            return False
        
    def data_selection(self, userID, debit, date, amount):
        
        """
        An auxiliary method required to confirm the data to be deleted from the database.
        If you output several lines, the user will be asked to specify the time.

        :param userID: ID of the user who creates the record. The ID is provided by telegram
        :type userID: :obj:`str`
        
        :param debit: A logical variable corresponding to a debit or credit. Accordingly, True if debit, False if credit
                      If the required type of expenses is specified, then the Debit parameter can be omitted.
        :type debit: :obj:`boolean`

        :param date: the record with the specified date will be deleted
        :type time: :obj:`str`
        
        :param amount: The entry with the specified price will be deleted
        :type type: :obj:`str`

        :return: List of expense or income records
        :rtype: :obj:`list` (list of tuple) if the request was successful.
        """
        
        if debit: 
            self.cursor.execute(f"SELECT * FROM User{userID}Debit WHERE date = '{date}' AND amount = {amount}")
            date = self.cursor.fetchall()
        else:
            self.cursor.execute(f"SELECT * FROM User{userID}Debit WHERE date = '{date}' AND amount = {amount}")
            date = self.cursor.fetchall()
        return date
        
            

