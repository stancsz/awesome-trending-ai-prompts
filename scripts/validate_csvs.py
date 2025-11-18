import glob
import csv
import sys
import codecs
from pathlib import Path

def check_utf8(path: Path):
    b = path.read_bytes()
    try:
        b.decode('utf-8')
        bom = b.startswith(codecs.BOM_UTF8)
        return True, bom, None
    except Exception as e:
        return False, False, str(e)

def check_header(path: Path):
    try:
        with path.open(encoding='utf-8', errors='strict') as fh:
            # strip actual newline and carriage return characters (handle LF/CRLF)
            first = fh.readline().rstrip('\n').rstrip('\r')
            return first == 'prompt,contributor,comment', first
    except Exception as e:
        return False, f'ERROR_READING_HEADER: {e}'

def parse_csv(path: Path):
    problems = []
    try:
        with path.open(encoding='utf-8', newline='') as fh:
            reader = csv.reader(fh)
            for i, row in enumerate(reader, start=1):
                # Basic sanity check: rows should have exactly 3 columns (but allow flexible)
                if len(row) != 3:
                    problems.append((i, f'expected 3 columns, got {len(row)}'))
                # Check for unescaped quotes inside fields by reserializing and comparing lengths
                # (This is heuristic; csv module already handles quoting, so parse errors will surface)
        return problems, None
    except csv.Error as e:
        return None, f'CSV_PARSE_ERROR: {e}'
    except Exception as e:
        return None, f'ERROR_PARSING: {e}'

def main():
    """
    Discover provider prompts.csv files by scanning only the first-level children
    of the repository root (non-recursive). This enforces the flattened layout
    and avoids picking up CSVs from nested script folders.
    """
    base = Path(__file__).resolve().parent.parent
    files = []
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        if "scripts" in child.parts:
            continue
        csv_path = child / "prompts.csv"
        if csv_path.exists():
            files.append(csv_path)
    files = sorted(files)

    if not files:
        print('No CSV files found.')
        return 0

    print(f'Found {len(files)} CSV file(s) to validate:')
    overall_ok = True

    for f in files:
        print('\\n---')
        print(f'File: {f}')
        utf8_ok, has_bom, utf8_err = check_utf8(f)
        print('UTF-8 valid:', utf8_ok, 'BOM:', has_bom)
        if not utf8_ok:
            print('  UTF-8 error:', utf8_err)
            overall_ok = False
            continue

        header_ok, header_val = check_header(f)
        print('Header exact match:', header_ok)
        if not header_ok:
            print('  Actual header line:', repr(header_val))
            overall_ok = False

        problems, parse_err = parse_csv(f)
        if parse_err:
            print('CSV parsing error:', parse_err)
            overall_ok = False
        else:
            if problems:
                print('CSV row issues (non-3-column rows):')
                for lineno, msg in problems[:10]:
                    print(f'  line {lineno}: {msg}')
                if len(problems) > 10:
                    print(f'  ...and {len(problems)-10} more')
                overall_ok = False
            else:
                print('CSV parse: OK (no obvious row-count issues)')

    print('\\nSummary: repository CSV validation', 'OK' if overall_ok else 'ISSUES FOUND')
    return 0 if overall_ok else 2

if __name__ == '__main__':
    sys.exit(main())
