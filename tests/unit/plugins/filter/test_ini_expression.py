# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Exercise the expression boundary through Ansible and the shipped templates."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from ansible.errors import AnsibleError, AnsibleFilterError, AnsibleUndefinedVariable
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar, trust_as_template

from ansible_collections.foundata.php.plugins.filter import _ini_expression


def render(value, macro="render_ini_value"):
    """Render with the real Ansible plugin loader, including FQCN filters/tests."""
    templates = (
        Path(_ini_expression.__file__).resolve().parents[2] / "roles/run/templates"
    )
    templar = Templar(loader=DataLoader(), variables={"value": value})
    templar = templar.copy_with_new_env(searchpath=[str(templates)])
    # A file contains surrounding text, so native scalar conversion cannot occur.
    source = (
        "{% from '_php_macros.j2' import " + macro + " %}INI:{{ " + macro + "(value) }}"
    )
    return templar.template(trust_as_template(source)).removeprefix("INI:")


@pytest.mark.parametrize(
    "expression",
    [
        *_ini_expression.ERROR_CONSTANTS,
        "E_ALL & ~E_DEPRECATED",
        "E_ALL & ~(E_DEPRECATED | E_USER_DEPRECATED)",
        "(E_ERROR | E_WARNING) ^ E_WARNING",
        "-1",
        "0",
        "!0",
        "~~E_ERROR",
        "\t E_ALL & -1 \t",
    ],
)
def test_valid_expression(expression):
    value = {"expression": expression}
    assert _ini_expression.ini_expression(value) == expression.strip(" \t")
    assert render(value) == expression.strip(" \t")
    assert value == {"expression": expression}


@pytest.mark.parametrize(
    "value",
    [
        {},
        {"expr": "E_ALL"},
        {"expression": "E_ALL", "extra": True},
        {"expression": None},
        {"expression": False},
        {"expression": 123},
        {"expression": []},
        *[
            {"expression": expression}
            for expression in (
                "",
                " \t",
                "E_TYPO",
                "PHP_VERSION",
                "e_all",
                "E_ÄLL",
                "E_ALL\n",
                "E_ALL\r",
                "E_ALL\x00",
                "E_ALL; comment",
                '"E_ALL"',
                "${MASK}",
                "E_ALL + 1",
                "1 << 2",
                "0xFF",
                "1.5",
                "E_ALL && E_ERROR",
                "E_ALL || E_ERROR",
                "E_ALL E_ERROR",
                "E_ALL(1)",
                "()",
                "(E_ALL",
                "E_ALL)",
                "E_ALL |",
                "| E_ALL",
                "~",
                "E_ALL ~ E_ERROR",
                "1 2",
                "--1",
                "E_ALL\nerror_reporting = 0",
            )
        ],
    ],
)
def test_invalid_expression(value):
    with pytest.raises(AnsibleFilterError, match="PHP INI expression"):
        _ini_expression.ini_expression(value)
    with pytest.raises(AnsibleError, match="PHP INI expression"):
        render(value)


@pytest.mark.parametrize("value", [None, [], "E_ALL", 1, False])
def test_expression_filter_requires_mapping(value):
    with pytest.raises(AnsibleFilterError, match="mapping"):
        _ini_expression.ini_expression(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, "On"),
        (False, "Off"),
        (-1, "-1"),
        (2.5, "2.5"),
        ("E_ALL", '"E_ALL"'),
        ("E_ALL & ~E_NOTICE", '"E_ALL & ~E_NOTICE"'),
        ("256M", '"256M"'),
        ("Off", '"Off"'),
        ("", '""'),
        ("Grüße", '"Grüße"'),
        ('a "quote"; C:\\php\\', '"a \\"quote\\"; C:\\\\php\\\\"'),
    ],
)
def test_scalar_quoting(value, expected):
    assert render(value) == expected


def test_section_and_extension_use_expression_renderer():
    directives = {"error_reporting": {"expression": "E_ALL"}, "user_agent": "E_ALL"}
    assert render(directives, "render_ini_directives") == (
        'error_reporting = E_ALL\nuser_agent = "E_ALL"'
    )
    assert render({"PHP": directives}, "render_ini_scope") == (
        '[PHP]\nerror_reporting = E_ALL\nuser_agent = "E_ALL"'
    )


def test_undefined_expression_propagates():
    templar = Templar(loader=DataLoader())
    with pytest.raises(AnsibleUndefinedVariable):
        templar.template(
            trust_as_template(
                "{{ {'expression': missing_value} | foundata.php._ini_expression }}"
            )
        )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        *[
            ({"expression": name}, f"get_defined_constants()['{name}']")
            for name in sorted(_ini_expression.ERROR_CONSTANTS)
        ],
        ({"expression": "E_WARNING | E_ERROR"}, "3"),
        ({"expression": "7 & 3"}, "3"),
        ({"expression": "7 ^ 3"}, "4"),
        ({"expression": "~0"}, "-1"),
        ({"expression": "!0"}, "1"),
        ({"expression": "!1"}, "0"),
        # INI binary operators associate left to right, including mixed operators.
        ({"expression": "1 | 2 & 2"}, "2"),
        ({"expression": "1 | (2 & 2)"}, "3"),
        (
            {"expression": "E_ALL & ~(E_NOTICE | E_DEPRECATED)"},
            "E_ALL & ~(E_NOTICE | E_DEPRECATED)",
        ),
        (-1, "-1"),
    ],
)
def test_effective_error_reporting(tmp_path, value, expected):
    """Start PHP with a rendered INI file and inspect the effective setting."""
    ini = tmp_path / "php.ini"
    ini.write_text(render({"PHP": {"error_reporting": value}}, "render_ini_scope"))
    image = os.environ.get("PHP_INI_TEST_IMAGE")
    if image:
        command = [
            "podman",
            "run",
            "--rm",
            "--network=none",
            "--pull=never",
            "--env",
            "PHP_INI_SCAN_DIR=",
            "--volume",
            f"{ini}:/test.ini:ro,Z",
            image,
            "php",
            "-c",
            "/test.ini",
        ]
    elif php := shutil.which("php"):
        command = [php, "-c", str(ini)]
    else:
        pytest.skip("Requires PHP CLI or PHP_INI_TEST_IMAGE")

    probe = (
        f"echo json_encode([php_ini_loaded_file(), error_reporting(), ({expected})]);"
    )
    result = subprocess.run(
        [*command, "-r", probe],
        env={**os.environ, "PHP_INI_SCAN_DIR": ""},
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    assert result.stderr == ""
    loaded, actual, reference = json.loads(result.stdout)
    assert loaded == command[-1]
    assert isinstance(reference, int)
    assert actual == reference
