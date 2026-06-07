#!/usr/bin/env python3
import re

def patch_file(path):
    with open(path, 'r') as f:
        text = f.read()

    original = text

    # ========== 1. FIX lv_canvas_draw_rect ==========
    # Replace: lv_canvas_draw_rect(canvas, 0, 0, WIDTH, HEIGHT, &dsc);
    # With:    lv_canvas_fill_bg(canvas, lv_color_black(), LV_OPA_COVER);
    text = re.sub(
        r'lv_canvas_draw_rect\([^)]+\);',
        'lv_canvas_fill_bg(canvas, lv_color_black(), LV_OPA_COVER);',
        text
    )

    # ========== 2. FIX lv_canvas_draw_image / lv_canvas_draw_img ==========
    # Replace canvas image drawing with regular lv_image child creation
    # Pattern: lv_canvas_draw_img(canvas, x, y, &img, &dsc);
    # or:     lv_canvas_draw_image(canvas, x, y, &img, &dsc);  (from previous patch)
    
    # Handle the rotate_canvas case (x=0, y=0, dsc=NULL)
    text = re.sub(
        r'lv_canvas_draw_image\(canvas,\s*0,\s*0,\s*&img,\s*NULL\)[^;]*;',
        '/* rotation not supported in LVGL 9 */',
        text
    )
    
    # Handle battery.c / output.c cases
    # Pattern: lv_canvas_draw_image(canvas, X, Y, &NAME, &img_dsc);
    text = re.sub(
        r'lv_canvas_draw_image\(([^,]+),\s*([^,]+),\s*([^,]+),\s*&([^,]+),\s*&([^)]+)\);',
        r'{ lv_obj_t *_img = lv_image_create(lv_obj_get_parent(\1));\n'
        r'  lv_image_set_src(_img, &\4);\n'
        r'  lv_obj_set_pos(_img, \2, \3); }',
        text
    )

    # ========== 3. FIX rotate_canvas function body ==========
    # If the function still has code that tries to draw, replace the whole body
    text = re.sub(
        r'(void\s+rotate_canvas\s*\([^)]*\)\s*\{)\s*'
        r'(?:[^}]*?)'
        r'(\})',
        r'\1\n  /* Rotation not supported in LVGL 9 */\n\2',
        text,
        flags=re.DOTALL
    )

    if text != original:
        with open(path, 'w') as f:
            f.write(text)
        print(f'✅ Patched: {path}')
        return True
    else:
        print(f'⏭️  No changes: {path}')
        return False

# Patch the three widget files
for f in [
    'boards/shields/nice_oled/widgets/battery.c',
    'boards/shields/nice_oled/widgets/output.c',
    'boards/shields/nice_oled/widgets/util.c'
]:
    patch_file(f)

print("\nDone. Commit and push these changes.")
