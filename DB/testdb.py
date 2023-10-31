import unittest
from database import DB


class TestDB(unittest.TestCase):
    db = DB()
    db.create_new_table()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_user(self):
        # self.assertTrue(self.db.add_user(telegram_id="2141223", ban=False))
        pass

    def test_data_record_1(self):
        self.assertTrue(
            self.db.data_record(
                telegram_id=2141223,
                amount="21412.22",
                debit=False,
                date="2022.05.21",
                type="food",
                priority=1,
            )
        )

    def test_data_read(self):
        self.assertEqual(
            list,
            type(
                self.db.data_getting(
                    telegram_id=2141223,
                    debit=False,
                    date_from="2000.02.11",
                    date_to="2023.10.21",
                    type="food",
                )
            ),
        )

    def test_data_compliance(self):
        self.db.add_user(telegram_id=51122, ban=False)
        self.db.data_record(
            telegram_id=51122,
            amount="2022.12",
            debit=False,
            date="2020.01.01",
            time="22:30:16",
            type="car",
            priority=4,
        )
        data = self.db.data_getting(
            telegram_id=51122,
            debit=False,
            date_from="2019.12.30",
            date_to="2020.01.02",
            type="car",
        )
        self.assertEqual(str(data[0][2]), "2020-01-01", msg="Не совпадает дата")
        self.assertEqual(str(data[0][3]), "22:30:16", msg="Не совпадает время")
        self.assertEqual(float(data[0][4]), 2022.12, msg="Не совпадает цена")
        self.assertEqual(data[0][5], False, msg="Не совпадает тип опреации")
        self.assertEqual(data[0][6], "car", msg="Не совпадает категория операции")
        self.assertEqual(data[0][7], 4, msg="Не совпадает приоритет операции")

    def test_data_delete(self):
        self.db.add_user(telegram_id=111116, ban=False)
        self.db.data_record(
            telegram_id=111116,
            amount="2022.12",
            debit=False,
            date="2020.01.01",
            time="22:30:16",
            type="car",
            priority=4,
        )
        self.assertTrue(
            self.db.data_delete(
                telegram_id=111116,
                debit=False,
                date="2020.01.01",
                amount=2022.12,
                type="car",
            )
        )

    def test_data_selection(self):
        telegram_id = 111116
        debit = False
        date = "2020-01-01"
        amount = 2022.12
        self.db.data_record(
            telegram_id=telegram_id,
            amount=amount,
            debit=debit,
            date=date,
            type="car",
            priority=3,
        )
        data = self.db.data_selection(
            telegram_id=telegram_id, debit=debit, date=date, amount=amount
        )
        self.assertEqual(str(data[0][2]), date, "Даты не совпадают")
        self.assertEqual(float(data[0][4]), amount, "Сумма не совпадают")
        self.assertEqual(data[0][5], debit, "Тип операции не совпадают")

    def test_get_and_record_types(self):
        telegram_id = 111116
        debit = False
        types = ["car", "food"]
        self.db.record_types(
            telegram_id=telegram_id,
            debit=debit,
            types=types
        )
        types_in_db = self.db.get_types(telegram_id=telegram_id, debit=debit)
        for type in types_in_db[0][0]:
            self.assertTrue(type in types, msg=f'{type}')
            
        debit = True
        types = ['stocks', 'jod']
        self.db.record_types(
            telegram_id=telegram_id,
            debit=debit,
            types=types
        )
        types_in_db = self.db.get_types(telegram_id=telegram_id, debit=debit)
        for type in types_in_db[0][0]:
            self.assertTrue(type in types, msg=f'{type}')
        
    def test_delete_types(self):
        telegram_id = 111116
        self.assertTrue(self.db.type_record_delete(telegram_id=telegram_id,debit=False, type='food'))
        
        


if __name__ == "__main__":
    unittest.main()
    # db = DB()
    # telegram_id = 111116
    # debit = False
    # types = ["car", "food"]
    # db.record_types(
    #     telegram_id=telegram_id,
    #     debit=debit,
    #     types=types
    # )
    # types_in_db = db.get_types(telegram_id=telegram_id, debit=debit)
    # print(types_in_db)
    
    # debit2 = True
    # types2 = ['stocks', 'jod']
    # db.record_types(
    #     telegram_id=telegram_id,
    #     debit=debit2,
    #     types=types2
    # )
    # types_in_db = db.get_types(telegram_id=telegram_id, debit=debit2)
    # print(types_in_db)
    