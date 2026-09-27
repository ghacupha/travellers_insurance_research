#!/usr/bin/env python3
"""Light offline QA of cached PDF hashes and transcribed numeric page tokens.

This checks page presence, not row-level parity to SEC HTML or semantic meaning.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re


def audit(history_path, inventory_path):
    history = json.loads(Path(history_path).read_text())
    inventory = json.loads(Path(inventory_path).read_text())
    sources = {item['id']: item for item in inventory['sources']}
    errors, checked = [], 0
    pages = {}
    for source in sources.values():
        pdf_path = Path(source['local_cache'])
        if not pdf_path.exists():
            errors.append(f"PDF cache missing: {pdf_path}")
            continue
        if sha256(pdf_path.read_bytes()).hexdigest() != source['sha256']:
            errors.append(f"PDF hash mismatch: {pdf_path}")
        text_path = pdf_path.with_suffix('.pages.json')
        if not text_path.exists():
            errors.append(f"Page-text cache missing: {text_path}")
            continue
        pages[source['id']] = json.loads(text_path.read_text())
    for fact in history['facts']:
        if fact['status'] != 'disclosed' or fact['value'] == 0:
            continue
        source_pages = pages.get(fact['source_id'])
        if source_pages is None:
            continue
        page_number = fact['pdf_page']
        if not 1 <= page_number <= len(source_pages):
            errors.append(f"Page outside cache: {fact['year']} {fact['metric']} p{page_number}")
            continue
        token = f"{abs(fact['value']):,}"
        if not re.search(r'(?<!\d)' + re.escape(token) + r'(?!\d)', source_pages[page_number-1]):
            errors.append(f"Numeric token absent: {fact['year']} {fact['metric']}={fact['value']} p{page_number}")
        checked += 1
    return checked, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', type=Path, default=Path('examples/travelers/historical_actuals.json'))
    parser.add_argument('--inventory', type=Path, default=Path('examples/travelers/source_inventory.json'))
    args = parser.parse_args()
    count, errors = audit(args.history, args.inventory)
    print(f'{count} disclosed numeric facts checked; {len(errors)} errors')
    for error in errors:
        print(error)
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
