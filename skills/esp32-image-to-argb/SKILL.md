---
name: esp32-image-to-argb
description: >
  Convert PNG/JPG images to ESP32-compatible C source files for LVGL or TFT_eSPI.
  Supports multiple pixel formats: RGB565, ARGB1555, ARGB8888, ARGB_4444, ALPHA_8.
  Use this whenever the user mentions converting images for ESP32, generating C
  arrays from image files, pixel format conversion for embedded displays, creating
  LVGL image assets, converting pictures to microcontroller C headers, or preparing
  display assets for ESP32/Arduino projects. Triggers on phrases like "convert image
  to RGB565", "generate LVGL image", "ESP32 image to C array", "TFT_eSPI image
  conversion", "convert PNG to C header for microcontroller", "ARGB8888 for ESP32",
  "image pixel format", and any request involving image-to-header conversion for
  embedded systems.
---

# ESP32 Image to C Header Converter

Convert PNG, JPG, BMP, GIF, or WebP images into C source files for ESP32
display projects. Generates both LVGL (`lv_image_dsc_t`) and TFT_eSPI output
in your choice of pixel format.

## ⚠️ Confirmation Gate (MANDATORY)

**Before running the script, you MUST confirm the operation with the user.**

Follow this exact workflow for every conversion:

1. **Gather parameters** from the user's request:
   - Input path (image file or directory)
   - Output directory (default: same as input)
   - Output format (`lvgl` or `tft_espi`, default: `lvgl`)
   - Pixel format (default: `RGB565`)
   - Whether to swap R/B channels (`--swap-rb`)
   - Variable name prefix (`--prefix`, optional)

2. **Show the summary** to the user using this exact template:

   ```
   ==============================================================
     ESP32 Image to C Header Converter
   ==============================================================
     Input:           /path/to/input
     Output dir:      /path/to/output
     Output format:   lvgl
     Pixel format:    RGB565 (2 bytes/pixel)
     Image:           icon.png (64×64) → icon.h + icon.c
   ==============================================================
     Proceed? [y/N]:
   ```

   If there are multiple images, list each one with dimensions.

3. **Wait for user confirmation.** Do NOT run the script until the user says yes.

4. **Run with `-y` flag** only after user confirms:
   ```bash
   python scripts/convert.py -i icon.png -o ./output -f lvgl -p RGB565 -y
   ```

   The `-y` flag is required because the script runs in a non-interactive
   subprocess without a terminal. The script will refuse to proceed without
   it in non-TTY mode.

**Why this matters:** Converting images to C arrays overwrites existing files.
Always confirm before writing.

## Quick Start

### Step 1: Determine output format

Check the project for clues about which display library is in use:

| Signal | Format to use |
|--------|--------------|
| `#include "lvgl.h"` or `lv_image_dsc_t` | `lvgl` |
| `tft.pushImage(...)` or TFT_eSPI references | `tft_espi` |
| No clear signal — ask the user | Default to `lvgl` |

### Step 2: Choose pixel format

| Format | Bits/pixel | Alpha | Best for |
|--------|-----------|-------|----------|
| **RGB565** (default) | 16 bits (2 bytes) | No | TFT displays, LVGL, general use |
| **ARGB1555** | 16 bits (2 bytes) | 1-bit | Simple transparency on 16-bit displays |
| **ARGB_4444** | 16 bits (2 bytes) | 4-bit | Legacy transparency |
| **ARGB8888** | 32 bits (4 bytes) | 8-bit | High-quality with full alpha, LVGL |
| **ALPHA_8** | 8 bits (1 byte) | 8-bit | Alpha masks only (no color) |

If no format is specified, **RGB565** is used as the default.

### Step 3: Confirm with user (see Confirmation Gate above)

Show the summary template to the user. Wait for them to say yes.

### Step 4: Run the script

Always include the `-y` flag since the script will be run in a non-interactive
subprocess (it will refuse without it when no terminal is available):

```bash
python <skill-dir>/scripts/convert.py \
  -i <path-to-image-or-directory> \
  -o <output-directory> \
  -f <lvgl|tft_espi> \
  -p <pixel-format> \
  -y
```

**Single image:**
```bash
python scripts/convert.py -i bird.png -o ./generated/ -f lvgl -y
# Produces: bird.h + bird.c  (RGB565 by default)
```

**With ARGB8888 format:**
```bash
python scripts/convert.py -i icon.png -f lvgl -p ARGB8888 -y
# Produces: icon.h + icon.c  (ARGB8888, 4 bytes/pixel)
```

**Batch directory:**
```bash
python scripts/convert.py -i ./assets/ -o ./generated/ -f tft_espi -p ARGB1555 -y
# Produces: one .h/.c pair per image found
```

**BGR swap** (for displays with BGR565 instead of RGB565):
```bash
python scripts/convert.py -i icon.png -f lvgl --swap-rb -y
```

### Step 5: Verify output

Check the generated `.h` and `.c` files. The variable name is derived from the
filename (special characters replaced with underscores). To override, use
`--prefix <name>` before running.

## Script Reference

### All options

```
-i, --input        Input image file or directory (required)
-o, --output       Output directory (default: same as input directory)
-f, --format       lvgl | tft_espi (default: lvgl)
-p, --pixel-format RGB565 | ARGB1555 | ARGB8888 | ARGB_4444 | ALPHA_8
                   (default: RGB565)
--swap-rb          Swap Red and Blue channels (for BGR displays)
--prefix NAME      Variable name prefix (default: derived from filename)
-y, --yes          Skip confirmation (required for automated/non-TTY runs)
```

### Script confirmation behavior

When run **with a real terminal** (manual use), you can omit `-y` to get an
interactive prompt:

```bash
python scripts/convert.py -i icon.png -o ./output -f lvgl
# Shows summary, then asks: Proceed? [y/N]:
```

When run **without a terminal** (via AI agent, CI, pipe), the script shows the
summary, then aborts with instructions to use `-y`. Always use `-y` when
running from a subprocess.

## Output Formats

### LVGL Format (`-f lvgl`)

Generates files compatible with **LVGL v9**:

```c
// icon.h — includes and extern declarations
extern const uint8_t icon_map[];
extern const lv_image_dsc_t icon;

// icon.c — pixel data + descriptor
const uint8_t icon_map[] = { /* bytes in little-endian */ };
const lv_image_dsc_t icon = {
    .header = { .cf = LV_COLOR_FORMAT_RGB565, .w = 64, .h = 64 },
    .data_size = sizeof(icon_map),
    .data = icon_map,
};
```

**LVGL color format constants by pixel format:**

| `-p` option | LVGL Constant | Bytes/pixel |
|-------------|---------------|-------------|
| RGB565 | `LV_COLOR_FORMAT_RGB565` | 2 |
| ARGB1555 | `LV_COLOR_FORMAT_ARGB1555` | 2 |
| ARGB8888 | `LV_COLOR_FORMAT_ARGB8888` | 4 |
| ARGB_4444 | `LV_COLOR_FORMAT_ARGB4444` | 2 |
| ALPHA_8 | `LV_COLOR_FORMAT_A8` | 1 |

All pixel data is stored as a `uint8_t` array in little-endian byte order.

### TFT_eSPI Format (`-f tft_espi`)

Generates a self-contained `.h` with the struct definition and a `.c` with the
data. The struct type varies with the pixel format:

- **16-bit formats** (RGB565, ARGB1555, ARGB_4444) → `image_t` with `uint16_t pixels[]`
- **32-bit format** (ARGB8888) → `image32_t` with `uint32_t pixels[]`
- **8-bit format** (ALPHA_8) → `image8_t` with `uint8_t pixels[]`

```c
// icon.h (for RGB565 — 16-bit format)
typedef struct {
    int width;
    int height;
    const uint16_t pixels[];
} image_t;
extern const image_t icon;

// icon.c
const image_t icon = { 64, 64, { 0xF800, 0x07E0, ... } };
```

**Note:** Alpha channel data is included in the pixel values for formats that
support it (ARGB1555, ARGB8888, ARGB_4444). For RGB565 output, alpha is
discarded and all pixels are treated as opaque. For ALPHA_8, only the alpha
channel is stored — no color data.

## Pixel Format Reference

### RGB565 (Default)

```
RRRRR GGGGGG BBBBB
15  11 10   5 4   0
```
- Red:   bits 15-11 (5 bits, from R[7:3])
- Green: bits 10-5  (6 bits, from G[7:2])
- Blue:  bits 4-0   (5 bits, from B[7:3])
- No alpha channel
- Best for TFT color displays
- Memory: 480×800 image = ~750 KB

### ARGB1555

```
A RRRRR GGGGG BBBBB
15 14 10 9   5 4  0
```
- Alpha:  bit 15 (1 if source alpha ≥ 128)
- Red:    bits 14-10 (5 bits)
- Green:  bits 9-5   (5 bits)
- Blue:   bits 4-0   (5 bits)
- Simple on/off transparency

### ARGB8888

```
AAAAAAAA RRRRRRRR GGGGGGGG BBBBBBBB
31    24 23    16 15     8 7      0
```
- Full 8 bits per channel
- Highest quality, largest size
- Memory: 480×800 image = ~1,500 KB
- Each pixel is 4 bytes (32 bits)

### ARGB_4444

```
AAAA RRRR GGGG BBBB
15 12 11  8 7  4 3  0
```
- Each channel: 4 bits (16 levels each)
- Legacy transparency format
- 2 bytes per pixel (same size as RGB565)

### ALPHA_8

```
AAAAAAAA
7      0
```
- Alpha channel only, no color
- 1 byte per pixel
- Useful for masks, blending, fonts

### Little-Endian Byte Order

Multi-byte pixel formats are stored in little-endian byte order within the
`uint8_t` array (LVGL format). The `convert.py` script handles this
automatically.

For TFT_eSPI format, the compiler manages byte order through native C types
(`uint16_t`, `uint32_t`).

### BGR565 Variant (`--swap-rb`)

Some TFT displays use BGR ordering. Enable `--swap-rb` to swap the red and blue
channel positions in the output. This works for all pixel formats with RGB
channels. ALPHA_8 is unaffected (no color channels to swap).

## Dependencies

- **Python 3.8+**
- **Pillow**: `pip install Pillow`

## Edge Cases Handled

| Case | Behavior |
|------|----------|
| Grayscale images (mode L) | Treated as R=G=B=value |
| Paletted images (mode P) | Converted to RGBA first |
| RGBA images with alpha → RGB565 | Alpha discarded |
| RGBA images with alpha → ARGB* | Alpha included in output |
| BMP/GIF/WebP input | Supported via Pillow (same as PNG/JPG) |
| Filenames with special chars | Sanitized to valid C identifiers |
| Empty directory | Prints message and exits cleanly |
| Single image vs directory | Auto-detected from path type |
| Confirmation gate | Shows summary, waits for user input |
| CI/automation | `-y`/`--yes` flag skips confirmation |
