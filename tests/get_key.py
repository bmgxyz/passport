import unittest
import passport

class GetKey(unittest.TestCase):
    def test_get_key_passphrase(self):
        key = passport.get_key("passphrase")
        self.assertEqual(key, "1e089e3c5323ad80")
    def test_get_key_blergh_camel_case(self):
        key = passport.get_key("BlErGh")
        self.assertEqual(key, "7b90a185339e252b")
    def test_get_key_special_characters(self):
        key = passport.get_key("\t\n`/!@#$%^&*()<>[]{}?")
        self.assertEqual(key, "da0680356a65dcb5")
