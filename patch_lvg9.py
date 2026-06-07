#!/usr/bin/env python3
import re
import glob

def patch_file(path):
    with open(path, 'r') as f:
        text = f.read()

    original = text

    # ========== 1. GLOBAL TYPE RENAMES ==========
    text = text.replace('lv_img_dsc_t', 'lv_image_dsc_t')
    text = text.replace('lv_draw_img_dsc_t', 'lv_draw_image_dsc_t')
    text = text.replace('lv_draw_img_dsc_init', 'lv_draw_image_dsc_init')
    text = text.replace('lv_img_create', 'lv_image_create')
    text = text.replace('lv_img_set_src', 'lv_image_set_src')
    text = text.replace('lv_img_set_pivot', 'lv_image_set_pivot')

    # ========== 2. COLOR FORMAT CONSTANTS ==========
    text = text.replace('LV_IMG_CF_INDEXED_1BIT', 'LV_COLOR_FORMAT_I1')
    text = text.replace('LV_IMG_CF_TRUE_COLOR_ALPHA', 'LV_COLOR_FORMAT_NATIVE_WITH_ALPHA')
    text = text.replace('LV_IMG_CF_TRUE_COLOR', 'LV_COLOR_FORMAT_NATIVE')
    text = text.replace('LV_IMG_CF_ALPHA_1BIT', 'LV_COLOR_FORMAT_A1')
    text = text.replace('LV_IMG_CF_ALPHA_2BIT', 'LV_COLOR_FORMAT_A2')
    text = text.replace('LV_IMG_CF_ALPHA_4BIT', 'LV_COLOR_FORMAT_A4')
    text = text.replace('LV_IMG_CF_ALPHA_8BIT', 'LV_COLOR_FORMAT_A8')
    text = text.replace('LV_IMG_CF_INDEXED_2BIT', 'LV_COLOR_FORMAT_I2')
    text = text.replace('LV_IMG_CF_INDEXED_4BIT', 'LV_COLOR_FORMAT_I4')
    text = text.replace('LV_IMG_CF_INDEXED_8BIT', 'LV_COLOR_FORMAT_I8')

    # ========== 3. FIX IMAGE HEADER STRUCTS (assets) ==========
    # Pattern A: old format with always_zero and reserved
    pattern_a = re.compile(
        r'\.header\.cf = ([^,]+),\s*'
        r'\.header\.always_zero = 0,\s*'
        r'\.header\.reserved = 0,\s*'
        r'\.header\.w = (\d+),\s*'
        r'\.header\.h = (\d+),'
    )
    
    def repl_a(m):
        cf = m.group(1)
        w = int(m.group(2))
        h = int(m.group(3))
        stride = (w + 7) // 8
        return (
            f'.header.magic = LV_IMAGE_HEADER_MAGIC,\n'
            f'  .header.cf = {cf},\n'
            f'  .header.flags = 0,\n'
            f'  .header.w = {w},\n'
            f'  .header.h = {h},\n'
            f'  .header.stride = {stride},'
        )
    
    text = pattern_a.sub(repl_a, text)

    # Pattern B: format with just w/h (no always_zero/reserved) - for luna_images.c
    pattern_b = re.compile(
        r'\.header\.cf = ([^,]+),\s*'
        r'\.header\.w = (\d+),\s*'
        r'\.header\.h = (\d+),'
    )
    
    def repl_b(m):
        cf = m.group(1)
        w = int(m.group(2))
        h = int(m.group(3))
        stride = (w + 7) // 8
        return (
            f'.header.magic = LV_IMAGE_HEADER_MAGIC,\n'
            f'  .header.cf = {cf},\n'
            f'  .header.flags = 0,\n'
            f'  .header.w = {w},\n'
            f'  .header.h = {h},\n'
            f'  .header.stride = {stride},'
        )
    
    text = pattern_b.sub(repl_b, text)

    # ========== 4. FIX lv_canvas_draw_text (removed in LVGL 9) ==========
    # Replace: lv_canvas_draw_text(canvas, x, y, width, &dsc, text);
    # With:   { lv_obj_t * _lbl = lv_label_create(canvas); lv_label_set_text(_lbl, text); lv_obj_set_pos(_lbl, x, y); }
    canvas_pattern = re.compile(
        r'lv_canvas_draw_text\('
        r'([^,]+),\s*'           # canvas
        r'([^,]+),\s*'           # x
        r'([^,]+),\s*'           # y
        r'([^,]+),\s*'           # width
        r'&([^,]+),\s*'          # &dsc
        r'([^)]+)\)'             # text
        r'\s*;'
    )
    
    def repl_canvas(m):
        canvas = m.group(1).strip()
        x = m.group(2).strip()
        y = m.group(3).strip()
        text_var = m.group(6).strip()
        return (
            f'{{ lv_obj_t * _lbl = lv_label_create({canvas});\n'
            f'  lv_label_set_text(_lbl, {text_var});\n'
            f'  lv_obj_set_pos(_lbl, {x}, {y}); }}'
        )
    
    text = canvas_pattern.sub(repl_canvas, text)

    if text != original:
        with open(path, 'w') as f:
            f.write(text)
        print(f'✅ Patched: {path}')
    else:
        print(f'⏭️  No changes: {path}')

# Patch ALL .c and .h files in the nice_oled shield
files = glob.glob('boards/shields/nice_oled/**/*.c', recursive=True)
files += glob.glob('boards/shields/nice_oled/**/*.h', recursive=True)

if not files:
    print("❌ No files found. Make sure you're in the zmk-nice-oled root.")
else:
    for f in files:
        patch_file(f)
    print(f"\n✅ Done. Processed {len(files)} files.")
