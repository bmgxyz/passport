import os
import unittest
import passport

class Create(unittest.TestCase):
    def test_create_blank_database(self):
        passport.create("testdb","blergh",silent=True)
        database_file = open("testdb","rb")
        self.assertEqual(database_file.read(), b"\x85[\xd4T")
        database_file.close()
        os.system("rm testdb")
