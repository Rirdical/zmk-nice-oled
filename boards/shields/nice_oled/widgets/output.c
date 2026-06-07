#include "output.h"
// #include "../assets/custom_fonts.h"
#include <fonts.h>
#include <zephyr/kernel.h>

LV_IMG_DECLARE(bt_no_signal);
LV_IMG_DECLARE(bt_unbonded);
LV_IMG_DECLARE(bt);
LV_IMG_DECLARE(usb);

#if !IS_ENABLED(CONFIG_ZMK_SPLIT) || IS_ENABLED(CONFIG_ZMK_SPLIT_ROLE_CENTRAL)
static void draw_usb_connected(lv_obj_t *canvas) {
    lv_draw_image_dsc_t img_dsc;
    lv_draw_image_dsc_init(&img_dsc);

    { lv_obj_t *_img = lv_image_create(lv_obj_get_parent(canvas));
  lv_image_set_src(_img, &usb);
  lv_obj_set_pos(_img, CONFIG_NICE_OLED_WIDGET_OUTPUT_USB_CUSTOM_X, CONFIG_NICE_OLED_WIDGET_OUTPUT_USB_CUSTOM_Y); }
}

static void draw_ble_unbonded(lv_obj_t *canvas) {
    lv_draw_image_dsc_t img_dsc;
    lv_draw_image_dsc_init(&img_dsc);

    { lv_obj_t *_img = lv_image_create(lv_obj_get_parent(canvas));
  lv_image_set_src(_img, &bt_unbonded);
  lv_obj_set_pos(_img, CONFIG_NICE_OLED_WIDGET_OUTPUT_BT_UNBONDED_CUSTOM_X, CONFIG_NICE_OLED_WIDGET_OUTPUT_BT_UNBONDED_CUSTOM_Y); }
}
#endif

static void draw_ble_disconnected(lv_obj_t *canvas) {
    lv_draw_image_dsc_t img_dsc;
    lv_draw_image_dsc_init(&img_dsc);

    { lv_obj_t *_img = lv_image_create(lv_obj_get_parent(canvas));
  lv_image_set_src(_img, &bt_no_signal);
  lv_obj_set_pos(_img, CONFIG_NICE_OLED_WIDGET_OUTPUT_BT_CUSTOM_X, CONFIG_NICE_OLED_WIDGET_OUTPUT_BT_CUSTOM_Y); }
}

static void draw_ble_connected(lv_obj_t *canvas) {
    lv_draw_image_dsc_t img_dsc;
    lv_draw_image_dsc_init(&img_dsc);

    { lv_obj_t *_img = lv_image_create(lv_obj_get_parent(canvas));
  lv_image_set_src(_img, &bt);
  lv_obj_set_pos(_img, CONFIG_NICE_OLED_WIDGET_OUTPUT_BT_CUSTOM_X, CONFIG_NICE_OLED_WIDGET_OUTPUT_BT_CUSTOM_Y); }
}

void draw_output_status(lv_obj_t *canvas, const struct status_state *state) {
#if IS_ENABLED(CONFIG_NICE_EPAPER_ON) &&                                                           \
    !IS_ENABLED(CONFIG_NICE_OLED_WIDGET_CENTRAL_SHOW_BATTERY_PERIPHERAL_ALL)
    lv_draw_label_dsc_t label_dsc;
    init_label_dsc(&label_dsc, LVGL_FOREGROUND, &pixel_operator_mono_16, LV_TEXT_ALIGN_LEFT);
    { lv_obj_t * _lbl = lv_label_create(canvas);
  lv_label_set_text(_lbl, "SIG");
  lv_obj_set_pos(_lbl, 0, 1); }

#if IS_ENABLED(CONFIG_NICE_OLED_WIDGET_OUTPUT_BACKGROUND)
    lv_draw_rect_dsc_t rect_white_dsc;
    init_rect_dsc(&rect_white_dsc, LVGL_FOREGROUND);
    lv_canvas_fill_bg(canvas, lv_color_black(), LV_OPA_COVER);
#endif

#else

#if IS_ENABLED(CONFIG_NICE_OLED_WIDGET_OUTPUT_BACKGROUND)
    lv_draw_rect_dsc_t rect_white_dsc;
    init_rect_dsc(&rect_white_dsc, LVGL_FOREGROUND);
    lv_canvas_fill_bg(canvas, lv_color_black(), LV_OPA_COVER);
#endif

#endif // CONFIG_NICE_EPAPER_ON

#if !IS_ENABLED(CONFIG_ZMK_SPLIT) || IS_ENABLED(CONFIG_ZMK_SPLIT_ROLE_CENTRAL)
    switch (state->selected_endpoint.transport) {
    case ZMK_TRANSPORT_USB:
        draw_usb_connected(canvas);
        break;

    case ZMK_TRANSPORT_BLE:
        if (state->active_profile_bonded) {
            if (state->active_profile_connected) {
                draw_ble_connected(canvas);
            } else {
                draw_ble_disconnected(canvas);
            }
        } else {
            draw_ble_unbonded(canvas);
        }
        break;
    }
#else
    if (state->connected) {
        draw_ble_connected(canvas);
    } else {
        draw_ble_disconnected(canvas);
    }
#endif
}
