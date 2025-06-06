# Copyright 2024 Secure Sauce LLC
# SPDX-License-Identifier: BUSL-1.1
r"""
# Reversible One Way Hash in `hmac` Module

The Python module `hmac` provides a number of functions for creating and
verifying message authentication codes (MACs). However, some of the hash
algorithms supported by hmac are insecure and should not be used. These
insecure hash algorithms include `MD4`, `MD5`, `RIPEMD-160` and `SHA-1`.

The MD4 hash algorithm is a cryptographic hash function that was designed
in the late 1980s. MD4 is no longer considered secure, and MACs created with
MD4 can be easily cracked by attackers.

The MD5 hash algorithm is a cryptographic hash function that was designed in
the early 1990s. MD5 is no longer considered secure, and MACs created with MD5
can be easily cracked by attackers.

RIPEMD-160 is a cryptographic hash function that was designed in 1996. It is
considered to be a secure hash function, but it is not as secure as SHA-256,
SHA-384, or SHA-512. In 2017, a collision attack was found for RIPEMD-160.
This means that it is possible to find two different messages that have the
same RIPEMD-160 hash. While this does not mean that RIPEMD-160 is completely
insecure, it does mean that it is not as secure as it once was.

The SHA-1 hash algorithm is also a cryptographic hash function that was
designed in the early 1990s. SHA-1 is no longer considered secure, and MACs
created with SHA-1 can be easily cracked by attackers.

# Example

```python linenums="1" hl_lines="6" title="hmac_new_digestmod_md5.py"
import hmac


key = b"my-secret-key"
message = b"Hello, world!"
hmac.new(key, msg=message, digestmod="md5")
```

??? example "Example Output"
    ```
    > precli tests/unit/rules/python/stdlib/hmac/examples/hmac_new_digestmod_md5.py
    ⛔️ Error on line 6 in tests/unit/rules/python/stdlib/hmac/examples/hmac_new_digestmod_md5.py
    PY006: Use of Weak Hash
    The hash function 'md5' is vulnerable to collision and pre-image attacks.
    ```

# Remediation

The recommendation is to swap the insecure hashing method to one of the more
secure alternatives, `SHA256`, `SHA-384`, or `SHA512`.

```python linenums="1" hl_lines="6" title="hmac_new_digestmod_md5.py"
import hmac


key = b"my-secret-key"
message = b"Hello, world!"
hmac.new(key, msg=message, digestmod="sha256")
```

# Default Configuration

```toml
enabled = true
level = "error"
weak_hashes = [
  "md4",
  "md5",
  "md5-sha1",
  "ripemd160",
  "sha",
  "sha1",
]
```

# See also

!!! info
    - [hmac — Keyed-Hashing for Message Authentication](https://docs.python.org/3/library/hmac.html)
    - [CWE-328: Use of Weak Hash](https://cwe.mitre.org/data/definitions/328.html)
    - [NIST Policy on Hash Functions](https://csrc.nist.gov/projects/hash-functions)

_New in version 0.1.0_

_Changed in version 0.4.1: Added md5-sha1_

"""  # noqa: E501
from typing import Optional

from precli.core.call import Call
from precli.core.location import Location
from precli.core.result import Result
from precli.i18n import _
from precli.rules import Rule


class HmacWeakHash(Rule):
    def __init__(self, id: str):
        super().__init__(
            id=id,
            name="reversible_one_way_hash",
            description=__doc__,
            cwe_id=328,
            message=_(
                "The hash function '{0}' is vulnerable to collision and "
                "pre-image attacks."
            ),
        )

    def analyze_call(self, context: dict, call: Call) -> Optional[Result]:
        if call.name_qualified in ["hmac.new"]:
            # hmac.new(key, msg=None, digestmod='')
            argument = call.get_argument(position=2, name="digestmod")

            if (
                argument.is_str
                and argument.value_str.lower()
                in self.config.parameters.get("weak_hashes")
            ):
                fixes = Rule.get_fixes(
                    context=context,
                    deleted_location=Location(node=argument.node),
                    description=_(
                        "For cryptographic purposes, use a hash length"
                        " of at least 256-bits with hashes such as SHA-256."
                    ),
                    inserted_content='"sha256"',
                )
                return Result(
                    rule_id=self.id,
                    location=Location(node=argument.node),
                    message=self.message.format(argument.value_str),
                    fixes=fixes,
                )
            if argument.value in [
                f"hashlib.{hash_name}"
                for hash_name in self.config.parameters.get("weak_hashes")
            ]:
                fixes = Rule.get_fixes(
                    context=context,
                    deleted_location=Location(node=argument.node),
                    description=_(
                        "For cryptographic purposes, use a hash length"
                        " of at least 256-bits with hashes such as SHA-256."
                    ),
                    inserted_content="hashlib.sha256",
                )
                return Result(
                    rule_id=self.id,
                    location=Location(node=argument.node),
                    message=self.message.format(argument.value),
                    fixes=fixes,
                )
        elif call.name_qualified in ["hmac.digest"]:
            # hmac.digest(key, msg, digest)
            argument = call.get_argument(position=2, name="digest")

            if (
                argument.is_str
                and argument.value_str.lower()
                in self.config.parameters.get("weak_hashes")
            ):
                fixes = Rule.get_fixes(
                    context=context,
                    deleted_location=Location(node=argument.node),
                    description=_(
                        "For cryptographic purposes, use a hash length"
                        " of at least 256-bits with hashes such as SHA-256."
                    ),
                    inserted_content='"sha256"',
                )
                return Result(
                    rule_id=self.id,
                    location=Location(node=argument.node),
                    message=self.message.format(argument.value_str),
                    fixes=fixes,
                )
            if argument.value in [
                f"hashlib.{hash_name}"
                for hash_name in self.config.parameters.get("weak_hashes")
            ]:
                fixes = Rule.get_fixes(
                    context=context,
                    deleted_location=Location(node=argument.node),
                    description=_(
                        "For cryptographic purposes, use a hash length"
                        " of at least 256-bits with hashes such as SHA-256."
                    ),
                    inserted_content="hashlib.sha256",
                )
                return Result(
                    rule_id=self.id,
                    location=Location(node=argument.node),
                    message=self.message.format(argument.value),
                    fixes=fixes,
                )
