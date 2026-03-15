"""
bmp2hex.py — Convert a BMP image file to a hex string.

Usage:
    python bmp2hex.py input.bmp [output.txt]
"""

import sys

def format_bytes(bytes: float, precision: int = 2) -> str:
    units = ["Bytes", "kB", "MB", "GB", "TB", "PB"]
    cur_unit = 0
    while bytes >= 1024 and cur_unit < len(units) - 1:
        bytes /= 1024
        cur_unit += 1
    return f"{round(bytes, precision)}{units[cur_unit]}"

def bmp_to_hex(input_path:str, output_path:str = None):
    with open(input_path, "rb") as f:
        data = f.read()

    # Validate BMP signature
    if data[:2] != b"BM":
        raise ValueError("Not a valid BMP file (missing 'BM' signature).")

    hex_string = data.hex()
    hex_string = hex_string.upper()

    len_hex = len(hex_string)
    print(f"Hex length: {len_hex} characters ({format_bytes(len_hex // 2)})")

    if output_path:
        with open(output_path, "w") as f:
            f.write(hex_string)
        print(f"Saved: {output_path}")
    else:
        print(f"\nHex output:\n{hex_string}")

    return hex_string


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    positional = [a for a in args if not a.startswith("--")]

    if len(positional) < 1:
        print("Error: input BMP file required.")
        print("Usage: python bmp2hex.py input.bmp [output.txt]")
        sys.exit(1)

    input_path  = positional[0]
    output_path = positional[1] if len(positional) >= 2 else None

    bmp_to_hex(input_path, output_path)

if __name__ == "__main__":
    main()