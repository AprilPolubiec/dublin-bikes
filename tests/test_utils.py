import unittest
import web.utils as utils

class TestUtils(unittest.TestCase):

    def test_group_by(self):
        obj_list = [ {"Id": 123, "Name": "April"}, {"Id": 456, "Name": "Aida"}, {"Id": 678, "Name": "Robert"} ]
        res = utils.group_by(obj_list, "Id")
        self.assertIn("123", res)
        self.assertIn("456", res)
        self.assertIn("678", res)
        print("done")

if __name__ == '__main__':
    unittest.main()