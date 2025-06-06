# Copyright 2025 Secure Sauce LLC
# SPDX-License-Identifier: BUSL-1.1
r"""
# Cleartext Transmission of Sensitive Information in the `smtplib` Module

The Python module `smtplib` provides a number of functions for accessing
SMTP servers. However, the default behavior of the module does not provide
utilize secure connections. This means that data transmitted over the network,
including passwords, is sent in cleartext. This makes it possible for attackers
to intercept and read this data.

The Python module smtplib should only in a secure mannner to protect sensitive
data when accessing SMTP servers.

# Example

```python linenums="1" hl_lines="24 25" title="smtplib_smtp_login.py"
import smtplib


def prompt(prompt):
    return input(prompt).strip()

fromaddr = prompt("From: ")
toaddrs  = prompt("To: ").split()
print("Enter message, end with ^D (Unix) or ^Z (Windows):")

# Add the From: and To: headers at the start!
msg = ("From: %s\r\nTo: %s\r\n\r\n" % (fromaddr, ", ".join(toaddrs)))
while True:
    try:
        line = input()
    except EOFError:
        break
    if not line:
        break
    msg = msg + line

print("Message length is", len(msg))

server = smtplib.SMTP('localhost')
server.login("user", "password")
server.set_debuglevel(1)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()
```

??? example "Example Output"
    ```
    > precli tests/unit/rules/python/stdlib/smtplib/examples/smtplib_smtp_login.py
    ⛔️ Error on line 25 in tests/unit/rules/python/stdlib/smtplib/examples/smtplib_smtp_login.py
    PY016: Cleartext Transmission of Sensitive Information
    The 'smtplib.SMTP.login' function will transmit authentication information such as a user, password in cleartext.
    ```

# Remediation

If the SMTP protocol must be used and sensitive data will be transferred, it
is recommended to secure the connection using `SMTP_SSL` class.
Alternatively, the `starttls` function can be used to enter a secure session.


```python linenums="1" hl_lines="24" title="smtplib_smtp_login.py"
import smtplib


def prompt(prompt):
    return input(prompt).strip()

fromaddr = prompt("From: ")
toaddrs  = prompt("To: ").split()
print("Enter message, end with ^D (Unix) or ^Z (Windows):")

# Add the From: and To: headers at the start!
msg = ("From: %s\r\nTo: %s\r\n\r\n" % (fromaddr, ", ".join(toaddrs)))
while True:
    try:
        line = input()
    except EOFError:
        break
    if not line:
        break
    msg = msg + line

print("Message length is", len(msg))

server = smtplib.SMTP_SSL('localhost')
server.login("user", "password")
server.set_debuglevel(1)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()
```

# Default Configuration

```toml
enabled = true
level = "error"
```

# See also

!!! info
    - [smtplib — SMTP protocol client](https://docs.python.org/3/library/smtplib.html)
    - [CWE-319: Cleartext Transmission of Sensitive Information](https://cwe.mitre.org/data/definitions/319.html)

_New in version 0.1.9_

"""  # noqa: E501
from typing import Optional

from precli.core.call import Call
from precli.core.location import Location
from precli.core.result import Result
from precli.i18n import _
from precli.rules import Rule


class SmtpCleartext(Rule):
    def __init__(self, id: str):
        super().__init__(
            id=id,
            name="cleartext_transmission",
            description=__doc__,
            cwe_id=319,
            message=_(
                "The POP protocol can transmit data in cleartext without "
                "encryption."
            ),
        )

    def analyze_call(self, context: dict, call: Call) -> Optional[Result]:
        if call.name_qualified not in [
            "smtplib.SMTP.login",
            "smtplib.SMTP.auth",
        ]:
            return

        symbol = context["symtab"].get(call.var_node.text.decode())
        if "starttls" in [
            x.identifier_node.text.decode() for x in symbol.call_history
        ]:
            return

        init_call = symbol.call_history[0]
        fixes = Rule.get_fixes(
            context=context,
            deleted_location=Location(node=init_call.identifier_node),
            description=_(
                "Use the 'SMTP_SSL' module to secure the connection."
            ),
            inserted_content="SMTP_SSL",
        )

        return Result(
            rule_id=self.id,
            location=Location(node=call.identifier_node),
            message=_(
                f"The '{call.name_qualified}' function will transmit "
                "authentication information such as a user, password in "
                "cleartext."
            ),
            fixes=fixes,
        )
