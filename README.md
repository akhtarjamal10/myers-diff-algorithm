# Myers Diff Algorithm Implementation

## Assignment 1 - Creative Problem Solving

This repository contains a Python implementation of Eugene Myers' O(ND) Difference Algorithm (1986) for computing minimal line and character-level diffs between files.

## Features

- **Part A: Line Diff** - Minimal line-by-line difference between two files
- **Part B: Highlight** - Character-level highlighting within changed lines
- **Performance**: O(ND) complexity where N+M is total lines and D is edit distance
- **Handles**: Raw bytes, Unicode, emojis, non-UTF-8 content

## Usage

```bash
# Line diff (Part A)
python src/main.py lines <file_a> <file_b>

# Line diff with character highlighting (Part B)
python src/main.py highlight <file_a> <file_b>
```

## Examples

### Example 1: Configuration File
```bash
python src/main.py lines samples/config_old.txt samples/config_new.txt
```
Output:
```
 server:
-  port = 8000
+  port = 8080
   host = localhost
-  debug = true
+  debug = false
```

### Example 2: With Highlighting
```bash
python src/main.py highlight samples/config_old.txt samples/config_new.txt
```
Output:
```
 server:
-  port = 8000
+  port = 8080
? 12-13 | 11-12
   host = localhost
-  debug = true
+  debug = false
? 10-13 | 10-14
```

### Example 3: Myers Paper Example
```bash
python src/main.py lines samples/paper_old.txt samples/paper_new.txt
```
Input: A = `a b c a b b a`, B = `c b a b a c` (one letter per line)

Output (5 edits - minimum):
```
-a
-b
 c
+b
 a
 b
-b
 a
+c
```

### Example 4: Unicode and Emojis
```bash
python src/main.py highlight samples/unicode_old.txt samples/unicode_new.txt
```
Correctly handles Unicode characters and emojis as single code points.

## Implementation Details

### Core Algorithm (myers_diff)
Implements Myers' O(ND) algorithm using:
- **V array**: Stores furthest reaching x-coordinate for each k-diagonal
- **Trace**: Records V array history for backtracking
- **Greedy approach**: Extends snakes (matching diagonals) as far as possible

### File Reading (read_file_lines)
- Opens files in binary mode (`rb`)
- Splits on `\n` byte
- Drops empty final piece if present
- Preserves `\r` as part of line content
- Handles non-UTF-8 bytes

### Output Formatting

#### Lines Command (format_lines_output)
- Prefix: ` ` (keep), `-` (delete), `+` (insert)
- **Delete-first rule**: In change blocks, all `-` lines before `+` lines

#### Highlight Command (format_highlight_output)
- Groups edits into change blocks
- Pairs deleted and inserted lines (1st with 1st, 2nd with 2nd, etc.)
- Applies Myers algorithm to character pairs
- Outputs `? <old_ranges> | <new_ranges>` after each paired `+` line
- Range format: `start-end` (end exclusive), merged adjacent ranges

### Character Ranges (get_char_ranges)
- Converts bytes to Unicode code points
- Runs Myers diff on character sequences
- Formats as comma-separated ranges (e.g., `3-5,9-12`)
- Uses `.` for no changes on one side

## Performance Optimizations

1. **O(ND) not O(NM)**: Uses Myers' algorithm, not classic DP
2. **No list insertions**: Avoids `list.insert(0, ...)` in Python
3. **Efficient data structures**: Dictionary for V array (sparse storage)
4. **Snake extension**: Greedy diagonal following reduces iterations

## Edge Cases Handled

- Empty files (no output)
- Identical files (all keep lines)
- Files that can't be read (exit code 2, error on stderr)
- Non-UTF-8 bytes (Part A only)
- Unpaired lines in change blocks (no `?` line)
- Emojis and multi-byte Unicode (correct code point counting)

## Project Structure

```
myers-diff-algorithm/
├── src/
│   └── main.py          # Complete implementation
├── samples/
│   ├── paper_old.txt    # Myers paper example (old)
│   ├── paper_new.txt    # Myers paper example (new)
│   ├── config_old.txt   # Config file example (old)
│   ├── config_new.txt   # Config file example (new)
│   ├── unicode_old.txt  # Unicode/emoji test (old)
│   └── unicode_new.txt  # Unicode/emoji test (new)
├── myers.toml           # Language configuration (Python)
├── .gitignore
└── test_runner.py       # Test suite
```

## Testing

Run the test suite:
```bash
python test_runner.py
```

Or test individual samples:
```bash
python src/main.py lines samples/paper_old.txt samples/paper_new.txt
python src/main.py highlight samples/config_old.txt samples/config_new.txt
```

## Exit Codes

- `0`: Success
- `2`: Cannot read file A or B (error message on stderr)

## Grading Criteria

- **Part A (40 marks)**: Minimal line diff, correct output format
- **Part B (20 marks)**: Character-level highlighting
- **Code Exam (40 marks)**: Understanding of implementation

## References

- Eugene W. Myers, "An O(ND) Difference Algorithm and Its Variations", *Algorithmica* (1986)
- Used by Git's default diff algorithm

## Author

Implemented for CPS Assignment 1, Semester 5, 2026-27
