# Copyright 2025 Secure Sauce LLC
# SPDX-License-Identifier: BUSL-1.1
r"""
# Inadequate Encryption Strength Using Weak Keys in SSLContext

Using weak key sizes for cryptographic algorithms like Elliptic Curve can
compromise the security of your encryption and digital signatures. Here's
a brief overview of the risks associated with weak key sizes for this
algorithm:

Elliptic Curve cryptography provides strong security with relatively small
key sizes compared to RSA and DSA. However, even in the case of EC, using
weak curve parameters or small key sizes can expose you to vulnerabilities.
The strength of an EC key depends on the curve's properties and the size of
the prime used.

Recommended EC key sizes depend on the curve you select, but for modern
applications, curves like NIST P-256 (secp256r1) with a 256-bit key size
are considered secure. Larger curves, like NIST P-384 or P-521, can provide
even higher security margins.

# Example

```python linenums="1" hl_lines="5" title="ssl_context_set_ecdh_curve_prime192v1.py"
import ssl


context = ssl.SSLContext()
context.set_ecdh_curve("prime192v1")
```

??? example "Example Output"
    ```
    > precli tests/unit/rules/python/stdlib/ssl/examples/ssl_context_set_ecdh_curve_prime192v1.py
    ⚠️  Warning on line 5 in tests/unit/rules/python/stdlib/ssl/examples/ssl_context_set_ecdh_curve_prime192v1.py
    PY019: Inadequate Encryption Strength
    Using 'EC' key sizes less than '224' bits is considered vulnerable to attacks.
    ```

# Remediation

Its recommended to increase the key size to at least 224 EC algorithms.

```python linenums="1" hl_lines="5" title="ssl_context_set_ecdh_curve_prime192v1.py"
import ssl


context = ssl.SSLContext()
context.set_ecdh_curve("prime256v1")
```

# Default Configuration

```toml
enabled = true
level = "warning"
ec_key_size_warning = 224
ec_key_size_error = 160
```

# See also

!!! info
    - [ssl — TLS/SSL wrapper for socket objects](https://docs.python.org/3/library/ssl.html#ssl.SSLContext.set_ecdh_curve)
    - [CWE-326: Inadequate Encryption Strength](https://cwe.mitre.org/data/definitions/326.html)
    - [Transport Layer Security (TLS) Parameters](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-parameters-8)

_New in version 0.2.3_

"""  # noqa: E501
import re
from typing import Optional

from precli.core.call import Call
from precli.core.level import Level
from precli.core.location import Location
from precli.core.result import Result
from precli.i18n import _
from precli.rules import Rule


class SslContextWeakKey(Rule):
    def __init__(self, id: str):
        super().__init__(
            id=id,
            name="inadequate_encryption_strength",
            description=__doc__,
            cwe_id=326,
            message=_(
                "Using '{0}' key sizes less than '{1}' bits is considered "
                "vulnerable to attacks."
            ),
        )

    def analyze_call(self, context: dict, call: Call) -> Optional[Result]:
        if call.name_qualified not in [
            "ssl.SSLContext.set_ecdh_curve",
            "ssl.create_default_context.set_ecdh_curve",
            "ssl._create_unverified_context.set_ecdh_curve",
        ]:
            return

        SIZE_WARN = self.config.parameters.get("ec_key_size_warning")
        SIZE_ERR = self.config.parameters.get("ec_key_size_error")

        arg = call.get_argument(position=0, name="curve_name")
        curve_name = arg.value

        result = re.search(r"sec[p|t](\d{3})(?:r1|r2|k1){1}", curve_name)
        if not result:
            result = re.search(r"prime(\d{3})v[1|2|3]", curve_name)
        if not result:
            result = re.search(r"brainpoolP(\d{3})r[1|2|3]", curve_name)
        if not result:
            result = re.search(r"brainpoolP(\d{3})r1tls13", curve_name)
        key_size = int(result.group(1)) if result else SIZE_WARN

        if key_size < SIZE_WARN:
            fixes = Rule.get_fixes(
                context=context,
                deleted_location=Location(node=arg.node),
                description=_(
                    f"Use a curve with a minimum size of {SIZE_WARN} bits."
                ),
                inserted_content='"secp256k1"',
            )

            return Result(
                rule_id=self.id,
                location=Location(node=arg.node),
                level=Level.ERROR if key_size < SIZE_ERR else Level.WARNING,
                message=self.message.format("EC", SIZE_WARN),
                fixes=fixes,
            )
