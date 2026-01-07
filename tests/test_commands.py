import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import json
from dbl.commands import (
    cmd_init, cmd_version, cmd_log, cmd_branch, cmd_checkout,
    cmd_rebase, cmd_validate, cmd_reset
)
from dbl.constants import CONFIG_FILE, LAYERS_DIR, MANIFEST_FILE


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.config = {
            'db_name': 'testdb',
            'engine': 'postgres',
            'host': 'localhost',
            'port': 5432,
            'user': 'admin',
            'password': 'pass'
        }

    @patch('dbl.commands.init.os.path.exists')
    @patch('dbl.commands.init.yaml.dump')
    @patch('dbl.commands.init.open', new_callable=mock_open)
    def test_cmd_init(self, mock_file, mock_yaml, mock_exists):
        mock_exists.return_value = False
        with patch('dbl.commands.init.save_manifest'):
            cmd_init(MagicMock())
        mock_file.assert_called()
        mock_yaml.assert_called_once()

    @patch('dbl.commands.help_cmd.VERSION', '1.0.0')
    @patch('dbl.commands.help_cmd.log')
    def test_cmd_version(self, mock_log):
        cmd_version(MagicMock())
        mock_log.assert_has_calls([
            unittest.mock.call("DBL (Database Layering) v1.0.0", "header"),
            unittest.mock.call("Repository: https://github.com/alann-estrada-KSH/dbl-sandbox", "info")
        ])

    @patch('dbl.commands.log.load_manifest')
    @patch('dbl.commands.log.log')
    def test_cmd_log(self, mock_log_func, mock_load):
        mock_load.return_value = {
            'current': 'master',
            'branches': {'master': [{'file': 'layer1.sql', 'msg': 'test'}]}
        }
        cmd_log(MagicMock())
        mock_log_func.assert_called()

    @patch('dbl.commands.branch.load_manifest')
    @patch('dbl.commands.branch.save_manifest')
    @patch('dbl.commands.branch.log')
    def test_cmd_branch_create(self, mock_log, mock_save, mock_load):
        mock_load.return_value = {'current': 'master', 'branches': {'master': []}}
        args = MagicMock()
        args.name = 'feature'
        args.delete = None
        cmd_branch(args)
        mock_save.assert_called()

    @patch('dbl.commands.branch.load_manifest')
    @patch('dbl.commands.branch.save_manifest')
    @patch('dbl.commands.reset.cmd_reset')
    @patch('dbl.commands.branch.get_target_db')
    @patch('dbl.commands.branch.load_config')
    @patch('dbl.commands.branch.log')
    def test_cmd_checkout(self, mock_log, mock_load_config, mock_get_target, mock_cmd_reset, mock_save, mock_load):
        mock_load.return_value = {'current': 'master', 'branches': {'master': [], 'feature': []}}
        mock_get_target.return_value = ('testdb', False)
        mock_load_config.return_value = self.config
        args = MagicMock()
        args.branch = 'feature'
        cmd_checkout(args)
        mock_save.assert_called()

    @patch('dbl.commands.rebase.load_manifest')
    @patch('dbl.commands.rebase.save_manifest')
    @patch('dbl.commands.rebase.log')
    def test_cmd_rebase(self, mock_log, mock_save, mock_load):
        mock_load.return_value = {
            'current': 'feature',
            'branches': {'master': [{'file': 'm1.sql'}], 'feature': [{'file': 'f1.sql'}]}
        }
        args = MagicMock()
        args.onto = 'master'
        args.dry_run = False
        args.no_backup = False
        cmd_rebase(args)
        mock_save.assert_called()

    @patch('dbl.commands.validate.load_manifest')
    @patch('dbl.state.get_target_db')
    @patch('dbl.commands.validate.load_config')
    @patch('dbl.config.get_engine')
    @patch('dbl.commands.validate.log')
    def test_cmd_validate(self, mock_log, mock_get_engine, mock_load_config, mock_get_target, mock_load):
        mock_load.return_value = {'current': 'master', 'branches': {'master': []}}
        mock_get_target.return_value = ('testdb', False)
        mock_load_config.return_value = self.config
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine
        mock_engine.inspect_db.return_value = {}
        args = MagicMock()
        args.branch = None
        args.fix = False
        cmd_validate(args)
        mock_log.assert_called()

    @patch('dbl.commands.reset.load_manifest')
    @patch('dbl.commands.reset.get_target_db')
    @patch('dbl.commands.reset.load_config')
    @patch('dbl.commands.reset.get_engine')
    @patch('dbl.commands.reset.confirm_action')
    @patch('dbl.commands.reset.run_command')
    @patch('dbl.commands.reset.log')
    @patch('dbl.commands.reset.os.path.exists')
    def test_cmd_reset(self, mock_exists, mock_log, mock_run, mock_confirm, mock_get_engine, mock_load_config, mock_get_target, mock_load):
        mock_load.return_value = {'current': 'master', 'branches': {'master': [{'file': 'layer1.sql'}]}}
        mock_get_target.return_value = ('testdb', False)
        mock_load_config.return_value = self.config
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine
        mock_confirm.return_value = True
        mock_exists.return_value = False
        args = MagicMock()
        cmd_reset(args)
        mock_run.assert_called()

    @patch('dbl.commands.init.load_config')
    @patch('dbl.commands.init.get_engine')
    @patch('dbl.commands.init.confirm_action')
    @patch('dbl.commands.init.run_command')
    @patch('dbl.commands.init.log')
    def test_cmd_import(self, mock_log, mock_run, mock_confirm, mock_get_engine, mock_load_config):
        from dbl.commands import cmd_import
        mock_load_config.return_value = self.config
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine
        mock_confirm.return_value = True
        args = MagicMock()
        args.file = 'snapshot.sql'
        cmd_import(args)
        mock_run.assert_called()

    @patch('dbl.commands.sandbox.load_config')
    @patch('dbl.commands.sandbox.get_engine')
    @patch('dbl.commands.sandbox.log')
    @patch('dbl.commands.sandbox.json.dump')
    @patch('dbl.commands.sandbox.open', new_callable=mock_open)
    def test_cmd_sandbox_start(self, mock_file, mock_json, mock_log, mock_get_engine, mock_load_config):
        from dbl.commands import cmd_sandbox
        mock_load_config.return_value = self.config
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine
        args = MagicMock()
        args.action = 'start'
        cmd_sandbox(args)
        mock_log.assert_called()

    @patch('dbl.commands.log.load_manifest')
    @patch('dbl.commands.log.log')
    def test_cmd_rev_parse(self, mock_log_func, mock_load):
        from dbl.commands import cmd_rev_parse
        mock_load.return_value = {
            'current': 'master',
            'branches': {'master': [{'file': 'layer1.sql', 'msg': 'test'}]}
        }
        args = MagicMock()
        args.ref = 'invalid'
        cmd_rev_parse(args)
        mock_log_func.assert_called()

    @patch('dbl.commands.branch.load_manifest')
    @patch('dbl.state.get_target_db')
    @patch('dbl.commands.branch.load_config')
    @patch('dbl.commands.init.get_engine')
    @patch('dbl.commands.branch.run_command')
    @patch('dbl.commands.branch.log')
    def test_cmd_merge(self, mock_log, mock_run, mock_get_engine, mock_load_config, mock_get_target, mock_load):
        from dbl.commands import cmd_merge
        mock_load.return_value = {'current': 'master', 'branches': {'master': [], 'feature': [{'file': 'f1.sql'}]}}
        mock_get_target.return_value = ('testdb', False)
        mock_load_config.return_value = self.config
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine
        args = MagicMock()
        args.branch = 'feature'
        cmd_merge(args)
        mock_run.assert_called()

    @patch('dbl.commands.update.log')
    def test_cmd_update(self, mock_log):
        from dbl.commands import cmd_update
        args = MagicMock()
        args.yes = False
        cmd_update(args)
        mock_log.assert_called()


if __name__ == '__main__':
    unittest.main()