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
    Myers' O(ND) algorithm with linear space.
    Uses divide-and-conquer to avoid storing full trace.
    Returns list of (operation, a_idx, b_idx) tuples.
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
    
    # For small inputs, use simple approach
    if n + m < 100:
        return myers_with_trace(a, b, n, m)
    
    # Use middle-snake divide and conquer for large inputs
    return linear_space_myers(a, b, 0, n, 0, m)


def myers_with_trace(a: list, b: list, n: int, m: int) -> list[tuple[str, int, int]]:
    """Myers with trace for small inputs."""
    max_d = n + m
    v = {1: 0}
    trace = [{}]
    
    for d in range(max_d + 1):
        trace.append({})
        
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                x = v.get(k + 1, 0)
            else:
                x = v.get(k - 1, 0) + 1
            
            y = x - k
            
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            
            v[k] = x
            trace[d + 1][k] = x
            
            if x >= n and y >= m:
                return backtrack_simple(trace, d, n, m)
    
    return []


def backtrack_simple(trace: list[dict], d: int, n: int, m: int) -> list[tuple[str, int, int]]:
    """Backtrack for small inputs."""
    x, y = n, m
    result = []
    
    for d_step in range(d, -1, -1):
        k = x - y
        v_prev = trace[d_step]
        
        if k == -d_step or (k != d_step and v_prev.get(k - 1, -1) < v_prev.get(k + 1, -1)):
            prev_k = k + 1
        else:
            prev_k = k - 1
        
        prev_x = v_prev.get(prev_k, 0)
        prev_y = prev_x - prev_k
        
        while x > prev_x and y > prev_y:
            x -= 1
            y -= 1
            result.append(('keep', x, y))
        
        if d_step > 0:
            if x == prev_x:
                y -= 1
                result.append(('insert', x, y))
            else:
                x -= 1
                result.append(('delete', x, y))
        
        x, y = prev_x, prev_y
    
    result.reverse()
    return result


def linear_space_myers(a: list, b: list, a_start: int, a_end: int, b_start: int, b_end: int) -> list[tuple[str, int, int]]:
    """
    Linear space Myers using middle-snake divide-and-conquer.
    """
    n = a_end - a_start
    m = b_end - b_start
    
    if n == 0 and m == 0:
        return []
    if n == 0:
        return [('insert', a_start, b_start + i) for i in range(m)]
    if m == 0:
        return [('delete', a_start + i, b_start) for i in range(n)]
    
    # Find middle snake
    snake = find_middle_snake(a, b, a_start, a_end, b_start, b_end)
    if snake is None:
        # Fallback for very small
        if n == 1 and m == 1:
            if a[a_start] == b[b_start]:
                return [('keep', a_start, b_start)]
            else:
                return [('delete', a_start, b_start), ('insert', a_start, b_start)]
        return myers_with_trace(a[a_start:a_end], b[b_start:b_end], n, m)
    
    x_start, x_end, y_start, y_end = snake
    
    # Recursively solve sub-problems
    result = []
    result.extend(linear_space_myers(a, b, a_start, x_start, b_start, y_start))
    
    # Add snake
    for i in range(x_end - x_start):
        result.append(('keep', x_start + i, y_start + i))
    
    result.extend(linear_space_myers(a, b, x_end, a_end, y_end, b_end))
    
    return result


def find_middle_snake(a: list, b: list, a_start: int, a_end: int, b_start: int, b_end: int):
    """
    Find the middle snake using forward and backward search.
    Returns (x_start, x_end, y_start, y_end) of the snake.
    """
    n = a_end - a_start
    m = b_end - b_start
    delta = n - m
    odd = delta % 2 == 1
    
    max_d = (n + m + 1) // 2 + 1
    
    v_forward = {1: 0}
    v_backward = {1: 0}
    
    for d in range(max_d + 1):
        # Forward search
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v_forward.get(k - 1, -1) < v_forward.get(k + 1, -1)):
                x = v_forward.get(k + 1, 0)
            else:
                x = v_forward.get(k - 1, 0) + 1
            
            y = x - k
            x_start_snake = x
            
            while x < n and y < m and a[a_start + x] == b[b_start + y]:
                x += 1
                y += 1
            
            v_forward[k] = x
            
            # Check for overlap
            if odd and k >= delta - d + 1 and k <= delta + d - 1:
                if x + v_backward.get(delta - k, -1) >= n:
                    return (a_start + x_start_snake, a_start + x, 
                            b_start + x_start_snake - k, b_start + y)
        
        # Backward search
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v_backward.get(k - 1, -1) < v_backward.get(k + 1, -1)):
                x = v_backward.get(k + 1, 0)
            else:
                x = v_backward.get(k - 1, 0) + 1
            
            y = x - k
            x_start_snake = x
            
            while x < n and y < m and a[a_end - 1 - x] == b[b_end - 1 - y]:
                x += 1
                y += 1
            
            v_backward[k] = x
            
            # Check for overlap
            if not odd and k + delta >= -d and k + delta <= d:
                if x + v_forward.get(k + delta, -1) >= n:
                    return (a_end - x, a_end - x_start_snake,
                            b_end - y, b_end - x_start_snake + k)
    
    return None


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
