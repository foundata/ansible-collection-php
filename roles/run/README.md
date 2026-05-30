# Ansible role: `foundata.php.run`

The `foundata.php.run` Ansible role (part of the `foundata.php` Ansible collection).



## Table of contents<a id="toc"></a>

- [Features](#features)
- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)<!-- ANSIBLE DOCSMITH TOC START -->
- [Role variables](#variables)
  - [`run_php_state`](#variable-run_php_state)
  - [`run_php_autoupgrade`](#variable-run_php_autoupgrade)
  - [`run_php_fpm_service_state`](#variable-run_php_fpm_service_state)
  - [`run_php_version`](#variable-run_php_version)
  - [`run_php_sapis`](#variable-run_php_sapis)
  - [`run_php_extensions_enabled`](#variable-run_php_extensions_enabled)
  - [`run_php_extensions_disable_unmanaged`](#variable-run_php_extensions_disable_unmanaged)
  - [`run_php_settings`](#variable-run_php_settings)
    - [`run_php_settings['shared']`](#variable-run_php_settings-sub-shared)
    - [`run_php_settings['fpm']`](#variable-run_php_settings-sub-fpm)
    - [`run_php_settings['cli']`](#variable-run_php_settings-sub-cli)
  - [`run_php_extension_settings`](#variable-run_php_extension_settings)
    - [`run_php_extension_settings['shared']`](#variable-run_php_extension_settings-sub-shared)
    - [`run_php_extension_settings['fpm']`](#variable-run_php_extension_settings-sub-fpm)
    - [`run_php_extension_settings['cli']`](#variable-run_php_extension_settings-sub-cli)
  - [`run_php_fpm_pool_defaults`](#variable-run_php_fpm_pool_defaults)
    - [`run_php_fpm_pool_defaults['php_admin_value']`](#variable-run_php_fpm_pool_defaults-sub-php_admin_value)
    - [`run_php_fpm_pool_defaults['php_admin_flag']`](#variable-run_php_fpm_pool_defaults-sub-php_admin_flag)
    - [`run_php_fpm_pool_defaults['php_value']`](#variable-run_php_fpm_pool_defaults-sub-php_value)
    - [`run_php_fpm_pool_defaults['php_flag']`](#variable-run_php_fpm_pool_defaults-sub-php_flag)
    - [`run_php_fpm_pool_defaults['env']`](#variable-run_php_fpm_pool_defaults-sub-env)
  - [`run_php_fpm_pools`](#variable-run_php_fpm_pools)
  - [`run_php_fpm_pools_delete_unmanaged`](#variable-run_php_fpm_pools_delete_unmanaged)
  - [`run_php_fpm_service_settings`](#variable-run_php_fpm_service_settings)
    - [`run_php_fpm_service_settings['global']`](#variable-run_php_fpm_service_settings-sub-global)
<!-- ANSIBLE DOCSMITH TOC END -->
- [Dependencies](#dependencies)
- [Compatibility](#compatibility)
- [External requirements](#requirements)



## Features<a id="features"></a>

Main features:

* **Multi-SAPI support**: enable FPM, CLI, or both via the single `run_php_sapis` variable. mod_php is intentionally not supported (not thread-safe; unavailable on Red Hat 9+); classic CGI is intentionally not supported either (legacy, superseded by FPM).
* **Platform-aware PHP version handling**: `run_php_version` accepts either a concrete stream (e.g. `"8.3"`) or `"default"`, which the role resolves to the distribution-default PHP version stream it knows for the current platform. The resolved version drives package names, INI directories and service names automatically.
* **Extension management** via `run_php_extensions_enabled`: extensions are enabled by short name, the role installs the matching distribution sub-package and renders a per-extension INI drop-in. Unknown extension names fail the run early with the list of names known for the current platform.
* **Per-SAPI INI scopes**: `run_php_settings['shared' | 'fpm' | 'cli']` and `run_php_extension_settings[...]` map directly to the per-SAPI INI directories on Debian-family platforms; on platforms with a shared INI directory (Red Hat, SUSE) the role rejects per-SAPI scopes at init time so misconfiguration surfaces before any side effects.
* **FPM pool management** via `run_php_fpm_pool_defaults` + `run_php_fpm_pools`:
  * Pool defaults are deep-merged with each pool's overrides, so common settings live in one place.
  * Per-pool runtime INI shadowing via `php_admin_value` / `php_admin_flag` / `php_value` / `php_flag`, and environment variables via `env`.
  * Pools can be marked `state: absent` to remove just one pool file, or `run_php_fpm_pools_delete_unmanaged: true` to enforce strict declarative ownership of the pool directory.
* **FPM `[global]` directives** managed via `run_php_fpm_service_settings['global']` and appended at the end of `php-fpm.conf`. Platform-shipped `[global]` defaults are preserved unless explicitly overridden (PHP-FPM INI last-wins).
* Designed for cross-platform compatibility, working seamlessly across Debian-family, Red Hat-family, and openSUSE.



## Example playbooks, using this role<a id="examples"></a>

Installation with automatic upgrade:

```yaml
---

- name: "Initialize the foundata.php.run role"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.php.run role"
      ansible.builtin.include_role:
        name: "foundata.php.run"
      vars:
        run_php_autoupgrade: true
```

Installation pinned to a specific PHP version, with extensions, INI overrides and a dedicated FPM pool:

```yaml
---

- name: "Initialize the foundata.php.run role"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.php.run role"
      ansible.builtin.include_role:
        name: "foundata.php.run"
      vars:
        run_php_version: "8.3"
        run_php_sapis:
          - "fpm"
          - "cli"
        run_php_extensions_enabled:
          - "mbstring"
          - "intl"
          - "bcmath"
          - "opcache"
          - "pgsql"
        # INI drop-in directives shared by every SAPI. On Debian-family use the
        # 'fpm:' / 'cli:' sub-keys to scope settings to a single SAPI.
        run_php_settings:
          shared:
            date.timezone: "UTC"
            expose_php: false
            memory_limit: "256M"
            max_execution_time: 30
        # Per-extension INI drop-in directives (here: tuning opcache).
        run_php_extension_settings:
          shared:
            opcache:
              opcache.memory_consumption: 256
              opcache.max_accelerated_files: 20000
              opcache.enable_cli: false
        # Defaults inherited by every pool below.
        run_php_fpm_pool_defaults:
          php_admin_value:
            memory_limit: "256M"
            upload_max_filesize: "64M"
            post_max_size: "64M"
          php_admin_flag:
            display_errors: false
            log_errors: true
        run_php_fpm_pools:
          app:
            listen: "/run/php-fpm-app.sock"
            pm: "dynamic"
            pm.max_children: 16
            pm.start_servers: 4
            pm.min_spare_servers: 2
            pm.max_spare_servers: 6
            # Override the inherited default just for this pool.
            php_admin_value:
              memory_limit: "512M"
            env:
              APP_ENV: "production"
        # [global] directives appended to php-fpm.conf. Platform stock values
        # for directives you do not list here are preserved.
        run_php_fpm_service_settings:
          global:
            log_level: "notice"
            emergency_restart_threshold: 10
            emergency_restart_interval: "1m"
```

Uninstall:

```yaml
---

- name: "Initialize the foundata.php.run role"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.php.run role"
      ansible.builtin.include_role:
        name: "foundata.php.run"
      vars:
        run_php_state: "absent"
```



## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `run_php_setup`: Manage basic resources, such as packages or service users.
- `run_php_config`: Manage settings, such as adapting or creating configuration files.
- `run_php_service`: Manage services and daemons, such as running states and service boot configurations.

There are also tags usually not meant to be called directly but listed for the sake of completeness** and edge cases:

- `run_php_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.


<!-- ANSIBLE DOCSMITH MAIN START -->

## Role variables<a id="variables"></a>

The following variables can be configured for this role:

| Variable | Type | Required | Default | Description (abstract) |
|----------|------|----------|---------|------------------------|
| `run_php_state` | `str` | No | `"present"` | Determines whether the managed resources should be `present` or `absent`.<br><br>`present` ensures that required components, such as software packages, are installed and configured.<br><br>`absent` reverts changes as much as possible, such as […](#variable-run_php_state) |
| `run_php_autoupgrade` | `bool` | No | `false` | If set to `true`, all managed packages will be upgraded during each Ansible run (e.g., when the package provider detects a newer version than the currently installed one). |
| `run_php_fpm_service_state` | `str` | No | `"enabled"` | Defines the status of the PHP-FPM (FastCGI Process Manager) service. FPM is the PHP SAPI (Server API, see `run_php_sapis` for the full primer) intended to be reached from a web server such as Apache or NGINX over a FastCGI socket; it is the only PHP […](#variable-run_php_fpm_service_state) |
| `run_php_version` | `str` | No | `"default"` | Selects which PHP version stream this role manages on the target host.<br><br>The value `"default"` keeps the role aligned with the PHP version stream shipped by the distribution in its standard repositories. The exact version that results depends on […](#variable-run_php_version) |
| `run_php_sapis` | `list` | No | `['fpm', 'cli']` | List of PHP SAPIs the role should install and manage on the host. This role manages the whole PHP runtime, not one specific SAPI and this variable defines which SAPI(s) to address.<br><br>A PHP SAPI (Server API) is the interface layer through which […](#variable-run_php_sapis) |
| `run_php_extensions_enabled` | `list` | No | `[]` | List of PHP extension short names to enable (and install if needed).<br><br>A "short name" is the name PHP itself uses in the `extension=...` INI directive (`extension=pgsql`, `extension=mbstring`, ...) and the same name distributions use as a suffix […](#variable-run_php_extensions_enabled) |
| `run_php_extensions_disable_unmanaged` | `bool` | No | `false` | Controls whether the role disables extensions that are not declared in `run_php_extensions_enabled`.<br><br>This is intentionally best-effort. PHP has no portable, cross-platform extension activation registry. Built-in extensions and extensions […](#variable-run_php_extensions_disable_unmanaged) |
| `run_php_settings` | `dict` | No | `{}` | PHP INI configuration as a scope-keyed nested dictionary. The role renders one or more drop-in `.ini` files into the appropriate SAPI INI directory on Debian-like systems, or into the single shared INI scan directory on shared-dir platforms […](#variable-run_php_settings) |
| `run_php_extension_settings` | `dict` | No | `{}` | INI directives applied per extension, scoped the same way as `run_php_settings`. Top-level keys are configuration scopes (`shared`, `fpm`, `cli`); second-level keys are extension short names; third-level keys are flat INI directives for that […](#variable-run_php_extension_settings) |
| `run_php_fpm_pool_defaults` | `dict` | No | `{}` | Defaults merged underneath every pool in `run_php_fpm_pools` at render time. Per-pool entries override defaults on any matching key (deep merge: pool's `php_admin_value.memory_limit` overrides the default's […](#variable-run_php_fpm_pool_defaults) |
| `run_php_fpm_pools` | `dict` | No | `{}` | PHP-FPM pools to manage. The dictionary is keyed by pool name, which is also the filename used in `pool.d/.conf`. Honored only when `"fpm"` is in `run_php_sapis`.<br><br>Each pool entry is a dictionary whose keys are PHP-FPM directive names verbatim […](#variable-run_php_fpm_pools) |
| `run_php_fpm_pools_delete_unmanaged` | `bool` | No | `false` | Controls whether the role removes pool files from `pool.d/` that are not declared in `run_php_fpm_pools`.<br><br>When `true`, any `*.conf` file in `pool.d/` whose stem does not match an entry in `run_php_fpm_pools` is deleted on every role run. This […](#variable-run_php_fpm_pools_delete_unmanaged) |
| `run_php_fpm_service_settings` | `dict` | No | `{}` | PHP-FPM service-level settings, written into the `[global]` section of the distribution's main `php-fpm.conf` via `ansible.builtin.blockinfile`. The role does not overwrite the distribution file, only the managed block inside it.<br><br>Top-level […](#variable-run_php_fpm_service_settings) |

### `run_php_state`<a id="variable-run_php_state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Determines whether the managed resources should be `present` or `absent`.

`present` ensures that required components, such as software packages, are
installed and configured.

`absent` reverts changes as much as possible, such as removing packages,
deleting created users, stopping services, restoring modified settings, …

- **Type**: `str`
- **Required**: No
- **Default**: `"present"`
- **Choices**: `present`, `absent`



### `run_php_autoupgrade`<a id="variable-run_php_autoupgrade"></a>

[*⇑ Back to ToC ⇑*](#toc)

If set to `true`, all managed packages will be upgraded during each Ansible
run (e.g., when the package provider detects a newer version than the
currently installed one).

- **Type**: `bool`
- **Required**: No
- **Default**: `false`



### `run_php_fpm_service_state`<a id="variable-run_php_fpm_service_state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Defines the status of the PHP-FPM (FastCGI Process Manager) service.
FPM is the PHP SAPI (Server API, see `run_php_sapis` for the full
primer) intended to be reached from a web server such as Apache or
NGINX over a FastCGI socket; it is the only PHP SAPI that runs as a
long-lived daemon and therefore the only one with a service state to
manage.

`enabled`: Service is running and will start automatically at boot.

`disabled`: Service is stopped and will not start automatically at boot.

`running`: Service is running but will not start automatically at boot.
This can be used to start a service on the first Ansible run without
enabling it for boot.

`unmanaged`: Service will not start at boot, and Ansible will not manage
its running state. This is primarily useful when services are monitored
and managed by systems other than Ansible.

The variable is honored only when `"fpm"` appears in `run_php_sapis`.
The CLI SAPI does not have a long-running daemon, so there is no service
lifecycle to manage for it. Setting this variable on a host where FPM is
not part of the SAPI selection results in a debug notice and the
variable is ignored.

- **Type**: `str`
- **Required**: No
- **Default**: `"enabled"`
- **Choices**: `enabled`, `disabled`, `running`, `unmanaged`



### `run_php_version`<a id="variable-run_php_version"></a>

[*⇑ Back to ToC ⇑*](#toc)

Selects which PHP version stream this role manages on the target host.

The value `"default"` keeps the role aligned with the PHP version stream
shipped by the distribution in its standard repositories. The exact version
that results depends on the OS release.

Pinning a concrete value such as `"8.3"` or `"8.2"` makes the role use the
matching package set and filesystem paths (resolved per platform in
`vars/<platform>.yml`). On distributions that ship only one PHP version stream
natively, a pinned non-default value requires the matching third-party
repository to already be configured (for example Sury on Debian, Remi on
RHEL). Setting up those repositories is intentionally out of scope for this
role yet.

Managing multiple parallel PHP version streams on the same host with a
single role invocation is not supported. If you need that, invoke the role
multiple times with different `run_php_version` values and take care that
each invocation manages a disjoint set of SAPIs, pools, and INI drop-ins (but
you can define shared variables for sure).

- **Type**: `str`
- **Required**: No
- **Default**: `"default"`



### `run_php_sapis`<a id="variable-run_php_sapis"></a>

[*⇑ Back to ToC ⇑*](#toc)

List of PHP SAPIs the role should install and manage on the host. This role
manages the whole PHP runtime, not one specific SAPI and this variable defines
which SAPI(s) to address.

A PHP SAPI (Server API) is the interface layer through which PHP receives
requests and returns responses. Different SAPIs are different runtime modes of
the same PHP installation; on most systems multiple SAPIs are installed side
by side and selected based on how PHP is invoked. The role currently supports
the following SAPI values:

- `"fpm"`: FastCGI Process Manager. A long-running daemon that web servers
  (Apache HTTPD, NGINX, ...) connect to over a FastCGI socket (Unix or TCP).
  The mainstream choice for serving web requests today. Only this SAPI has a
  service state to manage; see `run_php_fpm_service_state`.
- `"cli"`: Command-line interpreter. Used to run PHP scripts directly from a
  shell, in cron jobs, in deployment scripts, and by tools  like `composer`.
  Has no daemon and no listener.

The classic CGI SAPI (`php-cgi`) and `mod_php` (the in-process Apache SAPI)
are intentionally NOT supported values. Passing either of them hard-fails at
role start. `mod_php` is not thread-safe and requires the Apache prefork MPM
(which kills concurrency and performance). Red Hat deprecated it in RHEL 8
and mod_php is not available in RHEL 9. CGI is slower legacy SAPI that was
superseded by FPM long ago and is not uniformly packaged across distributions
(openSUSE Leap 16, for example, ships no `php8-cgi` package).

Any combination of the supported values is allowed (including a single entry).
An empty list is technically accepted but unusual: the role would only ensure
the common PHP runtime packages are present and would not manage any
SAPI-specific package or configuration.

If a value in the list is not installable on the target platform, the role
hard-fails before any install action with an actionable message.

Example:

```yaml
run_php_sapis:
  - "fpm"
  - "cli"
```

- **Type**: `list`
- **Required**: No
- **Default**: `['fpm', 'cli']`
- **Choices**: `fpm`, `cli`
- **List Elements**: `str`



### `run_php_extensions_enabled`<a id="variable-run_php_extensions_enabled"></a>

[*⇑ Back to ToC ⇑*](#toc)

List of PHP extension short names to enable (and install if needed).

A "short name" is the name PHP itself uses in the `extension=...` INI
directive (`extension=pgsql`, `extension=mbstring`, ...) and the same name
distributions use as a suffix in their package names (`php<ver>-pgsql` on
Debian, `php-pgsql` on RHEL/Fedora, `php8-pgsql` on openSUSE Leap).

Unknown names cause a hard failure with a message listing the extensions the
role knows about.

Where to look a short name up, in order of authoritativeness:

- `php -m` (CLI) or `php-fpm -m` (FPM) on any host that already has PHP
  installed. This is the most reliable source: it is the extension list as
  PHP itself sees it. Most names are lowercase, though a handful of
  historical built-ins are capitalized (`Core`, `PDO`, `Reflection`, `SPL`,
  `Phar`, please use lowercase then)
- The distribution's package search, with the platform-specific prefix
  stripped:
  - Debian / Ubuntu: `apt-cache search '^php<ver>-'`, strip `php<ver>-`.
  - RHEL / Fedora / AlmaLinux: `dnf list 'php-*'`, strip `php-`.
  - openSUSE Leap: `zypper search '^php<ver>-'`, strip `php<ver>-`.
- The PHP manual and PECL index for discovery and documentation:
  - https://www.php.net/manual/en/extensions.alphabetical.php lists bundled
    extensions by their human-readable display title (for example
    "PostgreSQL", "Multibyte String", "MySQL Improved Extension"). The short
    name does NOT appear in the index itself; click through to the entry and
    read it from the URL (`book.<shortname>.php`, so `book.pgsql.php` for
    PostgreSQL) or from the `extension=<shortname>` examples on the entry's
    "Installation" subpage.
  - https://www.php.net/manual/en/extensions.php gives a bundled-vs-PECL
    overview and explains the difference.
  - https://pecl.php.net/packages.php lists PECL extensions (`apcu`,
    `imagick`, `redis`, `xdebug`, `memcached`, ...) which are not part of the
    bundled index.

Case handling: the role requires every entry to be all lowercase(`[a-z0-9_]+`).
Any uppercase character (or other unexpected character) causes a hard failure
at role start with a message naming the offending entry.

Extensions are installed globally for the host's PHP installation. Per-SAPI
extension toggling like it is done on Debian (the `phpenmod -s fpm pgsql`
style) is not supported by this role.

The list defines the extensions the role guarantees to install and manage.
It is a "must-have" set, not the full set of extensions that will end up
active on the host: the base PHP packages on every supported distribution
ship a bundle of always-on extensions (for example `Core`, `date`, `pcre`,
`Reflection`, `SPL`, `standard`, and others, depending on the distribution's
`php-common` / `php<ver>-common` / `php8` meta package). Installing any
single SAPI usually pulls that meta package in as a dependency, so the
actually-active extension set is normally a superset of
`run_php_extensions_enabled`. The role does not try to disable or otherwise
interfere with those transitively-installed extensions based on this setting;
if you need to verify what is actually loaded on a given host, run
`php -m` (CLI) or `php-fpm -m` (FPM).

A non-exhaustive anchor list of short names you will commonly want,
grouped by purpose:

- Database: `pgsql`, `pdo_pgsql`, `mysqli`, `pdo_mysql`, `sqlite3`,
  `pdo_sqlite`, `odbc`, `pdo_odbc`.
- Networking: `curl`, `ldap`, `soap`, `ftp`, `imap`, `sockets`,
  `snmp`.
- Text and internationalisation: `mbstring`, `intl`, `iconv`,
  `gettext`.
- Data formats: `xml`, `simplexml`, `xmlreader`, `xmlwriter`, `dom`,
  `xsl`, `zip`, `bz2`.
- Graphics: `gd`, `exif`, `imagick` (PECL).
- Caching and performance: `opcache`, `apcu` (PECL), `redis` (PECL),
  `memcached` (PECL).
- Debug and profiling: `xdebug` (PECL), `tideways` (PECL).
- Crypto and math: `bcmath`, `gmp`, `sodium`, `openssl`.
- System: `posix`, `pcntl`, `shmop`, `sysvshm`, `sysvsem`,
  `sysvmsg`.

Example:

```yaml
run_php_extensions_enabled:
  - "pgsql"
  - "curl"
  - "intl"
  - "mbstring"
  - "opcache"
  - "xdebug"     # PECL, only useful on dev/debug hosts
```

- **Type**: `list`
- **Required**: No
- **Default**: `[]`
- **List Elements**: `str`



### `run_php_extensions_disable_unmanaged`<a id="variable-run_php_extensions_disable_unmanaged"></a>

[*⇑ Back to ToC ⇑*](#toc)

Controls whether the role disables extensions that are not declared in
`run_php_extensions_enabled`.

This is intentionally best-effort. PHP has no portable, cross-platform
extension activation registry. Built-in extensions and extensions loaded by
package-managed configuration may remain active even when they are not listed
here.

When set to `true`, extensions not listed in `run_php_extensions_enabled` are
disabled only on platforms where extension activation is represented by
removable SAPI-specific symlinks. On Debian-like platforms, the role removes
unmanaged symlinks from the selected SAPIs' `conf.d/` directories (for
example `/etc/php/<version>/fpm/conf.d/` and
`/etc/php/<version>/cli/conf.d/`) while leaving the canonical files in
`mods-available/` untouched.

On RHEL-like platforms and SUSE-like platforms, PHP extension drop-ins are
package-owned files in a shared INI scan directory (for example `/etc/php.d/`
on RHEL-like platforms and `/etc/php8/conf.d/` on openSUSE). The role does
not edit those package-owned files to comment out `extension=` or
`zend_extension=` directives. On those platforms this option does not disable
unmanaged extensions.

When set to `false` (which is the default), unmanaged extensions are left
untouched. Use this if  want to prevent accidental unavailability of
extensions loaded by default on your platform or you manage additional
extensions outside of this role.

- **Type**: `bool`
- **Required**: No
- **Default**: `false`



### `run_php_settings`<a id="variable-run_php_settings"></a>

[*⇑ Back to ToC ⇑*](#toc)

PHP INI configuration as a scope-keyed nested dictionary. The role renders
one or more drop-in `.ini` files into the appropriate SAPI INI directory on
Debian-like systems, or into the single shared INI scan directory on
shared-dir platforms (RHEL-like, SUSE-like).

Top-level keys are configuration scopes:

- `shared`: applies to every SAPI selected via `run_php_sapis`. This is the
  only cross-platform portable scope for php.ini.
- `fpm`, `cli`: apply only to that one SAPI. Works on Debian-like (per-SAPI
  conf.d/ directories exist) and hard-fails at role start on shared-dir
  platforms (RHEL-like, SUSE-like) since they cannot represent per-SAPI INI.
  On those platforms, restructure to `shared` or to
  `run_php_fpm_pool_defaults` / per-pool `php_admin_value`, or use fitting
  group variables in your inventory.

Inside each scope, top-level keys are INI section names (`PHP`, `Date`,
`opcache`, ...). Values are flat dictionaries of INI directives for that
section.

For configuration that is FPM-only and must stay portable across platforms,
prefer `run_php_fpm_pool_defaults` or per-pool `php_admin_value` /
`php_admin_flag` inside `run_php_fpm_pools`. Those end up inside the pool's
own `.conf` file and never touch the shared INI scan directory, so they work
on every platform.

The reserved key `extra_content` (a string, NOT a section dict) is a
last-resort escape hatch. It gets appended verbatim to the rendered drop-in
for that scope after the structured render. Use it for directives the
structured schema cannot express (this role's developers did not find any but
you never know all use cases). INI last-wins applies: an `extra_content` line
for a key already set via structured settings overrides the structured value.
Do not use this without a good reason. `extra_content` is never treated as an
INI section name.

Example:

```yaml
run_php_settings:
  shared:
    PHP:
      date.timezone: "UTC"
      expose_php: false
    extra_content: |
      ; raw INI directives appended verbatim
  fpm:
    PHP:
      upload_max_filesize: "64M"
      post_max_size: "64M"
  cli:
    PHP:
      memory_limit: "512M"
      max_execution_time: 0
```

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`

#### `run_php_settings['shared']`<a id="variable-run_php_settings-sub-shared"></a>

[*⇑ Back to ToC ⇑*](#toc)

Settings that apply to every selected SAPI. Renders into every selected
SAPI's INI directory on Debian-like platforms, and once into the shared
INI scan directory on shared-dir platforms (RHEL-like, SUSE-like).
This is the only cross-platform portable INI scope.

Top-level keys inside this dictionary are INI section names. The reserved
`extra_content` key is a string appended verbatim after the structured
render.

- **Type**: `dict`
- **Required**: No

#### `run_php_settings['fpm']`<a id="variable-run_php_settings-sub-fpm"></a>

[*⇑ Back to ToC ⇑*](#toc)

Settings that apply only to the FPM SAPI. Renders into `fpm/conf.d/` on
Debian-like platforms. Hard-fails on shared-dir platforms (RHEL-like,
SUSE-like) when non-empty, because a single shared INI directory cannot
represent per-SAPI INI. For cross-platform FPM-only INI, use
`run_php_fpm_pool_defaults` or per-pool `php_admin_value` /
`php_admin_flag` instead.

- **Type**: `dict`
- **Required**: No

#### `run_php_settings['cli']`<a id="variable-run_php_settings-sub-cli"></a>

[*⇑ Back to ToC ⇑*](#toc)

Settings that apply only to the CLI SAPI. Renders into `cli/conf.d/` on
Debian-like platforms. Hard-fails on shared-dir platforms (RHEL-like,
SUSE-like) when non-empty, because a single shared INI directory cannot
represent per-SAPI INI.

- **Type**: `dict`
- **Required**: No



### `run_php_extension_settings`<a id="variable-run_php_extension_settings"></a>

[*⇑ Back to ToC ⇑*](#toc)

INI directives applied per extension, scoped the same way as
`run_php_settings`. Top-level keys are configuration scopes (`shared`, `fpm`,
`cli`); second-level keys are extension short names; third-level keys are
flat INI directives for that extension.

The cross-platform rules are identical to `run_php_settings`:

- `shared['<ext>']` is portable everywhere. Renders into every selected SAPI's
  INI directory on Debian-like and once into the shared INI directory on
  shared-dir platforms (RHEL-like, SUSE-like).
- `<sapi>.<ext>` hard-fails on shared-dir platforms when non-empty. On
  Debian-like it renders into that SAPI's INI directory only.

Extension settings declared here for an extension that is not listed in
`run_php_extensions_enabled` produce a debug notice and the configuration is
skipped.

The most common case (settings that should apply uniformly to every SAPI) goes
under `shared:`. Per-SAPI behaviour such as enabling Xdebug only for CLI works
on Debian-like platforms via the matching SAPI scope; on shared-dir
platforms the same restructure-to-shared rule applies as for
`run_php_settings`.

Example:

```yaml
run_php_extension_settings:
  shared:
    opcache:
      opcache.memory_consumption: 256
      opcache.max_accelerated_files: 20000
      opcache.enable_cli: 0
  cli:
    xdebug:
      xdebug.mode: "debug"
      xdebug.start_with_request: "yes"
```

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`

#### `run_php_extension_settings['shared']`<a id="variable-run_php_extension_settings-sub-shared"></a>

[*⇑ Back to ToC ⇑*](#toc)

Extension settings that apply to every selected SAPI. The only
cross-platform portable per-extension scope.

- **Type**: `dict`
- **Required**: No

#### `run_php_extension_settings['fpm']`<a id="variable-run_php_extension_settings-sub-fpm"></a>

[*⇑ Back to ToC ⇑*](#toc)

Extension settings that apply only to the FPM SAPI. Renders on
Debian-like, hard-fails on shared-dir platforms (RHEL-like,
SUSE-like) when non-empty.

- **Type**: `dict`
- **Required**: No

#### `run_php_extension_settings['cli']`<a id="variable-run_php_extension_settings-sub-cli"></a>

[*⇑ Back to ToC ⇑*](#toc)

Extension settings that apply only to the CLI SAPI. Renders on
Debian-like, hard-fails on shared-dir platforms (RHEL-like,
SUSE-like) when non-empty.

- **Type**: `dict`
- **Required**: No



### `run_php_fpm_pool_defaults`<a id="variable-run_php_fpm_pool_defaults"></a>

[*⇑ Back to ToC ⇑*](#toc)

Defaults merged underneath every pool in `run_php_fpm_pools` at render time.
Per-pool entries override defaults on any matching key (deep merge: pool's
`php_admin_value.memory_limit` overrides the default's
`php_admin_value.memory_limit`).

This is the cross-platform portable way to set FPM-only INI: each pool ends
up with its own copy of these directives inside its `pool.d/<name>.conf` file,
so the values never enter the shared INI directory used by shared-dir
platforms (RHEL-like, SUSE-like) and behave identically on every platform.

The structure mirrors what PHP-FPM expects inside a pool block.
PHP-FPM has five associative-array bracket directives — the full
set is supported here. Pick `_admin` variants when the value must
not be overridable by application code at runtime (`ini_set()`):

- `php_admin_value`: dictionary of name to scalar value, locked
  from app code (PHP_INI_SYSTEM). Rendered as
  `php_admin_value[name] = value` lines.
- `php_admin_flag`: dictionary of name to boolean, locked from
  app code. YAML booleans render as PHP-FPM `on` / `off`. Rendered
  as `php_admin_flag[name] = on|off` lines.
- `php_value`: dictionary of name to scalar value, app may
  re-override via `ini_set()`. Rendered as
  `php_value[name] = value` lines.
- `php_flag`: dictionary of name to boolean, app may re-override.
  Rendered as `php_flag[name] = on|off` lines.
- `env`: dictionary of environment variable names to string
  values that the pool will export to its workers. Rendered as
  `env[NAME] = value` lines.

The list-shaped directive `access.suppress_path[]` (numerically
indexed, not associative) is not modeled as a typed key; use a
pool's `extra_content` for it.

The variable is honored only when `"fpm"` appears in `run_php_sapis`. Setting
it without FPM in the SAPI list produces a debug notice and the variable is
ignored.

Example:

```yaml
run_php_fpm_pool_defaults:
  php_admin_value:
    upload_max_filesize: "64M"
    post_max_size: "64M"
    memory_limit: "256M"
  php_admin_flag:
    display_errors: false
    log_errors: true
  php_value:
    default_socket_timeout: "60"
  php_flag:
    short_open_tag: false
  env:
    APP_ENV: "production"
```

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`

#### `run_php_fpm_pool_defaults['php_admin_value']`<a id="variable-run_php_fpm_pool_defaults-sub-php_admin_value"></a>

[*⇑ Back to ToC ⇑*](#toc)

Pool-level INI directives, scalar values. PHP_INI_SYSTEM —
locked from app code (cannot be overridden via `ini_set()`).
Rendered as `php_admin_value[<name>] = <value>` inside the
pool block.

- **Type**: `dict`
- **Required**: No

#### `run_php_fpm_pool_defaults['php_admin_flag']`<a id="variable-run_php_fpm_pool_defaults-sub-php_admin_flag"></a>

[*⇑ Back to ToC ⇑*](#toc)

Pool-level INI directives, boolean values. Locked from app
code. YAML booleans render as PHP-FPM `on` / `off`. Rendered
as `php_admin_flag[<name>] = <on|off>` inside the pool block.

- **Type**: `dict`
- **Required**: No

#### `run_php_fpm_pool_defaults['php_value']`<a id="variable-run_php_fpm_pool_defaults-sub-php_value"></a>

[*⇑ Back to ToC ⇑*](#toc)

Pool-level INI directives, scalar values. App code may
re-override via `ini_set()` at runtime. Use the `_admin`
variant when the value must survive app code. Rendered as
`php_value[<name>] = <value>` inside the pool block.

- **Type**: `dict`
- **Required**: No

#### `run_php_fpm_pool_defaults['php_flag']`<a id="variable-run_php_fpm_pool_defaults-sub-php_flag"></a>

[*⇑ Back to ToC ⇑*](#toc)

Pool-level INI directives, boolean values. App code may
re-override at runtime. Use the `_admin` variant when the
value must survive app code. YAML booleans render as
PHP-FPM `on` / `off`. Rendered as
`php_flag[<name>] = <on|off>` inside the pool block.

- **Type**: `dict`
- **Required**: No

#### `run_php_fpm_pool_defaults['env']`<a id="variable-run_php_fpm_pool_defaults-sub-env"></a>

[*⇑ Back to ToC ⇑*](#toc)

Environment variables exported to the workers of every pool.
Rendered as `env[<name>] = <value>` inside the pool block.

- **Type**: `dict`
- **Required**: No



### `run_php_fpm_pools`<a id="variable-run_php_fpm_pools"></a>

[*⇑ Back to ToC ⇑*](#toc)

PHP-FPM pools to manage. The dictionary is keyed by pool name, which is also
the filename used in `pool.d/<name>.conf`. Honored  only when `"fpm"` is in
`run_php_sapis`.

Each pool entry is a dictionary whose keys are PHP-FPM directive names
verbatim (with dots intact, since YAML accepts dots in unquoted keys). The
role's templates use bracket notation to read them (`pool['listen.owner']`).

Recognised per-pool fields:

- `state`: optional. `present` (default) renders `pool.d/<name>.conf`.
  `absent` deletes that file if present. Other fields are allowed on
  absent pools but ignored, so a pool definition can stay in inventory for
  fast re-deployment.
- PHP-FPM directives such as `user`, `group`, `listen`, `listen.owner`,
  `listen.group`, `listen.mode`, `pm`, `pm.max_children`, `pm.start_servers`,
  `pm.min_spare_servers`, ... Names are used 1:1 with what PHP-FPM expects.
- `php_admin_value`: dictionary of name to scalar value, locked from app
  code (PHP_INI_SYSTEM — `ini_set()` cannot change it). Rendered as
  `php_admin_value[name] = value`. Merges with
  `run_php_fpm_pool_defaults.php_admin_value`; pool-level keys win on
  conflict.
- `php_admin_flag`: dictionary of name to boolean, locked from app code.
  Rendered as `php_admin_flag[name] = on|off`. Merges with the matching
  default, pool-level wins on conflict.
- `php_value`: dictionary of name to scalar value; app code may re-override
  via `ini_set()`. Use the `_admin` variant when the value must survive app
  code. Rendered as `php_value[name] = value`. Merges with the matching
  default, pool-level wins on conflict.
- `php_flag`: dictionary of name to boolean; app code may re-override.
  Rendered as `php_flag[name] = on|off`. Merges with the matching default,
  pool-level wins on conflict.
- `env`: dictionary of environment variable names to values exported to the
  pool's workers. Merges with the matching default, pool-level wins on
  conflict.
- `extra_content`: raw string appended verbatim to the rendered pool file
  after the structured render. INI last-wins applies. Use this for the
  list-shaped directive `access.suppress_path[]` and anything else not
  modeled as a typed key.

Pools NOT listed in this dictionary are left on disk by default. To enable
strict declarative ownership of `pool.d/`, set
`run_php_fpm_pools_delete_unmanaged: true`.

Example:

```yaml
run_php_fpm_pools:
  www:
    state: "present"
    user: "www-data"
    group: "www-data"
    listen: "/run/php/php-fpm.sock"
    listen.owner: "www-data"
    listen.group: "www-data"
    listen.mode: "0660"
    pm: "dynamic"
    pm.max_children: 50
    pm.start_servers: 5
    pm.min_spare_servers: 5
    pm.max_spare_servers: 15
    php_admin_value:
      memory_limit: "256M"
    php_admin_flag:
      log_errors: true
    env:
      APP_ENV: "production"
    extra_content: |
      ; arbitrary additional directives
  legacy-app:
    state: "absent"
    listen: "/run/php/legacy-app.sock"
    pm: "static"
    pm.max_children: 4
```

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`



### `run_php_fpm_pools_delete_unmanaged`<a id="variable-run_php_fpm_pools_delete_unmanaged"></a>

[*⇑ Back to ToC ⇑*](#toc)

Controls whether the role removes pool files from `pool.d/` that are not
declared in `run_php_fpm_pools`.

When `true`, any `*.conf` file in `pool.d/` whose stem does not match an entry
in `run_php_fpm_pools` is deleted on every role run. This treats
`run_php_fpm_pools` as the single source of truth for the pool directory.

When `false` (the default), unknown files are left untouched. Explicit removal
of a specific pool can still be done by listing it with `state: "absent"` in
`run_php_fpm_pools`.

Honored only when `"fpm"` is in `run_php_sapis`.

- **Type**: `bool`
- **Required**: No
- **Default**: `false`



### `run_php_fpm_service_settings`<a id="variable-run_php_fpm_service_settings"></a>

[*⇑ Back to ToC ⇑*](#toc)

PHP-FPM service-level settings, written into the `[global]` section of the
distribution's main `php-fpm.conf` via `ansible.builtin.blockinfile`. The
role does not overwrite the distribution file, only the managed block inside
it.

Top-level keys correspond to PHP-FPM `php-fpm.conf` sections. The only
currently recognised section is `global`. Inside that dictionary, keys are
PHP-FPM directive names and values are their scalar values. Keys are used 1:1
with what PHP-FPM expects (dots intact, no quoting required by YAML).

Honored only when `"fpm"` is in `run_php_sapis`. Setting it without FPM in the
SAPI list produces a debug notice and the variable is ignored.

Example:

```yaml
run_php_fpm_service_settings:
  global:
    error_log: "/var/log/php-fpm/error.log"
    log_level: "notice"
    emergency_restart_threshold: 10
    emergency_restart_interval: "1m"
    process_control_timeout: "10s"
```

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`

#### `run_php_fpm_service_settings['global']`<a id="variable-run_php_fpm_service_settings-sub-global"></a>

[*⇑ Back to ToC ⇑*](#toc)

`[global]` directives of `php-fpm.conf`. Keys are PHP-FPM directive names
and values are their scalar values. Keys are used 1:1 with what PHP-FPM
expects (dots intact, no quoting required by YAML).

- **Type**: `dict`
- **Required**: No




<!-- ANSIBLE DOCSMITH MAIN END -->

## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__run_php_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

There are no special requirements not covered by Ansible itself.
