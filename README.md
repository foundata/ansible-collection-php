# Ansible collection: `foundata.php`

This repository contains the `foundata.php` Ansible Collection.



## Table of contents<a id="toc"></a>

- [Included content](#content)
- [Dependencies](#dependencies)
- [Licensing, copyright](#licensing-copyright)
- [Author information](#author-information)



## Included content<a id="content"></a>

### Role: `foundata.php.run`

The primary role in this collection: installs and maintains a PHP runtime, manages the CLI and PHP-FPM (FastCGI Process Manager) SAPIs, and configures INI directives, extensions and FPM pools from a single declarative set of variables. [Its `README.md`](./roles/run/README.md) covers configuration, usage examples, and more:

<!-- ANSIBLE DOCSMITH TOC-FULL run START -->
- [Ansible role: `foundata.php.run`](roles/run/README.md#ansible-role-foundataphprun)
  - [Table of contents](roles/run/README.md#toc)
  - [Features](roles/run/README.md#features)
  - [Example playbooks, using this role](roles/run/README.md#examples)
  - [Supported tags](roles/run/README.md#tags)
  - [Role variables](roles/run/README.md#variables)
    - [`run_php_state`](roles/run/README.md#variable-run_php_state)
    - [`run_php_autoupgrade`](roles/run/README.md#variable-run_php_autoupgrade)
    - [`run_php_fpm_service_state`](roles/run/README.md#variable-run_php_fpm_service_state)
    - [`run_php_version`](roles/run/README.md#variable-run_php_version)
    - [`run_php_sapis`](roles/run/README.md#variable-run_php_sapis)
    - [`run_php_extensions_enabled`](roles/run/README.md#variable-run_php_extensions_enabled)
    - [`run_php_extensions_disable_unmanaged`](roles/run/README.md#variable-run_php_extensions_disable_unmanaged)
    - [`run_php_settings`](roles/run/README.md#variable-run_php_settings)
      - [`run_php_settings['shared']`](roles/run/README.md#variable-run_php_settings-sub-shared)
      - [`run_php_settings['fpm']`](roles/run/README.md#variable-run_php_settings-sub-fpm)
      - [`run_php_settings['cli']`](roles/run/README.md#variable-run_php_settings-sub-cli)
    - [`run_php_extension_settings`](roles/run/README.md#variable-run_php_extension_settings)
      - [`run_php_extension_settings['shared']`](roles/run/README.md#variable-run_php_extension_settings-sub-shared)
      - [`run_php_extension_settings['fpm']`](roles/run/README.md#variable-run_php_extension_settings-sub-fpm)
      - [`run_php_extension_settings['cli']`](roles/run/README.md#variable-run_php_extension_settings-sub-cli)
    - [`run_php_fpm_pool_defaults`](roles/run/README.md#variable-run_php_fpm_pool_defaults)
      - [`run_php_fpm_pool_defaults['php_admin_value']`](roles/run/README.md#variable-run_php_fpm_pool_defaults-sub-php_admin_value)
      - [`run_php_fpm_pool_defaults['php_admin_flag']`](roles/run/README.md#variable-run_php_fpm_pool_defaults-sub-php_admin_flag)
      - [`run_php_fpm_pool_defaults['php_value']`](roles/run/README.md#variable-run_php_fpm_pool_defaults-sub-php_value)
      - [`run_php_fpm_pool_defaults['php_flag']`](roles/run/README.md#variable-run_php_fpm_pool_defaults-sub-php_flag)
      - [`run_php_fpm_pool_defaults['env']`](roles/run/README.md#variable-run_php_fpm_pool_defaults-sub-env)
    - [`run_php_fpm_pools`](roles/run/README.md#variable-run_php_fpm_pools)
    - [`run_php_fpm_pools_delete_unmanaged`](roles/run/README.md#variable-run_php_fpm_pools_delete_unmanaged)
    - [`run_php_fpm_service_settings`](roles/run/README.md#variable-run_php_fpm_service_settings)
      - [`run_php_fpm_service_settings['global']`](roles/run/README.md#variable-run_php_fpm_service_settings-sub-global)
  - [Dependencies](roles/run/README.md#dependencies)
  - [Compatibility](roles/run/README.md#compatibility)
  - [External requirements](roles/run/README.md#requirements)
<!-- ANSIBLE DOCSMITH TOC-FULL run END -->



## Dependencies<a id="dependencies"></a>

See `dependencies` in [`galaxy.yml`](./galaxy.yml).



## Licensing, copyright<a id="licensing-copyright"></a>

<!--REUSE-IgnoreStart-->
Copyright (c) 2026 foundata GmbH

This project is licensed under the GNU General Public License v3.0 or later (SPDX-License-Identifier: `GPL-3.0-or-later`), see [`LICENSES/GPL-3.0-or-later.txt`](LICENSES/GPL-3.0-or-later.txt) for the full text.

The [`REUSE.toml`](REUSE.toml) file provides detailed licensing and copyright information in a human- and machine-readable format. This includes parts that may be subject to different licensing or usage terms, such as third-party components. The repository conforms to the [REUSE specification](https://reuse.software/spec/). You can use [`reuse spdx`](https://reuse.readthedocs.io/en/latest/readme.html#cli) to create a [SPDX software bill of materials (SBOM)](https://en.wikipedia.org/wiki/Software_Package_Data_Exchange).
<!--REUSE-IgnoreEnd-->



## Author information<a id="author-information"></a>

This project was created and is maintained by foundata GmbH.

Initially based on an [Ansible skeleton](https://foundata.com/en/projects/ansible-skeletons/) developed by [foundata](https://foundata.com/).
