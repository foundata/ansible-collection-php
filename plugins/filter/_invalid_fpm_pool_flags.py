# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Validate the two boolean-only PHP-FPM pool directives during role init."""

from collections.abc import Mapping

from ansible.errors import AnsibleFilterError


def _invalid_flags(path, pool):
    for group in ("php_admin_flag", "php_flag"):
        flags = pool.get(group, {})
        if not isinstance(flags, Mapping):
            yield f"{path}.{group}"
            continue
        for name, value in flags.items():
            if not isinstance(value, bool):
                yield f"{path}.{group}.{name}"


def invalid_fpm_pool_flags(defaults, pools):
    """Name invalid inputs without including pool values in the diagnostic."""
    invalid = list(_invalid_flags("run_php_fpm_pool_defaults", defaults))
    for name, pool in pools.items():
        path = f"run_php_fpm_pools.{name}"
        if not isinstance(pool, Mapping):
            raise AnsibleFilterError(f"{path} must be a pool dictionary")
        if pool.get("state", "present") == "present":
            invalid.extend(_invalid_flags(path, pool))
    return invalid


class FilterModule:
    """Private filters for the run role."""

    def filters(self):
        """Expose the validation filter to role initialization."""
        return {"_invalid_fpm_pool_flags": invalid_fpm_pool_flags}
