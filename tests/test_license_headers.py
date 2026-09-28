# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Guard the reusable MIT header command against duplicate or unsafe edits."""
import unittest

from scripts.apply_license_headers import add_header


class LicenseHeaderTests(unittest.TestCase):
    def test_shebang_stays_first_and_repeat_is_idempotent(self):
        source = '#!/usr/bin/env python3\n"""Module."""\n'
        updated = add_header(source, '.py')
        self.assertTrue(updated.startswith('#!/usr/bin/env python3\n'))
        self.assertIn('# SPDX-License-Identifier: MIT\n', updated)
        self.assertEqual(add_header(updated, '.py'), updated)

    def test_existing_copyright_requires_review(self):
        with self.assertRaises(ValueError):
            add_header('# Copyright (c) Another author\n', '.py')


if __name__ == '__main__':
    unittest.main()
