import unittest
from unittest.mock import patch
from dbl.engines.postgres import PostgresEngine


class TestPostgresEngine(unittest.TestCase):
    def setUp(self):
        self.config = {
            'db_name': 'testdb',
            'engine': 'postgres',
            'host': 'localhost',
            'port': 5432,
            'user': 'admin',
            'password': 'pass',
            'container_name': 'test_container'
        }
        self.engine = PostgresEngine(self.config)

    @patch('dbl.engines.postgres.run_command')
    def test_inspect_db(self, mock_run_command):
        mock_run_command.return_value = "users|id|int|NO|nextval('users_id_seq'::regclass)||32|0\nusers|name|varchar|YES||100||"

        schema = self.engine.inspect_db('testdb')

        self.assertIn('users', schema)
        self.assertIn('id', schema['users'])
        self.assertIn('name', schema['users'])
        self.assertEqual(schema['users']['id']['type'], 'int')
        self.assertEqual(schema['users']['name']['type'], 'varchar')

    @patch('dbl.engines.postgres.run_command')
    def test_get_tables(self, mock_run_command):
        mock_run_command.return_value = "users\nproducts\n"

        tables = self.engine.get_tables('testdb')

        self.assertEqual(tables, ['users', 'products'])


if __name__ == '__main__':
    unittest.main()