# Copyright 2024 Secure Sauce LLC
# SPDX-License-Identifier: BUSL-1.1
r"""
# Reversible One Way Hash in `crypt` Module

The Python module `crypt` provides a number of functions for password
hashing. However, some of the hashing functions supported by `crypt` are weak
and should not be used. These weak hashing functions include `CRYPT` and
`MD5`.

The `CRYPT` hashing function is a weak hashing function because it is based
on a simple DES algorithm. This algorithm is relatively easy to crack, and
passwords hashed with crypt can be easily recovered by attackers.

The `MD5` hashing function is also a weak hashing function. MD5 is a
cryptographic hash function that was designed in the early 1990s. MD5 is
no longer considered secure, and passwords hashed with MD5 can be easily
cracked by attackers.

If using the crypt module, it is recommended to use more secure methods such
as `SHA256` and `SHA512`.

# Examples

=== "crypt.crypt"

    ```python linenums="1" hl_lines="4" title="crypt_crypt_method_md5.py"
    import crypt


    crypt.crypt("password", salt=crypt.METHOD_MD5)
    ```

    ??? example "Example Output"
        ```
        > precli tests/unit/rules/python/stdlib/crypt/examples/crypt_crypt_method_md5.py
        ⚠️  Warning on line 4 in tests/unit/rules/python/stdlib/crypt/examples/crypt_crypt_method_md5.py
        PY002: Use of Weak Hash
        Use of weak hash function 'crypt.METHOD_MD5' does not meet security expectations.
        ```

=== "crypt.mksalt"

    ```python linenums="1" hl_lines="4" title="crypt_mksalt_method_crypt.py"
    import crypt


    crypt.mksalt(crypt.METHOD_CRYPT)
    ```

    ??? example "Example Output"
        ```
        > precli tests/unit/rules/python/stdlib/crypt/examples/crypt_mksalt_method_crypt.py
        ⚠️  Warning on line 4 in tests/unit/rules/python/stdlib/crypt/examples/crypt_mksalt_method_crypt.py
        PY002: Use of Weak Hash
        Use of weak hash function 'crypt.METHOD_CRYPT' does not meet security expectations.
        ```

# Remediation

The recommendation is to swap the insecure hashing method to one of the more
secure alternatives, `SHA256` or `SHA512`.

=== "crypt.crypt"

    ```python linenums="1" hl_lines="4" title="crypt_crypt_method_md5.py"
    import crypt


    crypt.crypt("password", salt=crypt.METHOD_SHA256)
    ```

=== "crypt.mksalt"

    ```python linenums="1" hl_lines="4" title="crypt_mksalt_method_crypt.py"
    import crypt


    crypt.mksalt(crypt.METHOD_SHA512)
    ```

# Alternatives to Crypt

There are a number of alternatives to weak hashing functions. These
alternatives include `bcrypt`, `pbkdf2`, and `scrypt`.

 - `bcrypt` is a secure password hashing function that is based on the
   Blowfish block cipher. Bcrypt is considered to be one of the most secure
   password hashing functions available.

 - `PBKDF2` is a secure password hashing function that is based on the HMAC
   cryptographic function. PBKDF2 is considered to be one of the most secure
   password hashing functions available.

 - `scrypt` is a secure password hashing function that is based on the bcrypt
   algorithm. Scrypt is designed to be more secure than bcrypt, and it is also
   more resistant to GPU-based attacks.

# Default Configuration

```toml
enabled = true
level = "warning"
```

## See also

!!! info
    - [crypt — Function to check Unix passwords](https://docs.python.org/3/library/crypt.html)
    - [CWE-328: Use of Weak Hash](https://cwe.mitre.org/data/definitions/328.html)
    - [NIST Policy on Hash Functions](https://csrc.nist.gov/projects/hash-functions)

_New in version 0.1.0_

"""  # noqa: E501
from typing import Optional

from precli.core.call import Call
from precli.core.location import Location
from precli.core.result import Result
from precli.i18n import _
from precli.rules import Rule


WEAK_CRYPT_HASHES = (
    "crypt.METHOD_CRYPT",
    "crypt.METHOD_MD5",
)


class CryptWeakHash(Rule):
    def __init__(self, id: str):
        super().__init__(
            id=id,
            name="reversible_one_way_hash",
            description=__doc__,
            cwe_id=328,
            message=_(
                "Use of weak hash function '{0}' does not meet security "
                "expectations."
            ),
        )

    def analyze_call(self, context: dict, call: Call) -> Optional[Result]:
        if call.name_qualified in ["crypt.crypt"]:
            name = call.get_argument(position=1, name="salt").value

            if isinstance(name, str) and name in WEAK_CRYPT_HASHES:
                return Result(
                    rule_id=self.id,
                    location=Location(node=call.function_node),
                    message=self.message.format(name),
                )
        elif call.name_qualified in ["crypt.mksalt"]:
            name = call.get_argument(position=0, name="method").value

            if isinstance(name, str) and name in WEAK_CRYPT_HASHES:
                return Result(
                    rule_id=self.id,
                    location=Location(node=call.function_node),
                    message=self.message.format(name),
                )
