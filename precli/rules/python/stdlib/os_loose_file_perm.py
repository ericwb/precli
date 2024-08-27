# Copyright 2024 Secure Sauce LLC
r"""
# Incorrect Permission Assignment for Critical Resource using `os` Module

This rule identifies instances in code where potentially risky file or
directory permission modes are being set using functions like chmod, fchmod,
mknod, open, lchmod, and similar system calls. Setting inappropriate
permission modes can lead to security vulnerabilities, including unauthorized
access, data leakage, or privilege escalation.

Setting overly permissive modes (e.g., 0777, 0666) can expose files or
directories to unauthorized access or modification. The rule flags instances
where the mode may pose a security risk, particularly when:

 - Write permissions are granted to others (group or world): Modes like 0666
   (read/write for everyone) or 0777 (read/write/execute for everyone) are
   inherently dangerous.
 - Inappropriate permissions for sensitive files: Configuration files,
   credential files, and other sensitive files should not be globally readable
   or writable.

## Examples

```python linenums="1" hl_lines="8-9" title="os_chmod_o755_binop_stat.py"
import os
import stat


# 0o755 for rwxr-xr-x
os.chmod(
    "example.txt",
    stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP |
    stat.S_IROTH | stat.S_IXOTH,
)
```

??? example "Example Output"
    ```
    > precli tests/unit/rules/python/stdlib/os/examples/os_chmod_o755_binop_stat.py
    ⚠️  Warning on line 8 in tests/unit/rules/python/stdlib/os/examples/os_chmod_o755_binop_stat.py
    PY036: Incorrect Permission Assignment for Critical Resource
    Mode '0o755' grants excessive permissions, potentially allowing unauthorized access or modification.
    ```

## Remediation

 - Restrict file permissions: Use more restrictive permission modes that limit
   access to only the necessary users.
 - Review file sensitivity: Ensure that sensitive files are protected with
   the appropriate permissions.
 - Apply the principle of least privilege: Only grant the minimum required
   permissions for the intended functionality.

Safer Permissions Examples:

 - For general files: 0644 (read/write for owner, read-only for group and
   others)
 - For sensitive files: 0600 (read/write for owner only)
 - For executable scripts: 0755 (read/write/execute for owner, read/execute
   for group and others)

```python linenums="1" hl_lines="8" title="os_chmod_o755_binop_stat.py"
import os
import stat


# 0o644 for rw-r--r--
os.chmod(
    "example.txt",
    stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH,
)
```

## See also

!!! info
    - [os — Miscellaneous operating system interfaces — Python documentation](https://docs.python.org/3/library/os.html#os.chmod)
    - [stat — Interpreting stat() results — Python documentation](https://docs.python.org/3/library/stat.html#stat.S_ISUID)
    - [CWE-732: Incorrect Permission Assignment for Critical Resource](https://cwe.mitre.org/data/definitions/732.html)

_New in version 0.6.2_

"""  # noqa: E501
import stat

from precli.core.call import Call
from precli.core.level import Level
from precli.core.location import Location
from precli.core.result import Result
from precli.parsers.node_types import NodeTypes
from precli.rules import Rule


class OsLooseFilePermissions(Rule):
    def __init__(self, id: str):
        super().__init__(
            id=id,
            name="incorrect_permission",
            description=__doc__,
            cwe_id=732,
            message="Mode '{0}' grants excessive permissions, potentially "
            "allowing unauthorized access or modification.",
        )

    def _risky_mode(self, mode):
        return (
            mode & stat.S_IWOTH
            or mode & stat.S_IWGRP
            or mode & stat.S_IXGRP
            or mode & stat.S_IXOTH
        )

    def analyze_import_statement(
        self, context: dict, package: str, alias: str
    ) -> None:
        if package == "stat":
            for constant in dir(stat):
                if constant.startswith("S_"):
                    context["symtab"].put(
                        f"{alias}.{constant}",
                        NodeTypes.IDENTIFIER,
                        getattr(stat, constant),
                    )

    def analyze_import_from_statement(
        self, context: dict, package: str, alias: str
    ) -> None:
        if package.startswith("stat."):
            constant = package.split(".")[-1]
            context["symtab"].put(
                alias,
                NodeTypes.IDENTIFIER,
                getattr(stat, constant),
            )

    def analyze_call(self, context: dict, call: Call) -> Result | None:
        if call.name_qualified not in (
            "os.fchmod",
            "os.chmod",
            "os.lchmod",
            "os.mkdir",  # default mode=0o777
            "os.mkfifo",  # default mode=0o666
            "os.mknod",  # default mode=0o600
            "os.open",  # default mode=0o777
        ):
            return

        argument = call.get_argument(
            position=2 if call.name_qualified == "os.open" else 1,
            name="mode",
        )
        mode = argument.value

        if argument.node is not None:
            location = Location(node=argument.node)
            message = self.message
        elif call.name_qualified in ("os.mkdir", "os.open", "os.mkfifo"):
            if call.name_qualified in ("os.mkdir", "os.open"):
                mode = 0o777
            elif call.name_qualified == "os.mkfifo":
                mode = 0o666
            location = Location(node=call.arg_list_node)
            message = (
                f"The default mode value of '{oct(mode)}' is overly "
                "permissive, potentially allowing unauthorized access or "
                "modification."
            )

        if isinstance(mode, int) and self._risky_mode(mode):
            return Result(
                rule_id=self.id,
                location=location,
                level=Level.ERROR if mode & stat.S_IWOTH else Level.WARNING,
                message=message.format(oct(mode)),
            )