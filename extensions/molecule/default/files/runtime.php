<?php
// SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
// SPDX-License-Identifier: GPL-3.0-or-later

header('Content-Type: application/json');
echo json_encode([
    'sapi' => PHP_SAPI,
    'oauth' => extension_loaded('oauth'),
    'error_reporting' => error_reporting(),
    'expected_error_reporting' => E_ALL & ~(E_DEPRECATED | E_USER_DEPRECATED),
    'user_agent' => ini_get('user_agent'),
    'opcache.log_verbosity_level' => ini_get('opcache.log_verbosity_level'),
]);
