# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Internal validation of the run role's explicit PHP INI expressions.

Keep evaluation in PHP: its INI operator precedence and constant values differ
from Python and can change between PHP versions. This validates a small grammar
and an allowlist of core error-level constants, without interpreting the value.
"""

import re
from collections.abc import Mapping

from ansible.errors import AnsibleFilterError

ERROR_CONSTANTS = frozenset(
    (
        "E_ALL",
        "E_ERROR",
        "E_WARNING",
        "E_PARSE",
        "E_NOTICE",
        "E_CORE_ERROR",
        "E_CORE_WARNING",
        "E_COMPILE_ERROR",
        "E_COMPILE_WARNING",
        "E_USER_ERROR",
        "E_USER_WARNING",
        "E_USER_NOTICE",
        "E_STRICT",
        "E_RECOVERABLE_ERROR",
        "E_DEPRECATED",
        "E_USER_DEPRECATED",
    )
)
TOKEN = re.compile(r"[ \t]+|[A-Z_][A-Z_0-9]*|-?[0-9]+|[()|&^~!]")


def ini_expression(value):
    """Return a validated expression from an exact single-key mapping."""
    if not isinstance(value, Mapping) or set(value) != {"expression"}:
        raise AnsibleFilterError(
            "PHP INI expression requires a mapping with only the 'expression' key"
        )
    expression = value["expression"]
    if not isinstance(expression, str) or not expression.strip(" \t"):
        raise AnsibleFilterError("PHP INI expression must be a nonempty string")
    position = 0
    depth = 0
    operand = True
    for match in TOKEN.finditer(expression):
        if match.start() != position:
            raise AnsibleFilterError(
                "PHP INI expression contains unsupported characters"
            )
        position = match.end()
        token = match.group()
        if token.isspace():
            continue
        if operand and token in ("~", "!"):
            continue
        if operand and token == "(":
            depth += 1
        elif operand and (token in ERROR_CONSTANTS or re.fullmatch(r"-?[0-9]+", token)):
            operand = False
        elif not operand and token in ("|", "&", "^"):
            operand = True
        elif not operand and token == ")" and depth > 0:
            depth -= 1
        else:
            raise AnsibleFilterError(
                "Invalid PHP INI expression: use supported E_* constants, decimal "
                "integers, | & ^ ~ ! and balanced parentheses; use a numeric "
                "setting for unsupported constants or syntax"
            )
    if position != len(expression) or operand or depth:
        raise AnsibleFilterError("PHP INI expression is incomplete or unbalanced")
    return expression.strip(" \t")


class FilterModule:
    """Private role filter; the supported interface is the role's INI settings."""

    def filters(self):
        """Expose the internal expression validator to the role templates."""
        return {"_ini_expression": ini_expression}
