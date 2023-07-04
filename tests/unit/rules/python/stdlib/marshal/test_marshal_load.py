# Copyright 2023 Secure Saurce LLC
import os

from precli.core.level import Level
from precli.rules import Rule
from tests.unit.rules.python import test_case


class MarshalLoadTests(test_case.TestCase):
    def setUp(self):
        super().setUp()
        self.base_path = os.path.join(
            "tests",
            "unit",
            "rules",
            "python",
            "stdlib",
            "marshal",
            "examples",
        )

    def test_marshal_load_rule_meta(self):
        rule = Rule.get_by_id("PRE0009")
        self.assertEqual("PRE0009", rule.id)
        self.assertEqual("deserialization_of_untrusted_data", rule.name)
        self.assertEqual("", rule.help_url)
        self.assertEqual(True, rule.default_config.enabled)
        self.assertEqual(Level.WARNING, rule.default_config.level)
        self.assertEqual(-1.0, rule.default_config.rank)
        self.assertEqual("502", rule.cwe.cwe_id)

    def test_marshal_load(self):
        results = self.parser.parse(
            os.path.join(self.base_path, "marshal_load.py")
        )
        self.assertEqual(1, len(results))
        result = results[0]
        self.assertEqual("PRE0009", result.rule_id)
        self.assertEqual(10, result.location.start_line)
        self.assertEqual(10, result.location.end_line)
        self.assertEqual(18, result.location.start_column)
        self.assertEqual(30, result.location.end_column)
        self.assertEqual(Level.WARNING, result.level)
        self.assertEqual(-1.0, result.rank)

    def test_marshal_loads(self):
        results = self.parser.parse(
            os.path.join(self.base_path, "marshal_loads.py")
        )
        self.assertEqual(1, len(results))
        result = results[0]
        self.assertEqual("PRE0009", result.rule_id)
        self.assertEqual(5, result.location.start_line)
        self.assertEqual(5, result.location.end_line)
        self.assertEqual(0, result.location.start_column)
        self.assertEqual(13, result.location.end_column)
        self.assertEqual(Level.WARNING, result.level)
        self.assertEqual(-1.0, result.rank)