import os
import unittest
import passport

class ReadAndDecrypt(unittest.TestCase):
    def test_empty_database(self):
        test_file = open("testdb","wb")
        test_file.write(b"\x85[\xd4T")
        test_file.close()
        self.assertEqual(passport.read_and_decrypt("testdb","blergh"),
                ({},"blergh"))
        os.system("rm testdb")
    # TODO add more tests
