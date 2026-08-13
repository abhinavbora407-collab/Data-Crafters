import unittest
from database.database import init_db, query_db_one, query_df

class TestDatabase(unittest.TestCase):
    def test_database_initialization(self):
        init_db()
        result = query_db_one("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'users')

if __name__ == "__main__":
    unittest.main()
