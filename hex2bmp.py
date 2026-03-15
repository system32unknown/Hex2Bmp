"""
hex2bmp.py — Convert a hex string to a BMP image file.

Usage:
    python hex2bmp.py input.txt output.bmp
"""

import sys
import struct
import math

def hex_to_bmp(hex_string: str, output_path: str):
    # Clean up the hex string (remove whitespace/newlines)
    hex_string = hex_string.strip().replace("\n", "").replace(" ", "")

    # Convert hex string to raw bytes
    raw_bytes = bytes.fromhex(hex_string)

    print(f"Raw data: {len(raw_bytes)} bytes")
    print(f"Hex preview: {hex_string[:64]}...")

    # --- Attempt 1: treat raw bytes as a ready-made BMP file ---
    if raw_bytes[:2] == b"BM":
        print("Detected valid BMP header — writing directly.")
        with open(output_path, "wb") as f: f.write(raw_bytes)
        print(f"Saved: {output_path}")
        return

    # --- Attempt 2: wrap raw bytes in a proper BMP envelope ---
    # Treat the data as a 1-bit-per-pixel monochrome bitmap.
    # Guess dimensions from the data length.
    data_len = len(raw_bytes)

    # Try to find width/height that fits neatly.
    # BMP rows are padded to 4-byte boundaries.
    width = height = None
    for w in range(1, 1025):
        row_bytes = (w + 31) // 32 * 4   # 1bpp row stride
        if data_len % row_bytes == 0:
            h = data_len // row_bytes
            if 1 <= h <= 1024:
                width, height = w, h
                break

    if width is None:
        # Fall back: square-ish dimensions
        side = int(math.isqrt(data_len * 8))
        width = height = side
        print(f"Warning: could not detect dimensions; using {width}×{height}")

    print(f"Dimensions: {width} x {height} px (1bpp monochrome)")

    row_stride = (width + 31) // 32 * 4
    pixel_data_size = row_stride * height

    # Pad or trim pixel data to match expected size
    pixel_data = raw_bytes.ljust(pixel_data_size, b"\x00")[:pixel_data_size]

    # BMP file header (14 bytes)
    dib_header_size = 40          # BITMAPINFOHEADER
    color_table_size = 8          # 2 colours × 4 bytes
    pixel_offset = 14 + dib_header_size + color_table_size
    file_size = pixel_offset + pixel_data_size

    bmp_file_header = struct.pack(
        "<2sIHHI",
        b"BM",           # signature
        file_size,       # total file size
        0,               # reserved
        0,               # reserved
        pixel_offset,    # offset to pixel data
    )

    # DIB header — BITMAPINFOHEADER (40 bytes)
    bmp_dib_header = struct.pack(
        "<IiiHHIIiiII",
        dib_header_size,  # header size
        width,            # width
        -height,          # negative = top-down
        1,                # colour planes
        1,                # bits per pixel (monochrome)
        0,                # compression (none)
        pixel_data_size,  # image size
        2835,             # X pixels/metre (~72 dpi)
        2835,             # Y pixels/metre
        2,                # colours in table
        2,                # important colours
    )

    # Colour table: index 0 = black, index 1 = white (standard 1bpp BMP)
    color_table = (
        struct.pack("<BBBB", 0, 0, 0, 0) +       # black
        struct.pack("<BBBB", 255, 255, 255, 0)    # white
    )

    with open(output_path, "wb") as f:
        f.write(bmp_file_header)
        f.write(bmp_dib_header)
        f.write(color_table)
        f.write(pixel_data)

    print(f"Saved: {output_path}")


def main():
    if len(sys.argv) == 3:
        input_path, output_path = sys.argv[1], sys.argv[2]
        with open(input_path) as f:
            hex_string = f.read()
    else:
        print("Usage: python hex2bmp.py [input.txt output.bmp]")
        sys.exit(1)
    hex_to_bmp(hex_string, output_path)


if __name__ == "__main__":
    main()
