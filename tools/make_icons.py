#!/usr/bin/env python3
"""Generate the extension's toolbar icons.

Build-time helper only; not shipped code. Draws a rounded dark square with a white "M",
supersampled for antialiasing, and writes RGBA PNGs with the stdlib alone.

Usage: python3 tools/make_icons.py
"""

import os
import struct
import zlib

SIZES = (16, 32, 48, 128)
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons")

BG = (31, 35, 40)         # #1f2328
FG = (255, 255, 255)
CORNER = 0.22             # radius as a fraction of the icon size
STROKE = 0.075            # half-width of the "M" strokes, fraction of the icon size
SS = 4                    # supersampling factor per axis

# "M" as thick line segments in normalised coords, y increasing downward.
SEGMENTS = (
    ((0.24, 0.24), (0.24, 0.76)),
    ((0.24, 0.24), (0.50, 0.60)),
    ((0.50, 0.60), (0.76, 0.24)),
    ((0.76, 0.24), (0.76, 0.76)),
)


def inside_rounded_square(x, y, r):
    """x, y in [0, 1]; r is the corner radius in the same units."""
    if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
        return False
    cx = r if x < r else (1.0 - r if x > 1.0 - r else x)
    cy = r if y < r else (1.0 - r if y > 1.0 - r else y)
    dx, dy = x - cx, y - cy
    return dx * dx + dy * dy <= r * r


def point_segment_distance(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    length_sq = vx * vx + vy * vy
    t = 0.0 if length_sq == 0 else max(0.0, min(1.0, (wx * vx + wy * vy) / length_sq))
    dx, dy = px - (ax + t * vx), py - (ay + t * vy)
    return (dx * dx + dy * dy) ** 0.5


def on_glyph(x, y):
    return any(
        point_segment_distance(x, y, a[0], a[1], b[0], b[1]) <= STROKE
        for a, b in SEGMENTS
    )


def render(size):
    """Return raw RGBA rows for one icon."""
    rows = []
    step = 1.0 / (size * SS)
    for py in range(size):
        row = bytearray()
        for px in range(size):
            covered = 0
            glyph = 0
            for sy in range(SS):
                y = (py * SS + sy + 0.5) * step
                for sx in range(SS):
                    x = (px * SS + sx + 0.5) * step
                    if inside_rounded_square(x, y, CORNER):
                        covered += 1
                        if on_glyph(x, y):
                            glyph += 1
            total = SS * SS
            if covered == 0:
                row += bytes((0, 0, 0, 0))
                continue
            # Blend glyph over background by subsample coverage, then apply the
            # rounded-square alpha so the corners stay smooth.
            g = glyph / covered
            colour = tuple(round(BG[i] + (FG[i] - BG[i]) * g) for i in range(3))
            row += bytes(colour) + bytes((round(255 * covered / total),))
        rows.append(bytes(row))
    return rows


def write_png(path, size, rows):
    raw = b"".join(b"\x00" + row for row in rows)  # filter type 0 per scanline

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as handle:
        handle.write(png)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for size in SIZES:
        path = os.path.join(OUT_DIR, "%d.png" % size)
        write_png(path, size, render(size))
        print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    main()
