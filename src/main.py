import sys


def read_lines(path):
    with open(path, "rb") as f:
        lines = f.read().split(b"\n")
    if lines and not lines[-1]:
        lines.pop()
    return lines


def middle_snake(A, B, Ar, Br, n, m):
    delta, odd = n - m, (n - m) & 1
    max_d = (n + m + 1) // 2
    offset, size = max_d + 1, 2 * max_d + 3
    vf = [-1] * size
    vb = [-1] * size
    vf[offset + 1] = vb[offset + 1] = 0
    fs = fe = bs = be = 0

    for d in range(max_d + 1):
        for k in range(-d + fs, d - fe + 1, 2):
            idx = offset + k
            x = vf[idx + 1] if k == -d or (k != d and vf[idx - 1] < vf[idx + 1]) else vf[idx - 1] + 1
            y, x0, y0 = x - k, x, x - k
            while x < n and y < m and A[x] == B[y]:
                x += 1
                y += 1
            vf[idx] = x
            if x > n:
                fe += 2
                continue
            if y > m:
                fs += 2
                continue
            if odd:
                kb = delta - k
                if -d < kb < d:
                    xb = vb[offset + kb]
                    if xb != -1 and x + xb >= n:
                        return x0, y0, x, y

        for k in range(-d + bs, d - be + 1, 2):
            idx = offset + k
            x = vb[idx + 1] if k == -d or (k != d and vb[idx - 1] < vb[idx + 1]) else vb[idx - 1] + 1
            y, x0, y0 = x - k, x, x - k
            while x < n and y < m and Ar[x] == Br[y]:
                x += 1
                y += 1
            vb[idx] = x
            if x > n:
                be += 2
                continue
            if y > m:
                bs += 2
                continue
            if not odd:
                kf = delta - k
                if -d <= kf <= d:
                    xf = vf[offset + kf]
                    if xf != -1 and xf + x >= n:
                        return n - x, m - y, n - x0, m - y0

    raise RuntimeError("middle snake not found")


def diff_marks(a, b):
    ids, ia, ib = {}, [], []
    for item in a:
        if item not in ids:
            ids[item] = len(ids)
        ia.append(ids[item])
    for item in b:
        if item not in ids:
            ids[item] = len(ids)
        ib.append(ids[item])

    in_a, in_b = set(ia), set(ib)
    ma = [i for i, v in enumerate(ia) if v in in_b]
    mb = [i for i, v in enumerate(ib) if v in in_a]
    fa, fb = [ia[i] for i in ma], [ib[i] for i in mb]
    del_f, ins_f = bytearray(len(fa)), bytearray(len(fb))
    stack = [(0, len(fa), 0, len(fb))]

    while stack:
        a0, a1, b0, b1 = stack.pop()
        while a0 < a1 and b0 < b1 and fa[a0] == fb[b0]:
            a0 += 1
            b0 += 1
        while a0 < a1 and b0 < b1 and fa[a1 - 1] == fb[b1 - 1]:
            a1 -= 1
            b1 -= 1

        if a0 == a1:
            ins_f[b0:b1] = b"\x01" * (b1 - b0)
            continue
        if b0 == b1:
            del_f[a0:a1] = b"\x01" * (a1 - a0)
            continue

        A, B = fa[a0:a1], fb[b0:b1]
        n, m = a1 - a0, b1 - b0
        Ar, Br = A[::-1], B[::-1]
        A.append(-1)
        B.append(-2)
        Ar.append(-1)
        Br.append(-2)
        sx, sy, ex, ey = middle_snake(A, B, Ar, Br, n, m)
        stack.append((a0 + ex, a1, b0 + ey, b1))
        stack.append((a0, a0 + sx, b0, b0 + sy))

    del_a, ins_b = bytearray(b"\x01") * len(a), bytearray(b"\x01") * len(b)
    for fi, oi in enumerate(ma):
        del_a[oi] = del_f[fi]
    for fi, oi in enumerate(mb):
        ins_b[oi] = ins_f[fi]
    return del_a, ins_b


def ranges(marks):
    parts, start = [], marks.find(1)
    while start != -1:
        end = marks.find(0, start)
        if end == -1:
            end = len(marks)
        parts.append(f"{start}-{end}")
        if end >= len(marks):
            break
        start = marks.find(1, end)
    return ",".join(parts) or "."


def build_output(a, b, del_a, ins_b, highlight):
    out, i, j = [], 0, 0
    na, nb = len(a), len(b)

    while True:
        nd, ni = del_a.find(1, i), ins_b.find(1, j)
        if nd == ni == -1:
            break

        count = na - i
        if nd != -1:
            count = min(count, nd - i)
        if ni != -1:
            count = min(count, ni - j)
        if count:
            out.extend(b" " + line for line in a[i:i + count])
            i += count
            j += count

        de = del_a.find(0, i)
        ie = ins_b.find(0, j)
        de = na if de == -1 else de
        ie = nb if ie == -1 else ie
        deleted, inserted = a[i:de], b[j:ie]
        out.extend(b"-" + line for line in deleted)

        if not highlight:
            out.extend(b"+" + line for line in inserted)
        else:
            for k, line in enumerate(inserted):
                out.append(b"+" + line)
                if k < min(len(deleted), len(inserted)):
                    old = deleted[k].decode("utf-8", "surrogateescape")
                    new = line.decode("utf-8", "surrogateescape")
                    dm, im = diff_marks(old, new)
                    out.append(f"? {ranges(dm)} | {ranges(im)}".encode("utf-8"))

        i, j = de, ie

    if i < na:
        out.extend(b" " + line for line in a[i:])
    return out


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        print("usage: main.py lines|highlight A_PATH B_PATH", file=sys.stderr)
        return 2
    try:
        a, b = read_lines(sys.argv[2]), read_lines(sys.argv[3])
    except OSError as exc:
        print(f"error: cannot read file: {exc}", file=sys.stderr)
        return 2

    output = build_output(a, b, *diff_marks(a, b), sys.argv[1] == "highlight")
    if output:
        sys.stdout.buffer.write(b"\n".join(output) + b"\n")
        sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())