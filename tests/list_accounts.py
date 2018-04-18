import unittest
import passport

class ListAccounts(unittest.TestCase):
    def test_list_empty_database(self):
        self.assertEqual(passport.list_accounts({},"testdb",silent=True),
                "'testdb' is empty.")
    def test_list_not_empty_database(self):
        test_password_database = {"test-account1":"",
                "test-account2":"",
                "test-account3":""}
        self.assertEqual(
                passport.list_accounts(test_password_database,
                    "testdb",
                    silent=True),
                "test-account1\ntest-account2\ntest-account3")
