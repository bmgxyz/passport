import os
import unittest
import passport

class EncryptAndWrite(unittest.TestCase):
    def test_empty_database(self):
        passport.encrypt_and_write(
                "{}", "testdb", database_password="blergh")
        written_file = open("testdb", "rb")
        self.assertEqual(written_file.read(), b"\x85[\xd4T")
        written_file.close()
        os.system("rm testdb")
    # TODO add more tests
