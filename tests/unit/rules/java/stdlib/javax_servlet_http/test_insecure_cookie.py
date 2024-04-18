# Copyright 2024 Secure Saurce LLC
import os

from parameterized import parameterized

from precli.core.level import Level
from precli.parsers import java
from precli.rules import Rule
from tests.unit.rules import test_case


class InsecureCookieTests(test_case.TestCase):
    def setUp(self):
        super().setUp()
        self.rule_id = "JAV005"
        self.parser = java.Java()
        self.base_path = os.path.join(
            "tests",
            "unit",
            "rules",
            "java",
            "stdlib",
            "javax_servlet_http",
            "examples",
        )

    def test_rule_meta(self):
        rule = Rule.get_by_id(self.rule_id)
        self.assertEqual(self.rule_id, rule.id)
        self.assertEqual("insecure_cookie", rule.name)
        self.assertEqual(
            f"https://docs.securesauce.dev/rules/{self.rule_id}", rule.help_url
        )
        self.assertEqual(True, rule.default_config.enabled)
        self.assertEqual(Level.WARNING, rule.default_config.level)
        self.assertEqual(-1.0, rule.default_config.rank)
        self.assertEqual("614", rule.cwe.cwe_id)

    @parameterized.expand(
        [
            "CookieSecureFalse.java",
            "CookieSecureTrue.java",
        ]
    )
    def test(self, filename):
        self.check(filename)