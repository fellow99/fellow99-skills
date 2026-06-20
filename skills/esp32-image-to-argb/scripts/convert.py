#!/usr/bin/env python3
"""
ESP32 Image to C Header Converter

Converts PNG/JPG images to C source files for ESP32 projects.
Supports multiple pixel formats: RGB565, ARGB1555, ARGB8888, ARGB_4444, ALPHA_8.
Supports both TFT_eSPI (image struct) and LVGL (lv_image_dsc_t) output formats.

Usage:
    python convert.py -i image.png -o ./output -f lvgl
    python convert.py -i image.png -o ./output -f lvgl -p ARGB8888
    python convert.py -i ./assets/ -o ./output -f tft_espi -y

Before processing, the script shows a summary of inputs/outputs/parameters
and asks for confirmation. Use -y to skip confirmation (CI/automation).
"""

import argparse
import os
import re
import sys

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow (PIL) is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)

# ── Pixel Format Definitions ────────────────────────────────────────
# fmt_name: (bytes_per_pixel, has_alpha, c_type, lvgl_color_format)
#   c_type:         The C integer type used in TFT_eSPI output
#   lvgl_cf:        The LV_COLOR_FORMAT_* constant for LVGL output
#   has_alpha:      Whether the format carries an alpha channel
#   bytes_per_pixel: How many bytes each pixel occupies

PIXEL_FORMATS = {
    "RGB565":    {"bpp": 2, "has_alpha": False, "c_type": "uint16_t", "lvgl_cf": "LV_COLOR_FORMAT_RGB565"},
    "ARGB1555":  {"bpp": 2, "has_alpha": True,  "c_type": "uint16_t", "lvgl_cf": "LV_COLOR_FORMAT_ARGB1555"},
    "ARGB8888":  {"bpp": 4, "has_alpha": True,  "c_type": "uint32_t", "lvgl_cf": "LV_COLOR_FORMAT_ARGB8888"},
    "ARGB_4444": {"bpp": 2, "has_alpha": True,  "c_type": "uint16_t", "lvgl_cf": "LV_COLOR_FORMAT_ARGB4444"},
    "ALPHA_8":   {"bpp": 1, "has_alpha": True,  "c_type": "uint8_t",  "lvgl_cf": "LV_COLOR_FORMAT_A8"},
}

DEFAULT_PIXEL_FORMAT = "RGB565"

# ── Pixel Format Conversion ─────────────────────────────────────────
#
# These functions convert from 8-bit-per-channel RGBA (0-255 each)
# to the target pixel format's packed integer value.
#
# Pixel Format Bit Layouts (little-endian storage):
#
#   RGB565:
#     RRRRR GGGGGG BBBBB   (R[7:3] G[7:2] B[7:3])
#     15  11 10   5 4   0
#     LE: [GGGBBBBB][RRRRRGGG]
#
#   ARGB1555:
#     A RRRRR GGGGG BBBBB   (A:>=128→1, R[7:3] G[7:3] B[7:3])
#     15 14 10 9   5 4   0
#     LE: [GGGGGBBBBB][ARRRRRGG]
#
#   ARGB8888:
#     AAAAAAAA RRRRRRRR GGGGGGGG BBBBBBBB
#     31    24 23    16 15     8 7      0
#     LE: [BBBBBBBB][GGGGGGGG][RRRRRRRR][AAAAAAAA]
#
#   ARGB_4444:
#     AAAA RRRR GGGG BBBB   (A[7:4] R[7:4] G[7:4] B[7:4])
#     15 12 11  8 7   4 3  0
#     LE: [GGGGBBBB][AAAARRRR]
#
#   ALPHA_8:
#     AAAAAAAA   (A only, no color channels)
#     7      0
#     LE: [AAAAAAAA]
#

def rgba_to_rgb565(r: int, g: int, b: int, a: int, swap_rb: bool = False) -> int:
    """RGB888 → RGB565 (16-bit). Alpha is discarded."""
    if swap_rb:
        r, b = b, r
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def rgba_to_argb1555(r: int, g: int, b: int, a: int, swap_rb: bool = False) -> int:
    """RGBA8888 → ARGB1555 (16-bit). Alpha threshold at 128."""
    if swap_rb:
        r, b = b, r
    return ((1 if a >= 128 else 0) << 15) | ((r >> 3) << 10) | ((g >> 3) << 5) | (b >> 3)


def rgba_to_argb8888(r: int, g: int, b: int, a: int, swap_rb: bool = False) -> int:
    """RGBA8888 → ARGB8888 (32-bit). Stored as 0xAARRGGBB."""
    if swap_rb:
        r, b = b, r
    return (a << 24) | (r << 16) | (g << 8) | b


def rgba_to_argb4444(r: int, g: int, b: int, a: int, swap_rb: bool = False) -> int:
    """RGBA8888 → ARGB_4444 (16-bit). Each channel downscaled to 4 bits."""
    if swap_rb:
        r, b = b, r
    return ((a >> 4) << 12) | ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4)


def rgba_to_alpha8(r: int, g: int, b: int, a: int, swap_rb: bool = False) -> int:
    """RGBA8888 → ALPHA_8 (8-bit). Returns alpha channel only."""
    return a


# Map pixel format names to their conversion functions
PIXEL_CONVERTERS = {
    "RGB565":    rgba_to_rgb565,
    "ARGB1555":  rgba_to_argb1555,
    "ARGB8888":  rgba_to_argb8888,
    "ARGB_4444": rgba_to_argb4444,
    "ALPHA_8":   rgba_to_alpha8,
}


def pixel_to_lvgl_bytes(value: int, fmt: str) -> list[int]:
    """Convert a packed pixel integer to LVGL uint8_t array bytes (little-endian).

    Returns a list of byte values for one pixel in the uint8_t data array.
    LVGL stores multi-byte pixel formats in little-endian byte order.

    Examples:
      RGB565 value 0xF800 → [0x00, 0xF8] (blue=0, green=0, red=255)
      ARGB8888 value 0xFF00FF00 → [0x00, 0xFF, 0x00, 0xFF] (B,G,R,A LE)
    """
    bpp = PIXEL_FORMATS[fmt]["bpp"]
    return [(value >> (i * 8)) & 0xFF for i in range(bpp)]


def format_pixel_value(value: int, fmt: str) -> str:
    """Format a pixel value as a C hex literal for TFT_eSPI output."""
    bpp = PIXEL_FORMATS[fmt]["bpp"]
    hex_width = bpp * 2  # 2 hex chars per byte
    return f"0x{value:0{hex_width}X}"


# ── Formatting Helpers ──────────────────────────────────────────────

def format_hex_array(hex_values, cols: int = 16) -> str:
    """Format hex values into a nicely aligned C array."""
    lines = []
    for i in range(0, len(hex_values), cols):
        chunk = hex_values[i : i + cols]
        line = "\t" + ", ".join(chunk)
        if i + cols < len(hex_values):
            line += ","
        lines.append(line)
    return "\n".join(lines)


# ── File Name Sanitization ──────────────────────────────────────────

def sanitize_c_name(name: str) -> str:
    """Convert a filename stem to a valid C variable name."""
    name = re.sub(r"[^a-zA-Z0-9]", "_", name)
    if name and name[0].isdigit():
        name = "_" + name
    name = re.sub(r"_+", "_", name)
    return name.strip("_") or "image"


# ── TFT_eSPI Format ─────────────────────────────────────────────────

def generate_tft_espi(
    img: Image.Image,
    name: str,
    pixel_fmt: str,
    swap_rb: bool = False,
) -> tuple[str, str]:
    """Generate TFT_eSPI-compatible .h and .c files.

    Returns (header_content, source_content).

    The .h declares an image struct with a typed pixel array.
    The struct type varies with the pixel format:
      - 16-bit formats (RGB565, ARGB1555, ARGB_4444) → image_t with uint16_t[]
      - 32-bit format  (ARGB8888) → image32_t with uint32_t[]
      - 8-bit format   (ALPHA_8)  → image8_t with uint8_t[]
    """
    fmt_info = PIXEL_FORMATS[pixel_fmt]
    c_type = fmt_info["c_type"]
    converter = PIXEL_CONVERTERS[pixel_fmt]

    # Choose struct name based on c_type
    if c_type == "uint16_t":
        struct_name = "image_t"
    elif c_type == "uint32_t":
        struct_name = "image32_t"
    else:
        struct_name = "image8_t"

    img = img.convert("RGBA")
    width, height = img.size
    pixels = img.load()

    # Build pixel value array
    hex_values = []
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            value = converter(r, g, b, a, swap_rb)
            hex_values.append(format_pixel_value(value, pixel_fmt))

    pixels_str = format_hex_array(hex_values)

    header_guard = f"IMG_{name.upper()}_H"

    swap_note = " (BGR swap enabled)" if swap_rb else ""

    header = f"""#ifndef {header_guard}
#define {header_guard}

#ifdef __cplusplus
extern "C" {{
#endif

#include <stdint.h>

/* Image: {name}  [{width}x{height}]  Format: {pixel_fmt}{swap_note} */
typedef struct {{
    int width;
    int height;
    const {c_type} pixels[];
}} {struct_name};

extern const {struct_name} {name};

#ifdef __cplusplus
}}
#endif

#endif /* {header_guard} */
"""

    source = f"""#include "{name}.h"

/* {width}x{height} - {pixel_fmt}{swap_note} */
const {struct_name} {name} = {{
    {width},
    {height},
    {{
{pixels_str}
    }}
}};
"""
    return header, source


# ── LVGL Format ─────────────────────────────────────────────────────

def generate_lvgl(
    img: Image.Image,
    name: str,
    pixel_fmt: str,
    swap_rb: bool = False,
) -> tuple[str, str]:
    """Generate LVGL-compatible .h and .c files.

    Returns (header_content, source_content).

    LVGL v9 color format constants used:
      RGB565    → LV_COLOR_FORMAT_RGB565   (2 bytes/pixel, LE)
      ARGB1555  → LV_COLOR_FORMAT_ARGB1555  (2 bytes/pixel, LE)
      ARGB8888  → LV_COLOR_FORMAT_ARGB8888  (4 bytes/pixel, LE)
      ARGB_4444 → LV_COLOR_FORMAT_ARGB4444  (2 bytes/pixel, LE)
      ALPHA_8   → LV_COLOR_FORMAT_A8        (1 byte/pixel)

    All pixel data is stored as uint8_t array with little-endian byte order.
    """
    fmt_info = PIXEL_FORMATS[pixel_fmt]
    lvgl_cf = fmt_info["lvgl_cf"]
    converter = PIXEL_CONVERTERS[pixel_fmt]

    img = img.convert("RGBA")
    width, height = img.size
    pixels = img.load()

    # Build uint8_t byte array
    byte_values = []
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            value = converter(r, g, b, a, swap_rb)
            le_bytes = pixel_to_lvgl_bytes(value, pixel_fmt)
            byte_values.extend(f"0x{b:02X}" for b in le_bytes)

    map_name = f"{name}_map"
    img_name = name
    bytes_str = format_hex_array(byte_values, cols=16)

    header_guard = f"IMG_{name.upper()}_H"
    swap_note = " (BGR swap enabled)" if swap_rb else ""

    header = f"""#ifndef {header_guard}
#define {header_guard}

/* LVGL image header for '{name}' — do not modify by hand */
/* {width}x{height}  Format: {pixel_fmt}{swap_note} */

#ifdef __has_include
    #if __has_include("lvgl.h")
        #ifndef LV_LVGL_H_INCLUDE_SIMPLE
            #define LV_LVGL_H_INCLUDE_SIMPLE
        #endif
    #endif
#endif

#if defined(LV_LVGL_H_INCLUDE_SIMPLE)
    #include "lvgl.h"
#else
    #include "lvgl/lvgl.h"
#endif

#ifndef LV_ATTRIBUTE_MEM_ALIGN
#define LV_ATTRIBUTE_MEM_ALIGN
#endif

#ifndef LV_ATTRIBUTE_LARGE_CONST
#define LV_ATTRIBUTE_LARGE_CONST
#endif

#ifndef LV_ATTRIBUTE_IMAGE_{name.upper()}
#define LV_ATTRIBUTE_IMAGE_{name.upper()}
#endif

extern const LV_ATTRIBUTE_MEM_ALIGN LV_ATTRIBUTE_LARGE_CONST
    LV_ATTRIBUTE_IMAGE_{name.upper()} uint8_t {map_name}[];

extern const lv_image_dsc_t {img_name};

#endif /* {header_guard} */
"""

    source = f"""#include "{name}.h"

/* {width}x{height} - {pixel_fmt}{swap_note} */
const LV_ATTRIBUTE_MEM_ALIGN LV_ATTRIBUTE_LARGE_CONST
    LV_ATTRIBUTE_IMAGE_{name.upper()} uint8_t {map_name}[] = {{
{bytes_str}
}};

const lv_image_dsc_t {img_name} = {{
    .header = {{
        .cf = {lvgl_cf},
        .always_zero = 0,
        .reserved = 0,
        .w = {width},
        .h = {height},
    }},
    .data_size = sizeof({map_name}),
    .data = {map_name},
}};
"""
    return header, source


# ── Single Image Converter ──────────────────────────────────────────

def convert_image(
    input_path: str,
    output_dir: str,
    fmt: str,
    pixel_fmt: str,
    swap_rb: bool = False,
    prefix: str | None = None,
) -> str:
    """Convert a single image file to C source + header."""
    stem = os.path.splitext(os.path.basename(input_path))[0]
    name = prefix if prefix else sanitize_c_name(stem)

    img = Image.open(input_path)

    if fmt == "lvgl":
        header, source = generate_lvgl(img, name, pixel_fmt, swap_rb)
    elif fmt == "tft_espi":
        header, source = generate_tft_espi(img, name, pixel_fmt, swap_rb)
    else:
        raise ValueError(f"Unknown format: {fmt}")

    # Auto-detect alpha presence for informational output
    rgba = img.convert("RGBA")
    has_alpha_data = rgba.getextrema()[3][0] < 255  # alpha min < 255
    alpha_note = " (alpha in source)" if has_alpha_data else ""

    os.makedirs(output_dir, exist_ok=True)
    h_path = os.path.join(output_dir, f"{name}.h")
    c_path = os.path.join(output_dir, f"{name}.c")

    with open(h_path, "w", encoding="utf-8") as f:
        f.write(header)
    with open(c_path, "w", encoding="utf-8") as f:
        f.write(source)

    print(f"  {input_path} -> {name}.h + {name}.c  [{pixel_fmt}{alpha_note}]")

    return name


# ── Confirmation Gate ───────────────────────────────────────────────

def print_summary(args, image_files: list[str], output_dir: str):
    """Print the operation summary banner. Used for both interactive and
    non-interactive modes so the user always sees what will happen."""
    fmt_info = PIXEL_FORMATS[args.pixel_format]
    bpp = fmt_info["bpp"]

    img_details = []
    total_pixels = 0
    for f in image_files:
        try:
            img = Image.open(f)
            w, h = img.size
            img_details.append((os.path.basename(f), w, h))
            total_pixels += w * h
            img.close()
        except Exception:
            img_details.append((os.path.basename(f), "?", "?"))

    total_bytes = total_pixels * bpp
    if total_bytes >= 1024 * 1024:
        size_str = f"{total_bytes / (1024 * 1024):.1f} MB ({total_bytes:,} bytes)"
    elif total_bytes >= 1024:
        size_str = f"{total_bytes / 1024:.1f} KB ({total_bytes:,} bytes)"
    else:
        size_str = f"{total_bytes} bytes"

    print()
    print("=" * 62)
    print("  ESP32 Image to C Header Converter")
    print("=" * 62)
    print(f"  Input:           {args.input}")
    print(f"  Output dir:      {output_dir}")
    print(f"  Output format:   {args.format}")
    print(f"  Pixel format:    {args.pixel_format} ({bpp} bytes/pixel)")
    if args.swap_rb:
        print(f"  RGB swap:        YES (BGR mode)")
    if args.prefix:
        print(f"  Name prefix:     {args.prefix}")
    print(f"  Est. data size:  {size_str}")
    print(f"  Images found:    {len(image_files)}")

    # Show per-image details
    max_name_len = max(len(name) for name, _, _ in img_details) if img_details else 0
    for name, w, h in img_details:
        if w != "?":
            print(f"    - {name:<{max_name_len}}  {w}×{h}  →  {name.rsplit('.', 1)[0]}.h/.c")
        else:
            print(f"    - {name:<{max_name_len}}  (unknown)")
    print("=" * 62)


def confirm_operation(args, image_files: list[str], output_dir: str) -> bool:
    """Show operation summary and ask for confirmation before proceeding.

    In interactive mode (TTY): prints summary, prompts [y/N], waits for input.
    In non-interactive mode (no TTY): prints summary, then aborts with a clear
    message instructing the user to re-run with --yes.

    Returns True if user confirms, False to abort.
    """
    print_summary(args, image_files, output_dir)

    if args.yes:
        print("  ✓ Auto-confirmed (--yes flag set)")
        print()
        return True

    # Check whether we have a real terminal to read from
    if not sys.stdin.isatty():
        print()
        print("  ⚠  Non-interactive mode — no terminal available for confirmation.")
        print("  To proceed, re-run with the --yes / -y flag:")
        print(f"    python convert.py -i {args.input} -o {output_dir} "
              f"-f {args.format} -p {args.pixel_format} -y")
        print()
        return False

    try:
        response = input("  Proceed? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n  Aborted by user.")
        return False

    print()
    if response in ("y", "yes"):
        return True
    else:
        print("  ✗ Aborted by user.")
        return False


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convert images to ESP32 C source files (supports multiple pixel formats)"
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="Input image file or directory"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: same as input)"
    )
    parser.add_argument(
        "-f", "--format", choices=["lvgl", "tft_espi"], default="lvgl",
        help="Output format: lvgl or tft_espi (default: lvgl)"
    )
    parser.add_argument(
        "-p", "--pixel-format",
        choices=list(PIXEL_FORMATS.keys()),
        default=DEFAULT_PIXEL_FORMAT,
        help=f"Target pixel format (default: {DEFAULT_PIXEL_FORMAT})"
    )
    parser.add_argument(
        "--swap-rb", action="store_true",
        help="Swap Red and Blue channels (for BGR displays)"
    )
    parser.add_argument(
        "--prefix",
        help="Variable name prefix (default: derived from filename)"
    )
    parser.add_argument(
        "-y", "--yes", action="store_true",
        help="Skip confirmation prompt (for CI/automation)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: Input path not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output_dir = args.output or (
        args.input if os.path.isdir(args.input)
        else os.path.dirname(args.input) or "."
    )

    supported_exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}

    # Gather image files
    if os.path.isfile(args.input):
        ext = os.path.splitext(args.input)[1].lower()
        if ext not in supported_exts:
            print(f"ERROR: Unsupported format: {ext}", file=sys.stderr)
            sys.exit(1)
        image_files = [args.input]

    elif os.path.isdir(args.input):
        image_files = sorted(
            os.path.join(args.input, f)
            for f in os.listdir(args.input)
            if os.path.splitext(f)[1].lower() in supported_exts
        )
        if not image_files:
            print(f"No supported images found in: {args.input}")
            sys.exit(0)

    else:
        print(f"ERROR: Input is neither file nor directory: {args.input}", file=sys.stderr)
        sys.exit(1)

    # ── Confirmation Gate ──────────────────────────────────────────
    if not confirm_operation(args, image_files, output_dir):
        sys.exit(0)

    # ── Convert ────────────────────────────────────────────────────
    fmt_desc = args.format
    if fmt_desc == "lvgl":
        fmt_desc = "lvgl"
    else:
        fmt_desc = "tft_espi"

    swap_flag = ", swap_rb" if args.swap_rb else ""

    print(f"Converting {len(image_files)} image(s) from {args.input} → {output_dir}")
    print(f"  [format={fmt_desc}, pixel={args.pixel_format}{swap_flag}]")
    print()

    for f in image_files:
        convert_image(
            f, output_dir, args.format,
            args.pixel_format, args.swap_rb, args.prefix
        )

    print(f"\nDone. {len(image_files)} file(s) converted.")


if __name__ == "__main__":
    main()
