import sys  # Provides command-line arguments and standard input/output streams.


def read_lines(path):  # Loads one file into the byte lines used by the comparison.
    """Read a file as byte lines, preserving its original contents."""
    with open(path, "rb") as f:  # Binary mode preserves exact bytes, including unusual text.
        lines = f.read().split(b"\n")  # Split on newline bytes so each item represents one line.
    if lines and not lines[-1]:  # A final newline creates an empty split item, not an extra line.
        lines.pop()  # Remove only that artificial item; leave real empty lines intact.
    return lines  # Give the diff algorithm the file's lines without decoding them.


def middle_snake(A, B, Ar, Br, n, m):  # Finds a central match that divides a difficult comparison.
    """Find the middle matching run used to split a diff problem in half."""
    delta, odd = n - m, (n - m) & 1  # Track length imbalance and which search reaches the midpoint first.
    max_d = (n + m + 1) // 2  # No shortest path can need more edits than roughly half the combined length.
    offset, size = max_d + 1, 2 * max_d + 3  # Shift diagonal indexes so negative diagonals fit in arrays.
    vf = [-1] * size  # Store the farthest position reached by the forward search on each diagonal.
    vb = [-1] * size  # Store the farthest position reached by the backward search on each diagonal.
    vf[offset + 1] = vb[offset + 1] = 0  # Seed both searches just before their first diagonal step.
    fs = fe = bs = be = 0  # Track diagonals already known to run beyond each search boundary.

    for d in range(max_d + 1):  # Increase the allowed edit count until the searches meet.
        for k in range(-d + fs, d - fe + 1, 2):  # Extend forward paths across reachable diagonals at this edit count.
            idx = offset + k  # Convert the diagonal number into a valid array index.
            x = vf[idx + 1] if k == -d or (k != d and vf[idx - 1] < vf[idx + 1]) else vf[idx - 1] + 1  # Choose the prior path that reaches farther with one edit.
            y, x0, y0 = x - k, x, x - k  # Convert diagonal position to B's coordinate and remember the run's start.
            while x < n and y < m and A[x] == B[y]:  # Follow equal items without spending another edit.
                x += 1  # Advance through the matching run in A.
                y += 1  # Keep both sequence positions aligned through the match.
            vf[idx] = x  # Save the farthest forward position for this diagonal.
            if x > n:  # This path passed A's active boundary.
                fe += 2  # Exclude this diagonal and its parity-equivalent neighbor from later searches.
                continue  # No overlap check is useful for a path outside the active region.
            if y > m:  # This path passed B's active boundary.
                fs += 2  # Exclude this diagonal and its parity-equivalent neighbor from later searches.
                continue  # Continue with the next forward path.
            if odd:  # For odd length difference, forward paths can meet the previous backward layer.
                kb = delta - k  # Translate this forward diagonal to its matching backward diagonal.
                if -d < kb < d:  # Check only backward diagonals already reached in the prior layer.
                    xb = vb[offset + kb]  # Read how far the backward search reached on that diagonal.
                    if xb != -1 and x + xb >= n:  # The paths overlap when their combined progress spans A.
                        return x0, y0, x, y  # Return the forward matching run that splits the problem.

        for k in range(-d + bs, d - be + 1, 2):  # Extend backward paths over the reversed sequences.
            idx = offset + k  # Map this backward diagonal into the frontier array.
            x = vb[idx + 1] if k == -d or (k != d and vb[idx - 1] < vb[idx + 1]) else vb[idx - 1] + 1  # Choose the farther-reaching prior backward path.
            y, x0, y0 = x - k, x, x - k  # Derive the second coordinate and remember where this match begins.
            while x < n and y < m and Ar[x] == Br[y]:  # Consume equal items while moving from the ends toward the start.
                x += 1  # Move farther through reversed A.
                y += 1  # Keep the reversed sequences aligned.
            vb[idx] = x  # Save the farthest backward position on this diagonal.
            if x > n:  # This backward path passed A's reverse boundary.
                be += 2  # Stop exploring this diagonal and its paired diagonal.
                continue  # Try another backward path instead.
            if y > m:  # This backward path passed B's reverse boundary.
                bs += 2  # Stop exploring this diagonal and its paired diagonal.
                continue  # Continue searching other diagonals.
            if not odd:  # For even length difference, check overlap against the current forward layer.
                kf = delta - k  # Translate the backward diagonal to its forward counterpart.
                if -d <= kf <= d:  # Only compare against forward diagonals reached in this layer.
                    xf = vf[offset + kf]  # Read forward progress on the matching diagonal.
                    if xf != -1 and xf + x >= n:  # The searches meet once their progress covers A.
                        return n - x, m - y, n - x0, m - y0  # Convert the reverse match back to forward coordinates.

    raise RuntimeError("middle snake not found")  # Signal that no valid split was found for this subproblem.


def diff_marks(a, b):  # Computes which source lines are removed and which target lines are added.
    """Mark which input lines are deleted or inserted by a shortest diff."""
    ids, ia, ib = {}, [], []  # Map each distinct line to an integer and store both sequences as integers.
    for item in a:  # Assign IDs to lines in the original file.
        if item not in ids:  # Reuse an existing ID for repeated identical lines.
            ids[item] = len(ids)  # Give each new line a compact ID for fast equality checks.
        ia.append(ids[item])  # Preserve the original sequence using those IDs.
    for item in b:  # Assign IDs to lines in the new file, sharing the same mapping.
        if item not in ids:  # A shared mapping makes identical lines equal across files.
            ids[item] = len(ids)  # Record a new ID only for a line not seen in either file.
        ib.append(ids[item])  # Preserve the new sequence using those IDs.

    in_a, in_b = set(ia), set(ib)  # Find line IDs that appear in each file.
    ma = [i for i, v in enumerate(ia) if v in in_b]  # Keep original positions whose lines could match the new file.
    mb = [i for i, v in enumerate(ib) if v in in_a]  # Keep new-file positions whose lines could match the original.
    fa, fb = [ia[i] for i in ma], [ib[i] for i in mb]  # Build shorter sequences containing only possible matches.
    del_f, ins_f = bytearray(len(fa)), bytearray(len(fb))  # Zero means unchanged; one will mean deleted or inserted.
    stack = [(0, len(fa), 0, len(fb))]  # Begin with one pending comparison covering both filtered sequences.

    while stack:  # Resolve each pending range without recursive Python calls.
        a0, a1, b0, b1 = stack.pop()  # Take one original/new range pair from the work stack.
        while a0 < a1 and b0 < b1 and fa[a0] == fb[b0]:  # Skip the shared prefix already known to match.
            a0 += 1  # Move the original range past this equal line.
            b0 += 1  # Move the new range past the same equal line.
        while a0 < a1 and b0 < b1 and fa[a1 - 1] == fb[b1 - 1]:  # Skip the shared suffix before solving the middle.
            a1 -= 1  # Narrow the original range from its end.
            b1 -= 1  # Narrow the new range from its end.

        if a0 == a1:  # Nothing remains in the original range, so all remaining new lines are additions.
            ins_f[b0:b1] = b"\x01" * (b1 - b0)  # Mark every unmatched new line as inserted.
            continue  # This subproblem is complete; process the next pending range.
        if b0 == b1:  # Nothing remains in the new range, so all remaining original lines are removals.
            del_f[a0:a1] = b"\x01" * (a1 - a0)  # Mark every unmatched original line as deleted.
            continue  # This subproblem is complete; process the next pending range.

        A, B = fa[a0:a1], fb[b0:b1]  # Copy the unmatched middle ranges that still need comparison.
        n, m = a1 - a0, b1 - b0  # Record the active lengths before adding boundary markers.
        Ar, Br = A[::-1], B[::-1]  # Reverse copies let the search grow inward from the ends too.
        A.append(-1)  # Add a marker outside the valid IDs for the search's bounded sequence representation.
        B.append(-2)  # Use a different marker so it cannot appear equal to A's marker.
        Ar.append(-1)  # Keep the reversed A sequence's boundary representation consistent.
        Br.append(-2)  # Keep the reversed B sequence's boundary representation consistent.
        sx, sy, ex, ey = middle_snake(A, B, Ar, Br, n, m)  # Locate a middle match that partitions this range.
        stack.append((a0 + ex, a1, b0 + ey, b1))  # Queue the portion after the matching run.
        stack.append((a0, a0 + sx, b0, b0 + sy))  # Queue the portion before it; the run itself is unchanged.

    del_a, ins_b = bytearray(b"\x01") * len(a), bytearray(b"\x01") * len(b)  # Initially treat every input line as changed.
    for fi, oi in enumerate(ma):  # Map filtered original positions back to their source-file positions.
        del_a[oi] = del_f[fi]  # Clear positions found unchanged and retain deletion marks for changed ones.
    for fi, oi in enumerate(mb):  # Map filtered new-file positions back to their original locations.
        ins_b[oi] = ins_f[fi]  # Clear unchanged positions and keep insertion marks where needed.
    return del_a, ins_b  # Return parallel flags that identify deletions and insertions in the full files.


def ranges(marks):  # Turns character-change flags into compact position ranges.
    """Format consecutive marked positions as comma-separated ranges."""
    parts, start = [], marks.find(1)  # Start at the first changed position and collect each run.
    while start != -1:  # Continue until no more changed positions exist.
        end = marks.find(0, start)  # Find where this consecutive changed run ends.
        if end == -1:  # A missing zero means the changed run reaches the end.
            end = len(marks)  # Use the sequence length as the exclusive end position.
        parts.append(f"{start}-{end}")  # Store this run as a start-inclusive, end-exclusive range.
        if end >= len(marks):  # There cannot be another run after the final position.
            break  # Avoid searching past the end of the flags.
        start = marks.find(1, end)  # Search for the next changed run after this one.
    return ",".join(parts) or "."  # Join runs, or use a dot to indicate no changed characters.


def build_output(a, b, del_a, ins_b, highlight):  # Formats the flags as a readable line-based diff.
    """Combine change marks into diff lines, optionally showing within-line changes."""
    out, i, j = [], 0, 0  # Collect output lines and track positions in the old and new files.
    na, nb = len(a), len(b)  # Cache both lengths to detect when a file's remaining lines are exhausted.

    while True:  # Walk from one changed region to the next until neither file has changes left.
        nd, ni = del_a.find(1, i), ins_b.find(1, j)  # Find the next deletion and insertion positions.
        if nd == ni == -1:  # No marked positions remain in either file.
            break  # Finish the main loop and append any trailing unchanged lines.

        count = na - i  # Start with all remaining original lines as a possible unchanged span.
        if nd != -1:  # A deletion marks the end of unchanged content in the original file.
            count = min(count, nd - i)  # Stop the span before that deletion.
        if ni != -1:  # An insertion also ends the unchanged span in the new file.
            count = min(count, ni - j)  # Keep old and new positions synchronized before the change.
        if count:  # Emit unchanged lines only when at least one lies before the next change.
            out.extend(b" " + line for line in a[i:i + count])  # Prefix context lines with a space marker.
            i += count  # Advance the original-file cursor past emitted context.
            j += count  # Advance the new-file cursor by the same amount.

        de = del_a.find(0, i)  # Find where the current run of deletions ends.
        ie = ins_b.find(0, j)  # Find where the current run of insertions ends.
        de = na if de == -1 else de  # Treat an unfinished deletion run as ending at the file boundary.
        ie = nb if ie == -1 else ie  # Treat an unfinished insertion run as ending at the file boundary.
        deleted, inserted = a[i:de], b[j:ie]  # Extract both sides of this changed block.
        out.extend(b"-" + line for line in deleted)  # Show removed lines with the diff deletion marker.

        if not highlight:  # Basic mode does not need character-level details.
            out.extend(b"+" + line for line in inserted)  # Show each added line with the diff insertion marker.
        else:  # Highlight mode also reports character positions for paired replacements.
            for k, line in enumerate(inserted):  # Emit new lines and compare each with the corresponding old line.
                out.append(b"+" + line)  # Preserve the added line in the diff output.
                if k < min(len(deleted), len(inserted)):  # Only compare pairs when both sides have a line.
                    old = deleted[k].decode("utf-8", "surrogateescape")  # Decode safely for character-level comparison.
                    new = line.decode("utf-8", "surrogateescape")  # Decode the matching new line using the same policy.
                    dm, im = diff_marks(old, new)  # Reuse the diff algorithm to locate changed characters.
                    out.append(f"? {ranges(dm)} | {ranges(im)}".encode("utf-8"))  # Add old/new character ranges below the replacement.

        i, j = de, ie  # Resume both files immediately after this changed block.

    if i < na:  # Any original lines left now have no corresponding changes.
        out.extend(b" " + line for line in a[i:])  # Emit the remaining original lines as context.
    return out  # Give the caller complete output lines ready to write.


def main():  # Connects command-line options to file reading, diffing, and output.
    """Validate arguments, compare the files, and write the selected diff format."""
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):  # Require a mode and two file paths.
        print("usage: main.py lines|highlight A_PATH B_PATH", file=sys.stderr)  # Explain the accepted command format.
        return 2  # Use a nonzero status to signal invalid command-line input.
    try:  # File access can fail, so handle those errors cleanly for the user.
        a, b = read_lines(sys.argv[2]), read_lines(sys.argv[3])  # Load the original and updated files as byte lines.
    except OSError as exc:  # Catch missing files and other operating-system read errors.
        print(f"error: cannot read file: {exc}", file=sys.stderr)  # Report the cause on the error stream.
        return 2  # Signal that the requested comparison could not be performed.

    output = build_output(a, b, *diff_marks(a, b), sys.argv[1] == "highlight")  # Compute line marks and format the requested diff mode.
    if output:  # Avoid writing a newline when the comparison produces no output.
        sys.stdout.buffer.write(b"\n".join(output) + b"\n")  # Write bytes directly so file content remains intact.
        sys.stdout.buffer.flush()  # Ensure the diff is sent to the terminal or redirected output promptly.
    return 0  # Report successful completion, including when files are identical.


if __name__ == "__main__":  # Run the CLI only when this file is launched directly.
    raise SystemExit(main())  # Return main's status code to the operating system.