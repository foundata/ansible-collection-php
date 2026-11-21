# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Exercise the input types that YAML and inventories can supply."""

import pytest

from ansible_collections.foundata.php.plugins.filter._invalid_fpm_pool_flags import (
    invalid_fpm_pool_flags,
)


@pytest.mark.parametrize("group", ["php_flag", "php_admin_flag"])
@pytest.mark.parametrize("value", ["false", "off", "true", 0, 1, None, {}, []])
def test_only_booleans_are_flags(group, value):
    pool = {group: {"display_errors": value}}
    assert invalid_fpm_pool_flags(pool, {"app": pool}) == [
        f"run_php_fpm_pool_defaults.{group}.display_errors",
        f"run_php_fpm_pools.app.{group}.display_errors",
    ]


def test_booleans_other_directives_and_absent_pools():
    defaults = {"php_admin_flag": {"display_errors": False}, "env": {"DEBUG": "off"}}
    pools = {
        "app": {"php_flag": {"log_errors": True}, "php_value": {"precision": 3}},
        "old": {"state": "absent", "php_admin_flag": {"display_errors": "off"}},
    }
    assert invalid_fpm_pool_flags(defaults, pools) == []


def test_malformed_flag_group_names_the_group():
    assert invalid_fpm_pool_flags({}, {"app": {"php_flag": "off"}}) == [
        "run_php_fpm_pools.app.php_flag"
    ]
