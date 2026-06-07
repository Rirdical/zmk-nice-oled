#!/usr/bin/env python3
import re
import glob
import os

def patch_file(path):
    with open(path, 'r') as f:
        text = f.read()

    # 1. Replace old struct type with new LVGL 9 type
    text = text.replace('lv_img_dsc_t', 'lv_image_dsc_t')
    
    # 2. Replace old color format constant with new one
    text = text.replace('LV_IMG_CF_INDEXED_1BIT', 'LV_COLOR_FORMAT_I1')
    
    # 3. Find old header blocks and replace with new LVGL 9 format
    # This regex matches the old pattern:
    #   .header.cf = ...,
    #   .header.always_zero = 0,
    #   .header.reserved = 0,
    #   .header.w = ...,
    #   .header.h = ...,
    old_pattern = re.compile(
        r'\.header\.cf = ([^,]+),\s*'
        r'\.header\.always_zero = 0,\s*'
        r'\.header\.reserved = 0,\s*'
        r'\.header\.w = (\d+),\s*'
        r'\.header\.h = (\d+),'
    )
    
    def repl(m):
        cf = m.group(1)
        w = int(m.group(2))
        h = int(m.group(3))
        # For 1-bit images, stride = ceil(width / 8)
        stride = (w + 7) // 8
        return (
            f'.header.magic = LV_IMAGE_HEADER_MAGIC,\n'
            f'  .header.cf = {cf},\n'
            f'  .header.flags = 0,\n'
            f'  .header.w = {w},\n'
            f'  .header.h = {h},\n'
            f'  .header.stride = {stride},'
        )
    
    new_text = old_pattern.sub(repl, text)
    
    if new_text != text:
        with open(path, 'w') as f:
            f.write(new_text)
        print(f'✅ Patched: {path}')
    else:
        print(f'⏭️  No changes: {path}')

# Find all .c files in the assets folder
files = glob.glob('boards/shields/nice_oled/assets/*.c')

if not files:
    print("❌ No .c files found in boards/shields/nice_oled/assets/")
    print("   Make sure you are running this script from the zmk-nice-oled root folder.")
else:
    for f in files:
        patch_file(f)
    print(f"\n✅ Done. Processed {len(files)} files.")
