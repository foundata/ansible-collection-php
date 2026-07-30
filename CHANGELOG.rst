=============================================
foundata.php Ansible collection Release Notes
=============================================

.. contents:: Topics

v1.1.0
======

Release Summary
---------------

Release Date: 2026-07-30

Maintenance and bugfix release.

Minor Changes
-------------

- The Molecule ``default`` scenario now selects the test backend per platform via a ``type`` key: ``podman`` (container, the default when omitted) or ``libvirt`` (QEMU/KVM virtual machine from a vendor cloud image via a session libvirt daemon, without root privileges). VM platforms allow tests containers cannot cover; commented ``libvirt`` alternates for every platform are included in ``molecule.yml``. ``molecule login`` now works through a per-instance login command for both backends. See ``extensions/molecule/README.md`` for requirements and usage.
- ``run`` role - On EL9, ``run_php_state: "absent"`` now runs ``dnf module reset php`` when a concrete ``run_php_version`` is pinned, so an uninstall no longer leaves the host pinned to the PHP version this role selected. The reset is unconditional: a php module stream enabled before this role was adopted is reset as well and has to be re-enabled manually. With ``run_php_version: "default"`` the module stream is not touched in either direction.

Security Fixes
--------------

- ``run`` role - PHP-FPM pool files were rendered world-readable (``0644``) although ``env`` and ``php_admin_value`` entries commonly carry application credentials such as database passwords. Pool files are now rendered ``0600`` (only the FPM master process, running as root, reads them) and the render task suppresses its diff output so pool contents no longer leak into ``--diff`` / check-mode logs.
- ``run`` role - Pool names from ``run_php_fpm_pools`` were used verbatim as ``pool.d/<name>.conf`` paths and ``[<name>]`` section headers, so a name containing path separators, ``..``, brackets or whitespace could target files outside the pool directory or render a malformed section. Pool names must now match ``[A-Za-z0-9._-]+`` and the role fails during initialization otherwise.

Bugfixes
--------

- The comment written into neutralized distribution config files contained a stray double quote in the Debian hint (``dpkg -S '<file>'"``), so the suggested command could not be copied and pasted as-is. The quote is removed.
- ``run`` role - A pinned ``run_php_version`` was silently ignored on openSUSE Leap: package names, INI paths, service and binary are unversioned there and the repositories ship exactly one PHP series (``php8``, 8.4 in Leap 16.0), so the role installed the distribution stream while reporting the pinned version as the effective one. The role now resolves the effective version to the distribution stream on platforms that cannot honor a pin, and reports an unfulfillable pin as a warning during initialization. The run continues, so a single ``run_php_version`` in ``group_vars`` stays usable for inventories that mix such a platform with others.
- ``run`` role - Managing the php-fpm ``[global]`` block no longer fails when ``run_php_fpm_service_settings`` is left at its documented default of ``{}`` while FPM is enabled. The template loop accessed ``['global']`` unguarded (Ansible templates the ``block:`` argument regardless of the ``state:`` value), raising an undefined-key error; the access is now guarded with ``| default({})``.
- ``run`` role - Pinning ``run_php_version`` on EL9 generated nonexistent package names: the package prefix switched to ``php<version>-`` although EL9 delivers alternative versions as DNF module streams that keep the unversioned ``php-*`` package names. The prefix now stays ``php-`` on EL9.
- ``run`` role - Pinning ``run_php_version`` on an EL9 host that had no php module stream enabled (the usual case) aborted the run: the detection of the currently enabled stream passed the ``None`` returned by ``regex_search`` on to ``first``.
- ``run`` role - Platform-specific task files are now guaranteed to run before the shared default tasks. The former single include loop did not preserve that order with several platforms in one play: Ansible batches the includes across hosts and the insertion order depends on when results arrive (non-deterministic), so default tasks could run before platform-specific ones. The includes are now two sequential tasks, which is a hard ordering barrier.
- ``run`` role - The EL9 DNF module stream tasks (``tasks/setup/install/redhat_9.yml``) were unreachable on AlmaLinux, Rocky Linux, and CentOS Stream because the platform dispatch resolves per-distribution filenames only. Added ``almalinux_9.yml``, ``rocky_9.yml`` and ``centos_9.yml`` which include the shared EL9 module stream tasks, so pinning ``run_php_version`` now enables the matching ``php:<version>`` stream on all EL9 derivatives.
- ``run`` role - The documentation of the ``unmanaged`` service state falsely claimed the service "will not start at boot". The role leaves the service completely alone in this state: both the running state and the boot (enablement) state stay exactly as they are. The description now documents the real behavior.
- ``run`` role - The rendered PHP-FPM configuration (pool files and the managed ``[global]`` block) was only syntax-checked indirectly by the service reload, so with ``run_php_fpm_service_state`` set to ``disabled`` or ``unmanaged`` an invalid configuration could complete the run successfully and only surface at the next (possibly manual) service start. Every change to FPM configuration now notifies a validation handler that runs ``php-fpm --test`` regardless of the service state.
- ``run`` role - The service restart and reload handlers were gated only on ``run_php_fpm_service_state != 'unmanaged'``. With ``run_php_fpm_service_state: "disabled"`` a configuration change still notified them and, because handlers run after the service management tasks, the restart started the just-stopped unit again (and the reload failed on the inactive unit), leaving a running service although the declared state is stopped. The handlers are now gated on ``run_php_fpm_service_state in ['enabled', 'running']``.
- ``run`` role - ``run_php_extensions_disable_unmanaged: true`` removed the activation symlinks of base extensions bundled by ``php<version>-common`` on Debian-like platforms (``pdo``, ``phar``, ``ctype``, ``iconv``, ...) unless every one of them was listed in ``run_php_extensions_enabled``, breaking the base PHP installation and dependent extensions (e.g. every ``pdo_*`` driver fails to load without ``pdo``). Extensions the role classifies as builtin are now always kept.
- ``run`` role - ``run_php_state: "absent"`` installed ``python3-rpm`` (and ``python3-libdnf5`` on Fedora) for its package inventory but never removed them, so an uninstall could leave more packages behind than it found. Helpers that were absent before are now removed again at the end; helpers that were already present (like ``python3-rpm`` on EL, which dnf itself needs) are left alone.
- ``run`` role - ``run_php_state: "absent"`` only removed packages, so rendered INI drop-ins, FPM pool files (which can carry credentials in ``env`` / ``php_admin_value`` entries) and the managed ``[global]`` block survived the uninstall. All rendered files now carry an ownership marker; the uninstall sweeps the configuration directories for it (removing renamed or de-listed pools as well), removes the role's INI namespace and currently declared pool files by name (covering deployments that predate the marker), and strips the managed block from ``php-fpm.conf`` before the package removal, so RPM platforms no longer keep it in a ``php-fpm.conf.rpmsave``.
- ``run`` role - ``run_php_version`` accepted arbitrary strings which reached package names and, on EL9, the ``dnf module enable php:<value>`` command. The role now fails during initialization unless the value is ``default`` or a plain ``MAJOR.MINOR`` version.

v1.0.0
======

Release Summary
---------------

Release Date: 2026-05-30

First public release, providing all functionality and files.
