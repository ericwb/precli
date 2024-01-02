# Copyright 2023 Secure Saurce LLC
import os

from parameterized import parameterized

from precli.core.level import Level
from precli.parsers import python
from precli.rules import Rule
from tests.unit.rules import test_case


class HostKeyPolicyTests(test_case.TestCase):
    def setUp(self):
        super().setUp()
        self.rule_id = "PY511"
        self.parser = python.Python(enabled=[self.rule_id])
        self.base_path = os.path.join(
            "tests",
            "unit",
            "rules",
            "python",
            "paramiko",
            "examples",
        )

    def test_paramiko_no_host_key_verify_rule_meta(self):
        rule = Rule.get_by_id(self.rule_id)
        self.assertEqual(self.rule_id, rule.id)
        self.assertEqual("improper_certificate_validation", rule.name)
        self.assertEqual(
            f"https://docs.securesauce.dev/rules/{self.rule_id}", rule.help_url
        )
        self.assertEqual(True, rule.default_config.enabled)
        self.assertEqual(Level.WARNING, rule.default_config.level)
        self.assertEqual(-1.0, rule.default_config.rank)
        self.assertEqual("295", rule.cwe.cwe_id)

    @parameterized.expand(
        [
            "host_key_auto_add_policy.py",
            "host_key_auto_add_policy_import_paramiko.py",
            "host_key_auto_add_policy_in_func.py",
            "host_key_auto_add_policy_kwarg.py",
            "host_key_auto_add_policy_single_statement.py",
            "host_key_auto_add_policy_walrus.py",
            "host_key_warning_policy_single_statement.py",
        ]
    )
    def test(self, filename):
        self.check(filename)