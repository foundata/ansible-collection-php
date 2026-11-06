# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Use Ansible's collection loader when templating in unit tests."""

from ansible.plugins.loader import init_plugin_loader

init_plugin_loader()
