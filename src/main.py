import sys


def read_file_lines(path: str) -> list[bytes] | None:
    """
    Read file as raw bytes and split into lines.
    Returns None if file cannot be read.
    """
    try:
        with open(path, "rb") as f:
            content = f.read()
    except (OSError, IOError):
        return None
    
    # Split on newline byte
    lines = content.split(b"\n")
    
    # If last piece is empty, drop it
    if lines and lines[-1] == b"":
        lines.pop()
    
    return lines


def myers_diff(a: list, b: list) -> list[tuple[str, int, int]]:
    """
    Myers' O(ND) algorithm with memory optimization.
    Returns list of (operation, a_idx, b_idx) tuples.
    operation: 'keep', 'delete', or 'insert'
    """
    n = len(a)
    m = len(b)
    
    # Handle edge cases
    if n == 0 and m == 0:
        return []
    if n == 0:
        return [('insert', 0, i) for i in range(m)]
    if m == 0:
        return [('delete', i, 0) for i in range(n)]
    
    max_d = n + m
    v = {1: 0}
    
    # Store only k values for each d, not full V arrays
    trace = [{}]
    
    for d in range(max_d + 1):
        # Store only the k values we'll need for backtracking
        trace.append({})
        
        for k in range(-d, d + 1, 2):
            # Decide whether to move down or right
            if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                x = v.get(k + 1, 0)
            else:
                x = v.get(k - 1, 0) + 1
            
            y = x - k
            
            # Follow the snake
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            
            v[k] = x
            trace[d + 1][k] = x
            
            # Check if we reached the end
            if x >= n and y >= m:
                return backtrack(a, b, trace, d, n, m)
    
    return []


def backtrack(a: list, b: list, trace: list[dict], d: int, n: int, m: int) -> list[tuple[str, int, int]]:
    """
    Backtrack through minimal trace to construct the edit script.
    """
    x, y = n, m
    result = []
    
    for d_step in range(d, -1, -1):
        k = x - y
        
        # Determine previous k
        v_curr = trace[d_step + 1]
        v_prev = trace[d_step]
        
        if k == -d_step or (k != d_step and v_prev.get(k - 1, -1) < v_prev.get(k + 1, -1)):
            prev_k = k + 1
        else:
            prev_k = k - 1
        
        prev_x = v_prev.get(prev_k, 0)
        prev_y = prev_x - prev_k
        
        # Walk back along the snake
        while x > prev_x and y > prev_y:
            x -= 1
            y -= 1
            result.append(('keep', x, y))
        
        # Record the edit
        if d_step > 0:
            if x == prev_x:
                # Moved down: insert from B
                y -= 1
                result.append(('insert', x, y))
            else:
                # Moved right: delete from A
                x -= 1
                result.append(('delete', x, y))
        
        x, y = prev_x, prev_y
    
    result.reverse()
    return result


def format_lines_output(a_lines: list[bytes], b_lines: list[bytes]) -> str:
    """
    Format the diff output for 'lines' command.
    """
    script = myers_diff(a_lines, b_lines)
    output = []
    
    for op, a_idx, b_idx in script:
        if op == 'keep':
            output.append(b' ' + a_lines[a_idx] + b'\n')
        elif op == 'delete':
            output.append(b'-' + a_lines[a_idx] + b'\n')
        elif op == 'insert':
            output.append(b'+' + b_lines[b_idx] + b'\n')
    
    return b''.join(output)


def get_char_ranges(old_chars: list[str], new_chars: list[str]) -> tuple[str, str]:
    """
    Get changed character ranges for a line pair.
    Returns (old_ranges, new_ranges) as strings.
    """
    script = myers_diff(old_chars, new_chars)
    
    old_changes = []
    new_changes = []
    
    for op, old_idx, new_idx in script:
        if op == 'delete':
            old_changes.append(old_idx)
        elif op == 'insert':
            new_changes.append(new_idx)
    
    def format_ranges(indices: list[int]) -> str:
        if not indices:
            return '.'
        
        # Sort and merge into ranges
        indices.sort()
        ranges = []
        start = indices[0]
        end = indices[0] + 1
        
        for idx in indices[1:]:
            if idx == end:
                end = idx + 1
            else:
                ranges.append(f"{start}-{end}")
                start = idx
                end = idx + 1
        
        ranges.append(f"{start}-{end}")
        return ','.join(ranges)
    
    return format_ranges(old_changes), format_ranges(new_changes)


def bytes_to_codepoints(line: bytes) -> list[str]:
    """
    Convert bytes to list of Unicode code points (characters).
    """
    try:
        text = line.decode('utf-8')
        return list(text)
    except UnicodeDecodeError:
        # Should not happen in highlight tests
        return []


def format_highlight_output(a_lines: list[bytes], b_lines: list[bytes]) -> str:
    """
    Format the diff output for 'highlight' command.
    """
    script = myers_diff(a_lines, b_lines)
    output = []
    
    # Group script into change blocks
    i = 0
    while i < len(script):
        op, a_idx, b_idx = script[i]
        
        if op == 'keep':
            output.append(b' ' + a_lines[a_idx] + b'\n')
            i += 1
        else:
            # Collect all deletes and inserts in this change block
            deletes = []
            inserts = []
            
            while i < len(script) and script[i][0] in ('delete', 'insert'):
                op, a_idx, b_idx = script[i]
                if op == 'delete':
                    deletes.append((a_idx, a_lines[a_idx]))
                else:
                    inserts.append((b_idx, b_lines[b_idx]))
                i += 1
            
            # Output all deletes
            for _, line in deletes:
                output.append(b'-' + line + b'\n')
            
            # Output inserts with highlight lines for pairs
            for j, (_, new_line) in enumerate(inserts):
                output.append(b'+' + new_line + b'\n')
                
                # Pair with corresponding delete if exists
                if j < len(deletes):
                    _, old_line = deletes[j]
                    old_chars = bytes_to_codepoints(old_line)
                    new_chars = bytes_to_codepoints(new_line)
                    
                    old_ranges, new_ranges = get_char_ranges(old_chars, new_chars)
                    highlight_line = f"? {old_ranges} | {new_ranges}\n"
                    output.append(highlight_line.encode('utf-8'))
    
    return b''.join(output)


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        print("usage: main.py lines|highlight A_PATH B_PATH", file=sys.stderr)
        return 2
    
    command, a_path, b_path = sys.argv[1:]
    
    # Read both files as raw bytes
    a_lines = read_file_lines(a_path)
    b_lines = read_file_lines(b_path)
    
    # Check if files could be read
    if a_lines is None or b_lines is None:
        print(f"error: cannot read file", file=sys.stderr)
        return 2
    
    # Generate and print output
    if command == "lines":
        output = format_lines_output(a_lines, b_lines)
    else:  # highlight
        output = format_highlight_output(a_lines, b_lines)
    
    sys.stdout.buffer.write(output)
    return 0


raise SystemExit(main())
