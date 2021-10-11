import unittest
from utils import Utils


class UtilsTest(unittest.TestCase):
    def setUp(self):
        self.__utils = Utils()

    def test_get_express3id_by_name_fail(self):
        code = self.__utils.get_express3id_by_name("ABYRVALG")
        self.assertEqual(code, -1)

    def test_get_express3id_by_name_success(self):
        code = self.__utils.get_express3id_by_name("Санкт-Петербург")
        self.assertEqual(code, 2004000)

    def test_get_rid(self):
        params = {
            'dir':          0,
            'tfl':          3,
            'checkSeats':   1,
            'code0':  2004000,
            'code1':  2000000,
            'dt0': '01.01.2022'
        }
        rid = self.__utils.get_rid(5827, params)
        self.assertNotEqual(rid, '-1')

    def test_request_by_rid(self):
        params = {
            'dir': 0,
            'tfl': 3,
            'checkSeats': 1,
            'code0': 2004000,
            'code1': 2000000,
            'dt0': '01.01.2022'
        }
        rid = self.__utils.get_rid(5827, params)
        response = self.__utils.request_by_rid(5827, rid)
        self.assertGreater(len(response), 0)



if __name__ == '__main__':
    unittest.main()
