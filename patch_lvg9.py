#!/usr/bin/env python3
import re
import glob

def patch_file(path):
    with open(path, 'r') as f:
        text = f.read()

    original = text

    # ========== 1. SIMPLE STRING REPLACEMENTS ==========
    # Types
    text = text.replace('lv_img_dsc_t', 'lv_image_dsc_t')
    text = text.replace('lv_draw_img_dsc_t', 'lv_draw_image_dsc_t')
    text = text.replace('lv_draw_img_dsc_init', 'lv_draw_image_dsc_init')
    
    # Functions
    text = text.replace('lv_img_create', 'lv_image_create')
    text = text.replace('lv_img_set_src', 'lv_image_set_src')
    text = text.replace('lv_img_set_pivot', 'lv_image_set_pivot')
    text = text.replace('lv_img_set_angle', 'lv_image_set_rotation')
    text = text.replace('lv_img_set_zoom', 'lv_image_set_scale')
    text = text.replace('lv_canvas_draw_img', 'lv_canvas_draw_image')
    text = text.replace('lv_img_set_antialias', 'lv_image_set_antialias')
    text = text.replace('lv_img_set_offset_x', 'lv_image_set_offset_x')
    text = text.replace('lv_img_set_offset_y', 'lv_image_set_offset_y')
    text = text.replace('lv_img_set_size_mode', 'lv_image_set_size_mode')
    
    # Constants
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
    text = text.replace('LV_IMG_ZOOM_NONE', 'LV_ZOOM_NONE')

    # Remove old header fields (must happen BEFORE regex)
    text = text.replace('.header.always_zero = 0,', '')
    text = text.replace('.header.reserved = 0,', '')
    text = text.replace('.header.reserved2 = 0,', '')

    # ========== 2. REGEX: FIX IMAGE HEADER STRUCTS ==========
    # Match .header.cf = ... followed by .header.w = ... and .header.h = ...
    pattern = re.compile(
        r'(\s*\.header\.cf = [^,]+,)\s*'
        r'(\s*\.header\.w = \d+,)\s*'
        r'(\s*\.header\.h = \d+,)'
    )
    
    def repl_header(m):
        cf_line = m.group(1).strip()
        w_line = m.group(2).strip()
        h_line = m.group(3).strip()
        
        w = int(re.search(r'w = (\d+)', w_line).group(1))
        h = int(re.search(r'h = (\d+)', h_line).group(1))
        stride = (w + 7) // 8
        cf_val = re.search(r'cf = ([^,]+)', cf_line).group(1)
        
        return (
            f'\n  .header.magic = LV_IMAGE_HEADER_MAGIC,\n'
            f'  .header.cf = {cf_val},\n'
            f'  .header.flags = 0,\n'
            f'  {w_line}\n'
            f'  {h_line}\n'
            f'  .header.stride = {stride},'
        )
    
    text = pattern.sub(repl_header, text)

    # ========== 3. REGEX: FIX lv_canvas_draw_text ==========
    canvas_text_pattern = re.compile(
        r'lv_canvas_draw_text\s*\(\s*'
        r'([^,]+),\s*'
        r'([^,]+),\s*'
        r'([^,]+),\s*'
        r'([^,]+),\s*'
        r'&([^,]+),\s*'
        r'([^)]+)\)\s*;'
    )
    
    def repl_canvas_text(m):
        canvas = m.group(1).strip()
        x = m.group(2).strip()
        y = m.group(3).strip()
        text_var = m.group(6).strip()
        return (
            f'{{ lv_obj_t * _lbl = lv_label_create({canvas});\n'
            f'  lv_label_set_text(_lbl, {text_var});\n'
            f'  lv_obj_set_pos(_lbl, {x}, {y}); }}'
        )
    
    text = canvas_text_pattern.sub(repl_canvas_text, text)

    # ========== 4. REGEX: FIX lv_canvas_transform (9 params, multi-line) ==========
    # lv_canvas_transform(canvas, &img, angle, zoom, offset_x, offset_y, pivot_x, pivot_y, antialias);
    # NOTE: NO simple replacement for lv_canvas_transform - only regex handles it
    transform_pattern = re.compile(
        r'lv_canvas_transform\s*\(\s*'
        r'([^,]+),\s*'      # 1. canvas
        r'&([^,]+),\s*'     # 2. &img
        r'([^,]+),\s*'     # 3. angle
        r'([^,]+),\s*'     # 4. zoom
        r'([^,]+),\s*'     # 5. offset_x
        r'([^,]+),\s*'     # 6. offset_y
        r'([^,]+),\s*'     # 7. pivot_x
        r'([^,]+),\s*'     # 8. pivot_y
        r'([^)]+)\)'       # 9. antialias
        r'\s*;',
        re.DOTALL
    )
    
    def repl_transform(m):
        canvas = m.group(1).strip()
        img = m.group(2).strip()
        return f'lv_canvas_draw_image({canvas}, 0, 0, &{img}, NULL);  /* rotation removed in LVGL 9 */'
    
    text = transform_pattern.sub(repl_transform, text)

    if text != original:
        with open(path, 'w') as f:
            f.write(text)
        print(f'✅ Patched: {path}')
        return True
    else:
        print(f'⏭️  No changes: {path}')
        return False

# Patch ALL .c and .h files in the nice_oled shield
files = glob.glob('boards/shields/nice_oled/**/*.c', recursive=True)
files += glob.glob('boards/shields/nice_oled/**/*.h', recursive=True)

patched = 0
if not files:
    print("❌ No files found. Are you in the zmk-nice-oled root folder?")
    print("   Run: cd zmk-nice-oled")
else:
    for f in files:
        if patch_file(f):
            patched += 1
    print(f"\n✅ Done. Patched {patched}/{len(files)} files.")
