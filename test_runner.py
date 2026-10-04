#!/usr/bin/env python3
"""
Test runner for Myers diff implementation
"""
import subprocess
import sys

def run_test(name, cmd, expected_exit_code=0):
    """Run a single test and report results"""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"Command: {cmd}")
    print('='*60)
    
    result = subprocess.run(cmd, shell=True, capture_output=True)
    
    print("STDOUT:")
    print(result.stdout.decode('utf-8', errors='replace'))
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr.decode('utf-8', errors='replace'))
    
    print(f"Exit code: {result.returncode}")
    
    if result.returncode == expected_exit_code:
        print("[PASS]")
        return True
    else:
        print(f"[FAIL] (expected {expected_exit_code}, got {result.returncode})")
        return False

def main():
    tests = [
        ("Paper example - lines", "python src/main.py lines samples/paper_old.txt samples/paper_new.txt", 0),
        ("Config example - lines", "python src/main.py lines samples/config_old.txt samples/config_new.txt", 0),
        ("Unicode example - lines", "python src/main.py lines samples/unicode_old.txt samples/unicode_new.txt", 0),
        ("Paper example - highlight", "python src/main.py highlight samples/paper_old.txt samples/paper_new.txt", 0),
        ("Config example - highlight", "python src/main.py highlight samples/config_old.txt samples/config_new.txt", 0),
        ("Unicode example - highlight", "python src/main.py highlight samples/unicode_old.txt samples/unicode_new.txt", 0),
        ("Identical files", "python src/main.py lines samples/config_old.txt samples/config_old.txt", 0),
        ("File not found", "python src/main.py lines samples/nonexistent.txt samples/config_old.txt", 2),
        ("Invalid command", "python src/main.py invalid samples/config_old.txt samples/config_new.txt", 2),
    ]
    
    passed = 0
    failed = 0
    
    for name, cmd, expected_exit in tests:
        if run_test(name, cmd, expected_exit):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print('='*60)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
