#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Apply or check the project's MIT SPDX headers on first-party source files.

Run ``python3 scripts/apply_license_headers.py --write`` to update files and
``python3 scripts/apply_license_headers.py --check`` to verify coverage.
"""
import argparse
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = ('bizplan/', 'scripts/', 'tests/', 'features/steps/')
COMMENT_PREFIX = {'.py': '#', '.sh': '#', '.js': '//', '.mjs': '//',
                  '.ts': '//', '.tsx': '//', '.sql': '--'}
OWNER = '2026 ghacupha'
ENCODING = re.compile(r'coding[:=]\s*[-\w.]+')


def source_files(root=ROOT):
    """Select only version-controlled or newly added first-party source files."""
    result = subprocess.run(
        ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
        cwd=root, check=True, stdout=subprocess.PIPE)
    paths = (Path(name.decode('utf-8')) for name in result.stdout.split(b'\0') if name)
    return sorted(root / path for path in paths
                  if path.as_posix().startswith(SOURCE_ROOTS)
                  and path.suffix in COMMENT_PREFIX)


def add_header(text, suffix):
    """Return licensed source, preserving interpreter and encoding directives."""
    prefix = COMMENT_PREFIX[suffix]
    header = (f'{prefix} SPDX-FileCopyrightText: {OWNER}\n'
              f'{prefix} SPDX-License-Identifier: MIT\n')
    lines = text.splitlines(keepends=True)
    position = 1 if lines and lines[0].startswith('#!') else 0
    if (suffix == '.py' and position < len(lines)
            and ENCODING.search(lines[position])):
        position += 1
    remainder = ''.join(lines[position:])
    if remainder == header + '\n':
        return ''.join(lines[:position]) + header
    if remainder.startswith(header):
        return text
    if any(re.match(r'^\s*(?:#|//|--)\s*(?:SPDX-License-Identifier:|Copyright|©)', line)
           for line in lines[:12]):
        raise ValueError('Existing license or copyright notice needs manual review')
    return ''.join(lines[:position]) + header + ('\n' if remainder else '') + remainder


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--write', action='store_true', help='insert missing headers')
    action.add_argument('--check', action='store_true', help='fail if a header is missing')
    args = parser.parse_args(argv)
    changed = []
    for path in source_files():
        original = path.read_text(encoding='utf-8')
        try:
            updated = add_header(original, path.suffix)
        except ValueError as error:
            parser.error('%s: %s' % (path.relative_to(ROOT), error))
        if updated != original:
            changed.append(path)
            if args.write:
                path.write_text(updated, encoding='utf-8')
    if changed:
        for path in changed:
            print('%s: %s' % ('updated' if args.write else 'missing header',
                              path.relative_to(ROOT)))
    print('%d source files checked; %d %s' %
          (len(source_files()), len(changed), 'updated' if args.write else 'missing'))
    return 1 if changed and args.check else 0


if __name__ == '__main__':
    sys.exit(main())
