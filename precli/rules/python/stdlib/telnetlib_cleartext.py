# Copyright 2024 Secure Sauce LLC
# SPDX-License-Identifier: BUSL-1.1
r"""
# Cleartext Transmission of Sensitive Information in the `telnetlib` Module

The Python module `telnetlib` is a low-level module that provides access to
the telnet protocol. The telnet protocol is a cleartext protocol, which means
that all data transmitted over the connection is visible to anyone who can
sniff the network traffic. This includes passwords, usernames, and other
sensitive data.

If you need to access a remote system over a network, you should use a more
secure protocol, such as SSH. SSH is a secure shell protocol that encrypts
all data transmitted over the connection. This makes it much more difficult
for attackers to eavesdrop on your communications.

If you must use telnetlib, you should take steps to mitigate the risks
associated with using a cleartext protocol. For example, you should only use
telnetlib to connect to systems that you trust. You should also use a strong
password and enable encryption if possible.

Here are some additional reasons why you should not use telnetlib:

- It is not secure. As mentioned above, telnetlib transmits data in
  cleartext, which makes it vulnerable to eavesdropping.

- It is not recommended by security experts. Security experts recommend
  using more secure protocols, such as SSH.

# Example

```python linenums="1" hl_lines="2 9" title="telnetlib_telnet.py"
import getpass
import telnetlib


HOST = "localhost"
user = input("Username: ")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)
tn.read_until(b"login: ")
tn.write(user.encode('ascii') + b"\n")
if password:
    tn.read_until(b"Password: ")
    tn.write(password.encode('ascii') + b"\n")

tn.write(b"ls\n")
tn.write(b"exit\n")
```

??? example "Example Output"
    ```
    > precli tests/unit/rules/python/stdlib/telnetlib/examples/telnetlib_telnet.py
    ⛔️ Error on line 9 in tests/unit/rules/python/stdlib/telnetlib/examples/telnetlib_telnet.py
    PY020: Cleartext Transmission of Sensitive Information
    The 'telnetlib.Telnet' module transmits data in cleartext without encryption.
    ```

# Remediation

If you need to access a remote system over a network, you should use a more
secure protocol, such as SSH. SSH is a secure shell protocol that encrypts
all data transmitted over the connection. This makes it much more difficult
for attackers to eavesdrop on your communications.

There are better alternatives. There are a number of other Python modules
that provide access to the telnet protocol, such as Paramiko. These modules
are more secure than telnetlib and should be used instead.

```python linenums="1" hl_lines="2 9" title="telnetlib_telnet.py"
import getpass
import paramiko


HOST = "localhost"
user = input("Username: ")
password = getpass.getpass()

client = paramiko.SSHClient()
client.connect(HOST, username=user, password=password)
channel = client.invoke_shell()
client.close()
```

# Alternatives to telnetlib

There are a number of alternatives to ftplib that provide security features.
These alternatives include:

 - `Paramiko`: Paramiko is a Python module that provides secure access to
   SSH servers. Paramiko uses encryption to protect data transmitted over the
   network.

 - `Twisted`: Twisted is a Python framework that provides a number of
   network protocols, including SSH. Twisted can be used to create secure
   SSH clients and servers.

# Default Configuration

```toml
enabled = true
level = "error"
```

# See also

!!! info
    - [telnetlib — Telnet client](https://docs.python.org/3/library/telnetlib.html)
    - [CWE-319: Cleartext Transmission of Sensitive Information](https://cwe.mitre.org/data/definitions/319.html)
    - [Paramiko](https://www.paramiko.org/)
    - [Twisted](https://twisted.org/)

_New in version 0.1.0_

"""  # noqa: E501
from typing import Optional

from precli.core.call import Call
from precli.core.location import Location
from precli.core.result import Result
from precli.i18n import _
from precli.rules import Rule


class TelnetlibCleartext(Rule):
    def __init__(self, id: str):
        super().__init__(
            id=id,
            name="cleartext_transmission",
            description=__doc__,
            cwe_id=319,
            message=_(
                "The '{0}' module transmits data in cleartext without "
                "encryption."
            ),
        )

    def analyze_call(self, context: dict, call: Call) -> Optional[Result]:
        if call.name_qualified in ["telnetlib.Telnet"]:
            return Result(
                rule_id=self.id,
                location=Location(node=call.function_node),
                message=self.message.format(call.name_qualified),
            )
