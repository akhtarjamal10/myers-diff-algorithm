# Implementation Complete - Myers Diff Algorithm

## ✅ What Has Been Implemented

### Part A: Line Diff (40 marks)
- ✅ Myers' O(ND) algorithm implemented correctly
- ✅ Reads files as raw bytes (`rb` mode)
- ✅ Handles line splitting on `\n` with proper edge cases
- ✅ Delete-first rule in change blocks
- ✅ Correct output format with ` `, `-`, `+` prefixes
- ✅ Exit code 2 for file read errors

### Part B: Character Highlighting (20 marks)
- ✅ Character-level diff using Myers algorithm
- ✅ Proper pairing of deleted/inserted lines
- ✅ Range format: `start-end` (end exclusive)
- ✅ Unicode code point counting (emojis = 1 character)
- ✅ Range merging for adjacent positions
- ✅ `? old_ranges | new_ranges` format

## 🎯 Test Results

All sample tests pass:

1. **paper_old.txt → paper_new.txt**: 5 edits (minimal) ✅
2. **config_old.txt → config_new.txt**: Correct port/debug changes ✅
3. **unicode_old.txt → unicode_new.txt**: Unicode and emoji handling ✅

Edge cases tested:
- Empty files ✅
- Identical files ✅
- Non-existent files (exit code 2) ✅

## 📊 Implementation Details

**Total Implementation**: 254 lines in `src/main.py`

**Key Functions**:
1. `read_file_lines()` - File reading with byte handling
2. `myers_diff()` - Core O(ND) algorithm
3. `backtrack()` - Reconstructs edit script
4. `format_lines_output()` - Part A formatting
5. `format_highlight_output()` - Part B formatting
6. `get_char_ranges()` - Character diff ranges
7. `bytes_to_codepoints()` - Unicode handling

## 📝 Next Steps (Follow the cpsdiff guide)

### 1. Test Locally (Unlimited)
```bash
cpsdiff test
```
This runs public tests on your laptop. It's free and unlimited.

### 2. Submit for Grading
```bash
cpsdiff submit
```
This submits your code for grading (counts against your allowance).

### 3. Check Status
```bash
cpsdiff status
```
Shows latest result, remaining submissions, and deadline.

### 4. Keep Iterating
```bash
# Make changes to src/main.py
git add src/main.py
git commit -m "Your change description"
git push
cpsdiff submit
```

## ⚠️ Important Notes

1. **cpsdiff tool required**: Make sure you have installed cpsdiff and logged in:
   ```bash
   cpsdiff --version
   cpsdiff login su-xxxxx
   ```

2. **Deadline**: Tuesday, October 6, 2026, 20:00 IST (in ~2 days)

3. **Performance**: The implementation uses O(ND) algorithm which should handle files up to 500,000 lines within the time limits.

4. **Code Exam (40 marks)**: 
   - Before the exam, make your repository public on GitHub
   - Be prepared to explain:
     - How the V array works
     - Snake extension logic
     - The backtracking process
     - Time complexity analysis

## 🔍 Quick Verification

Run these commands to verify everything works:

```bash
# Test Part A
python src/main.py lines samples/paper_old.txt samples/paper_new.txt
python src/main.py lines samples/config_old.txt samples/config_new.txt

# Test Part B
python src/main.py highlight samples/config_old.txt samples/config_new.txt
python src/main.py highlight samples/unicode_old.txt samples/unicode_new.txt

# Test error handling
python src/main.py lines nonexistent.txt samples/config_old.txt
# Should print error and exit with code 2
```

## 📚 Algorithm Explanation

### Myers' O(ND) Algorithm
The algorithm works by:

1. **V Array**: For each diagonal k, stores the furthest x-coordinate reached
2. **D iterations**: Tries edit distances from 0 to max_d
3. **Snake extension**: Follows matching diagonals greedily
4. **Trace**: Records V array history for backtracking
5. **Backtrack**: Reconstructs the edit script by walking back through trace

### Why O(ND) not O(NM)?
- Traditional DP: O(N×M) time and space
- Myers: O((N+M)×D) where D is the actual edit distance
- For similar files, D << N+M, making it much faster

## 🎓 Understanding Your Code (For the Exam)

Key concepts to understand:

1. **What is a k-diagonal?** 
   - k = x - y, represents a diagonal in the edit graph
   
2. **What is a snake?**
   - A sequence of matching elements on a diagonal
   
3. **Why do we extend snakes greedily?**
   - Maximizes progress without increasing edit distance
   
4. **How does backtracking work?**
   - Walks backwards through trace to reconstruct the path
   
5. **Delete-first rule?**
   - In change blocks, output all `-` lines before any `+` line

## 🚀 Files Created

- `src/main.py` - Complete implementation (modified)
- `README.md` - Project documentation (new)
- `test_runner.py` - Test suite (new)

All files have been committed and pushed to GitHub.

## 📞 Support

If you encounter issues:
- Email: prateek@sitare.org
- Check the cpsdiff guide for detailed instructions
- Review the assignment PDF for requirements

---

**Status**: Implementation complete and tested ✅  
**Committed**: Yes (commit fa6899b)  
**Pushed**: Yes  
**Ready for**: cpsdiff test and cpsdiff submit
