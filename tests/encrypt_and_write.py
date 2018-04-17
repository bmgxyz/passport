import os
import unittest
import passport

class EncryptAndWrite(unittest.TestCase):
    def test_empty_database(self):
        passport.encrypt_and_write("{}", "testdb", database_password="blergh")
        written_file = open("testdb", "rb")
        self.assertEqual(written_file.read(), b"\x85[\xd4T")
        written_file.close()
        os.system("rm testdb")
    def test_arbitrary_data(self):
        passport.encrypt_and_write(
                "\t\n`!@#$%^&*()_+[]{};'<>,.?/",
                "testdb",
                database_password="\t\n`!@#$%^&*()_+[]{};'<>,.?/")
        written_file = open("testdb", "rb")
        self.assertEqual(written_file.read(),
                (b"\x8d\xd0\xa5\\\xea\x15+D|W\xfe@\xef\x80-u\xc9\xb69e1J\xbd4t."
                b"BPUzY"))
        written_file.close()
        os.system("rm testdb")
