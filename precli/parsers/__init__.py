# Copyright 2025 Secure Sauce LLC
import importlib
from abc import ABC
from abc import abstractmethod
from importlib.metadata import entry_points
from typing import Optional

import tree_sitter
from tree_sitter import Node

from precli.core.artifact import Artifact
from precli.core.level import Level
from precli.core.location import Location
from precli.core.result import Result
from precli.core.suppression import Suppression
from precli.core.symtab import Symbol
from precli.rules import Rule


class Parser(ABC):
    """
    Base class of a language specific parser.

    The parser handles most of the main functions including parsing nodes,
    processing rules based on those nodes, and compiling a list of results.

    Each parser is designed to operate on a specific programming language.
    """

    def __init__(self, lang: str):
        """Initialize a new parser."""
        self._lexer = lang
        tree_sitter_lang = importlib.import_module(f"tree_sitter_{lang}")
        self.language = tree_sitter.Language(tree_sitter_lang.language())
        self.tree_sitter_parser = tree_sitter.Parser(self.language)
        self.rules = {}
        self.wildcards = {}
        self.skip_tests = True

        discovered_rules = entry_points(group=f"precli.rules.{lang}")
        for rule in discovered_rules:
            self.rules[rule.name] = rule.load()(rule.name)

            if self.rules[rule.name].wildcards:
                for k, v in self.rules[rule.name].wildcards.items():
                    if k in self.wildcards:
                        self.wildcards[k] += v
                    else:
                        self.wildcards[k] = v

        def child_by_type(self, type: str) -> Optional[Node]:
            # Return first child with type as specified
            child = list(filter(lambda x: x.type == type, self.named_children))
            return child[0] if child else None

        setattr(Node, "child_by_type", child_by_type)

    @property
    def lexer(self) -> str:
        """The name of the lexer"""
        return self._lexer

    @abstractmethod
    def file_extensions(self) -> list[str]:
        """File extension of files this parser can handle."""

    @abstractmethod
    def rule_prefix(self) -> str:
        """The prefix for the rule ID"""

    @abstractmethod
    def get_file_encoding(self, file_contents: str) -> str:
        """The prefix for the rule ID"""

    def is_valid_code(self, code: str) -> bool:
        """Check whether the give code matches the language of this parser."""
        tree = self.tree_sitter_parser.parse(code)
        if not tree.root_node.has_error:
            return True

    @staticmethod
    def _expand_rule_list(rule_list: list[str]) -> list[str]:
        """Expand rule range if exists in the rule list"""
        expanded_rules = []
        for rule in rule_list:
            if "-" in rule:
                (rule_start, rule_end) = rule.split("-", maxsplit=1)
                if rule_start[:-3] == rule_end[:-3]:
                    try:
                        start = int(rule_start[-3:])
                        end = int(rule_end[-3:])
                        for i in range(start, end + 1):
                            expanded_rules.append(f"{rule_start[:-3]}{i:03d}")
                    except ValueError:
                        pass
            else:
                expanded_rules.append(rule)
        return expanded_rules

    def parse(
        self,
        artifact: Artifact,
        config: Optional[dict] = None,
    ) -> list[Result]:
        """File extension of files this parser can handle."""
        config = {} if config is None else config
        enabled = config.get("enabled")
        disabled = config.get("disabled")

        if enabled is not None:
            enabled = Parser._expand_rule_list(enabled)
        if disabled is not None:
            disabled = Parser._expand_rule_list(disabled)

        rule_conf = config["rule"] if "rule" in config else {}

        for rule in self.rules.values():
            if enabled is not None:
                if (
                    enabled == ["all"]
                    or rule.id in enabled
                    or rule.name in enabled
                ):
                    rule.enabled = True
                else:
                    rule.enabled = False
            elif disabled is not None and (
                disabled == ["all"]
                or rule.id in disabled
                or rule.name in disabled
            ):
                rule.enabled = False

            # Override the level and parameters if given in config
            if rule.id in rule_conf:
                if "level" in rule_conf[rule.id]:
                    rule.config.level = Level(rule_conf[rule.id].get("level"))
                for parameter, value in rule_conf[rule.id].items():
                    if parameter not in ("enabled", "level"):
                        rule.config.parameters[parameter] = value

        self.results = []
        self.context = {"artifact": artifact}
        if artifact.contents is None:
            with open(artifact.file_name, "rb") as fdata:
                artifact.contents = fdata.read()
        artifact.encoding = self.get_file_encoding(artifact.contents)
        tree = self.tree_sitter_parser.parse(artifact.contents)

        @property
        def string(self) -> str:
            return self.text.decode(encoding=artifact.encoding)

        setattr(Node, "string", string)

        self.visit([tree.root_node])

        # Run any custom queries if defined
        custom_rules = [rule for rule in self.rules.values() if rule.query]
        for rule in custom_rules:
            query = self.language.query(rule.query)
            captures = query.captures(tree.root_node)
            for location in captures.get(rule.location_node, []):
                result = Result(
                    rule_id=rule.id,
                    location=Location(node=location),
                    message=rule.message,
                )
                self.results.append(result)

        for result in self.results:
            result.artifact = artifact

            suppression = self.suppressions.get(result.location.start_line)
            if suppression and result.rule_id in suppression.rules:
                result.suppression = suppression

        return self.results

    def visit(self, nodes: list[Node]):
        """
        Generic visitor of nodes.

        THis function will visit each node and attempt to call a more
        specific visit function if defined based on the node type.
        """
        for node in nodes:
            # print(node)

            self.context["node"] = node
            visitor_fn = getattr(self, f"visit_{node.type}", self.visit)
            visitor_fn(node.children)

    def visit_comment(self, nodes: list[Node]):
        comment = self.context["node"].string

        suppressed = self.SUPPRESS_COMMENT.search(comment)
        if suppressed is None:
            return

        matches = suppressed.groupdict()
        suppressed_rules = matches.get("rules")

        if suppressed_rules is None:
            return

        rules = set()
        for rule in self.SUPPRESSED_RULES.finditer(suppressed_rules):
            rule_name_or_id = rule.group(1)
            if Rule.get_by_id(rule_name_or_id) is not None:
                rules.add(rule_name_or_id)

        if not rules:
            return

        suppression = Suppression(
            location=Location(node=self.context["node"]),
            rules=rules,
        )

        prev_node = self.context["node"].prev_sibling
        node = self.context["node"]

        if prev_node.end_point[0] == node.start_point[0]:
            self.suppressions[node.start_point[0] + 1] = suppression
        else:
            self.suppressions[node.start_point[0] + 2] = suppression

        # TODO: add the justification to the suppression

    def visit_ERROR(self, nodes: list[Node]):
        err_node = self.child_by_type(self.context["node"], "ERROR")
        if err_node is None:
            err_node = self.context["node"]

        raise SyntaxError(
            "Syntax error while parsing file.",
            (
                self.context["artifact"].file_name,
                err_node.start_point[0] + 1,
                err_node.start_point[1] + 1,
                err_node.text.decode(errors="ignore"),
                err_node.end_point[0] + 1,
                err_node.end_point[1] + 1,
            ),
        )

    def child_by_type(self, node: Node, type: str) -> Optional[Node]:
        # Return first child with type as specified
        child = list(filter(lambda x: x.type == type, node.named_children))
        return child[0] if child else None

    def join_symbol(self, nodetext: str, symbol: Symbol):
        if isinstance(symbol.value, str):
            value = nodetext.replace(symbol.name, symbol.value, 1)
        else:
            value = symbol.value
        return value

    @abstractmethod
    def is_test_code(self) -> bool:
        """
        Determine if analyzing test code.

        This function determines if the current position of the analysis
        is within unit test code. The purpose of which is to potentially
        ignore rules in test code.
        """

    def analyze_node(self, node_type: str, **kwargs: dict) -> None:
        """
        Process the rules based on node_type.

        This function will iterate through all rules that are designed to
        handle the given node type (node_type).
        """
        if self.skip_tests and self.is_test_code():
            return

        fn = f"analyze_{node_type}"
        for rule in self.rules.values():
            if hasattr(rule, fn) and rule.enabled:
                context = self.context
                context["symtab"] = self.current_symtab
                if "global_symtab" in vars(self):
                    context["global_symtab"] = self.global_symtab

                analyze_fn = getattr(rule, fn)
                result = analyze_fn(self.context, **kwargs)

                if result is not None:
                    self.results.append(result)
