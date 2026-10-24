#!/usr/bin/env python3
"""Проверка синтаксиса Pascal файлов для БЭСМ-6"""

import sys
import re

def check_pascal_file(filename):
    errors = []
    
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # Проверка 1: Длина строк
    for i, line in enumerate(lines, 1):
        if len(line.rstrip('\n\r')) > 72:
            errors.append(f"Line {i}: too long ({len(line.rstrip())} > 72)")
    
    # Проверка 2: Обязательные директивы (только для zone2500)
    content = ''.join(lines)
    
    if 'zone2500' in filename or '2348' in filename:
        required_patterns = [
            (r'\*name\s+\w+', '*name directive'),
            (r'\*pascal', '*pascal directive'),
            (r'\*execute', '*execute directive'),
            (r'\*end file', '*end file'),
            (r'program\s+\w+', 'program declaration'),
        ]
        
        for pattern, desc in required_patterns:
            if not re.search(pattern, content, re.IGNORECASE):
                errors.append(f"Missing: {desc}")
    
    # Проверка 3: Сбалансированность begin/end
    # end. считается как begin
    begins = len(re.findall(r'\bbegin\b', content, re.IGNORECASE))
    ends = len(re.findall(r'\bend\b', content, re.IGNORECASE))
    end_dot = len(re.findall(r'\bend\.\s*$', content, re.MULTILINE))
    
    # end. заменяет один end, добавляем один begin
    effective_begins = begins + end_dot
    effective_ends = ends
    
    if effective_begins != effective_ends:
        errors.append(f"Unbalanced begin/end: {effective_begins} begin, {effective_ends} end")
    
    # Проверка 4: Директива компилятора
    if '(*=e+*)' not in content and '(*=e+*)' not in content:
        errors.append("Missing compiler directive (*=e+*)")
    
    # Проверка 5: External объявления
    externals = re.findall(r'(Function|Procedure)\s+\w+[^;]*;\s*external;', content, re.IGNORECASE)
    
    return errors, len(externals)

def main():
    import glob
    
    print("=== Pascal Syntax Validator for BESM-6 ===\n")
    
    files = glob.glob('zone2500/*.pas')
    
    if not files:
        print("No zone2500 files found!")
        return 1
    
    all_ok = True
    total_files = 0
    total_errors = 0
    total_ext = 0
    
    for filename in sorted(files):
        total_files += 1
        print(f"Checking: {filename}")
        
        try:
            errors, ext_count = check_pascal_file(filename)
            total_ext += ext_count
            
            if errors:
                all_ok = False
                total_errors += len(errors)
                for err in errors:
                    print(f"  ✗ {err}")
            else:
                print(f"  ✓ Syntax OK")
                if ext_count > 0:
                    print(f"  → External refs: {ext_count}")
        except Exception as e:
            all_ok = False
            total_errors += 1
            print(f"  ✗ Error: {e}")
        
        print()
    
    print(f"=== Summary ===")
    print(f"Files: {total_files}")
    print(f"Errors: {total_errors}")
    print(f"External refs: {total_ext}")
    
    if all_ok:
        print("\n✓ All zone2500 files ready for compilation!")
        return 0
    else:
        print("\n✗ Some files have errors")
        return 1

if __name__ == '__main__':
    sys.exit(main())
