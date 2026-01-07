import unittest
from unittest.mock import patch, MagicMock
import json
from dbl.state import get_state, _process_table
from dbl.engines.postgres import PostgresEngine


class TestState(unittest.TestCase):
    def setUp(self):
        self.config = {
            'db_name': 'testdb',
            'engine': 'postgres',
            'host': 'localhost',
            'port': 5432,
            'user': 'admin',
            'password': 'pass',
            'track_tables': [],
            'ignore_tables': []
        }
        self.engine = PostgresEngine(self.config)

    @patch('dbl.state._process_table')
    @patch.object(PostgresEngine, 'inspect_db')
    @patch.object(PostgresEngine, 'get_tables')
    def test_get_state_schema_only(self, mock_get_tables, mock_inspect_db, mock_process):
        mock_inspect_db.return_value = {'table1': {'id': {'type': 'int'}}, 'table2': {'name': {'type': 'varchar'}}}
        mock_get_tables.return_value = ['table1', 'table2']
        mock_process.side_effect = [('table1', 'hash1', None, None), ('table2', 'hash2', None, None)]

        result = get_state(self.engine, 'testdb', self.config)

        self.assertIn('schema', result)
        self.assertIn('data', result)
        self.assertEqual(len(result['data']), 2)  # 2 data tables

    @patch.object(PostgresEngine, 'get_primary_keys')
    @patch.object(PostgresEngine, 'execute_query')
    @patch('dbl.state.run_command')
    def test_process_table_with_pk(self, mock_run_command, mock_execute_query, mock_get_pk):
        mock_get_pk.return_value = ['id']
        mock_execute_query.return_value = "psql ... -c 'SELECT * FROM table1 ORDER BY id'"
        mock_run_command.return_value = "1|test\n2|data\n"

        result = _process_table(self.engine, 'testdb', 'table1', self.config)

        table, hash_val, pk_issue, error = result
        self.assertEqual(table, 'table1')
        self.assertIsInstance(hash_val, str)
        self.assertIsNone(pk_issue)
        self.assertIsNone(error)

    @patch.object(PostgresEngine, 'get_primary_keys')
    @patch.object(PostgresEngine, 'dump_table_data')
    def test_process_table_without_pk(self, mock_dump, mock_get_pk):
        mock_get_pk.return_value = []
        mock_dump.return_value = "test data\n"

        result = _process_table(self.engine, 'testdb', 'table1', self.config)

        table, hash_val, pk_issue, error = result
        self.assertEqual(table, 'table1')
        self.assertIsInstance(hash_val, str)
        self.assertEqual(pk_issue, 'table1')  # Without PK
        self.assertIsNone(error)


if __name__ == '__main__':
    unittest.main()