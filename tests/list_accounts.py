import unittest
import passport

class ListAccounts(unittest.TestCase):
    # TODO add some tests
    def test_list_empty_database(self):
        self.assertEqual(passport.list_accounts({},"testdb",silent=True),
                "'testdb' is empty.")
