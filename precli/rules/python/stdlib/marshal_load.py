# Copyright 2025 Secure Sauce LLC
# SPDX-License-Identifier: BUSL-1.1
r"""
# Deserialization of Untrusted Data in the `marshal` Module

The Python `marshal` module provides a way to serialize and deserialize
Python objects. However, it is important to be aware that malicious data
can be used to attack applications that use the marshal module. For example,
a malicious data could be used to cause the decoder to execute arbitrary code.

# Example

```python linenums="1" hl_lines="10" title="marshal_load.py"
import marshal


data = {'name': 'John Doe', 'age': 30}

with open('data.dat', 'wb') as f:
    marshal.dump(data, f)

with open('data.dat', 'rb') as f:
    loaded_data = marshal.load(f)
```

??? example "Example Output"
    ```
    > precli tests/unit/rules/python/stdlib/marshal/examples/marshal_load.py
    ⚠️  Warning on line 10 in tests/unit/rules/python/stdlib/marshal/examples/marshal_load.py
    PY011: Deserialization of Untrusted Data
    Potential unsafe usage of 'marshal.load' that can allow instantiation of arbitrary objects.
    ```

# Remediation

To avoid this vulnerability, it is important to only deserialize data from
trusted sources. If you are deserializing data from an untrusted source,
you should first sanitize the data to remove any potential malicious code.

# Default Configuration

```toml
enabled = true
level = "warning"
```

# See also

!!! info
    - [marshal — Internal Python object serialization](https://docs.python.org/3/library/marshal.html)
    - [CWE-502: Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)

_New in version 0.1.0_

"""  # noqa: E501
from typing import Optional

from precli.core.call import Call
from precli.core.location import Location
from precli.core.result import Result
from precli.i18n import _
from precli.rules import Rule


class MarshalLoad(Rule):
    def __init__(self, id: str):
        super().__init__(
            id=id,
            name="deserialization_of_untrusted_data",
            description=__doc__,
            cwe_id=502,
            message=_(
                "Potential unsafe usage of '{0}' that can allow instantiation"
                " of arbitrary objects."
            ),
        )

    def analyze_call(self, context: dict, call: Call) -> Optional[Result]:
        if call.name_qualified in ["marshal.load", "marshal.loads"]:
            # marshal.load(file, /)
            # marshal.loads(bytes, /)
            return Result(
                rule_id=self.id,
                location=Location(node=call.function_node),
                message=self.message.format(call.name_qualified),
            )
